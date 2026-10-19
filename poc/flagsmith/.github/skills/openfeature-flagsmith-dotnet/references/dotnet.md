# .NET service and BFF reference

Use this reference for the backend route in the [Skill](../SKILL.md). Integrate with an existing ASP.NET Core application; do not replace its identity, tenancy, or error-handling infrastructure.

## Contents

- [Packages and configuration](#packages-and-configuration)
- [Local-only startup](#local-only-startup)
- [Trusted evaluation context](#trusted-evaluation-context)
- [Business decisions and errors](#business-decisions-and-errors)
- [BFF contract](#bff-contract)
- [Cross-service consistency](#cross-service-consistency)
- [Evaluation modes and lifecycle](#evaluation-modes-and-lifecycle)
- [Acceptance matrix](#acceptance-matrix)

## Packages and configuration

Keep the application's supported target framework. The executable reference targets .NET 10; older .NET and .NET Framework applications need their own compatibility check. Core OpenFeature support does not imply that the entire provider dependency graph supports a target.

| Package | Reference version |
| --- | --- |
| `OpenFeature` | `2.14.1` |
| `OpenFeature.Contrib.Providers.Flagsmith` | `0.3.1` |
| `Flagsmith` | `9.0.0` |

Use `Directory.Packages.props` when the project already uses central package management. Preserve its restore and lockfile conventions. [Source evidence](official-sources.md) establishes package constraints, not target-application certification.

Non-sensitive configuration:

```json
{
  "FeatureFlags": {
    "ApiUrl": "https://flags-api.internal.example.com/api/v1/",
    "RefreshSeconds": 30,
    "SmokeFlag": "checkout_v2",
    "SmokeExpected": false
  },
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "FlagsmithSdk": "Warning"
    }
  }
}
```

Inject `FeatureFlags__EnvironmentKey` from the existing secret service. Local evaluation requires a server-side `ser.` key. Keep keys out of files, build arguments, and logs. Require an explicit HTTPS API URL ending in `/api/v1/`; reject embedded credentials, query strings, and fragments.

`SmokeFlag` must name a real, approved flag in the target environment, with its expected enabled state. The example name is illustrative, not permission to create or alter a production flag.

## Local-only startup

**The failure to avoid:** Flagsmith 9 catches environment-document HTTP errors and may use `/flags/` or `/identities/` when no document is loaded. A successful `GetEnvironmentFlags()` or smoke evaluation alone therefore does not prove local readiness.

The [compiled helper](../examples/dotnet/LocalEvaluation.cs) enforces the actual requirement:

1. A `DelegatingHandler` permits only GET requests to the exact private environment-document URI.
2. The underlying transport has redirects disabled, preventing a redirect from bypassing that boundary.
3. The SDK loads its document; any attempted remote fallback is blocked before transport and logged.
4. An approved smoke flag is evaluated from that document. Missing flags, unexpected values, or failed startup prevent the host from accepting traffic.
5. Only then is the OpenFeature provider registered.

Copy the helper into the application's infrastructure layer and retain its namespace or adapt the import. Register the OpenFeature client before `builder.Build()`:

```csharp
using FeatureFlagReference;
using OpenFeature;

builder.Logging.AddFilter("FlagsmithSdk", LogLevel.Warning);
builder.Services.AddSingleton<FeatureClient>(_ => Api.Instance.GetClient());
```

After `builder.Build()`, before `RunAsync()`:

```csharp
var section = app.Configuration.GetSection("FeatureFlags");
var apiUri = new Uri(section["ApiUrl"]
    ?? throw new InvalidOperationException("FeatureFlags:ApiUrl is required."),
    UriKind.Absolute);
var key = section["EnvironmentKey"]
    ?? throw new InvalidOperationException("FeatureFlags:EnvironmentKey is required.");
var smokeFlag = section["SmokeFlag"]
    ?? throw new InvalidOperationException("An approved smoke flag is required.");
var expected = section.GetValue<bool?>("SmokeExpected")
    ?? throw new InvalidOperationException("The expected smoke state is required.");
var loggerFactory = app.Services.GetRequiredService<ILoggerFactory>();

using var http = new HttpClient(new EnvironmentDocumentOnlyHandler(
    apiUri,
    new SocketsHttpHandler { AllowAutoRedirect = false },
    loggerFactory.CreateLogger("FeatureFlags")))
{ Timeout = TimeSpan.FromSeconds(2) };

var flagsmith = LocalEvaluation.CreateClient(
    apiUri, key, http, loggerFactory.CreateLogger("FlagsmithSdk"),
    section.GetValue<int>("RefreshSeconds"));
try
{
    await LocalEvaluation.VerifyAndRegisterAsync(flagsmith, smokeFlag, expected);
    await app.RunAsync();
}
finally
{
    await Api.Instance.ShutdownAsync();
}
```

The exact SDK logger category matters: a filter for `Flagsmith` does not match a logger named `FlagsmithSdk`. The pinned SDK writes the complete environment document at Information. Keep that category at Warning or above, including provider-specific overrides. Verify that warnings/errors still reach the existing sink; record refresh status and age separately without logging bodies.

The helper intentionally implements **local-only** evaluation. Remote-to-Proxy mode needs a different, explicitly selected configuration; do not remove the guard to repair a local-mode outage.

The [executable regression harness](../examples/dotnet/Program.cs) supplies a synthetic HTTP transport, not a live server. It checks document failure while `/flags/` would succeed, local identity evaluation without HTTP, unknown-flag error details, log filtering, and blocked origins/methods/paths.

## Trusted evaluation context

Authentication, authorization, and tenant resolution run before constructing context:

```csharp
using OpenFeature.Model;

static EvaluationContext CreateFlagContext(
    string canonicalIdentity, string tenantId, string plan, string region) =>
    EvaluationContext.Builder()
        .SetTargetingKey(canonicalIdentity)
        .Set("tenant_id", tenantId)
        .Set("plan", plan)
        .Set("region", region)
        .Build();
```

Read these values from verified identity/tenant relationships and server-owned subscription data, not request bodies, query parameters, or unchecked headers.

Use stable, non-PII identifiers. One option is a versioned HMAC over unambiguously encoded tenant and subject identifiers. Keep the HMAC key server-side; if a public browser route needs the same bucket, issue the derived identifier through the session API. Key rotation or identity changes can rebucket users and need a migration plan.

Tenant rollouts use a stable tenant targeting key; user rollouts use a tenant-scoped user key. Background jobs explicitly select their tenant/task bucketing unit.

The .NET provider uses identity evaluation when `TargetingKey` is present and maps flat context entries to traits. Without a targeting key, it evaluates environment defaults; do not expect a `plan` segment to apply. Do not copy the browser provider's nested `traits` structure into .NET.

Pass invocation context. Never call `Api.Instance.SetContext`, `client.SetContext`, or replace a provider per request. If transaction-context propagation is already used, verify concurrent isolation and cleanup. `AsyncLocal` does not cross HTTP, message, or process boundaries automatically.

## Business decisions and errors

Expose a domain decision such as `CheckoutFeatureDecisions`, not Flagsmith SDK types in controllers:

```csharp
static async Task<bool> IsCheckoutV2Enabled(
    FeatureClient client, EvaluationContext context, ILogger logger)
{
    var details = await client.GetBooleanDetailsAsync("checkout_v2", false, context);
    if (details.ErrorType != OpenFeature.Constant.ErrorType.None)
        logger.LogWarning("Flag evaluation failed: {FlagKey}, {ErrorType}",
            "checkout_v2", details.ErrorType);
    return details.Value;
}
```

Default returns do not necessarily throw. Observe Details, counters, and traces, distinguishing a normal off state from a missing flag, type mismatch, or provider failure. Do not log context, user/tenant identifiers as metric labels, or raw rules.

Boolean flags use `enabled` with `UsingBooleanConfigValue=false`, not the string `"true"`. Verify String, Integer, Double, Object, and disabled semantics for the pinned provider; browser behavior can differ.

Memoize repeated decisions only within the request and complete evaluation semantics. A process-wide dictionary keyed only by flag mixes users. Multiple flag reads are not automatically a strict snapshot.

## BFF contract

`GET /api/ui-features` uses the existing authentication and trusted tenant resolution. It evaluates a fixed, reviewed allowlist:

```json
{
  "schemaVersion": 1,
  "contextVersion": "opaque-session-tenant-permission-version",
  "evaluatedAt": "2026-10-16T00:00:00Z",
  "expiresAt": "2026-10-16T00:00:30Z",
  "degraded": false,
  "flags": { "checkout_v2": false }
}
```

This is an application protocol, not Flagsmith SDK state or OFREP.

| Field or behavior | Contract |
| --- | --- |
| Allowlist | Code or an approved contract defines exposed keys; no arbitrary browser key lookup |
| Identity binding | The session API and BFF share an opaque `contextVersion` that changes with relevant identity, tenant, and permission changes |
| Caching | `Cache-Control: private, no-store`; no shared CDN caching; any process cache includes complete identity and permission versions |
| Invalid identity | Return 401/403 through the existing session/permission path |
| Unavailable dependency | Return 503 when the request cannot be served safely |
| Degraded ordinary UI | Return approved conservative values with `degraded=true` and observable errors; Angular suppresses new UI even if a positive value is present |
| Freshness | Server controls TTL; 30 seconds is a starting budget, not a guarantee |
| Business execution | APIs authorize and evaluate independently; a browser Boolean is not a business decision |

Do not return all environment flags. If frontend and backend must share one decision, include it in the same authoritative business response or persist the operation mode. Two separate HTTP requests cannot guarantee consistency during a configuration change.

## Cross-service consistency

A service evaluates flags that affect only its implementation. For order/payment/fulfillment protocol changes, the authoritative service selects `checkoutMode` at transaction start and persists it with the order/outbox. Consumers validate that business mode and process idempotently; do not send a generic `featureFlags` dictionary.

Validate forwarded identity/tenant data at trust boundaries. `traceparent` is for observability, not trusted targeting. OpenFeature domains are not Flagsmith environments.

## Evaluation modes and lifecycle

| Mode | Key and endpoint | Tradeoff |
| --- | --- | --- |
| Local, recommended hot path | Server key; private Core | Rules in process; periodic refresh; no remote evaluation with the guard |
| Remote to Edge Proxy | Client key; Proxy `/api/v1/` | An internal hop per evaluation; send complete traits; Proxy does not persist identity traits |
| Remote to Core | Verify key type for target API/SDK | Simple POC, but control-plane dependency and possible trait persistence |
| Approved offline snapshot | Trusted server snapshot and SDK OfflineHandler | Requires integrity, encryption, environment binding, expiry, revocation, and update procedures |

The sample's two-second timeout and zero retries are starting budgets. Caller cancellation does not replace HTTP timeout; the contrib provider does not guarantee forwarding every cancellation token.

Keep the native SDK process-owned. The pinned provider's shutdown does not guarantee stopping native SDK polling, and the client does not offer a deterministic `IDisposable` contract. Do not recreate it per request or repeatedly recreate local-mode hosts in one process. The executable harness exits its process after its checks. Applications needing repeated lifecycle teardown must verify a supported release mechanism or choose remote evaluation explicitly.

Define an approved last-known-good window. A successful Boolean does not prove rules are fresh. Track document fetch success and accepted document validity separately; a successful HTTP status alone is not proof that parsing/evaluation succeeded. Expose stale age and apply the business policy when the window expires.

Cold startup without a verified document fails. Cold-start offline operation requires the separately approved snapshot design. Avoid rolling every healthy instance during a control-plane outage. Emergency transaction controls need a separate local enforcement mechanism.

## Acceptance matrix

| Scenario | Expected result |
| --- | --- |
| Off/on | Legacy/new behavior; approved conservative default |
| Document endpoint fails, `/flags/` succeeds | Startup fails; zero remote evaluation requests reach transport |
| Successful local identity evaluation | Correct result; no HTTP in the evaluation hot path |
| SDK logging at application Information | No document bodies; warning/error diagnostics preserved |
| Unknown key or wrong type | Default plus identifiable error details |
| Concurrent users/tenants | No shared context or cache contamination |
| Percentage rollout | Stable repeats; rebucketing changes documented |
| Traits/disabled configuration | Flat .NET traits work; browser differences explicitly tested |
| Warm outage or stale rules | Last-known-good within approved window; observable policy beyond it |
| Cold outage or offline snapshot | Fail startup, or validate the approved signed/environment-bound snapshot |
| Key rotation/revocation | Observable failure and recovery without logging keys |
| BFF boundary | No forged tenant/plan, arbitrary key lookup, or shared response cache |
| Frontend identity change | Late responses cannot restore old decisions |
| Transaction/rollback | One persisted business mode; old path and schema remain compatible |

Use an OpenFeature test provider or existing test seams, isolating global API state between tests. Use a designated staging Flagsmith environment for live contract checks, never production flag mutations.
