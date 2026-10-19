# Direct-SDK feature flag POC specification

Date: 2026-10-16
Status: Development specification for review; application implementation has not started.

## 1. Goal and approved scope

Create `poc\` containing one Angular page and one ASP.NET Core application. Demonstrate independent frontend and backend feature flags, fixed synthetic user switching, segment targeting, stable percentage rollout, dynamic changes, and return to legacy behavior.

The frontend and backend each integrate OpenFeature and the official Flagsmith Provider/SDK directly. Do not introduce a feature-query HTTP API, BFF snapshot, application-owned Provider, flag proxy, shared evaluation service, or application-side targeting algorithm.

Keep the demonstration deliberately artificial: an old/new UI block and an old/new backend response. Do not implement products, prices, discounts, orders, authentication, a business database, SSR, remote configuration types, experimentation statistics, cloud infrastructure, or an administration UI.

The additional proposals from the planning conversation are not implicitly approved. Provider initialization, observable failures, and identity isolation are correctness requirements, not additional demonstration modules.

## 2. Architecture and local topology

| Component | Address | Responsibility |
| --- | --- | --- |
| Angular standalone CSR application | `http://localhost:4200` | Fixed user selector, frontend old/new block, backend invocation and result |
| ASP.NET Core Minimal API | `http://127.0.0.1:5000` | Evaluate the backend flag for the selected synthetic user and execute one response branch |
| Existing private Flagsmith | `http://localhost:8000` | Dashboard, frontend remote evaluation, backend environment documents |

Frontend decision path: Angular -> OpenFeature Web SDK -> official Flagsmith browser Provider -> Flagsmith SDK evaluation endpoint.

Backend decision path: ASP.NET Core -> OpenFeature .NET SDK -> official Flagsmith Provider -> process-owned Flagsmith SDK with local evaluation. Only initial document loading and periodic document refresh contact Flagsmith.

The Angular development proxy forwards `/api` to the demo backend for ordinary application requests. It must not proxy Flagsmith traffic or evaluate, forward, or cache frontend flags.

### Flagsmith isolation

Create two dedicated Flagsmith Projects, each with one `local` Environment:

| Project | Environment | Only feature | Key used by application |
| --- | --- | --- | --- |
| `poc-frontend` | `local` | `frontend_demo_v2` | Client-side environment key |
| `poc-backend` | `local` | `backend_demo_v2` | Server-side `ser.` environment key |

Projects, not just Environments, separate the inventories because Flagsmith feature and segment definitions are project-scoped. The browser must not receive the backend key, flag inventory, or environment document.

Reuse the workstation deployment described in [the local deployment guide](../../../deploy/local-development.md). This task does not provision another instance or modify production/shared environments. Outside a loopback-only workstation deployment, require HTTPS and a restricted SDK entry point before using the browser route; CORS alone is not access control.

## 3. Toolchain and dependency baseline

| Component | Version / constraint |
| --- | --- |
| .NET target | `net10.0`; supported .NET 10 SDK |
| OpenFeature .NET | `2.14.1` |
| .NET Flagsmith Provider | `0.3.1` |
| Flagsmith .NET SDK | `9.0.0` |
| Angular runtime, compiler, CLI, build tooling | `20.3.0` |
| OpenFeature Web SDK | `1.10.0` |
| Flagsmith browser Provider | `0.3.0` |
| Flagsmith JavaScript SDK | `12.4.0` |
| RxJS / TypeScript / tslib | `7.8.2` / `5.9.3` / `2.8.1` |
| Node | Node 22 with version at least `22.12.0`, or Node 24 |
| Angular unit tests | Vitest `3.2.4`, jsdom `26.1.0`, Angular build `unit-test` builder |
| .NET unit/integration tests | xUnit `2.9.3`, runner `3.1.5`, Test SDK `17.14.1`, MVC Testing `10.0.0` |
| Browser tests | Playwright Test `1.56.1`, Chromium only |
| Existing local Flagsmith baseline | `2.285.0` |
| Script runtime | Windows PowerShell 7.4 or newer |

Pin direct package versions and commit npm and NuGet lockfiles when implementation is authorized. Package existence and peer constraints are evidence, not proof of a successful application restore or build. Do not upgrade the existing Skill examples as part of the POC.

## 4. Flag contract

| Field | Frontend | Backend |
| --- | --- | --- |
| Key | `frontend_demo_v2` | `backend_demo_v2` |
| Type | Boolean `enabled` state | Boolean `enabled` state |
| Application default | `false` | `false` |
| Off behavior | Neutral block, `Frontend: legacy` | `mode=legacy`, `message=Backend: legacy` |
| On behavior | Visually distinct block, `Frontend: new` | `mode=new`, `message=Backend: new` |
| Audience | Synthetic demo users | Synthetic demo users |
| Browser exposure | Public | Not exposed as a flag |
| Owner | POC application maintainers | POC application maintainers |
| Review / retirement date | 2026-11-30 | 2026-11-30 |

The review date is maintenance metadata, not an automatically enforced expiry. Use `UsingBooleanConfigValue=false` on .NET. Do not emulate a Boolean rollout with the strings `"true"`/`"false"` or multivariate configuration values.

## 5. Fixed user and evaluation-context contract

One checked-in source, `poc\shared\demo-users.json`, defines exactly 20 synthetic users:

- IDs are `demo-user-001` through `demo-user-020`, without random IDs or timestamps.
- Labels are `User 001` through `User 020`.
- Users 001-005 have Boolean `beta=true`; users 006-020 have Boolean `beta=false`.
- The initial selection is `demo-user-001`. Selection is tab-local; reload selects the initial user again.
- The file contains no personal data, credentials, roles, subscription entitlements, or real tenant identifiers.

The frontend serves this static fixture through Angular assets. The backend copies the same file to its build/publish output and loads and validates it once. Do not create a users API or maintain two separate user lists.

For both tiers, the targeting key is the exact user ID. The browser context is `{ targetingKey: user.id, traits: { beta: user.beta } }`; the .NET invocation context has that targeting key and a flat Boolean `beta` attribute.

The backend accepts only a known user ID and derives attributes from its own loaded fixture. It never accepts a browser-supplied traits dictionary. This is a synthetic identity selector, not authentication: anyone with local access can choose any fixture user. No flag or trait grants a real permission.

Changing selection clears the previous frontend decision and backend result immediately. Late initialization, refresh, context-change, or backend responses for an older selection must not appear under the new selection.

## 6. Page and backend response

### Page

One page contains:

1. A fixed user selector and read-only display of ID and `beta`.
2. A frontend block with the exact text and appearance from the flag contract.
3. A `Call backend` button and the most recent backend result for the selected user.
4. Small inline loading/error messages for frontend SDK and backend invocation failures.

Do not add a separate diagnostics dashboard, user-cohort grid, routing, or component library. Use English UI labels to match the repository's executable-reference language convention. Text as well as color distinguishes the frontend states.

Switching users clears the backend result and invalidates in-flight responses. The button can be clicked again for the new user. Browser flags have no input into the backend response.

### Endpoint

`GET /api/demo?userId=demo-user-001`

Successful response, with `Cache-Control: no-store`:

```json
{
  "userId": "demo-user-001",
  "mode": "legacy",
  "message": "Backend: legacy"
}
```

An enabled decision returns `mode=new` and `message=Backend: new` with the same user ID. There is no flag dictionary, key, SDK document, or rule in this response.

Missing, empty, malformed, or unknown IDs return HTTP 400 Problem Details with title `Unknown demo user.`. Validate before evaluating a flag. A frontend HTTP error is displayed as an error, not a fabricated legacy success.

This is the only application endpoint required by the POC. Ordinary legacy/default evaluation returns HTTP 200 and is distinguishable from evaluation errors in backend logs. Do not add flag-query or BFF routes.

## 7. Frontend SDK lifecycle

- Own one official `FlagsmithClientProvider` in OpenFeature domain `poc-ui` for the application lifetime. Use the browser Provider, not the Node.js server Provider.
- Load and validate the static user fixture and local public configuration with bounded HTTP requests. Show an explicit configuration error when either is invalid.
- Initialize through `OpenFeature.setProviderAndWait` with the selected user. Read the decision through `getBooleanDetails('frontend_demo_v2', false)`.
- Configure an explicit private API URL, `cacheFlags=false`, `enableAnalytics=false`, and `realtime=false`. Disable event tracking; do not enable persistent browser SDK state.
- Bound SDK HTTP requests to 2 seconds through the supported `fetch` option and an abort signal. The pinned JavaScript SDK has no typed `requestTimeoutMilliseconds` option; do not invent one. Schedule `provider.flagsmithClient.getFlags()` every 5 seconds after the previous operation finishes; `realtime=false` alone does not poll.
- Serialize all context changes and refreshes. Immediately reset the visible decision on user changes and use a monotonically increasing selection generation to reject late work.
- Observe Ready/ConfigurationChanged and Error/Stale events. Events during an older operation must not publish state for a newer selection. Publish only after the owned operation completes for the current identity; events never authorize a positive decision by themselves.
- Update Angular reactive state explicitly. A synchronous SDK getter is not an Angular change-notification mechanism.
- On failed initialization, refresh, context change, missing flag (`reason=DEFAULT` in the pinned browser Provider), or SDK error, show legacy UI plus a sanitized inline error. Do not treat a missing flag as a verified normal-off result.
- A successful decision is usable for at most 15 seconds. Check the clock on reads, run an independent expiry timer, and clear old positive state before refreshing on tab visibility restoration.
- Retry through the single bounded refresh schedule. No overlapping requests, per-component Providers, or uncontrolled retry loops.
- On application teardown, cancel timers, remove listeners, invalidate pending work, and shut down only this application's owned domain/Provider. Do not remove another owner or domain.

## 8. Backend SDK lifecycle

Adapt the repository's [local-only helper](../../../.github/skills/openfeature-flagsmith-dotnet/examples/dotnet/LocalEvaluation.cs) into POC-owned infrastructure without changing the original reference.

- Own one native Flagsmith client and one official OpenFeature Provider per application process. Pass evaluation context per invocation; never mutate global or client context per HTTP request.
- Only allow GET to the exact configured `/api/v1/environment-document/` URI through the underlying transport. Disable redirects; reject remote `/flags/`, `/identities/`, wrong-origin, and wrong-method fallback attempts before transport.
- HTTPS is required except for literal `localhost`, `127.0.0.1`, or `::1` HTTP URLs in ASP.NET Core `Development`. Reject URL credentials, query, fragment, other paths, other hosts over HTTP, and non-server keys. Do not weaken the existing Skill helper globally.
- Refresh the environment document every 10 seconds, use a 2-second timeout, zero retries, and disable analytics.
- Before accepting requests, load the document and verify `backend_demo_v2` exists. Both enabled and disabled values are valid startup states. Missing/malformed documents or missing flags fail startup with a nonzero process exit.
- Do not retain the reference helper's fixed `SmokeExpected` check for this toggleable demo flag: enabling the demo must not make a later restart fail.
- During requests, call `GetBooleanDetailsAsync` with default `false` and a newly constructed invocation context. On evaluation error, log a bounded reason and execute the legacy branch; do not swallow unexpected application exceptions.
- Filter the exact `FlagsmithSdk` logging category to Warning; preserve SDK warnings/errors and safe application diagnostics. Do not log keys, environment documents, raw traits, or raw request/response bodies.
- A warm Flagsmith outage can leave the native SDK using last-known-good rules. Report this boundary in the runbook; this POC does not implement a backend maximum-age controller or promise an emergency-stop deadline.
- Call OpenFeature shutdown at process exit. Flagsmith 9 polling has no verified deterministic in-process disposal: tests that construct multiple local-mode hosts must use separate child processes rather than leaving pollers behind.

Frontend expiry and backend last-known-good behavior are deliberately different. This POC is not an authorization system or a guarantee that both tiers change simultaneously.

## 9. Flagsmith scenarios and stable rollout

Configure the following independently in each dedicated project. Preserve segment IDs while changing percentage thresholds.

| Scenario | Environment default | Segment overrides | Expected demonstration |
| --- | --- | --- | --- |
| Off | Disabled | None active | All users see legacy |
| On | Enabled | None active | All users see new |
| Beta only | Disabled | `beta-users`: `beta=true`, enabled override | Users 001-005 new; others legacy |
| Percentage | Disabled | One `stable-rollout` segment with native Percentage Split and enabled override | Deterministic cohort at 10%, then 50%, then 100% |
| Rollback | Disabled | Disable/remove all active enabling overrides; no identity overrides | All users return to legacy |

Percentage Split is a native segment rule, not an application-side hash, random choice, multivariate Boolean value, or paid experimentation feature. Use the pinned deployment's supported native identity-based split. Leave beta overrides inactive when testing percentage-only behavior.

Acceptance evaluates stability per tier and Environment. The same ID need not have the same bucket across different Projects, Environments, segments, or evaluation engines. Do not promise exact 10% or 50% counts in 20 users. For an unchanged native split segment, increasing the threshold must retain previously included users within that tier; recreate neither the segment nor identities during the comparison.

Identity overrides take precedence over segment overrides. Setting only the environment default to off does not defeat an enabled override. The runbook must explicitly remove competing overrides before baseline and rollback scenarios.

## 10. Configuration and operational boundaries

| Input | Storage / behavior |
| --- | --- |
| Frontend URL and client key | Ignored `poc\frontend\public\poc-config.json`, created from a checked-in keyless example |
| Frontend fixture | Public static asset from `poc\shared\demo-users.json` |
| Backend URL / refresh | Non-sensitive appsettings; Development launch profile binds loopback |
| Backend server key | .NET user-secrets with a fixed POC UserSecretsId, or process environment |
| Management credentials | Existing local Flagsmith setup only; never in the POC |

Validate that frontend configuration is not a `ser.` key. Do not log or attach configuration containing keys. A client key is public by design, but using a local ignored file avoids accidentally reusing another environment.

Allow the browser origin `http://localhost:4200` in local Flagsmith CORS. No backend CORS exception is needed when the Angular business proxy is used. Local HTTP is a loopback-only development exception, not deployment guidance.

PowerShell helpers must anchor an explicit repository root, use argument arrays, verify paths, propagate external exit codes, and never change unrelated processes or the Flagsmith database. Start each dev server in a foreground terminal; Ctrl+C owns that terminal's process. No global process-name termination or persistent hidden daemon is required.

## 11. Acceptance matrix

| ID | Check | Required result |
| --- | --- | --- |
| A01 | Frontend SDK path | Browser SDK traffic goes directly to private Flagsmith; no frontend flag-query call to the backend |
| A02 | Backend SDK path | Warm local evaluation makes no remote evaluation HTTP requests |
| A03 | Off/on combinations | Each of the four frontend/backend combinations works independently |
| A04 | Fixture integrity | Exactly 20 IDs, five beta users, one fixture source, unknown IDs rejected |
| A05 | Beta targeting | First five users new, remaining users legacy in the beta-only scenario |
| A06 | Stable repeats | For each user, ten repeated evaluations and selected-user reloads give the same result under unchanged rules |
| A07 | Percentage expansion | 10% included set is a subset of 50%; 100% includes all users; no exact small-sample count assertion |
| A08 | Identity race | Delayed old SDK or API work cannot restore the previous user's state |
| A09 | Dynamic change | On a healthy local deployment and foreground browser, new outcomes appear within a 20-second acceptance budget without rebuild/restart |
| A10 | Startup states | Backend starts with the flag either on or off; absent document/flag fails startup |
| A11 | Default/error | Missing flags and refresh/evaluation failures are observable; frontend uses legacy, backend follows section 8 |
| A12 | Loopback and transport | HTTP exception only in Development on exact loopback; redirects and remote fallback blocked |
| A13 | Exposure | No server key, backend flag inventory, or environment document in browser assets/responses/logs |
| A14 | Rollback | After clearing enabling overrides, both demonstrations return to legacy within the healthy propagation budget |
| A15 | Ownership | No duplicated timers/Providers or leaked test pollers after mounting, teardown, or test completion |

A09 is a measured acceptance budget under healthy local conditions, not an unconditional propagation or kill-switch guarantee.

Use automated tests for deterministic contracts and races. Use the real local Flagsmith deployment for provider compatibility, native segment evaluation, percentage behavior, and propagation. Mocked browser/API responses do not count as live Flagsmith acceptance.

## 12. Deliverables and implementation gate

Deliver the application, shared fixture, locked dependencies, focused tests, Windows helpers, and a repeatable Flagsmith setup/demo runbook under `poc\`. Preserve all existing reference examples and user-owned changes.

The [development plan](../plans/2026-10-16-feature-flag-poc-plan.md) decomposes this specification. Review these two documents before application implementation. Creating this specification or executing the future plan does not authorize a commit, branch change, push, cloud deployment, production mutation, or database reset.

## 13. Evidence

- [Repository integration Skill](../../../.github/skills/openfeature-flagsmith-dotnet/SKILL.md) and [version evidence](../../../.github/skills/openfeature-flagsmith-dotnet/references/official-sources.md).
- [Browser Provider 0.3.0 metadata](https://registry.npmjs.org/@openfeature%2fflagsmith-client-provider/0.3.0): Web SDK `^1.0.0`, Flagsmith JavaScript `^12.1.2`.
- [Browser Provider release source](https://github.com/open-feature/js-sdk-contrib/blob/cf5d541f90423a84009ad3a957e010043ef5ff7b/libs/providers/flagsmith-client/src/lib/flagsmith-client-provider.ts): nested traits, context lifecycle, native client access, missing-flag `DEFAULT` reason.
- [Flagsmith JavaScript 12.4.0 types](https://github.com/Flagsmith/flagsmith-js-client/blob/v12.4.0/types.d.ts): supported `fetch` option and native context/refresh contracts.
- [Flagsmith 9 flag lookup](https://github.com/Flagsmith/flagsmith-dotnet-client/blob/v9.0.0/Flagsmith.FlagsmithClient/Flags.cs): unknown features throw when no default handler is configured; enabled and disabled known features are both valid.
- [Flagsmith segments](https://docs.flagsmith.com/flagsmith-concepts/segments) and [native Percentage Split](https://docs.flagsmith.com/flagsmith-concepts/segments/segment-rule-operators?operators=percent): rule precedence, identity-based stable split, increasing thresholds.
- [Angular build 20.3.0 metadata](https://registry.npmjs.org/@angular%2fbuild/20.3.0) and [unit-test schema](https://github.com/angular/angular-cli/blob/20.3.0/packages/angular/build/src/builders/unit-test/schema.json): Node/TypeScript peers and Vitest builder options.
- [ASP.NET Core integration testing](https://learn.microsoft.com/en-us/aspnet/core/test/integration-tests?view=aspnetcore-10.0): WebApplicationFactory and isolated test-service overrides.

Evidence was reviewed on 2026-10-16. This document records a development design, not completed build, browser, or live-provider verification.
