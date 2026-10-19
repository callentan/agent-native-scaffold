---
name: openfeature-flagsmith-dotnet
description: Use when adding or changing feature flags, remote configuration, or rollout controls in existing .NET services or Angular applications using OpenFeature and private Flagsmith.
---

# OpenFeature and Flagsmith integration

Use OpenFeature for decisions and private Flagsmith for evaluation. Preserve authentication, authorization, tenancy, configuration, and observability. Frontend scope: Angular only.

## Route the task

| Requested work | Read | Verify |
| --- | --- | --- |
| .NET service | [.NET reference](references/dotnet.md) | Local-only startup, invocation context, error details |
| Angular with existing BFF | [Angular reference](references/frontend.md), [BFF contract](references/dotnet.md#bff-contract) | Identity isolation, degraded defaults, expiry/tab restoration, reactive UI |
| Public Angular page | [Browser route](references/frontend.md#public-browser-provider) | Restricted endpoint, public flags, controlled refresh |
| Existing Angular SSR | [SSR reference](references/frontend.md#ssr-and-hydration) | Request-owned snapshots, browser boundary, matching hydration |
| Full-stack integration | Both implementation references | Independent API authorization and decisions |
| Explicit deployment request | [Official sources](references/official-sources.md) | Platform, chart, database, network, secrets, licensing |

Collect only route-relevant inputs. Frontend-only work excludes backend and infrastructure changes; report incompatible BFF contracts. Explanation/review tasks do not authorize implementation.

## Defaults and inputs

Backend: contrib Flagsmith provider, local evaluation, process-owned SDK, trusted invocation context. Enterprise UI: allowlisted BFF snapshots. Rollout: explicitly tenant- or user-scoped stable bucketing. Failure: observable, conservative legacy behavior.

Inspect versions, lockfiles, registration, identity/tenancy, API clients, and tests. For Angular, identify version, standalone/NgModule structure, state management, and CSR/SSR mode. Confirm private URLs, key types, defaults, freshness budgets, ownership, and rollback. Ask only about blocking decisions.

## Workflow

1. **Contract:** key, type, default, owner, purpose, audience, browser exposure, expiry date, failure policy. These are application-owned fields.
2. **Compatibility:** check [version evidence](references/official-sources.md), published metadata, and target lockfiles; keep explicit private URLs and environment boundaries.
3. **Implementation:** adapt the [working .NET](examples/dotnet/LocalEvaluation.cs) or [Angular](examples/angular/feature-session.service.ts) example, preserving typed validation and lifecycle guards.
4. **Verification:** exercise the selected acceptance matrix, outage/recovery, and rollback. For skill changes, use [evaluation scenarios](evals/README.md).
5. **Release:** deploy only when authorized. Retire flags after active versions stop referencing them; use expand/migrate/contract for data changes.

## Common mistakes

- OpenFeature is an SDK standard, not a flag server. Do not assume native OFREP or introduce flagd.
- Flagsmith 9 can fall back remotely without a local document. Require the document-only HTTP guard and approved smoke flag, not just `GetEnvironmentFlags()`.
- SDK Information logs can contain complete documents. Filter the exact `FlagsmithSdk` category to Warning; preserve safe diagnostics.
- Keep .NET user context invocation-scoped. .NET traits are flat; browser-provider traits are nested.
- Degraded, expired, or identity-mismatched Angular snapshots cannot enable new UI.
- Flags do not replace authorization, entitlements, tenant isolation, or transaction protocols.
- Keep server keys, tokens, rules, and sensitive traits out of browsers/telemetry. Do not promise instantaneous kill switches or unlicensed enterprise features.

## Implementation handoff

Report **scope**, **files**, **locked versions**, **flag contract**, **failure/freshness policy**, **evidence**, **rollback**, and **not run**. Distinguish local reference checks from target-application, identity, staging, and cloud acceptance. Write skills and documentation in idiomatic English.
