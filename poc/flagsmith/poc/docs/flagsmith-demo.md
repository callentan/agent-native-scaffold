# Local Flagsmith targeting and rollout runbook

This runbook is the **local-only** acceptance procedure for the Flagsmith POC.
It uses the already-running private Flagsmith instance at
`http://localhost:8000`. It does not deploy to the cloud, provision
infrastructure, stop or reset Flagsmith, or change a Flagsmith environment
automatically. All Flagsmith changes below are manual Dashboard actions by an
operator who is explicitly authorized to use the two dedicated POC Projects.

The runbook deliberately separates:

- **Controlled browser evidence**: the Playwright tests use deterministic
  browser routes and are not live Flagsmith acceptance.
- **Live acceptance evidence**: the operator changes the local Projects and
  records measured results in the A01-A15 worksheet. A live result is not a
  PASS unless the check was actually run.

## 1. Scope and authorization gate

Use only synthetic users and the existing workstation Flagsmith instance. Do
not use a shared development or production Project. Do not use cloud
Flagsmith, cloud deployment, or infrastructure for this POC.

Do not begin the live matrix until every prerequisite below is explicitly
confirmed:

1. `http://localhost:8000` is the current local Flagsmith instance and is
   already running. Reuse it; do not stop, reset, migrate, or recreate its
   database for this runbook.
2. The operator can access the local Dashboard and is authorized to configure
   the two POC Projects.
3. The dedicated Projects and their `local` Environments exist as described
   in section 2, or the operator is authorized to create them manually.
4. The `poc-frontend`/`local` client-side environment key and the
   `poc-backend`/`local` server-side `ser.` environment key have been
   explicitly supplied through the local development configuration paths in
   section 4. Never infer or copy keys from another Environment.
5. The local POC flags and segments are present and the operator is
   authorized to change them for the duration of the matrix.

The checked-in `poc/frontend/public/poc-config.example.json` is intentionally
keyless. It is not evidence that a live client key is configured. If any gate
item is missing, record the applicable live checks as `NOT RUN` with the
missing prerequisite; do not substitute controlled mocks.

## 2. Create the two isolated local Projects and Environments

Projects are separate because Flagsmith feature and segment inventories are
Project-scoped. Configure these exact names in the local Dashboard:

| Project | Environment | Boolean feature | Application key |
| --- | --- | --- | --- |
| `poc-frontend` | `local` | `frontend_demo_v2` | client-side environment key |
| `poc-backend` | `local` | `backend_demo_v2` | server-side `ser.` environment key |

For each Project, use the Dashboard to create or verify one Environment named
`local`. If an existing Project or Environment is not the designated POC
resource, stop and obtain authorization rather than editing it. Do not create
duplicate Projects with suffixed names: the worksheet must identify the exact
Project/Environment that was tested.

For each feature:

1. Create the feature in the matching Project's `local` Environment.
2. Use the exact Boolean feature key in the table above.
3. Use a Boolean enabled state, not a string or multivariate configuration
   value.
4. Set the Environment default to **disabled** before the first Off or
   targeting scenario.
5. Confirm that no identity override or segment override is active before
   recording the baseline.

The frontend browser may receive only the `poc-frontend` client-side key and
the public `frontend_demo_v2` evaluation. Never put the backend server key,
`backend_demo_v2`, an Environment document, management credentials, or raw
Flagsmith rules in browser assets, browser storage, responses, or logs.

In the local Flagsmith configuration, allow the exact browser origin
`http://localhost:4200` for SDK requests. Do not use a wildcard as a
replacement for the approved local origin. The Angular dev proxy forwards
business requests under `/api` to `http://127.0.0.1:5000`; it must not proxy
Flagsmith traffic or evaluate flags.

## 3. Fixed 20-user fixture and cohort definitions

The single checked-in source is
`poc/shared/demo-users.json`. It contains exactly these IDs, labels, and
traits:

| IDs | Labels | `beta` |
| --- | --- | --- |
| `demo-user-001` through `demo-user-005` | `User 001` through `User 005` | `true` |
| `demo-user-006` through `demo-user-020` | `User 006` through `User 020` | `false` |

Use the exact targeting key (the ID) for both SDKs. The browser context is
`{ targetingKey: user.id, traits: { beta: user.beta } }`. The backend derives
the flat `beta` attribute from its own loaded copy of the same fixture and
does not accept browser-supplied traits.

Use these explicit sets in the worksheet and in every rollout comparison:

```text
ALL_USERS = {
  demo-user-001, demo-user-002, demo-user-003, demo-user-004, demo-user-005,
  demo-user-006, demo-user-007, demo-user-008, demo-user-009, demo-user-010,
  demo-user-011, demo-user-012, demo-user-013, demo-user-014, demo-user-015,
  demo-user-016, demo-user-017, demo-user-018, demo-user-019, demo-user-020
}

BETA_USERS = {
  demo-user-001, demo-user-002, demo-user-003, demo-user-004, demo-user-005
}

NON_BETA_USERS = {
  demo-user-006, demo-user-007, demo-user-008, demo-user-009, demo-user-010,
  demo-user-011, demo-user-012, demo-user-013, demo-user-014, demo-user-015,
  demo-user-016, demo-user-017, demo-user-018, demo-user-019, demo-user-020
}
```

There are only 20 synthetic users; do not add random IDs, timestamps, real
people, roles, entitlements, or tenant identifiers. The initial browser
selection is `demo-user-001`. A reload deliberately selects that initial user
again; the selected user is not persisted.

For each native Percentage Split tier, collect observations separately:

```text
tenPercent    = set of IDs returned enabled at threshold 10
fiftyPercent  = set of IDs returned enabled at threshold 50
hundredPercent = set of IDs returned enabled at threshold 100
```

These are observations, not predetermined cohorts. Do not require exactly two
or ten enabled users in this 20-user sample. For an unchanged native split
segment, assert only that every member of `tenPercent` is in `fiftyPercent`
and that `hundredPercent` equals `ALL_USERS`.

## 4. Local application configuration

### 4.1 Frontend client key

From the repository root, copy the checked-in keyless example to the ignored
local file and fill it only with the `poc-frontend`/`local` client key:

```powershell
Set-Location 'C:\shs_repos\teamplay\poc\flagsmith'
Copy-Item -LiteralPath '.\poc\frontend\public\poc-config.example.json' `
  -Destination '.\poc\frontend\public\poc-config.json'
```

The resulting local-only file has this shape; replace the placeholder locally
and do not paste the key into this document or a report:

```json
{
  "flagsmithApiUrl": "http://localhost:8000/api/v1/",
  "flagsmithClientKey": "<client key for poc-frontend/local>"
}
```

The frontend parser rejects an empty key, a server-side `ser.` key, a
non-loopback URL, credentials, query/fragment text, or a path other than
`/api/v1/`. The browser uses `http://localhost:8000/api/v1/` directly.

### 4.2 Backend server key

The backend uses local evaluation and therefore requires the
`poc-backend`/`local` server-side key beginning with `ser.`. Store it in the
existing .NET user-secrets store or in the process environment; never commit
it:

```powershell
Set-Location 'C:\shs_repos\teamplay\poc\flagsmith'
dotnet user-secrets set 'FeatureFlags:EnvironmentKey' '<ser.server-key-for-poc-backend-local>' `
  --project '.\poc\backend\Poc.Api.csproj'
```

The environment-variable alternative for the backend process is:

```powershell
$env:FeatureFlags__EnvironmentKey = '<ser.server-key-for-poc-backend-local>'
```

The Development appsettings already point the backend at
`http://127.0.0.1:8000/api/v1/` and set a 10-second document refresh. The
backend accepts only the exact environment-document URI through its guarded
transport, uses a 2-second timeout and zero retries, and validates that
`backend_demo_v2` exists at startup. Both enabled and disabled flag states
are valid startup states.

### 4.3 Start the local applications

Start each process in its own foreground PowerShell terminal. Do not use a
hidden daemon or a machine-wide process-name termination command:

```powershell
# Terminal 1: backend
Set-Location 'C:\shs_repos\teamplay\poc\flagsmith'
dotnet run --project '.\poc\backend\Poc.Api.csproj' --launch-profile 'Poc.Api'
```

```powershell
# Terminal 2: frontend
Set-Location 'C:\shs_repos\teamplay\poc\flagsmith\poc\frontend'
npm.cmd start -- --host localhost --port 4200
```

The backend endpoint is `GET http://127.0.0.1:5000/api/demo?userId=<id>`.
The browser page is `http://localhost:4200`. Stop only the foreground terminal
that owns an application process after the run; do not stop or reset the
Flagsmith containers.

## 5. Native segments and scenario transitions

Create and maintain the following logical segments separately in each
Project's `local` Environment. Record the actual Flagsmith segment ID in the
worksheet; the names below are stable labels, not substitutes for IDs.

### 5.1 Native beta targeting

In both Projects, create or verify a segment named `beta-users` with the
native trait rule:

- trait/attribute name: `beta`
- comparison: Boolean equals `true`
- no percentage rule

Add an enabled feature-state override for the matching Boolean feature only
when running the Beta only scenario. The frontend receives nested browser
traits; the backend provider evaluates the backend invocation context
derived from the fixture. Do not create an application-side filter or a
second segment implementation.

Expected beta-only membership is `BETA_USERS` enabled and
`NON_BETA_USERS` legacy. This expectation is recorded, not a live result,
until the local segment has been evaluated.

### 5.2 Native Percentage Split

In both Projects, create or verify one segment named `stable-rollout` with
the native Flagsmith **Percentage Split** rule based on the identity
targeting key. Enable the matching feature through that segment only for the
Percentage scenario.

Run the same segment through these thresholds in order:

1. Set the native split threshold to `10`, save/publish, wait for the local
   configuration to converge, and evaluate all 20 IDs. Record `tenPercent`.
2. Edit the **same** segment rule in place to `50`; do not delete/recreate the
   segment or identities. Save/publish, wait for convergence, and record
   `fiftyPercent`.
3. Edit the same rule in place to `100`; wait for convergence and record
   `hundredPercent`.
4. Apply the stable-expansion assertion described in section 7.

Use the Flagsmith native operator; do not emulate a split with a hash,
random choice, multivariate value, or application code. A 20-user sample is
too small to turn 10% or 50% into an exact-count assertion. The same ID is
not promised to have the same bucket across different Projects,
Environments, segments, or evaluation engines.

### 5.3 Disable competing overrides before every transition

Identity overrides take precedence over segment overrides. An Environment
default of disabled does **not** defeat an enabled identity or segment
override. Before each scenario, inspect and explicitly disable/remove every
competing enabling override:

| Scenario | Environment default | Active segment overrides | Identity overrides | Expected demonstration |
| --- | --- | --- | --- | --- |
| Off | Disabled | None active | None | All users see legacy |
| On | Enabled | None active | None | All users see new |
| Beta only | Disabled | `beta-users` enabled only | None | Users 001-005 new; others legacy |
| Percentage | Disabled | `stable-rollout` enabled only | None | Native stable cohort at 10, then 50, then 100 |
| Rollback | Disabled | None active | None | All users return to legacy |

For `beta-users`, `stable-rollout`, and every identity override, use the
Dashboard's feature-state controls in the corresponding Project. Do not
leave both segments active during a percentage-only comparison. Do not
delete/recreate segments between thresholds. If the intended active override
cannot be shown unambiguously, mark the affected live check `NOT RUN`.

Run the table independently in `poc-frontend/local` and
`poc-backend/local`. Changing one Project must not be used as evidence about
the other Project.

## 6. Stable repeats and reload procedure

Run this procedure after each scenario has converged and before changing the
next rule:

1. For every ID in `ALL_USERS`, evaluate the frontend flag and the backend
   endpoint ten times without changing the rule. Record whether each result
   remains the expected value.
2. For a noninitial user, such as `demo-user-006`, reload
   `http://localhost:4200`. Confirm that the selector returns to
   `demo-user-001`, then re-select `demo-user-006`; the selector is
   deliberately not persisted.
3. Click **Call backend** after selecting the user and confirm the response
   contains that exact `userId`. A previous user's result must be cleared
   immediately and must not reappear after a delayed response.
4. Repeat the same selected user after a second reload. Do not count a
   cached page or a single successful read as stable evidence.
5. Record the ten observations and any elapsed time in the worksheet or an
   attached operator log. Never claim PASS from a controlled browser route;
   controlled and live evidence remain separate.

Frontend decisions refresh through the owned browser Provider without
persistent SDK state. A successful decision is usable for at most 15 seconds.
The backend keeps one process-owned local-evaluation client and refreshes its
environment document every 10 seconds. These are different freshness
boundaries; they do not promise simultaneous changes.

## 7. Update latency and percentage acceptance

### 7.1 Healthy foreground 20-second budget

Measure each dynamic change on a healthy local instance with the browser tab
foregrounded:

1. Select a known user and record the current observed result.
2. Start a stopwatch immediately before saving/publishing one authorized
   Dashboard change.
3. Without rebuilding or restarting either application, poll the same
   frontend user and call the backend for the same ID. Stop at the first
   observed result that matches the new rule.
4. Record the elapsed seconds from the save/publish action to the first
   visible frontend result and the first matching backend response.
5. The healthy acceptance budget is **20 seconds**. If either tier exceeds
   20 seconds, record the measured value and `FAIL`; do not increase a
   timeout or repeat until it appears successful.
6. Repeat for the reverse change where required by A09/A14. A change that
   needs a process restart, page rebuild, or Flagsmith restart is not a
   passing dynamic-change result.

The 20-second budget is an acceptance measurement under healthy local
conditions, not an unconditional propagation guarantee or an emergency-stop
deadline.

### 7.2 Stable expansion assertion

Collect `tenPercent`, `fiftyPercent`, and `hundredPercent` separately after
each native split threshold has converged. The reusable controlled assertion
in `poc/tests/demo.spec.ts` checks the required relationships without
asserting exact counts:

```typescript
for (const id of tenPercent) {
  expect(fiftyPercent.has(id)).toBe(true);
}
expect([...hundredPercent].sort()).toEqual([...allUsers].sort());
```

For live evidence, copy the observed IDs into the worksheet and note the
actual segment ID for each Project. A failure means the rule, segment, key,
or convergence state must be investigated; do not broaden the test to permit
an unstable cohort.

## 8. Four independent frontend/backend combinations

Set the two Projects independently and run all four combinations with at
least `demo-user-001` and `demo-user-006`:

| Combination | `poc-frontend/local` | `poc-backend/local` | Expected page / response |
| --- | --- | --- | --- |
| 1 | Off | Off | `Frontend: legacy`; `mode=legacy`, `Backend: legacy` |
| 2 | On | Off | `Frontend: new`; `mode=legacy`, `Backend: legacy` |
| 3 | Off | On | `Frontend: legacy`; `mode=new`, `Backend: new` |
| 4 | On | On | `Frontend: new`; `mode=new`, `Backend: new` |

The browser must make direct SDK traffic to the local Flagsmith API for the
frontend flag and must not receive backend flag data. The backend response
contains only the selected user ID, mode, and message; it does not expose a
flag dictionary, rule, key, or environment document.

## 9. Rollback

Rollback is a configuration transition, not deletion and not a process kill:

1. In **both** Projects, deactivate/remove all enabling `beta-users`,
   `stable-rollout`, and identity feature-state overrides.
2. Set both Environment defaults to disabled.
3. Save/publish and keep both applications running.
4. Wait for healthy propagation and measure the result using section 7.
5. Evaluate every ID in `ALL_USERS`. The frontend must show
   `Frontend: legacy`; the backend must return `mode=legacy` and
   `Backend: legacy`.
6. Record the transition and elapsed seconds as A14. If an enabling override
   remains, the default-off state is not a rollback and must not be marked
   PASS.

Do not delete the Projects, Environments, flags, segments, fixture, or local
database as part of rollback.

## 10. Bounded outage semantics

These behaviors are intentionally different and are not an instant kill
switch:

| Condition | Frontend behavior | Backend behavior |
| --- | --- | --- |
| Initial configuration/document unavailable | Shows legacy UI with a sanitized configuration/service error; no new decision is authorized | A missing/malformed document or missing `backend_demo_v2` fails startup with a nonzero exit |
| Healthy refresh | Browser Provider refreshes through the direct local SDK path; a successful decision is fresh for at most 15 seconds | Native local evaluation refreshes the environment document every 10 seconds |
| Warm frontend refresh outage | Failed/expired work cannot enable new UI; the service publishes legacy plus a sanitized inline error and retries through its bounded schedule | Not applicable |
| Warm backend Flagsmith outage | Not applicable | The native SDK may continue using last-known-good rules; there is no application maximum-age controller or emergency-stop deadline |
| Request/evaluation error | Legacy UI and observable sanitized error | Bounded reason is logged and the legacy response branch is used; unexpected application exceptions are not fabricated as success |
| Browser tab restored after staleness | Expired positive state is cleared before a refresh; a prior positive result is not treated as indefinitely valid | Not applicable |

The local transport rejects redirects, wrong methods, wrong paths, remote
fallback evaluation, URL credentials, query/fragment text, and non-loopback
HTTP outside Development. This protects the backend key and ensures the
backend path remains native local evaluation. It does not make the POC an
authorization system.

## 11. Acceptance worksheet (A01-A15)

Fill `observed`, `elapsed seconds`, and `result` only while executing the
live check. `PASS` means the check was run and the measured result met its
expected condition. If the authorization gate is not satisfied, use
`NOT RUN — <exact missing prerequisite>` in `observed`, leave elapsed time as
`—`, and set `result` to `NOT RUN`. Do not store keys, tokens, documents, or
passwords in this worksheet.

Segment IDs are the actual IDs shown by the local Dashboard/API. Logical
names such as `beta-users` and `stable-rollout` are not IDs. Use `—` when a
check has no segment.

| scenario | project/environment | flag | segment ID | selected user IDs | expected | observed | elapsed seconds | result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A01 — frontend SDK path | `poc-frontend/local` | `frontend_demo_v2` | — | `demo-user-001` | Browser SDK traffic goes directly to `localhost:8000`; no frontend flag-query call to the backend | `NOT RUN — requires authorized client key, configured local Project/Environment, and running localhost:8000` | — | NOT RUN |
| A02 — backend SDK path | `poc-backend/local` | `backend_demo_v2` | — | `demo-user-001` | Warm local evaluation makes no remote evaluation HTTP requests | `NOT RUN — requires authorized ser. server key, configured local Project/Environment, and running backend` | — | NOT RUN |
| A03 — off/on combinations | `poc-frontend/local` + `poc-backend/local` | both flags | — | `demo-user-001`, `demo-user-006` | All four independent combinations in section 8 produce the corresponding UI and response | `NOT RUN — requires both explicitly configured keys and operator authorization for both Projects` | — | NOT RUN |
| A04 — fixture integrity | local frontend and backend | both flags | — | `ALL_USERS` | Exactly 20 IDs, five beta users, one fixture source, and unknown IDs are rejected | `NOT RUN — requires running local applications with the designated POC configuration` | — | NOT RUN |
| A05 — beta targeting | `poc-frontend/local` and `poc-backend/local` | `frontend_demo_v2`, `backend_demo_v2` | `beta-users` (record each actual ID) | `ALL_USERS` | `BETA_USERS` new; `NON_BETA_USERS` legacy in beta-only mode | `NOT RUN — requires native beta segment enabled only in each authorized local Project` | — | NOT RUN |
| A06 — stable repeats | both `local` Environments | both flags | active scenario segment (record actual ID) | `ALL_USERS`; reload `demo-user-006` | Ten repeated evaluations and selected-user reloads are stable under unchanged rules | `NOT RUN — requires configured keys, stable rules, and a healthy foreground browser` | — | NOT RUN |
| A07 — percentage expansion | `poc-frontend/local` and `poc-backend/local` | both flags | `stable-rollout` (record each actual ID) | `ALL_USERS` | `tenPercent` is a subset of `fiftyPercent`; `hundredPercent` equals `ALL_USERS`; no exact-count assertion | `NOT RUN — requires native split observations at 10/50/100 in both authorized local Environments` | — | NOT RUN |
| A08 — identity race | local frontend and backend | both flags | — | `demo-user-001` then `demo-user-002` | Delayed old SDK/API work cannot restore user A state after selecting user B | `NOT RUN — requires live local applications and an authorized configured client/server pair` | — | NOT RUN |
| A09 — dynamic change | both `local` Environments | both flags | active scenario segment (record actual ID) | `demo-user-001`, `demo-user-006` | Healthy foreground changes appear without rebuild/restart within 20 seconds | `NOT RUN — requires authorized local Dashboard changes and measured foreground propagation` | — | NOT RUN |
| A10 — startup states | `poc-backend/local` | `backend_demo_v2` | — | — | Backend starts with flag on and off; absent document/flag fails startup | `NOT RUN — requires the authorized server key and a separate disposable child-process test; shared deployment must remain up` | — | NOT RUN |
| A11 — default/error | both `local` Environments | both flags | — | `demo-user-001` | Missing flags and refresh/evaluation failures are observable; frontend is legacy, backend follows section 10 | `NOT RUN — requires authorized local failure simulation without mutating or stopping the shared Flagsmith instance` | — | NOT RUN |
| A12 — loopback/transport | `poc-backend/local` | `backend_demo_v2` | — | — | Only Development literal-loopback HTTP is allowed; redirects and remote fallback are blocked | `NOT RUN — requires the configured server key and authorized local transport/startup checks` | — | NOT RUN |
| A13 — exposure | browser and backend local paths | both flags | — | `ALL_USERS` | No server key, backend inventory, or Environment document appears in browser assets/responses/logs | `NOT RUN — requires authorized live browser/network/log inspection with both local apps running` | — | NOT RUN |
| A14 — rollback | both `local` Environments | both flags | none active after rollback | `ALL_USERS` | Clearing all enabling overrides and using default off returns both tiers to legacy within the healthy budget | `NOT RUN — requires authorized rollback changes and measured propagation; no overrides were changed by this runbook` | — | NOT RUN |
| A15 — ownership | local frontend and backend | both flags | — | — | No duplicated timers/Providers or leaked test pollers after mount, teardown, or test completion | `NOT RUN — requires live lifecycle observation; controlled test evidence is separate` | — | NOT RUN |

## 12. Controlled evidence versus live evidence

`poc/tests/demo.spec.ts` contains controlled Playwright tests for the page
contract, identity race, backend boundary, sanitization, and independent
frontend/backend combinations. Those tests intercept the browser's Flagsmith
and backend routes; they do not configure or query the local Flagsmith
Dashboard and therefore do not satisfy A01-A03 or the native targeting,
percentage, propagation, outage, and rollback portions of A05-A15.

The helper test uses manually specified literal sets to verify only the
stable-expansion relationship. It does not assert an exact 10% or 50% count.
Treat its result as controlled evidence, not live Flagsmith evidence.

Run the controlled suite from `poc\tests`:

```powershell
Set-Location 'C:\shs_repos\teamplay\poc\flagsmith\poc\tests'
& '..\frontend\node_modules\.bin\playwright.cmd' test 'demo.spec.ts' `
  --config='playwright.config.ts' --workers=1
```

When live prerequisites are later authorized, append measured observations to
the worksheet without overwriting controlled evidence. Keep actual keys and
raw Environment documents out of the report.
