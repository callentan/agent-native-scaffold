import { DOCUMENT } from '@angular/common';
import { TestBed } from '@angular/core/testing';
import { provideZonelessChangeDetection } from '@angular/core';
import { NOOP_PROVIDER, OpenFeature, ProviderEvents } from '@openfeature/web-sdk';
import { FlagsmithClientProvider } from '@openfeature/flagsmith-client-provider';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { DemoUser } from './demo-contracts';
import { FeatureDemoService } from './feature-demo.service';

interface PendingIdentityRequest {
  readonly url: string;
  readonly method: string;
  readonly body: unknown;
  readonly signal: AbortSignal | undefined;
  readonly resolve: (response: Response) => void;
  readonly reject: (error: unknown) => void;
}

class FetchFixture {
  private readonly fixtureUsers = Array.from({ length: 20 }, (_, index) => {
    const number = index + 1;
    const suffix = number.toString().padStart(3, '0');
    return {
      id: `demo-user-${suffix}`,
      label: `User ${suffix}`,
      beta: number <= 5
    };
  });

  config: unknown = {
    flagsmithApiUrl: 'http://localhost:8000/api/v1/',
    flagsmithClientKey: 'client-key'
  };
  ignoreAborts = false;
  readonly identityRequests: PendingIdentityRequest[] = [];
  analyticsRequests = 0;

  fetch = (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
    const url = new URL(input.toString(), 'http://localhost:4200');
    if (url.pathname === '/poc-config.json') {
      return Promise.resolve(jsonResponse(this.config));
    }
    if (url.pathname === '/demo-users.json') {
      return Promise.resolve(jsonResponse(this.fixtureUsers));
    }
    if (url.pathname.endsWith('/analytics/flags/')) {
      this.analyticsRequests++;
      return Promise.resolve(jsonResponse({}));
    }
    if (url.pathname.endsWith('/identities/')) {
      const bodyText = typeof init?.body === 'string' ? init.body : undefined;
      const body = bodyText ? JSON.parse(bodyText) as { identifier?: string } : undefined;
      const identity = body?.identifier
        ?? url.searchParams.get('identifier')
        ?? '';
      return new Promise<Response>((resolve, reject) => {
        const request: PendingIdentityRequest = {
          url: url.toString(),
          method: init?.method ?? 'GET',
          body: body ?? undefined,
          signal: init?.signal ?? undefined,
          resolve,
          reject
        };
        this.identityRequests.push(request);
        if (!this.ignoreAborts) {
          init?.signal?.addEventListener('abort', () => {
            reject(init.signal?.reason
              ?? new DOMException('The operation was aborted.', 'AbortError'));
          }, { once: true });
        }
        void identity;
      });
    }
    return Promise.reject(new Error(`Unexpected test request: ${url}`));
  };

  respond(index: number, enabled: boolean, includeFlag = true): void {
    const request = this.identityRequests[index];
    if (!request) throw new Error(`No pending identity request at ${index}.`);
    request.resolve(jsonResponse({
      identifier: requestIdentity(request),
      flags: includeFlag ? [{
        enabled,
        feature_state_value: null,
        feature: { id: 1, name: 'frontend_demo_v2' }
      }] : []
    }));
  }

  fail(index: number, status = 503): void {
    const request = this.identityRequests[index];
    if (!request) throw new Error(`No pending identity request at ${index}.`);
    request.resolve(new Response('service unavailable', {
      status,
      headers: { 'content-type': 'text/plain' }
    }));
  }
}

function requestIdentity(request: PendingIdentityRequest): string {
  const body = request.body as { identifier?: string } | undefined;
  if (body?.identifier) return body.identifier;
  return new URL(request.url).searchParams.get('identifier') ?? '';
}

function jsonResponse(value: unknown): Response {
  return new Response(JSON.stringify(value), {
    status: 200,
    headers: { 'content-type': 'application/json' }
  });
}

async function settle(): Promise<void> {
  for (let index = 0; index < 100; index++) {
    await Promise.resolve();
  }
}

describe('FeatureDemoService', () => {
  let service: FeatureDemoService;
  let fixture: FetchFixture;
  let testDocument: Document;

  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date('2026-10-16T00:00:00.000Z'));
    fixture = new FetchFixture();
    testDocument = document;
    Object.defineProperty(testDocument, 'visibilityState', {
      configurable: true,
      value: 'visible'
    });
    vi.stubGlobal('fetch', fixture.fetch);
    TestBed.configureTestingModule({
      providers: [
        provideZonelessChangeDetection(),
        FeatureDemoService,
        { provide: DOCUMENT, useValue: testDocument }
      ]
    });
    service = TestBed.inject(FeatureDemoService);
  });

  afterEach(async () => {
    service?.ngOnDestroy();
    await OpenFeature.clearProviders();
    TestBed.resetTestingModule();
    vi.unstubAllGlobals();
    vi.useRealTimers();
  });

  async function initialize(enabled: boolean, includeFlag = true): Promise<void> {
    const initialization = service.initialize();
    await settle();
    expect(fixture.identityRequests).toHaveLength(1);
    fixture.respond(0, enabled, includeFlag);
    await initialization;
    await settle();
  }

  it('starts in a safe legacy state and owns one official browser Provider', async () => {
    expect(service.state()).toEqual({
      userId: null,
      status: 'loading',
      enabled: false,
      error: null,
      evaluatedAt: null
    });

    await initialize(false);

    expect(OpenFeature.getProvider('poc-ui')).toBeInstanceOf(FlagsmithClientProvider);
    expect(OpenFeature.getProvider('poc-ui')).toBe(OpenFeature.getProvider('poc-ui'));
    expect(service.state().enabled).toBe(false);
  });

  it('passes the exact nested beta context to the official Provider', async () => {
    await initialize(true);

    const provider = OpenFeature.getProvider('poc-ui');
    expect(provider).toBeInstanceOf(FlagsmithClientProvider);
    expect(OpenFeature.getContext('poc-ui')).toEqual({
      targetingKey: 'demo-user-001',
      traits: { beta: true }
    });
    expect(fixture.identityRequests[0].url).toBe('http://localhost:8000/api/v1/identities/');
    expect(fixture.identityRequests[0].body).toEqual({
      identifier: 'demo-user-001',
      traits: [{ trait_key: 'beta', trait_value: true }]
    });
  });

  it.each([
    { enabled: false, expected: false },
    { enabled: true, expected: true }
  ])('publishes a normal $enabled decision without an error', async ({ enabled, expected }) => {
    await initialize(enabled);

    expect(service.state()).toMatchObject({
      userId: 'demo-user-001',
      status: 'ready',
      enabled: expected,
      error: null
    });
    expect(service.enabled()).toBe(expected);
    expect(service.state().evaluatedAt).toBeTypeOf('number');
  });

  it('treats a missing flag as an observable safe error rather than normal off', async () => {
    await initialize(false, false);

    expect(service.enabled()).toBe(false);
    expect(service.state().status).toBe('error');
    expect(service.state().error).toMatch(/flag/i);
  });

  it('turns an SDK failure into a sanitized legacy state', async () => {
    const initialization = service.initialize();
    await settle();
    expect(fixture.identityRequests).toHaveLength(1);
    fixture.fail(0);
    await initialization;

    expect(service.state().enabled).toBe(false);
    expect(service.state().status).toBe('error');
    expect(service.state().error).toMatch(/unavailable|refresh/i);
    expect(service.state().error).not.toContain('service unavailable');
  });

  it('does not reuse the previous user decision when identity evaluation fails', async () => {
    const originalError = console.error.bind(console);
    const diagnostics: unknown[][] = [];
    const errorSpy = vi.spyOn(console, 'error').mockImplementation((...args) => {
      diagnostics.push(args);
      if (!args.some((argument) =>
        String(argument).includes('Error running FlagsmithClientProvider'))) {
        originalError(...args);
      }
    });
    try {
      await initialize(true);
      const [, nextUser] = service.users();
      const selection = service.selectUser(nextUser);
      await settle();

      expect(fixture.identityRequests).toHaveLength(2);
      fixture.fail(1);
      await selection;

      expect(service.state()).toMatchObject({
        userId: nextUser.id,
        status: 'error',
        enabled: false
      });
      expect(service.state().error).toMatch(/unavailable|refresh/i);
      expect(service.enabled()).toBe(false);
      expect(diagnostics).toHaveLength(1);
      expect(diagnostics[0].map(String).join(' '))
        .toContain('Error running FlagsmithClientProvider');
    } finally {
      errorSpy.mockRestore();
    }
  });

  it('does not rebind its Provider when queued context work drains after destruction', async () => {
    await initialize(false);
    const [, firstUser, queuedUser] = service.users();
    const firstSelection = service.selectUser(firstUser);
    const queuedSelection = service.selectUser(queuedUser);
    await settle();

    expect(fixture.identityRequests).toHaveLength(2);
    service.ngOnDestroy();
    fixture.respond(1, true);
    await firstSelection;
    await settle();
    if (fixture.identityRequests.length === 3) {
      fixture.respond(2, true);
    }
    await queuedSelection;
    await settle();

    expect(OpenFeature.getProvider('poc-ui')).toBe(NOOP_PROVIDER);
    expect(fixture.identityRequests).toHaveLength(2);
    expect(service.state().enabled).toBe(false);
  });

  it('does not read or flush persisted Flagsmith events when storage is disabled', async () => {
    const storageKey = 'FLAGSMITH_EVENT_client-key';
    localStorage.setItem(storageKey, JSON.stringify({
      'client-key': { frontend_demo_v2: 1 }
    }));
    const getItemSpy = vi.spyOn(Storage.prototype, 'getItem');
    const setItemSpy = vi.spyOn(Storage.prototype, 'setItem');
    getItemSpy.mockClear();
    setItemSpy.mockClear();
    try {
      await initialize(true);
      await vi.advanceTimersByTimeAsync(10_001);
      await settle();

      expect(getItemSpy).not.toHaveBeenCalledWith(storageKey);
      expect(setItemSpy).not.toHaveBeenCalledWith(
        storageKey,
        expect.any(String)
      );
      expect(fixture.analyticsRequests).toBe(0);
    } finally {
      getItemSpy.mockRestore();
      setItemSpy.mockRestore();
      localStorage.removeItem(storageKey);
    }
  });

  it('refreshes natively every five seconds and never overlaps a mutation', async () => {
    await initialize(true);

    await vi.advanceTimersByTimeAsync(5_000);
    expect(fixture.identityRequests).toHaveLength(2);
    await vi.advanceTimersByTimeAsync(1_000);
    expect(fixture.identityRequests).toHaveLength(2);

    fixture.respond(1, false);
    await settle();
    expect(service.state().enabled).toBe(false);

    await vi.advanceTimersByTimeAsync(4_999);
    expect(fixture.identityRequests).toHaveLength(2);
    await vi.advanceTimersByTimeAsync(1);
    expect(fixture.identityRequests).toHaveLength(3);
  });

  it('publishes only the newest selection after A, B, and C are serialized', async () => {
    await initialize(false);
    const [userA, userB, userC] = service.users();

    const a = service.selectUser(userA);
    const b = service.selectUser(userB);
    const c = service.selectUser(userC);
    expect(service.state()).toMatchObject({
      userId: 'demo-user-003',
      status: 'loading',
      enabled: false
    });

    await settle();
    expect(fixture.identityRequests).toHaveLength(2);
    fixture.respond(1, true);
    await settle();
    expect(fixture.identityRequests).toHaveLength(3);
    fixture.respond(2, true);
    await settle();
    expect(fixture.identityRequests).toHaveLength(4);
    fixture.respond(3, false);
    await Promise.all([a, b, c]);

    expect(service.state()).toMatchObject({
      userId: 'demo-user-003',
      status: 'ready',
      enabled: false,
      error: null
    });
  });

  it('observes an old failure without permanently rejecting the queue', async () => {
    await initialize(false);
    const [userA, userB, userC] = service.users();
    const a = service.selectUser(userA);
    const b = service.selectUser(userB);
    const c = service.selectUser(userC);

    await settle();
    const originalError = console.error.bind(console);
    const errorSpy = vi.spyOn(console, 'error').mockImplementation((...args) => {
      const text = args.map(String).join(' ');
      const isExpectedDiagnostic = text.includes(
        "Error running FlagsmithClientProvider's context change handler"
      ) && text.includes('service unavailable');
      if (!isExpectedDiagnostic) originalError(...args);
    });
    let expectedDiagnostic = false;
    try {
      fixture.fail(1);
      await settle();
      expectedDiagnostic = errorSpy.mock.calls.some((args) => {
        const text = args.map(String).join(' ');
        return text.includes("Error running FlagsmithClientProvider's context change handler")
          && text.includes('service unavailable');
      });
    } finally {
      errorSpy.mockRestore();
    }
    expect(expectedDiagnostic).toBe(true);
    expect(fixture.identityRequests).toHaveLength(3);
    fixture.respond(2, true);
    await settle();
    expect(fixture.identityRequests).toHaveLength(4);
    fixture.respond(3, true);
    await Promise.all([a, b, c]);

    expect(service.state()).toMatchObject({
      userId: 'demo-user-003',
      status: 'ready',
      enabled: true,
      error: null
    });
  });

  it('expires a positive decision at fifteen seconds while refresh remains pending', async () => {
    await initialize(true);
    fixture.ignoreAborts = true;

    await vi.advanceTimersByTimeAsync(5_000);
    expect(fixture.identityRequests).toHaveLength(2);
    await vi.advanceTimersByTimeAsync(10_000);

    expect(service.enabled()).toBe(false);
    expect(service.state()).toMatchObject({
      status: 'error',
      enabled: false
    });
    expect(service.state().error).toMatch(/expired/i);
  });

  it('clears stale state before fetching after visibility restoration', async () => {
    await initialize(true);
    vi.setSystemTime(new Date('2026-10-16T00:00:16.000Z'));
    testDocument.dispatchEvent(new Event('visibilitychange'));

    expect(service.enabled()).toBe(false);
    expect(service.state().error).toMatch(/expired|stale/i);
    await settle();
    expect(fixture.identityRequests).toHaveLength(2);
  });

  it('uses the two-second transport deadline and returns safely on a stalled response', async () => {
    const initialization = service.initialize();
    await settle();
    expect(fixture.identityRequests).toHaveLength(1);

    await vi.advanceTimersByTimeAsync(2_001);
    await initialization;

    expect(service.enabled()).toBe(false);
    expect(service.state().status).toBe('error');
  });

  it('ignores provider events and late work from a previous generation', async () => {
    await initialize(true);
    const provider = OpenFeature.getProvider('poc-ui');
    const [userA, userB] = service.users();
    const pending = service.selectUser(userB);
    (provider as FlagsmithClientProvider).events.emit(ProviderEvents.ConfigurationChanged);
    expect(service.enabled()).toBe(false);

    await settle();
    fixture.respond(1, true);
    await pending;
    expect(service.state().userId).toBe(userB.id);
    expect(service.enabled()).toBe(true);

    const oldState = service.state();
    const next = service.selectUser(userA);
    await settle();
    fixture.respond(2, false);
    await next;
    await settle();
    expect(service.state().userId).toBe(userA.id);
    expect(service.state()).not.toBe(oldState);
  });

  it('cleans the native interval when teardown races initial Provider startup', async () => {
    const initialization = service.initialize();
    await settle();
    expect(fixture.identityRequests).toHaveLength(1);
    const provider = OpenFeature.getProvider('poc-ui');
    expect(provider).toBeInstanceOf(FlagsmithClientProvider);
    const nativeClient = (provider as FlagsmithClientProvider).flagsmithClient;

    service.ngOnDestroy();
    fixture.respond(0, true);
    await initialization;
    await settle();
    await vi.advanceTimersByTimeAsync(2_001);
    await settle();

    if (!('analyticsInterval' in nativeClient)) {
      throw new Error('The official native client did not expose analyticsInterval.');
    }
    expect(nativeClient.analyticsInterval).toBeNull();
    expect(vi.getTimerCount()).toBe(0);
    expect(fixture.identityRequests).toHaveLength(1);
  });

  it('cancels timers/listeners and prevents late publication during teardown', async () => {
    await initialize(true);
    const provider = OpenFeature.getProvider('poc-ui');
    if (!(provider instanceof FlagsmithClientProvider)
      || !('analyticsInterval' in provider.flagsmithClient)) {
      throw new Error('The official native client did not expose analyticsInterval.');
    }
    expect(provider.flagsmithClient.analyticsInterval).not.toBeNull();
    const [userB] = service.users().slice(1, 2);
    const pending = service.selectUser(userB);
    await settle();
    expect(fixture.identityRequests).toHaveLength(2);

    service.ngOnDestroy();
    fixture.respond(1, false);
    await pending;
    await settle();
    await vi.advanceTimersByTimeAsync(1_999);
    await vi.advanceTimersByTimeAsync(1);
    await vi.advanceTimersByTimeAsync(60_000);

    expect(service.enabled()).toBe(false);
    expect(service.state().enabled).toBe(false);
    expect(provider.flagsmithClient.analyticsInterval).toBeNull();
    expect(vi.getTimerCount()).toBe(0);
    const requestCount = fixture.identityRequests.length;
    testDocument.dispatchEvent(new Event('visibilitychange'));
    await vi.advanceTimersByTimeAsync(5_000);
    expect(fixture.identityRequests).toHaveLength(requestCount);
  });
});
