# Angular frontend reference

Angular is the only frontend framework covered by this [Skill](../SKILL.md). Preserve the existing Angular version, authentication interceptors, state management, and standalone/NgModule structure.

## Contents

- [Choose a route](#choose-a-route)
- [BFF snapshots](#bff-snapshots)
- [Angular integration](#angular-integration)
- [SSR and hydration](#ssr-and-hydration)
- [Public browser provider](#public-browser-provider)
- [Acceptance matrix](#acceptance-matrix)

## Choose a route

| Route | Browser receives | Appropriate use |
| --- | --- | --- |
| BFF snapshot, recommended | Evaluated, allowlisted UI values | Multi-tenant enterprise applications and sensitive targeting |
| Browser Flagsmith provider | Client key, public flags, submitted identity/traits | Public pages and non-sensitive UI with accepted client visibility |
| BFF snapshot with Angular SSR | HTML and an allowlisted request-owned snapshot | Existing server rendering with matching client hydration |

All routes leave authorization and final business decisions on the API. Hidden UI is not authorization. Frontend-only work with an existing BFF does not authorize backend changes; report missing protocol fields as a dependency.

## BFF snapshots

Use the [.NET BFF contract](dotnet.md#bff-contract). The existing session interface must provide the same opaque `contextVersion` as the BFF. Do not manufacture it in the browser or learn the expected identity from an unbound response.

The browser needs no Flagsmith key. Use its existing `HttpClient` to request `/api/ui-features`, validate unknown JSON, and consume the allowlisted result through OpenFeature.

The [working service](../examples/angular/feature-session.service.ts) and [regression tests](../examples/angular/feature-session.spec.ts) cover the complete BFF example rather than leaving lifecycle rules as prose:

| Responsibility | Implementation |
| --- | --- |
| Initial state | Legacy UI with no snapshot |
| Identity binding | `setSession(contextVersion)` immediately clears the previous state, cancels work, and increments generation |
| Request boundary | Existing `HttpClient` and interceptors; two-second timeout |
| Validation | Schema, primitive types, exact context version, finite timestamps, and a non-expired interval |
| Degradation | `degraded=true` reports telemetry and suppresses new UI, even when `checkout_v2=true` |
| Late responses | Subscription cancellation plus generation/context guards |
| Expiry | A separate expiry timer remains active during refresh; provider reads also check the clock |
| Refresh | A 15-second starting cadence; failures clear new UI and schedule a bounded retry |
| 401/403 | Clear state and stop retrying that session; existing auth infrastructure owns sign-in/permission handling |
| Tab restoration | Recheck TTL before refreshing; do not trust throttled background timers |
| Teardown | Cancel requests/timers, remove listeners, clear state, and replace the owned `ui` binding with the no-op Provider only if it is still the active owner |

The example installs one synchronous, application-owned snapshot Provider in domain `ui`. Refreshes atomically replace validated state rather than asynchronously swapping Providers; this removes the old-install/new-identity race. The Provider implements Boolean `checkout_v2`; other types return their caller defaults until the contract is deliberately extended.

`checkoutV2()` is deliberately an uncached accessor. It reads the Angular state signal, preserving template dependency tracking, and rechecks the clock on every call. `Date.now()` is not reactive: wrapping this decision in a cached `computed` can retain an expired positive value, especially during SSR or throttled browser timers.

Browser teardown compares the active Provider metadata object with the retained instance before replacing its binding. This releases the global closure without removing a newer application's Provider. SSR never registers a global binding and performs no global Provider cleanup.

This is an application-owned result adapter, not a second targeting engine or a Flagsmith `IState` adapter. Flagsmith targeting stays on the BFF. Do not turn the SDK's demo/test `TypedInMemoryProvider` into a production lifecycle policy by assumption.

Reference dependencies are OpenFeature Web `1.10.0`, Angular `20.3.0`, and RxJS `7.8.2`; the example pins its compiler/runtime together. These are a runnable reference baseline, not an instruction to upgrade an existing application. Use compatible lifecycle/state equivalents on older supported Angular versions.

## Angular integration

1. Copy the service into the existing feature infrastructure and provide `FEATURE_TELEMETRY` with the project's telemetry function. It is intentionally required: a missing sink must not silently discard failures. Only bounded reason codes are reported; do not forward raw errors, contexts, or payloads.
2. Register the root service once. Domain `ui` belongs to this integration; select a distinct domain when an application already owns that name. Do not create services or Providers per page component.
3. After existing session initialization, call `setSession` with the authenticated context version. Subscribe to login, logout, tenant, and permission-version changes; call `setSession(null)` on logout. Own that subscription through the existing lifecycle mechanism.
4. Bind templates to `checkoutV2()` and the read-only `state()`. A synchronous SDK getter alone is not a reactive source. Route guards improve navigation but do not replace API authorization.
5. Preserve legacy UI or a skeleton while loading or degraded. Destroying a page component must not shut down the application-owned Provider.

Angular versions supporting `provideAppInitializer` can use it to sequence existing session initialization and initial feature loading. Earlier projects can retain `APP_INITIALIZER`. An initializer must return a bounded Promise or completing Observable, not a permanent session stream. The service itself starts in a safe state and need not block bootstrap.

Do not issue a second unauthenticated fetch to bypass an existing interceptor. For same-origin BFF calls, use the project's normal cookie/token policy. Cross-origin credentials require a separately approved security design.

The 15-second refresh and 30-second server TTL are starting values. Measure propagation, skew, background throttling, and failure windows; add fleet-level jitter where appropriate. A blocked JavaScript event loop cannot guarantee instant visual changes, so API enforcement remains authoritative.

## SSR and hydration

SSR uses the BFF route, not the browser Flagsmith provider. Fetch decisions with the current request's trusted session/tenant context, and provide a separate service/state instance for that render. Do not place user snapshots in process-global caches.

Pass the validated response into `setSession(contextVersion, snapshot)` on the server. In server mode the example performs no browser HTTP, timers, listener registration, or global OpenFeature Provider registration. The Angular state is request-owned; the template reads the snapshot directly.

Transfer only allowlisted fields using the project's safe Angular transfer-state mechanism and private response-cache policy. Never embed raw rules or credentials. Restore the same snapshot and expected context version in the browser before the first feature-dependent render; the service rechecks TTL and identity, avoiding a second request while it is valid. Expired, degraded, or mismatched transfer data returns to conservative UI and refreshes in the browser.

If a snapshot expires between rendering and hydration, use the project's established hydration-safe loading boundary and fetch fresh state; do not blindly force an expired decision to match HTML. Personalized pages must not statically prerender one user's decisions for other users.

## Public browser provider

Use `@openfeature/flagsmith-client-provider`, not the Node.js `@openfeature/flagsmith-provider`.

| Package | Reference version |
| --- | --- |
| `@openfeature/web-sdk` | `1.10.0` |
| `@openfeature/flagsmith-client-provider` | `0.3.0` |
| `@flagsmith/flagsmith` | `12.4.0` |

Check peer dependencies and the existing package manager/lockfile before installation. Provider `0.3.0` requires Web SDK `^1.0.0` and Flagsmith JS `^12.1.2`.

Within the Angular application-owned service, initialize once:

```typescript
import { OpenFeature } from '@openfeature/web-sdk';
import { FlagsmithClientProvider } from '@openfeature/flagsmith-client-provider';

export async function initializePublicUi(
  clientKey: string,
  canonicalIdentity: string,
  locale: string
) {
  const provider = new FlagsmithClientProvider({
    environmentID: clientKey,
    api: 'https://flags-public.example.com/api/v1/',
    cacheFlags: false,
    enableAnalytics: false,
    realtime: false
  });
  await OpenFeature.setProviderAndWait('public-ui', provider, {
    targetingKey: canonicalIdentity,
    traits: { locale }
  });
  return provider;
}
```

The owning service must observe initialization rejection and Provider Error/Stale events, clear unsafe UI, and report sanitized errors through existing telemetry. Subscribe to ConfigurationChanged/Ready to update Angular state; remove listeners at teardown. Use Details to distinguish default/error results from a normal off state.

Before identity changes, clear old UI, then await `OpenFeature.setContext('public-ui', ...)`. Serialize updates and verify the current generation before publishing state. Logout sets the named domain's empty context and handles failures; reloading the browser runtime is an option for stronger session isolation.

Security and freshness boundaries:

- Use only a client environment key. Configure an explicit private `api`; never fall through to SaaS defaults.
- Prefer a separate frontend environment containing only public flags. Restrict exposed SDK paths/methods and preflight; do not expose the entire management API. CORS is not authentication or abuse prevention.
- Browser traits such as locale are untrusted. They cannot prove roles, subscription plans, or tenant eligibility. Disabling client-side trait persistence does not make submitted traits trustworthy.
- Persistent cache is disabled in the reference. Any cache needs environment/user/tenant isolation, TTL, and logout cleanup. Do not use `skipAPI: true` as an emergency-control default.
- `realtime: false` does not enable polling. The owning service schedules `provider.flagsmithClient.getFlags()`, handles errors, and publishes changes. Define a stale-result policy.
- Enabling realtime also requires a verified private SSE path, load-balancer timeout, reconnection, and fallback polling. OpenFeature does not provide a push server.
- Disabled String/Number configuration semantics can differ from .NET. Use BFF-authoritative results when exact cross-tier agreement matters.

## Acceptance matrix

| Scenario | Expected result |
| --- | --- |
| Cold load/off/on | Conservative initial UI; correct reactive transition |
| `degraded=true` with a positive flag | New UI remains off; telemetry identifies degradation |
| Invalid JSON/type/context version | No installation; observable fallback |
| Login/logout/tenant/permission change | Immediate clearing; late old work cannot restore UI |
| Pending refresh reaches TTL | Independent expiry still clears old UI |
| Background suspension/restoration | Clock rechecked before stale decisions are used |
| Timeout/401/403/503 | Safe state and existing auth handling; no raw error exposure |
| Repeated component mounting | No duplicate application Providers, subscriptions, or listeners |
| SSR concurrent users | No server-side browser SDK or shared user state |
| Hydration | Matching, valid transferred state; expired data follows the safe loading path |
| Browser manipulation | API still rejects unauthorized or disallowed business operations |

The executable service tests run without a real BFF. Target-application template, interceptor, SSR transport, and live-provider checks remain separate acceptance work; do not describe those as covered by a local service harness.

For a BFF implementation handoff, name the trusted `contextVersion` source and explicitly account for **late-work rejection**, **degraded defaults**, **expiry during refresh**, **visibility-restoration checks**, and **teardown**. Start from the typed working service so shortening an explanation does not remove an implemented guard.
