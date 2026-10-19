import { DOCUMENT, isPlatformBrowser } from '@angular/common';
import { DestroyRef, inject, Injectable, PLATFORM_ID, signal } from '@angular/core';
import { createFlagsmithInstance } from '@flagsmith/flagsmith';
import type { IFlagsmith } from '@flagsmith/flagsmith/types';
import { FlagsmithClientProvider } from '@openfeature/flagsmith-client-provider';
import {
  NOOP_PROVIDER,
  OpenFeature,
  ProviderStatus,
  ProviderEvents
} from '@openfeature/web-sdk';
import {
  DemoUser,
  FrontendState,
  parseDemoUsers,
  parsePublicConfig,
  PublicConfig
} from './demo-contracts';

const DOMAIN = 'poc-ui';
const FLAG_KEY = 'frontend_demo_v2';
const USERS_URL = '/demo-users.json';
const CONFIG_URL = '/poc-config.json';
const REQUEST_TIMEOUT_MS = 2_000;
const REFRESH_INTERVAL_MS = 5_000;
const MAX_FRESH_MS = 15_000;

const fetchWithTimeout: typeof fetch = (input, init) => {
  const inherited = init?.signal
    ?? (input instanceof Request ? input.signal : undefined);
  const signals = [AbortSignal.timeout(REQUEST_TIMEOUT_MS)];
  if (inherited) signals.push(inherited);
  return fetch(input, { ...init, signal: AbortSignal.any(signals) });
};

type AsyncStorageCallback = (error: Error | null, result: string | null) => void;

type DisabledAsyncStorage = {
  readonly getItemSync: (key: string) => null;
  readonly getItem: (key: string, callback?: AsyncStorageCallback) => Promise<null>;
  readonly setItem: (key: string, value: string) => Promise<null>;
};

const disabledAsyncStorage: DisabledAsyncStorage = Object.freeze({
  getItemSync: (_key: string): null => null,
  getItem: async (_key: string, callback?: AsyncStorageCallback): Promise<null> => {
    callback?.(null, null);
    return null;
  },
  setItem: async (_key: string, _value: string): Promise<null> => null
});

const SAFE_STATE: FrontendState = {
  userId: null,
  status: 'loading',
  enabled: false,
  error: null,
  evaluatedAt: null
};

type FlagsmithClientWithAnalyticsInterval = IFlagsmith<string, string> & {
  analyticsInterval: ReturnType<typeof setInterval> | null;
};

function hasAnalyticsInterval(
  client: IFlagsmith<string, string>
): client is FlagsmithClientWithAnalyticsInterval {
  return 'analyticsInterval' in client;
}

@Injectable({ providedIn: 'root' })
export class FeatureDemoService {
  private readonly document = inject(DOCUMENT);
  private readonly browser = isPlatformBrowser(inject(PLATFORM_ID));
  private readonly destroyRef = inject(DestroyRef);
  private readonly userState = signal<readonly DemoUser[]>([]);
  private readonly frontendState = signal<FrontendState>(SAFE_STATE);

  readonly users = this.userState.asReadonly();
  readonly state = this.frontendState.asReadonly();

  private config: PublicConfig | null = null;
  private provider: FlagsmithClientProvider | null = null;
  private nativeClient: IFlagsmith<string, string> | null = null;
  private desiredUser: DemoUser | null = null;
  private initialization: Promise<void> | null = null;
  private sdkQueue: Promise<void> = Promise.resolve();
  private generation = 0;
  private expiryTimer: ReturnType<typeof setTimeout> | undefined;
  private refreshTimer: ReturnType<typeof setTimeout> | undefined;
  private destroyed = false;

  private readonly visibilityChanged = (): void => {
    if (this.destroyed || !this.browser || this.document.visibilityState !== 'visible') return;
    const current = this.state();
    const expired = current.evaluatedAt !== null
      && Date.now() >= current.evaluatedAt + MAX_FRESH_MS;
    if (expired && this.desiredUser) {
      const user = this.desiredUser;
      const generation = ++this.generation;
      this.clearExpiryTimer();
      this.publishError(user, 'Frontend flag decision expired.', false);
      void this.runRefresh(generation, user);
      return;
    }
    void this.refresh();
  };

  constructor() {
    if (this.browser) {
      this.document.addEventListener('visibilitychange', this.visibilityChanged);
    }
    this.destroyRef.onDestroy(() => this.ngOnDestroy());
  }

  async initialize(): Promise<void> {
    if (this.destroyed) return;
    if (this.initialization) return this.initialization;

    this.initialization = this.loadConfiguration()
      .then(async ({ config, users }) => {
        if (this.destroyed) return;
        this.config = config;
        this.userState.set(users);
        this.createProvider(config);
        await this.selectUser(users[0]);
      })
      .catch(() => {
        if (!this.destroyed) {
          this.frontendState.set({
            userId: null,
            status: 'error',
            enabled: false,
            error: 'Frontend configuration is invalid.',
            evaluatedAt: null
          });
        }
      });
    return this.initialization;
  }

  selectUser(user: DemoUser): Promise<void> {
    if (this.destroyed) return Promise.resolve();
    const knownUser = this.userState().find((candidate) => candidate.id === user.id
      && candidate.label === user.label
      && candidate.beta === user.beta);
    if (!knownUser) {
      this.frontendState.set({
        userId: null,
        status: 'error',
        enabled: false,
        error: 'Unknown demo user.',
        evaluatedAt: null
      });
      return Promise.resolve();
    }

    this.desiredUser = knownUser;
    const generation = ++this.generation;
    this.clearTimers();
    this.frontendState.set({
      userId: knownUser.id,
      status: 'loading',
      enabled: false,
      error: null,
      evaluatedAt: null
    });
    if (!this.provider) {
      this.publishError(knownUser, 'Frontend configuration is invalid.', false);
      return Promise.resolve();
    }
    const provider = this.provider;

    return this.enqueue(async () => {
      if (this.destroyed) return;
      try {
        const context = {
          targetingKey: knownUser.id,
          traits: { beta: knownUser.beta }
        };
        if (OpenFeature.getProvider(DOMAIN) !== provider) {
          await OpenFeature.setProviderAndWait(DOMAIN, provider, context);
        } else {
          await OpenFeature.setContext(DOMAIN, context);
        }
        if (this.destroyed) {
          this.stopNativeClient();
          return;
        }
        this.publishIfCurrent(generation, knownUser);
      } catch {
        if (this.destroyed) {
          this.stopNativeClient();
          return;
        }
        if (this.isCurrent(generation, knownUser)) {
          this.publishError(knownUser, 'Frontend flag service is unavailable.', true);
        }
      }
    });
  }

  refresh(): Promise<void> {
    if (this.destroyed || !this.provider || !this.desiredUser) return Promise.resolve();
    return this.runRefresh(this.generation, this.desiredUser);
  }

  enabled(): boolean {
    const current = this.state();
    return current.status === 'ready'
      && current.enabled
      && current.evaluatedAt !== null
      && Date.now() < current.evaluatedAt + MAX_FRESH_MS;
  }

  ngOnDestroy(): void {
    if (this.destroyed) return;
    this.destroyed = true;
    this.generation++;
    this.desiredUser = null;
    this.clearTimers();
    this.document.removeEventListener('visibilitychange', this.visibilityChanged);

    if (this.provider) {
      this.provider.events.removeHandler(ProviderEvents.Ready, this.providerReady);
      this.provider.events.removeHandler(
        ProviderEvents.ConfigurationChanged,
        this.providerConfigurationChanged
      );
      this.provider.events.removeHandler(ProviderEvents.Error, this.providerError);
      this.provider.events.removeHandler(ProviderEvents.Stale, this.providerStale);
      if (OpenFeature.getProvider(DOMAIN) === this.provider) {
        OpenFeature.setProvider(DOMAIN, NOOP_PROVIDER);
      }
      this.stopNativeClient();
      void this.provider.onClose();
      void this.sdkQueue.then(() => this.stopNativeClient(), () => this.stopNativeClient());
    }
    this.frontendState.set(SAFE_STATE);
  }

  private readonly providerReady = (): void => {};
  private readonly providerConfigurationChanged = (): void => {};
  private readonly providerError = (): void => {};
  private readonly providerStale = (): void => {};

  private async loadConfiguration(): Promise<{ config: PublicConfig; users: readonly DemoUser[] }> {
    const [configValue, usersValue] = await Promise.all([
      this.readJson(CONFIG_URL),
      this.readJson(USERS_URL)
    ]);
    return {
      config: parsePublicConfig(configValue),
      users: parseDemoUsers(usersValue)
    };
  }

  private async readJson(url: string): Promise<unknown> {
    const response = await fetchWithTimeout(url);
    if (!response.ok) throw new Error('Frontend static asset request failed.');
    return response.json();
  }

  private createProvider(config: PublicConfig): FlagsmithClientProvider {
    if (this.provider) return this.provider;
    const nativeClient = createFlagsmithInstance();
    const provider = new FlagsmithClientProvider({
      environmentID: config.flagsmithClientKey,
      api: config.flagsmithApiUrl,
      cacheFlags: false,
      enableAnalytics: false,
      realtime: false,
      enableLogs: false,
      enableEvents: false,
      AsyncStorage: disabledAsyncStorage,
      flagsmithInstance: nativeClient,
      fetch: fetchWithTimeout
    });
    provider.events.addHandler(ProviderEvents.Ready, this.providerReady);
    provider.events.addHandler(
      ProviderEvents.ConfigurationChanged,
      this.providerConfigurationChanged
    );
    provider.events.addHandler(ProviderEvents.Error, this.providerError);
    provider.events.addHandler(ProviderEvents.Stale, this.providerStale);
    this.provider = provider;
    this.nativeClient = nativeClient;
    return provider;
  }

  private stopNativeClient(): void {
    const nativeClient = this.nativeClient ?? this.provider?.flagsmithClient;
    if (!nativeClient) return;
    nativeClient.stopListening();
    if (!hasAnalyticsInterval(nativeClient)) return;
    if (nativeClient.analyticsInterval !== null) {
      clearInterval(nativeClient.analyticsInterval);
      nativeClient.analyticsInterval = null;
    }
  }

  private enqueue(operation: () => Promise<void>): Promise<void> {
    const running = this.sdkQueue.then(operation, operation);
    this.sdkQueue = running.then(() => undefined, () => undefined);
    return running;
  }

  private runRefresh(generation: number, user: DemoUser): Promise<void> {
    if (this.destroyed || !this.provider) return Promise.resolve();
    return this.enqueue(async () => {
      if (this.destroyed) return;
      try {
        await this.provider?.flagsmithClient.getFlags();
        this.publishIfCurrent(generation, user);
      } catch {
        if (this.isCurrent(generation, user)) {
          this.publishError(user, 'Frontend flag service is unavailable.', true);
        }
      }
    });
  }

  private publishIfCurrent(generation: number, user: DemoUser): void {
    if (!this.isCurrent(generation, user) || !this.provider) return;
    if (this.provider.flagsmithClient.getContext().identity?.identifier !== user.id) return;
    try {
      const client = OpenFeature.getClient(DOMAIN);
      if (client.providerStatus !== ProviderStatus.READY) {
        this.publishError(user, 'Frontend flag service is unavailable.', true);
        return;
      }
      const details = client.getBooleanDetails(FLAG_KEY, false);
      if (details.reason === 'DEFAULT'
        || details.reason === 'ERROR'
        || details.errorCode !== undefined) {
        this.publishError(user, 'Frontend flag is unavailable.', true);
        return;
      }
      const evaluatedAt = Date.now();
      this.frontendState.set({
        userId: user.id,
        status: 'ready',
        enabled: details.value,
        error: null,
        evaluatedAt
      });
      this.armExpiry(generation, user, evaluatedAt);
      this.scheduleRefresh(generation, user);
    } catch {
      this.publishError(user, 'Frontend flag service is unavailable.', true);
    }
  }

  private publishError(user: DemoUser, error: string, retry: boolean): void {
    this.clearExpiryTimer();
    this.frontendState.set({
      userId: user.id,
      status: 'error',
      enabled: false,
      error,
      evaluatedAt: null
    });
    if (retry) this.scheduleRefresh(this.generation, user);
  }

  private armExpiry(generation: number, user: DemoUser, evaluatedAt: number): void {
    this.clearExpiryTimer();
    const remaining = Math.max(0, evaluatedAt + MAX_FRESH_MS - Date.now());
    this.expiryTimer = setTimeout(() => {
      if (!this.isCurrent(generation, user)) return;
      const nextGeneration = ++this.generation;
      this.publishError(user, 'Frontend flag decision expired.', false);
      this.scheduleRefresh(nextGeneration, user);
    }, remaining);
  }

  private scheduleRefresh(generation: number, user: DemoUser): void {
    if (this.destroyed) return;
    clearTimeout(this.refreshTimer);
    this.refreshTimer = setTimeout(() => {
      this.refreshTimer = undefined;
      if (this.isCurrent(generation, user)) void this.runRefresh(generation, user);
    }, REFRESH_INTERVAL_MS);
  }

  private clearExpiryTimer(): void {
    clearTimeout(this.expiryTimer);
    this.expiryTimer = undefined;
  }

  private clearTimers(): void {
    this.clearExpiryTimer();
    clearTimeout(this.refreshTimer);
    this.refreshTimer = undefined;
  }

  private isCurrent(generation: number, user: DemoUser): boolean {
    return !this.destroyed
      && generation === this.generation
      && this.desiredUser?.id === user.id;
  }
}
