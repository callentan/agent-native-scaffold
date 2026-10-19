import { DOCUMENT, isPlatformBrowser } from '@angular/common';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { DestroyRef, inject, Injectable, InjectionToken, PLATFORM_ID, signal } from '@angular/core';
import { JsonValue, NOOP_PROVIDER, OpenFeature, Provider, ResolutionDetails } from '@openfeature/web-sdk';
import { Subscription, timeout } from 'rxjs';

export type FailureReason = 'invalid-snapshot' | 'degraded' | 'expired' | 'unauthorized' | 'unavailable';
export const FEATURE_TELEMETRY = new InjectionToken<(reason: FailureReason) => void>('FEATURE_TELEMETRY');

export interface UiFeatureSnapshot {
  readonly schemaVersion: 1;
  readonly contextVersion: string;
  readonly evaluatedAt: string;
  readonly expiresAt: string;
  readonly degraded: boolean;
  readonly flags: { readonly checkout_v2: boolean };
}

class InvalidSnapshot extends Error {}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

export function parseSnapshot(value: unknown, expectedContext: string): UiFeatureSnapshot {
  if (!expectedContext || !isRecord(value) || value.schemaVersion !== 1
      || value.contextVersion !== expectedContext
      || typeof value.evaluatedAt !== 'string' || typeof value.expiresAt !== 'string'
      || typeof value.degraded !== 'boolean' || !isRecord(value.flags)
      || typeof value.flags.checkout_v2 !== 'boolean') {
    throw new InvalidSnapshot('Invalid UI feature snapshot.');
  }
  const evaluatedAt = Date.parse(value.evaluatedAt);
  const expiresAt = Date.parse(value.expiresAt);
  if (!Number.isFinite(evaluatedAt) || !Number.isFinite(expiresAt)
      || expiresAt <= evaluatedAt || expiresAt <= Date.now()) {
    throw new InvalidSnapshot('Invalid or expired UI feature snapshot.');
  }
  return {
    schemaVersion: 1,
    contextVersion: expectedContext,
    evaluatedAt: value.evaluatedAt,
    expiresAt: value.expiresAt,
    degraded: value.degraded,
    flags: { checkout_v2: value.flags.checkout_v2 }
  };
}

class UiSnapshotProvider implements Provider {
  readonly metadata = { name: 'BFF UI snapshot' };
  readonly runsOn = 'client' as const;
  constructor(private readonly current: () => UiFeatureSnapshot | null) {}

  resolveBooleanEvaluation(key: string, fallback: boolean): ResolutionDetails<boolean> {
    const snapshot = this.current();
    if (key !== 'checkout_v2') return { value: fallback, reason: 'DEFAULT' };
    if (!snapshot || snapshot.degraded || Date.parse(snapshot.expiresAt) <= Date.now()) {
      return { value: false, reason: 'DEFAULT' };
    }
    return { value: snapshot.flags.checkout_v2, reason: 'STATIC' };
  }
  resolveStringEvaluation(_key: string, fallback: string): ResolutionDetails<string> {
    return { value: fallback, reason: 'DEFAULT' };
  }
  resolveNumberEvaluation(_key: string, fallback: number): ResolutionDetails<number> {
    return { value: fallback, reason: 'DEFAULT' };
  }
  resolveObjectEvaluation<T extends JsonValue>(_key: string, fallback: T): ResolutionDetails<T> {
    return { value: fallback, reason: 'DEFAULT' };
  }
}

@Injectable({ providedIn: 'root' })
export class FeatureSessionService {
  private readonly http = inject(HttpClient);
  private readonly document = inject(DOCUMENT);
  private readonly browser = isPlatformBrowser(inject(PLATFORM_ID));
  private readonly report = inject(FEATURE_TELEMETRY);
  private readonly mutableState = signal<{
    snapshot: UiFeatureSnapshot | null;
    loading: boolean;
    error: FailureReason | null;
  }>({ snapshot: null, loading: false, error: null });
  readonly state = this.mutableState.asReadonly();
  readonly checkoutV2 = (): boolean => {
    const snapshot = this.state().snapshot;
    if (!snapshot || snapshot.degraded || Date.parse(snapshot.expiresAt) <= Date.now()) return false;
    return this.browser
      ? OpenFeature.getClient('ui').getBooleanValue('checkout_v2', false)
      : snapshot.flags.checkout_v2;
  };
  private readonly provider = new UiSnapshotProvider(() => this.state().snapshot);

  private context: string | null = null;
  private generation = 0;
  private request?: Subscription;
  private expiryTimer?: ReturnType<typeof setTimeout>;
  private refreshTimer?: ReturnType<typeof setTimeout>;
  private destroyed = false;
  private readonly visibilityChanged = () => {
    if (this.document.visibilityState !== 'visible') return;
    const snapshot = this.state().snapshot;
    if (snapshot && Date.parse(snapshot.expiresAt) <= Date.now()) this.invalidate('expired');
    this.refresh();
  };

  constructor() {
    if (this.browser) {
      // One synchronous provider per browser app; refreshes replace state, not providers.
      OpenFeature.setProvider('ui', this.provider);
      this.document.addEventListener('visibilitychange', this.visibilityChanged);
    }
    inject(DestroyRef).onDestroy(() => {
      this.destroyed = true;
      this.generation++;
      this.request?.unsubscribe();
      this.clearTimers();
      this.mutableState.set({ snapshot: null, loading: false, error: null });
      if (this.browser) {
        this.document.removeEventListener('visibilitychange', this.visibilityChanged);
        if (OpenFeature.getProviderMetadata('ui') === this.provider.metadata) {
          OpenFeature.setProvider('ui', NOOP_PROVIDER);
        }
      }
    });
  }

  setSession(contextVersion: string | null, transferredSnapshot?: unknown): void {
    if (this.destroyed) return;
    this.generation++;
    this.context = contextVersion;
    this.request?.unsubscribe();
    this.clearTimers();
    this.mutableState.set({ snapshot: null, loading: false, error: null });
    if (!contextVersion) return;
    if (transferredSnapshot !== undefined && this.accept(transferredSnapshot, contextVersion)) return;
    if (this.browser) this.refresh();
  }

  refresh(): void {
    if (!this.browser || !this.context || this.destroyed) return;
    const context = this.context;
    const generation = ++this.generation;
    this.request?.unsubscribe();
    clearTimeout(this.refreshTimer);
    this.mutableState.update((state) => ({ ...state, loading: true }));
    this.request = this.http.get<unknown>('/api/ui-features').pipe(timeout(2_000)).subscribe({
      next: (value) => {
        if (generation !== this.generation || context !== this.context) return;
        if (!this.accept(value, context)) this.scheduleRefresh();
      },
      error: (error: unknown) => {
        if (generation !== this.generation || context !== this.context) return;
        const unauthorized = error instanceof HttpErrorResponse && [401, 403].includes(error.status);
        this.invalidate(unauthorized ? 'unauthorized' : 'unavailable');
        if (unauthorized) this.context = null;
        else this.scheduleRefresh();
      }
    });
  }

  private accept(value: unknown, context: string): boolean {
    let snapshot: UiFeatureSnapshot;
    try {
      snapshot = parseSnapshot(value, context);
    } catch (error) {
      if (!(error instanceof InvalidSnapshot)) throw error;
      this.invalidate('invalid-snapshot');
      return false;
    }
    if (snapshot.degraded) {
      this.invalidate('degraded');
      this.scheduleRefresh();
      return true;
    }
    this.clearTimers();
    this.mutableState.set({ snapshot, loading: false, error: null });
    if (this.browser) {
      const expire = () => {
        const remaining = Date.parse(snapshot.expiresAt) - Date.now();
        if (remaining > 0) {
          this.expiryTimer = setTimeout(expire, Math.min(remaining, 2_147_483_647));
          return;
        }
        this.invalidate('expired');
        this.refresh();
      };
      this.expiryTimer = setTimeout(expire, Math.min(Date.parse(snapshot.expiresAt) - Date.now(), 2_147_483_647));
      this.scheduleRefresh();
    }
    return true;
  }

  private invalidate(reason: FailureReason): void {
    this.clearTimers();
    this.mutableState.set({ snapshot: null, loading: false, error: reason });
    this.report(reason);
  }

  private scheduleRefresh(): void {
    if (!this.browser || !this.context || this.destroyed) return;
    clearTimeout(this.refreshTimer);
    this.refreshTimer = setTimeout(() => this.refresh(), 15_000);
  }

  private clearTimers(): void {
    clearTimeout(this.expiryTimer);
    clearTimeout(this.refreshTimer);
  }
}
