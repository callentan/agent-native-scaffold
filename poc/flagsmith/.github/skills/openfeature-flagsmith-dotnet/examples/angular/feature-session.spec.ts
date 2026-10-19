import '@angular/compiler';
import assert from 'node:assert/strict';
import { test, type TestContext } from 'node:test';
import { DOCUMENT } from '@angular/common';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Injector, PLATFORM_ID } from '@angular/core';
import { OpenFeature, TypedInMemoryProvider } from '@openfeature/web-sdk';
import { Subject } from 'rxjs';
import { FeatureSessionService, FEATURE_TELEMETRY, parseSnapshot } from './feature-session.service.js';

class Requests {
  readonly pending: Subject<unknown>[] = [];
  get(url: string) {
    assert.equal(url, '/api/ui-features');
    const response = new Subject<unknown>();
    this.pending.push(response);
    return response.asObservable();
  }
  respond(index: number, value: unknown) {
    this.pending[index].next(value);
    this.pending[index].complete();
  }
}

function snapshot(contextVersion = 'session-a', degraded = false) {
  return {
    schemaVersion: 1,
    contextVersion,
    evaluatedAt: new Date(Date.now() - 100).toISOString(),
    expiresAt: new Date(Date.now() + 30_000).toISOString(),
    degraded,
    flags: { checkout_v2: true }
  };
}

function setup(t: TestContext, platform = 'browser') {
  t.mock.timers.enable({ apis: ['Date', 'setTimeout', 'setInterval'], now: 1_800_000_000_000 });
  const http = new Requests();
  const events: string[] = [];
  const document = Object.assign(new EventTarget(), { visibilityState: 'visible' });
  const injector = Injector.create({
    providers: [
      FeatureSessionService,
      { provide: HttpClient, useValue: http },
      { provide: DOCUMENT, useValue: document },
      { provide: PLATFORM_ID, useValue: platform },
      { provide: FEATURE_TELEMETRY, useValue: (reason: string) => events.push(reason) }
    ]
  });
  const service = injector.get(FeatureSessionService);
  let destroyed = false;
  const destroy = () => {
    if (!destroyed) injector.destroy();
    destroyed = true;
  };
  t.after(async () => {
    destroy();
    await OpenFeature.clearProviders();
    t.mock.timers.reset();
  });
  return { service, http, events, document, destroy };
}

test('defaults to the legacy UI, then installs a valid BFF decision', (t) => {
  const { service, http } = setup(t);
  assert.equal(service.checkoutV2(), false);
  service.setSession('session-a');
  http.respond(0, snapshot());
  assert.equal(service.checkoutV2(), true);
  assert.equal(OpenFeature.getClient('ui').getBooleanValue('checkout_v2', false), true);
});

test('degraded=true overrides a positive payload and reports degradation', (t) => {
  const { service, http, events } = setup(t);
  service.setSession('session-a');
  http.respond(0, snapshot('session-a', true));
  assert.equal(service.checkoutV2(), false);
  assert.equal(OpenFeature.getClient('ui').getBooleanValue('checkout_v2', false), false);
  assert(events.includes('degraded'));
});

test('rejects mismatched context versions', (t) => {
  const { service, http, events } = setup(t);
  service.setSession('session-b');
  http.respond(0, snapshot('session-a'));
  assert.equal(service.checkoutV2(), false);
  assert(events.includes('invalid-snapshot'));
});

test('clears the old identity immediately and ignores a late old response', (t) => {
  const { service, http } = setup(t);
  service.setSession('session-a');
  http.respond(0, snapshot());
  service.refresh();
  service.setSession('session-b');
  assert.equal(service.checkoutV2(), false);
  http.respond(1, snapshot('session-a'));
  assert.equal(service.checkoutV2(), false);
  http.respond(2, snapshot('session-b'));
  assert.equal(service.checkoutV2(), true);
});

test('expiry clears the UI even while a refresh request is pending', (t) => {
  const { service, http } = setup(t);
  service.setSession('session-a');
  http.respond(0, snapshot());
  t.mock.timers.tick(15_000);
  assert.equal(http.pending.length, 2);
  t.mock.timers.tick(15_001);
  assert.equal(service.checkoutV2(), false);
  assert.equal(OpenFeature.getClient('ui').getBooleanValue('checkout_v2', false), false);
});

test('provider reads recheck the clock before a throttled expiry callback runs', (t) => {
  const { service, http } = setup(t);
  service.setSession('session-a');
  http.respond(0, snapshot());
  t.mock.timers.setTime(Date.now() + 31_000);
  assert.equal(OpenFeature.getClient('ui').getBooleanValue('checkout_v2', false), false);
});

test('the browser accessor rechecks TTL even after a valid result was previously read', (t) => {
  const { service, http } = setup(t);
  service.setSession('session-a');
  http.respond(0, snapshot());
  assert.equal(service.checkoutV2(), true);
  t.mock.timers.setTime(Date.now() + 31_000);
  assert.equal(service.checkoutV2(), false);
});

test('the SSR accessor cannot retain a cached positive result beyond TTL', (t) => {
  const { service } = setup(t, 'server');
  service.setSession('session-a', snapshot());
  assert.equal(service.checkoutV2(), true);
  t.mock.timers.setTime(Date.now() + 31_000);
  assert.equal(service.checkoutV2(), false);
});

test('tab restoration invalidates an expired snapshot before refreshing', (t) => {
  const { service, http, document } = setup(t);
  service.setSession('session-a');
  http.respond(0, snapshot());
  t.mock.timers.setTime(Date.now() + 31_000);
  document.dispatchEvent(new Event('visibilitychange'));
  assert.equal(service.checkoutV2(), false);
  assert.equal(http.pending.length, 2);
});

test('logout cancels outstanding work and removes the previous decision', (t) => {
  const { service, http } = setup(t);
  service.setSession('session-a');
  service.setSession(null);
  http.respond(0, snapshot());
  t.mock.timers.tick(60_000);
  assert.equal(service.checkoutV2(), false);
  assert.equal(http.pending.length, 1);
});

test('request timeout is observable and returns to the conservative UI', (t) => {
  const { service, events } = setup(t);
  service.setSession('session-a');
  t.mock.timers.tick(2_001);
  assert.equal(service.checkoutV2(), false);
  assert(events.includes('unavailable'));
});

test('SSR uses request-owned state without HTTP or global provider registration', (t) => {
  const { service, http } = setup(t, 'server');
  const before = OpenFeature.getProviderMetadata('ui').name;
  service.setSession('session-a', snapshot());
  assert.equal(service.checkoutV2(), true);
  assert.equal(http.pending.length, 0);
  assert.equal(OpenFeature.getProviderMetadata('ui').name, before);
});

test('valid transferred state avoids a second request during hydration', (t) => {
  const { service, http } = setup(t);
  service.setSession('session-a', snapshot());
  assert.equal(service.checkoutV2(), true);
  assert.equal(http.pending.length, 0);
});

test('401/403 clear the decision and stop retries for the unauthorized context', (t) => {
  const { service, http, events } = setup(t);
  for (const status of [401, 403]) {
    service.setSession(`session-${status}`);
    http.pending.at(-1)!.error(new HttpErrorResponse({ status }));
    assert.equal(service.checkoutV2(), false);
    const count = http.pending.length;
    t.mock.timers.tick(60_000);
    assert.equal(http.pending.length, count);
  }
  assert.deepEqual(events, ['unauthorized', 'unauthorized']);
});

test('a refresh failure clears old positive state and schedules a safe retry', (t) => {
  const { service, http, events } = setup(t);
  service.setSession('session-a');
  http.respond(0, snapshot());
  service.refresh();
  http.pending[1].error(new HttpErrorResponse({ status: 503 }));
  assert.equal(service.checkoutV2(), false);
  assert(events.includes('unavailable'));
  t.mock.timers.tick(15_000);
  http.respond(2, snapshot());
  assert.equal(service.checkoutV2(), true);
});

test('teardown cancels requests, expiry, refresh, and visibility listeners', (t) => {
  const { service, http, document, destroy } = setup(t);
  service.setSession('session-a');
  http.respond(0, snapshot());
  service.refresh();
  destroy();
  http.respond(1, snapshot());
  document.dispatchEvent(new Event('visibilitychange'));
  t.mock.timers.tick(60_000);
  assert.equal(service.checkoutV2(), false);
  assert.equal(http.pending.length, 2);
});

test('teardown releases the application-owned global provider binding', (t) => {
  const { destroy } = setup(t);
  const owned = OpenFeature.getProviderMetadata('ui');
  destroy();
  assert.notEqual(OpenFeature.getProviderMetadata('ui'), owned);
  assert.equal(OpenFeature.getClient('ui').getBooleanValue('checkout_v2', false), false);
});

test('an old service teardown cannot replace a newer provider owner', (t) => {
  const { destroy } = setup(t);
  const replacement = new TypedInMemoryProvider({});
  OpenFeature.setProvider('ui', replacement);
  destroy();
  assert.equal(OpenFeature.getProviderMetadata('ui'), replacement.metadata);
});

test('separate SSR injectors do not share user snapshots', (t) => {
  const { service, document } = setup(t, 'server');
  const second = Injector.create({
    providers: [
      FeatureSessionService,
      { provide: HttpClient, useValue: new Requests() },
      { provide: DOCUMENT, useValue: document },
      { provide: PLATFORM_ID, useValue: 'server' },
      { provide: FEATURE_TELEMETRY, useValue: () => {} }
    ]
  });
  t.after(() => second.destroy());
  service.setSession('session-a', snapshot());
  const other = second.get(FeatureSessionService);
  other.setSession('session-b', {
    ...snapshot('session-b'), flags: { checkout_v2: false }
  });
  assert.equal(service.checkoutV2(), true);
  assert.equal(other.checkoutV2(), false);
  service.setSession(null);
  assert.equal(other.state().snapshot?.contextVersion, 'session-b');
});

test('snapshot validation rejects malformed values and expired data', () => {
  for (const invalid of [
    null, [], { ...snapshot(), schemaVersion: 2 },
    { ...snapshot(), flags: { checkout_v2: 'true' } },
    { ...snapshot(), expiresAt: new Date(0).toISOString() }
  ]) {
    assert.throws(() => parseSnapshot(invalid, 'session-a'));
  }
});
