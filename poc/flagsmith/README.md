# Flagsmith + OpenFeature technical design

This repository targets **existing .NET microservices and an Angular front end**. It uses OpenFeature to provide a consistent feature flag interface in application code, while Flagsmith manages configuration, segmentation, and gradual rollouts. The design supports private deployment on Azure and China Telecom eSurfing Cloud.

Documentation review date: **2026-10-16**. This repository delivers an integration Skill, implementation references, and deployment designs. It is not an application that has already been integrated with a business system or running in either cloud.

## Deliverables

| Content | Entry point |
| --- | --- |
| Reusable integration Skill | [SKILL.md](.github/skills/openfeature-flagsmith-dotnet/SKILL.md) |
| .NET microservice and BFF integration | [.NET implementation reference](.github/skills/openfeature-flagsmith-dotnet/references/dotnet.md) |
| Angular integration, including CSR, SPA, SSR, and hydration | [Angular front-end implementation reference](.github/skills/openfeature-flagsmith-dotnet/references/frontend.md) |
| Executable local reference examples | [Angular](.github/skills/openfeature-flagsmith-dotnet/examples/angular) and [.NET](.github/skills/openfeature-flagsmith-dotnet/examples/dotnet) |
| Minimal direct-SDK local-only POC and repeatable Windows handoff | [POC entry point](poc/README.md) |
| Private deployment on Azure and China Telecom eSurfing Cloud | [Deployment design](docs/private-deployment.md) |
| Deployment directory, configuration prerequisites, and release process | [Deployment README](deploy/README.md) |
| Local development with Docker Compose | [Local deployment guide](deploy/local-development.md) |
| Architecture, sequence, and dual-cloud deployment diagrams | [Scenarios and diagrams](docs/architecture.md) |
| Official sources, versions, and compatibility evidence | [Sources and verification record](docs/sources.md) |
| Non-sensitive starting point for the official Helm chart | [values.common.yaml](deploy/helm/values.common.yaml) |

## Core choices

Business code calls `OpenFeature SDK → Flagsmith Provider → Flagsmith SDK`. Server-side local evaluation is the default, and the server creates trusted tenant and user context. For enterprise applications, the front end should normally use a BFF to obtain **allowlisted, already evaluated results**. It should not receive rules or server keys. Public, non-sensitive UI flags may use the official browser Provider with a restricted evaluation endpoint.

Both clouds use the same Flagsmith containers and Helm chart. Differences belong at the Kubernetes, database, network, image registry, and secrets service layers. The default is **an independent control plane and database in each cloud, with no cross-cloud dual writes**. If disaster recovery is required, design a single-writer primary and standby within the same data domain.

## Verification

The executable examples are local reference checks, not acceptance of a target application. The Angular service and tests cover the BFF snapshot path. The .NET harness exercises local-only startup and evaluation with a synthetic transport. Neither example validates a target application's identity integration or a live cloud deployment.

Run the repository's example, structure, language, and link checks from Windows PowerShell 7:

```powershell
pwsh.exe -NoLogo -NoProfile -File 'C:\path\to\flagsmith\scripts\Test-Examples.ps1' `
  -RepositoryRoot 'C:\path\to\flagsmith' `
  -Restore
```

Use an absolute path for the checkout. Omit `-Restore` when the example dependencies are already available. The command runs checks only. It does not provision resources, connect to a production identity system, or perform live-cloud acceptance.

## Using the Skill

This repository includes `.github/skills/openfeature-flagsmith-dotnet/`. Tools that support project-level Agent Skills can discover this directory according to their own rules. Other tools can read `SKILL.md` directly or copy the **entire directory** into a supported skills directory while preserving `references/` and `examples/`.

Example task:

> Use the `openfeature-flagsmith-dotnet` Skill to add feature flags to an existing ASP.NET Core order service and Angular front end. First identify the authentication, multi-tenant, and configuration systems. Use private Flagsmith, adopt a BFF for the front end, keep the legacy checkout path, and report implementation and regression results.

Read the Skill's input checklist and boundaries before preparing the deployment environment. The Helm examples use placeholder domains, certificates, Secrets, image locations, and resource quotas. Replace them with values that have been validated for the target environment before going live.
