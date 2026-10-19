# Direct-SDK feature flag POC

This is a **local-only** Angular/.NET demonstration. It uses the existing
workstation Flagsmith deployment at `http://localhost:8000`; it does not
provision, deploy, or mutate Azure, CCE, cloud resources, or a Flagsmith
database. The application has one page, one `GET /api/demo` endpoint, two
independent Boolean flags, and one checked-in fixture of 20 synthetic users.
It has no product, pricing, order, authentication, business database, BFF,
feature-query API, custom Provider, or shared evaluation service.

## Read first

- [Development specification](../docs/superpowers/specs/2026-10-16-feature-flag-poc-design.md)
- [Implementation plan](../docs/superpowers/plans/2026-10-16-feature-flag-poc-plan.md)
- [Existing local Flagsmith deployment guide](../deploy/local-development.md)
- [Native targeting and rollout runbook](docs/flagsmith-demo.md)

The runbook is the operator procedure for the two dedicated local Projects.
Controlled Playwright routes are not live Flagsmith acceptance. Do not mark
A01-A15 `PASS` unless the local Projects, flags, keys, authorization, and
measured behavior are actually available.

## Toolchain preflight

Use PowerShell 7.4 or newer and run these checks before restoring:

```powershell
pwsh.exe --version
dotnet --version
node --version
npm.cmd --version
```

The pinned baseline is .NET `net10.0`, Node 22.12+ (or Node 24), Angular
20.3.0, OpenFeature .NET 2.14.1, Flagsmith .NET Provider 0.3.1, Flagsmith
.NET SDK 9.0.0, OpenFeature Web SDK 1.10.0, browser Provider 0.3.0,
Flagsmith JavaScript 12.4.0, Vitest 3.2.4, jsdom 26.1.0, and Playwright
1.56.1 with Chromium. The committed npm and NuGet lockfiles are authoritative;
the helper uses locked restore.

## Local Flagsmith configuration

Use only the existing local deployment guide and the two dedicated Projects:

| Project | Environment | Boolean feature | Application key |
| --- | --- | --- | --- |
| `poc-frontend` | `local` | `frontend_demo_v2` | public client-side environment key |
| `poc-backend` | `local` | `backend_demo_v2` | private `ser.` server-side key |

The browser must receive only the frontend client key. Never put the backend
key, backend flag inventory, environment document, management credentials, or
raw rules in browser assets, responses, or logs.

Copy the checked-in keyless example to the ignored local configuration file.
Replace the placeholder locally; do not paste the value into source, reports,
or command history:

```powershell
Copy-Item -LiteralPath 'C:\shs_repos\teamplay\poc\flagsmith\poc\frontend\public\poc-config.example.json' `
  -Destination 'C:\shs_repos\teamplay\poc\flagsmith\poc\frontend\public\poc-config.json'
```

The backend server key belongs in the existing fixed UserSecretsId
`flagsmith-poc-backend`, or in the process environment. The documented value
below is a placeholder, not a usable credential:

```powershell
dotnet user-secrets set 'FeatureFlags:EnvironmentKey' '<ser.server-key-for-poc-backend-local>' `
  --project 'C:\shs_repos\teamplay\poc\flagsmith\poc\backend\Poc.Api.csproj'
```

For a single foreground process instead, enter the value only in that
terminal:

```powershell
$env:FeatureFlags__EnvironmentKey = Read-Host 'Enter the local poc-backend ser. key'
```

The appsettings files contain only non-sensitive local URL and refresh
settings. Missing configuration is an actionable startup error; the helper
never creates keys, starts Flagsmith, or enables a mock mode.

## Repeatable Windows helper

Run every helper command with the absolute worktree root below. The helper
resolves paths from `-RepositoryRoot`, uses `npm.cmd`, passes native arguments
as arrays, sets an explicit working directory, checks native exit codes, and
restores the caller directory. It does not kill unrelated processes or create
hidden daemons.

```powershell
pwsh.exe -NoLogo -NoProfile -NonInteractive -File 'C:\shs_repos\teamplay\poc\flagsmith\poc\scripts\Invoke-Poc.ps1' `
  -RepositoryRoot 'C:\shs_repos\teamplay\poc\flagsmith' -Action Restore
```

```powershell
pwsh.exe -NoLogo -NoProfile -NonInteractive -File 'C:\shs_repos\teamplay\poc\flagsmith\poc\scripts\Invoke-Poc.ps1' `
  -RepositoryRoot 'C:\shs_repos\teamplay\poc\flagsmith' -Action Build
```

```powershell
pwsh.exe -NoLogo -NoProfile -NonInteractive -File 'C:\shs_repos\teamplay\poc\flagsmith\poc\scripts\Invoke-Poc.ps1' `
  -RepositoryRoot 'C:\shs_repos\teamplay\poc\flagsmith' -Action Test
```

```powershell
pwsh.exe -NoLogo -NoProfile -NonInteractive -File 'C:\shs_repos\teamplay\poc\flagsmith\poc\scripts\Invoke-Poc.ps1' `
  -RepositoryRoot 'C:\shs_repos\teamplay\poc\flagsmith' -Action TestBrowser
```

`Restore` performs locked NuGet restore for the app and tests, `npm ci`, and
the pinned Playwright Chromium installation. `Build` uses no restore.
`Test` uses no NuGet restore and runs non-watch Angular tests. `TestBrowser`
runs Chromium only; the checked-in Playwright configuration owns one bounded
frontend dev server and reaps it.

## Two foreground terminals

Start each server in a separate PowerShell terminal. These commands remain in
the foreground; Ctrl+C stops only the process owned by that terminal.

**Terminal 1 — backend**

```powershell
pwsh.exe -NoLogo -NoProfile -NonInteractive -File 'C:\shs_repos\teamplay\poc\flagsmith\poc\scripts\Invoke-Poc.ps1' `
  -RepositoryRoot 'C:\shs_repos\teamplay\poc\flagsmith' -Action StartBackend
```

**Terminal 2 — frontend**

```powershell
pwsh.exe -NoLogo -NoProfile -NonInteractive -File 'C:\shs_repos\teamplay\poc\flagsmith\poc\scripts\Invoke-Poc.ps1' `
  -RepositoryRoot 'C:\shs_repos\teamplay\poc\flagsmith' -Action StartFrontend
```

The backend listens on `http://127.0.0.1:5000` and the Angular page on
`http://localhost:4200`. The frontend business proxy forwards only `/api`
requests to the backend; frontend flag evaluation goes directly to the local
Flagsmith API. The only application endpoint is
`GET /api/demo?userId=demo-user-001`.

## Boundaries to call out during a demo

- **Loopback HTTP exception:** HTTP is allowed only for literal loopback hosts
  in ASP.NET Core Development and for the local browser origin. This is not
  deployment guidance; use HTTPS and a restricted SDK entry point elsewhere.
- **Cold start:** The backend must load a valid environment document containing
  `backend_demo_v2` before accepting requests. Missing keys, documents, or
  flags fail startup; do not reuse an unrelated process on the port.
- **Frontend expiry:** A successful browser decision is usable for at most
  15 seconds. Expired or failed refresh work cannot authorize a new UI and is
  shown as legacy plus a sanitized inline error.
- **Backend last-known-good:** A warm Flagsmith outage may leave the native
  backend SDK using its last-known-good rules. This POC has no maximum-age
  controller or emergency-stop deadline.
- **Bucket independence:** Native percentage cohorts are stable only within an
  unchanged Project, Environment, segment, and evaluation tier. Do not promise
  the same bucket across the separate frontend and backend Projects or exact
  counts in a 20-user sample.
- **Controlled versus live:** Mocked browser/API routes prove application
  behavior only. They do not count as live provider, targeting, percentage,
  propagation, or rollback evidence.

## Local artifacts and safety

`poc/frontend/public/poc-config.json`, local secret/config artifacts, Angular
cache, Playwright reports/results, and POC-generated logs are ignored. Keep
the keyless example and checked-in appsettings files. Do not commit the local
key, user-secret value, test reports, or generated build output.

No cloud command, cloud plan, cloud resource, cloud key, commit, push, or live
Flagsmith mutation is part of this handoff.
