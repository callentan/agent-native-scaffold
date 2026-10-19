# Direct-SDK feature flag POC implementation plan

> **For the implementing agent:** Use executing-plans in the current session, or subagent-driven-development only when delegation is requested. Track steps with checkboxes. Do not start application implementation until the user has reviewed the specification and plan.

**Goal:** Build the smallest separate Angular/ASP.NET Core demonstration of independent flags, fixed user switching, and native stable percentage rollout.

**Architecture:** Each tier uses its own OpenFeature SDK and official Flagsmith Provider/SDK. The page directly connects to the frontend Flagsmith Project, while the backend evaluates its own Project's rules locally. A single backend demo endpoint returns an old/new execution result, never frontend decisions.

**Stack:** Angular 20.3.0, .NET 10, OpenFeature Web 1.10.0 and .NET 2.14.1, Flagsmith browser Provider 0.3.0 and .NET Provider 0.3.1, Vitest, xUnit, Playwright, Windows PowerShell 7.4+.

**Specification:** [Direct-SDK POC specification](../specs/2026-10-16-feature-flag-poc-design.md). Read it before this plan; its requirements and acceptance IDs are authoritative.

## Global constraints

- Only two Boolean flags: `frontend_demo_v2` and `backend_demo_v2`; default `false`.
- Two dedicated Flagsmith Projects, each with one `local` Environment.
- Exactly 20 users, IDs `demo-user-001` through `demo-user-020`; users 001-005 are beta.
- Targeting key is the exact fixed user ID, not a random session ID.
- Frontend refresh is 5 seconds, SDK HTTP timeout through the supported fetch option is 2 seconds, frontend decision validity is at most 15 seconds.
- Backend document refresh is 10 seconds, timeout is 2 seconds, retries are zero.
- Healthy local foreground propagation acceptance budget is 20 seconds.
- Only one business endpoint: `GET /api/demo?userId=demo-user-001`.
- No product/quote/order domain, real authentication, database, BFF, feature-query HTTP API, custom runtime Provider, or application bucketing.
- Keep documentation and UI labels in English, following the repository convention.
- All scripts use PowerShell 7 with an explicit root, argument arrays, checked exit codes, and foreground server ownership.
- Do not modify the existing Skill examples. Do not create branches, commit, push, deploy, or reset data without explicit authorization.

## File map

All application paths below are future deliverables, not files claimed to exist at planning time.

| Path | Responsibility |
| --- | --- |
| `poc\README.md` | Prerequisites, configuration, commands, acceptance status and links |
| `poc\shared\demo-users.json` | Single source of synthetic users |
| `poc\backend\Poc.Api.csproj` | Web SDK, `net10.0`, exact runtime packages and fixture output copy |
| `poc\backend\packages.lock.json` | Generated NuGet lockfile |
| `poc\backend\Program.cs` | DI, startup, the one endpoint, shutdown |
| `poc\backend\DemoUsers.cs` | Load/validate fixed users and perform exact ID lookup |
| `poc\backend\DemoReply.cs` | Typed business response and deterministic legacy/new branch |
| `poc\backend\LocalEvaluation.cs` | POC adaptation of native SDK setup and document-only transport |
| `poc\backend\appsettings.json` | Non-secret defaults and precise SDK logging filter |
| `poc\backend\Properties\launchSettings.json` | Loopback Development launch profile |
| `poc\backend.tests\Poc.Api.Tests.csproj` | xUnit/MVC Testing packages and project reference |
| `poc\backend.tests\packages.lock.json` | Generated NuGet test lockfile |
| `poc\backend.tests\DemoContractTests.cs` | Fixture and response tests |
| `poc\backend.tests\LocalEvaluationTests.cs` | Synthetic-document transport, context and startup tests |
| `poc\backend.tests\DemoEndpointTests.cs` | HTTP contract, validation, no-store and concurrent identities |
| `poc\backend.tests\Fixtures\` | Synthetic document transport and process-isolated SDK/API test support |
| `poc\frontend\package.json`, `package-lock.json` | Pinned dependencies and scripts |
| `poc\frontend\angular.json` | Standalone application, shared assets, build/dev-server/Vitest targets |
| `poc\frontend\tsconfig.json`, `tsconfig.app.json`, `tsconfig.spec.json` | Strict compiler/test configuration |
| `poc\frontend\proxy.conf.json` | Business `/api` forwarding only |
| `poc\frontend\public\poc-config.example.json` | Keyless public-configuration template |
| `poc\frontend\public\poc-config.json` | Ignored developer-supplied client configuration |
| `poc\frontend\src\index.html`, `main.ts`, `styles.css` | HTML entry, standalone bootstrap and minimal global styles |
| `poc\frontend\src\app\demo-contracts.ts` | Runtime validators and typed user/config/response contracts |
| `poc\frontend\src\app\demo-contracts.spec.ts` | Invalid fixtures/configuration/response tests |
| `poc\frontend\src\app\feature-demo.service.ts` | Application-owned official Provider lifecycle and reactive frontend state |
| `poc\frontend\src\app\feature-demo.service.spec.ts` | Direct SDK initialization, refresh, expiry and identity races |
| `poc\frontend\src\app\app.component.ts`, `.html`, `.css`, `.spec.ts` | Single-page display, user selection and backend invocation |
| `poc\tests\playwright.config.ts`, `demo.spec.ts` | Browser integration with controlled network fixtures |
| `poc\docs\flagsmith-demo.md` | Exact native-configuration scenarios and live acceptance worksheet |
| `poc\scripts\Invoke-Poc.ps1` | Restore/build/test and foreground server commands |
| `poc\scripts\Test-PocScripts.ps1` | Dependency-free parser/argument/exit-code helper tests |
| `.gitignore` | Ignore local config, runtime secrets and generated reports |
| `README.md` | Link completed POC once implemented; preserve reference documentation |

Do not create a solution solely for this two-project backend. Project-reference paths suffice. Do not introduce extra dependency-injection facades or an `IFeatureFlagService`; endpoint decisions use the injected OpenFeature `FeatureClient`.

## Execution and command conventions

Each task contains one red/green test cycle and an independently reviewable deliverable. Scaffolding and dependency restoration belong to that deliverable, not a separate architecture task.

For the development workstation, all command paths below are absolute. `Invoke-Poc.ps1` will anchor `RepositoryRoot` using `Resolve-Path`, then select the appropriate working directory before every external call. Until that helper exists in task 5, run a single test/build command from a terminal explicitly opened at the working directory printed with that command. Do not combine setup and commands into an inline multi-step PowerShell string.

Use package-manager scaffolding when it matches the file map, but suppress implicit Git initialization and dependency installation. Then pin the direct dependencies before the first restore. Do not use an unpinned `npx` scaffolder, install globally, or upgrade the Skill samples.

### Task 1: Backend old/new behavior through the real SDK

**Files:** Create `poc\shared\demo-users.json`, `poc\backend\` and `poc\backend.tests\` files from the map. Update only directly relevant ignore rules.

**Acceptance:** A02, A04, A10-A13, backend portion of A15.

- [ ] **Step 1: Establish the contract tests and project configuration.**

Create the Web project and xUnit project with exact dependencies from specification section 3, nullable enabled and warnings as errors. Set `RestorePackagesWithLockFile=true`. Use the checked-in synthetic user file as a content item copied to build and publish output:

```xml
<Content Include="..\shared\demo-users.json"
         Link="demo-users.json"
         CopyToOutputDirectory="PreserveNewest"
         CopyToPublishDirectory="PreserveNewest" />
```

Define the contract types in the named files:

- `DemoUser(string Id, string Label, bool Beta)`.
- `DemoUsers.Load(string path)` validates exact count, ordered expected IDs, labels, and beta assignments; invalid data fails startup.
- `DemoUsers.Find(string? id)` returns the matching `DemoUser` or null using ordinal exact matching.
- `DemoReply(string UserId, string Mode, string Message)` and `DemoReply.Create(string userId, bool enabled)`.

Add this response test and a fixture test asserting 20 users, five beta users, duplicate rejection, and rejection of an unknown or whitespace-padded ID:

```csharp
using Xunit;

public sealed class DemoReplyTests
{
    [Theory]
    [InlineData(false, "legacy", "Backend: legacy")]
    [InlineData(true, "new", "Backend: new")]
    public void MapsTheEvaluatedBranch(bool enabled, string mode, string message)
    {
        var reply = DemoReply.Create("demo-user-001", enabled);
        Assert.Equal("demo-user-001", reply.UserId);
        Assert.Equal(mode, reply.Mode);
        Assert.Equal(message, reply.Message);
    }
}
```

Restore after the manifests exist. Working directory: `C:\shs_repos\teamplay\poc\flagsmith\poc\backend.tests`. Run:

```powershell
dotnet test 'C:\shs_repos\teamplay\poc\flagsmith\poc\backend.tests\Poc.Api.Tests.csproj' --verbosity minimal
```

Expected red result: the specified production contract types/behavior do not yet satisfy the tests. Dependency/network failures are not an acceptable red test; resolve them first and retain the real error output.

- [ ] **Step 2: Implement fixture validation and the two response branches.**

Use JSON deserialization with `JsonSerializerDefaults.Web` into typed records so the shared camel-case JSON maps to the C# records, then validate the complete fixture. Do not silently generate missing users or ignore malformed entries. The response branch is:

```csharp
public sealed record DemoReply(string UserId, string Mode, string Message)
{
    public static DemoReply Create(string userId, bool enabled) =>
        new(userId, enabled ? "new" : "legacy",
            enabled ? "Backend: new" : "Backend: legacy");
}
```

- [ ] **Step 3: Add failing local-evaluation and HTTP tests before wiring the endpoint.**

Adapt the repository reference's synthetic HTTP transport. Use the actual contrib Provider and Flagsmith SDK, not an HTTP flags facade or a hand-coded percentage algorithm. Include:

| Test | Assertion |
| --- | --- |
| Startup with known flag off/on | Both start successfully |
| Missing document, even with a transport that would return flags | Startup rejected; zero remote evaluation requests reach transport |
| Missing flag in a valid document | Startup rejected |
| Invalid URL, scheme, server key, redirect | Rejected before unsafe transport |
| Repeated identity evaluations | Invocation targeting key and flat beta traits are used; hot path adds zero HTTP requests |
| Distinct concurrent users | No global context mutation or cross-user result |
| HTTP input validation | Missing/empty/unknown ID gives 400 and `Unknown demo user.` |
| HTTP success | Exact reply shape and `Cache-Control: no-store`; no flag inventory |
| Unknown flag after initialization | Legacy response plus bounded evaluation-error logging |
| SDK application Information logging | No document body/key; Warning still observable |

Keep one local-mode SDK lifetime per child process. `Fixtures\` must provide child-process ownership with explicit working directory, bounded readiness timeout, captured stdout/stderr, exact PID cleanup, and nonzero failure propagation. Pure contract tests stay in-process. `WebApplicationFactory<Program>` may run inside the child, replacing only the native HTTP transport with the synthetic one. Do not use an application environment that bypasses SDK startup.

Expose `public partial class Program` for HTTP integration tests. The test-support transport is an injection seam, not a production feature service.

- [ ] **Step 4: Implement native initialization and direct endpoint evaluation.**

Copy and adapt `LocalEvaluation.cs`, retaining the document-only HTTP guard and disabled redirects. Keep the original Skill file unchanged. Permit HTTP only for exact loopback in Development, using the actual host environment rather than a browser/request flag.

Initialize before accepting traffic. Read `GetEnvironmentFlags()` and await `IsFeatureEnabled("backend_demo_v2")` to prove the feature exists; accept either Boolean result and configure no native default handler that could conceal a missing startup flag. Register `FlagsmithProvider` with `UsingBooleanConfigValue=false`.

Inject `FeatureClient` into the endpoint. After `DemoUsers.Find` succeeds, construct context and obtain the decision:

```csharp
var context = EvaluationContext.Builder()
    .SetTargetingKey(user.Id)
    .Set("beta", user.Beta)
    .Build();
var details = await featureClient.GetBooleanDetailsAsync(
    "backend_demo_v2", false, context);
if (details.ErrorType != OpenFeature.Constant.ErrorType.None)
    logger.LogWarning("Backend demo flag evaluation failed: {ErrorType}",
        details.ErrorType);
var reply = DemoReply.Create(user.Id,
    details.ErrorType == OpenFeature.Constant.ErrorType.None && details.Value);
```

Here `user` is the validated `DemoUser`, `featureClient` is the injected OpenFeature client, and `logger` is the endpoint's injected application logger. Return `Results.Ok(reply)` with no-store. Invalid input uses `Results.Problem(statusCode: 400, title: "Unknown demo user.")` before evaluation.

Configure loopback binding, native refresh/timeout/retry settings, `FlagsmithSdk=Warning`, and server-key loading through user-secrets/environment. Shut down the owned OpenFeature API on process exit, without claiming deterministic native poller disposal.

- [ ] **Step 5: Run the backend tests to green and build.**

Working directory: `C:\shs_repos\teamplay\poc\flagsmith\poc\backend.tests`.

```powershell
dotnet test 'C:\shs_repos\teamplay\poc\flagsmith\poc\backend.tests\Poc.Api.Tests.csproj' --no-restore --verbosity minimal
```

Then run the production project build as a separate command from `poc\backend`:

```powershell
dotnet build 'C:\shs_repos\teamplay\poc\flagsmith\poc\backend\Poc.Api.csproj' --no-restore --verbosity minimal
```

Expected: tests pass, warnings-as-errors build succeeds, child processes exit, no persistent test pollers remain. Review the task diff; do not commit without authorization.

### Task 2: Frontend direct-SDK lifecycle with fixed identities

**Files:** Create frontend package/configuration/entry files, `demo-contracts.ts`, `feature-demo.service.ts` and their tests. Reuse the shared user fixture from task 1.

**Acceptance:** A01, frontend portions of A04, A06, A08-A09, A11, A13, A15.

- [ ] **Step 1: Create a minimal standalone Angular workspace and failing tests.**

Use the exact Angular/runtime versions from the specification. Configure the `@angular/build:application` build, `@angular/build:dev-server` serve, and `@angular/build:unit-test` test targets. The test target requires `buildTarget`, `tsConfig`, and `runner=vitest` in Angular 20.3.0; do not copy a newer Angular test schema.

Serve `public\` and copy the shared fixture through an asset glob with `input=../shared`, `glob=demo-users.json`, and output at the public root. Configure strict TypeScript and Angular templates. Include Vitest `3.2.4` and jsdom `26.1.0`; use the Angular builder to initialize TestBed and compile Angular code.

Define these interfaces:

```typescript
export interface DemoUser {
  readonly id: string;
  readonly label: string;
  readonly beta: boolean;
}

export interface PublicConfig {
  readonly flagsmithApiUrl: string;
  readonly flagsmithClientKey: string;
}

export interface DemoReply {
  readonly userId: string;
  readonly mode: 'legacy' | 'new';
  readonly message: 'Backend: legacy' | 'Backend: new';
}

export interface FrontendState {
  readonly userId: string | null;
  readonly status: 'loading' | 'ready' | 'error';
  readonly enabled: boolean;
  readonly error: string | null;
  readonly evaluatedAt: number | null;
}
```

Implement runtime parser exports named `parseDemoUsers`, `parsePublicConfig`, and `parseDemoReply`, accepting `unknown`. Parsing failures are explicit errors surfaced at the corresponding UI boundary. Require response mode/message agreement and the expected selected user ID.

Define root `FeatureDemoService` with read-only `users` and `state` signals, `initialize(): Promise<void>`, `selectUser(user: DemoUser): Promise<void>`, `refresh(): Promise<void>`, `enabled(): boolean`, and `ngOnDestroy(): void`. It owns the official Provider directly; it is not a custom Provider or remote evaluation API.

Test the official browser Provider using a controlled native Flagsmith client or native HTTP fixtures. Do not substitute a custom application Provider. Use fake timers and deferred promises to test:

- Explicit API/client key and `poc-ui` binding; server-key and invalid-host rejection.
- Correct nested beta traits, one Provider, initial safe state.
- Normal off, normal on, missing flag with `reason=DEFAULT`, SDK error.
- Native five-second refresh; only one mutation in flight.
- User A pending refresh, then B, then C; only C may publish.
- Failure of A does not leave the queue permanently rejected.
- Expiry at exactly 15 seconds even while refresh remains pending.
- Visibility restoration clears stale state before fetching.
- Teardown cancels timers/listeners and prevents late publication.

Working directory: `C:\shs_repos\teamplay\poc\flagsmith\poc\frontend`. Restore after creating/pinning the manifest; run:

```powershell
npm --prefix 'C:\shs_repos\teamplay\poc\flagsmith\poc\frontend' test -- --watch=false
```

Expected red result: the newly specified validators and lifecycle fail their behavioral assertions, rather than a dependency or test-builder error.

- [ ] **Step 2: Implement validated configuration and direct Provider initialization.**

The checked-in configuration example has the local private URL and an empty key. Empty keys are intentionally rejected; the developer supplies their actual frontend client key in the ignored local file. Never ship a server key or select a SaaS URL by omission.

Create the official Provider once. Use the supported fetch injection to enforce the deadline rather than supplying an unsupported timeout property:

```typescript
const fetchWithTimeout: typeof fetch = (input, init) => {
  const inherited = init?.signal
    ?? (input instanceof Request ? input.signal : undefined);
  const signals = [AbortSignal.timeout(2000)];
  if (inherited) signals.push(inherited);
  return fetch(input, { ...init, signal: AbortSignal.any(signals) });
};
const provider = new FlagsmithClientProvider({
  environmentID: config.flagsmithClientKey,
  api: config.flagsmithApiUrl,
  cacheFlags: false,
  enableAnalytics: false,
  realtime: false,
  enableLogs: false,
  enableEvents: false,
  fetch: fetchWithTimeout
});
await OpenFeature.setProviderAndWait('poc-ui', provider, {
  targetingKey: user.id,
  traits: { beta: user.beta }
});
const client = OpenFeature.getClient('poc-ui');
const details = client.getBooleanDetails('frontend_demo_v2', false);
```

`config` and `user` have passed the parsers and exact fixed-user lookup. The fetch deadline also aborts stalled response-body reads; preserve caller cancellation. Leave event tracking and SDK verbose logging disabled. Match the pinned SDK's real types; do not force compatibility with casts. Test transport timeout without replacing the official Provider.

- [ ] **Step 3: Implement serialized refresh, selection generations, expiry, and teardown.**

Apply this operation order, with every SDK mutation on the same queue:

1. On selection, increment generation, publish legacy/loading immediately, and remember the desired user.
2. Enqueue `OpenFeature.setContext('poc-ui', context)` after any current native operation.
3. After awaiting, compare both generation and desired user before reading and publishing SDK details.
4. Enqueue native `provider.flagsmithClient.getFlags()` for refresh; schedule the next refresh only after completion.
5. During an owned operation, Ready/ConfigurationChanged events cannot publish. Afterwards, publish only the active generation and matching native identity.
6. Missing/default/error details publish a sanitized error with `enabled=false`; failed queue entries are observed and do not block later work.
7. Maintain an independent 15-second deadline; `enabled()` rechecks current time rather than retaining an expired true value in a cached computed.
8. On visibility restoration or teardown, invalidate stale work before any new publication.

Use Angular signals for state updates and `DestroyRef`/application ownership for cleanup. Do not copy the BFF snapshot sample, install an in-memory runtime Provider, or replace the Provider for each user.

- [ ] **Step 4: Run lifecycle/contract tests to green and build.**

Working directory: `C:\shs_repos\teamplay\poc\flagsmith\poc\frontend`.

```powershell
npm --prefix 'C:\shs_repos\teamplay\poc\flagsmith\poc\frontend' test -- --watch=false
```

Run separately:

```powershell
npm --prefix 'C:\shs_repos\teamplay\poc\flagsmith\poc\frontend' run build
```

Expected: deterministic timer/race tests and strict production compilation pass. Leave no active test timers or Provider closures. Review this deliverable without claiming live-provider acceptance.

### Task 3: Single page and ordinary backend invocation

**Files:** Create component files, business-only proxy, Playwright configuration and tests; add Playwright `1.56.1` to the frontend development manifest and regenerate its lockfile.

**Acceptance:** A01, A03-A04, A08, user-visible portion of A13.

- [ ] **Step 1: Write page and request-race tests.**

Use Angular TestBed/HttpTestingController for component requests. Add stable selectors `demo-user`, `frontend-result`, `call-backend`, `backend-result`, `frontend-error`, and `backend-error`.

Use this browser contract:

```typescript
import { expect, test } from '@playwright/test';

test('initial user is fixed and backend result starts empty', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByTestId('demo-user')).toHaveValue('demo-user-001');
  await expect(page.getByTestId('backend-result')).toBeEmpty();
});
```

The Playwright configuration uses `baseURL=http://localhost:4200`, `testDir` pointing to `poc\tests`, and one Chromium project. Before page navigation, controlled `page.route` fixtures provide users, public config, native frontend SDK responses, and `/api/demo` results, including required cross-origin response headers. Every mocked SDK response must use the pinned native protocol shape, not a made-up frontend flags endpoint. These tests need only the frontend dev server, not a real-key backend or Flagsmith process.

Add tests for all four frontend/backend combinations, exact user ID submission, backend errors, response-user mismatch, immediate clearing on selection, and a delayed user-A response after user-B selection. Assert that no browser request asks the backend for feature flags.

Run the Angular test command from task 2 and Playwright using its checked-in CLI entry from the frontend working directory:

```powershell
node 'C:\shs_repos\teamplay\poc\flagsmith\poc\frontend\node_modules\@playwright\test\cli.js' test --config 'C:\shs_repos\teamplay\poc\flagsmith\poc\tests\playwright.config.ts'
```

Expected red result: missing page behavior or failed contract assertions. If Chromium is missing, install the matching Playwright Chromium as a separate, explicit prerequisite; do not count installation failure as a red test.

- [ ] **Step 2: Implement the minimal template and direct business call.**

Bind the select to the fixture users and show the selected ID/beta value. Render the frontend result using `FeatureDemoService.enabled()` and reactive status. Use visible text, neutral legacy styling, and a distinct new-state border/background.

Configure only this business proxy:

```json
{
  "/api": {
    "target": "http://127.0.0.1:5000"
  }
}
```

Use Angular `HttpClient` to call `/api/demo` with `userId` as a parameter. Before each call capture selection generation and user ID. Apply a two-second timeout, validate `unknown` JSON with `parseDemoReply`, and publish only if both still match. On selection, cancel/invalidate the previous request and clear its result immediately. An error displays the sanitized failure, not a fabricated successful response.

The frontend decision must not change merely because backend `mode` changes, and the backend request must not include the frontend Boolean or trait dictionary.

- [ ] **Step 3: Run page tests to green and verify the browser boundary.**

Run Angular and browser commands separately from their explicitly stated working directory. Inspect captured network requests for direct frontend Flagsmith traffic, ordinary `/api/demo` calls, and absence of server keys/environment documents. Controlled tests prove UI wiring only, not live segment or native local/remote parity.

### Task 4: Reproducible native targeting and rollout acceptance

**Files:** Create `poc\docs\flagsmith-demo.md`; extend `poc\tests\demo.spec.ts` only with reusable browser interactions, keeping controlled and live evidence separate.

**Acceptance:** A05-A07, A09, A14, live portions of A01-A03 and A10-A13.

- [ ] **Step 1: Write the live acceptance worksheet before configuring a deployment.**

Provide a record for each specification acceptance ID with the fields `scenario`, `project/environment`, `flag`, `segment ID`, `selected user IDs`, `expected`, `observed`, `elapsed seconds`, and `result`. Do not pre-fill passing observations or store keys/documents.

Define cohorts as sets of the 20 IDs and specify these assertions:

```typescript
import { expect } from '@playwright/test';

export function assertStableExpansion(
  tenPercent: ReadonlySet<string>,
  fiftyPercent: ReadonlySet<string>,
  hundredPercent: ReadonlySet<string>,
  allUsers: ReadonlySet<string>
): void {
  for (const id of tenPercent) {
    expect(fiftyPercent.has(id)).toBe(true);
  }
  expect([...hundredPercent].sort()).toEqual([...allUsers].sort());
}
```

Define `tenPercent`, `fiftyPercent`, and `hundredPercent` as observations collected separately for each tier after configuration convergence. No assertion requires exactly two or ten included users. Live runs require an explicitly designated local POC deployment and operator configuration; they must never mutate another environment automatically.

- [ ] **Step 2: Document exact Flagsmith setup and scenario transitions.**

Document creation of the two Projects/Environments, one Boolean feature in each, frontend client key versus backend server key, local CORS origin, shared beta contract, and native Percentage Split.

Use the specification's scenario table verbatim in substance. For beta-only targeting, enable only the `beta=true` override. For percentage-only targeting, disable beta and identity overrides, use one native split segment, and edit its threshold in place from 10 to 50 to 100.

Explain that turning an environment default off is insufficient while an enabling override is active. Rollback must deactivate all enabling segment/identity overrides and then use default off. Do not delete/recreate segments between cohort comparisons or emulate splitting in application code.

- [ ] **Step 3: Execute the live scenarios when implementation and a local instance exist.**

For each tier, run off, on, beta-only, and percentage-only scenarios. Repeat each user's evaluation ten times, reload the selected user where applicable, and verify stable membership. Re-select the same noninitial user after reload because the selector is deliberately not persisted.

Measure configuration changes with a foreground page and healthy local instance; require observed convergence within 20 seconds. Verify all four independent on/off combinations. Record any failure rather than broadening timeouts until it appears successful.

Run backend startup once with the flag on and once off. With a separate disposable test process, verify cold failure without a document; do not bring down a shared deployment. If testing warm outage manually, explain frontend legacy/error versus backend native last-known-good behavior and do not label it an instant kill switch.

- [ ] **Step 4: Complete the evidence record or mark the live run unexecuted.**

Acceptance passes only on measured results. If local deployment or keys are unavailable, mark live checks `NOT RUN` with the exact prerequisite and do not replace them with mocks. A development handoff may contain this blocker; application acceptance is incomplete until the live matrix is executed.

### Task 5: Windows helpers and repeatable handoff

**Files:** Create `poc\scripts\Invoke-Poc.ps1`, `Test-PocScripts.ps1`; expand `poc\README.md`; update root README and `.gitignore` as directly required.

**Acceptance:** Operational requirements in specification section 10 and completion evidence for A01-A15.

- [ ] **Step 1: Specify and test the helper command contract.**

Use this parameter surface:

```powershell
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$RepositoryRoot,
    [Parameter(Mandatory)]
    [ValidateSet('Restore', 'Build', 'Test', 'TestBrowser', 'StartBackend', 'StartFrontend')]
    [string]$Action
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
```

`Test-PocScripts.ps1` uses the PowerShell parser and child PowerShell invocations to assert: unknown actions fail, a nonexistent root fails, roots with spaces remain one argument, native failures are propagated, and operations do not depend on the caller's directory. Test argument forwarding with a temporary fixture under the session artifact directory, not with real servers or user secrets. Delete only the named fixture files created by the test.

Working directory: `C:\shs_repos\teamplay\poc\flagsmith`. Run:

```powershell
pwsh.exe -NoLogo -NoProfile -NonInteractive -File 'C:\shs_repos\teamplay\poc\flagsmith\poc\scripts\Test-PocScripts.ps1' -RepositoryRoot 'C:\shs_repos\teamplay\poc\flagsmith'
```

Expected red result: helper behavior fails these assertions before implementation.

- [ ] **Step 2: Implement bounded commands and foreground startup.**

Resolve and verify the supplied repository and project paths. Resolve native executable paths once; on Windows use the application entry such as `npm.cmd` rather than accidentally invoking a PowerShell policy-blocked `npm.ps1`. For every native process, use a `[string[]]` argument array, set/restore an explicit working directory, and check `$LASTEXITCODE`.

| Action | Commands / ownership |
| --- | --- |
| `Restore` | Locked-mode NuGet restore for app/tests, `npm ci`, matching Playwright Chromium installation |
| `Build` | Backend build with no restore, frontend production build |
| `Test` | Backend tests with no restore, frontend non-watch unit tests |
| `TestBrowser` | Playwright Chromium tests; test runner owns any test-only dev servers and reaps them |
| `StartBackend` | Foreground `dotnet run` using loopback Development profile; Ctrl+C ends that process |
| `StartFrontend` | Foreground `npm start` on localhost:4200 with business proxy; Ctrl+C ends that process |

Initial implementation restores to generate lockfiles after manifest changes; subsequent `Restore` uses them without updating versions. Restoring does not create config keys, start Flagsmith, mutate the database, or silently enable a mock mode. Missing configuration produces actionable nonzero errors.

Playwright owns one bounded frontend dev server with an explicit working directory; its controlled browser tests intercept SDK and backend requests before navigation. The separate backend tests exercise the real backend SDK against a synthetic document transport. These are test fixtures, not production fallback modes or application flag APIs. Do not launch a real-key backend or Flagsmith server implicitly, and do not reuse an unrelated server just because its port responds.

- [ ] **Step 3: Write the developer and demo handoff.**

Document preflight versions, the existing local Flagsmith guide, the two Projects/keys, creation of ignored public config, and server-key setup using user-secrets or environment without committing the value. Keep examples PowerShell-only and avoid passing actual secrets in documented command lines.

Provide separate absolute-path helper invocations for restore, build, tests, and the two foreground server terminals. Link the native targeting runbook. Clearly label the localhost HTTP exception, cold-start requirement, frontend expiry, backend last-known-good limitation, and per-environment bucket independence.

Ignore `poc-config.json`, local secrets/config artifacts, `.angular\`, Playwright reports/test results, and any POC-generated logs. Preserve the existing global `node_modules`, `dist`, `bin`, and `obj` ignores.

- [ ] **Step 4: Run the smallest complete verification set and review scope.**

Run parser/helper tests, backend tests, frontend tests, both builds, and controlled Chromium tests through the new helper. Run live acceptance separately with operator configuration and attach its actual status.

Confirm the only demo endpoint is `/api/demo`, no custom runtime Provider exists, frontend assets contain only public configuration, the fixture has one source, and unrelated existing files and staged user changes are untouched.

The repository's `scripts\validate-skill.mjs` also scans unrelated Markdown for English text. If it fails on a pre-existing user-owned document, record the baseline failure; do not rewrite or unstage that document to make this POC appear green.

Do not commit automatically. If the user explicitly authorizes commits later, stage only the intended POC changes and include the required co-author trailer.

## Specification coverage and completion gate

| Requirement | Primary task |
| --- | --- |
| Backend direct SDK, native local evaluation, response contract | 1 |
| Frontend direct SDK, refresh, defaults, identity lifecycle | 2 |
| Minimal separate frontend/backend page and four combinations | 3 |
| Fixed users and exact contracts | 1-3 |
| Native beta targeting and stable percentage expansion | 4 |
| Healthy propagation, real-provider checks, rollback | 4 |
| Windows operation, secrets, documentation, repeatability | 5 |

Before reporting implementation complete, record files, exact locked versions, flag contract, failure/freshness behavior, test evidence, live acceptance evidence, rollback steps, and every unexecuted check. No generated lockfiles, application build, browser run, or live Flagsmith acceptance exists merely because this plan has been written.
