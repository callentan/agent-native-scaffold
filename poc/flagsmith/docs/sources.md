# Official sources, versions, and verification record

Access and verification date: **2026-10-16 (UTC+08:00)**. The sources below are official documentation, repositories maintained by the OpenFeature and Flagsmith organizations, and NuGet or npm release metadata. The `main` branches and online documentation can change. Lock the versions used in production and retain the enterprise artifacts and approval records.

## 1. Reference versions and conclusions

| Item | Verified result | Use and limitation |
| --- | --- | --- |
| OpenFeature .NET | NuGet has `2.14.1` | Uses `Api.Instance`, `FeatureClient`, invocation context, and Details |
| Flagsmith .NET Provider | NuGet has `OpenFeature.Contrib.Providers.Flagsmith 0.3.1` | The current csproj requires `OpenFeature [2.0,3.0)` and `Flagsmith [8.0.1,10.0)` |
| Flagsmith .NET SDK | NuGet has `9.0.0` | Within the dependency range above; overall compatibility with the target framework still requires a build |
| OpenFeature Web | npm `@openfeature/web-sdk 1.10.0` | Client-side reads are synchronous; initialization and context updates are asynchronous |
| Browser Flagsmith Provider | npm `@openfeature/flagsmith-client-provider 0.3.0` | Peers: Web SDK `^1.0.0`, `@flagsmith/flagsmith ^12.1.2` |
| Flagsmith JS SDK | npm `@flagsmith/flagsmith 12.4.0` | Satisfies the browser Provider peer range; do not confuse it with the Node SDK |
| Official Helm Chart | Published index has `0.84.0` with appVersion `2.285.0` | Published 2026-10-15; the values in this repository follow this structure and do not represent cloud validation |
| Angular reference example | The source and lock files pin Angular `20.3.0`, OpenFeature Web `1.10.0`, and RxJS `7.8.2` | Local service and test reference only; target application, identity, and live-cloud acceptance remain unverified |
| .NET local evaluation example | The `net10.0` harness pins OpenFeature `2.14.1`, Flagsmith Provider `0.3.1`, and Flagsmith `9.0.0` | Local-only startup and evaluation with a synthetic transport; target application, identity, and live-cloud acceptance remain unverified |

These versions are **a snapshot from this research**, not a promise that any project can install them together without validation. The .NET Provider README still contains older Requirements text that conflicts with the csproj. This document follows the actual dependency range in the csproj and requires a release-package metadata and restore check during implementation.

The checked-in Angular and .NET examples are executable local reference checks for the pinned package combinations. The Angular example contains a service and tests, and the .NET example is a local-only startup harness. They are not acceptance of a target business application and have not been validated against a real identity system or a live cloud environment. Do not treat this document as a production certification report. Browser and Provider examples use only verified interfaces. General OpenFeature capabilities are not assumed to exist in every Provider implementation.

## 2. Application and SDK sources

| ID | Official source | Evidence |
| --- | --- | --- |
| S01 | [Flagsmith: OpenFeature](https://docs.flagsmith.com/integrating-with-flagsmith/openfeature) | Official recommendation to use OpenFeature as the SDK interface |
| S02 | [OpenFeature .NET SDK](https://openfeature.dev/docs/reference/sdks/server/dotnet/) | Initialization, invocation context, Details, domain, shutdown, and transaction context |
| S03 | [.NET Flagsmith Provider README](https://github.com/open-feature/dotnet-sdk-contrib/blob/main/src/OpenFeature.Contrib.Providers.Flagsmith/README.md), [source](https://github.com/open-feature/dotnet-sdk-contrib/blob/main/src/OpenFeature.Contrib.Providers.Flagsmith/FlagsmithProvider.cs), [csproj](https://github.com/open-feature/dotnet-sdk-contrib/blob/main/src/OpenFeature.Contrib.Providers.Flagsmith/OpenFeature.Contrib.Providers.Flagsmith.csproj) | Package name, constructor, flattened traits, enabled and value fields, disabled behavior, dependency range, and lifecycle boundaries |
| S04 | [Flagsmith .NET SDK](https://github.com/Flagsmith/flagsmith-dotnet-client), [configuration](https://github.com/Flagsmith/flagsmith-dotnet-client/blob/main/Flagsmith.FlagsmithClient/FlagsmithConfiguration.cs), [client](https://github.com/Flagsmith/flagsmith-dotnet-client/blob/main/Flagsmith.FlagsmithClient/FlagsmithClient.cs) | Private URL, local evaluation, polling, timeouts, remote traits, fallback, and disposal boundaries |
| S05 | [OpenFeature Web SDK](https://openfeature.dev/docs/reference/sdks/client/web/) | Synchronous evaluation, asynchronous context, Provider events, and the difference between Web and Node |
| S06 | [Browser Flagsmith Provider README](https://github.com/open-feature/js-sdk-contrib/blob/main/libs/providers/flagsmith-client/README.md), [source](https://github.com/open-feature/js-sdk-contrib/blob/main/libs/providers/flagsmith-client/src/lib/flagsmith-client-provider.ts) | `FlagsmithClientProvider`, nested traits, context changes, disabled behavior differences, and events |
| S07 | [Node Flagsmith Provider](https://github.com/open-feature/js-sdk-contrib/blob/main/libs/providers/flagsmith/README.md) | `@openfeature/flagsmith-provider` is for Node, not the browser Provider |
| S08 | [Flagsmith JavaScript SDK documentation](https://docs.flagsmith.com/integrating-with-flagsmith/sdks/client-side-sdks/javascript) | `api`, caching, `defaultFlags`, `getFlags`, realtime updates, and SSR state |
| S09 | [OpenFeature Web in-memory Provider](https://github.com/open-feature/js-sdk/blob/main/packages/web/src/provider/in-memory-provider/in-memory-provider.ts) | `TypedInMemoryProvider`, variants configuration, demo and test positioning; it does not provide a production refresh strategy |
| S10 | [Flagsmith: security](https://docs.flagsmith.com/administration-and-security/governance-and-compliance/security) | Client-side trait persistence and its risks; it does not replace authorization |
| S11 | [Flagsmith server-side SDKs](https://docs.flagsmith.com/integrating-with-flagsmith/sdks/server-side), [SDK overview](https://docs.flagsmith.com/integrating-with-flagsmith/sdks/) | Local and remote evaluation, server and client key use, and updates |
| S12 | [Evaluation context concepts](https://openfeature.dev/docs/reference/concepts/evaluation-context/) | Standard context model; the way a particular Provider maps it still requires implementation review |

Package release metadata:

- [NuGet: OpenFeature](https://www.nuget.org/packages/OpenFeature/2.14.1), [Flagsmith Provider](https://www.nuget.org/packages/OpenFeature.Contrib.Providers.Flagsmith/0.3.1), [Flagsmith](https://www.nuget.org/packages/Flagsmith/9.0.0).
- [npm: browser Provider 0.3.0](https://registry.npmjs.org/@openfeature%2fflagsmith-client-provider/0.3.0), [Web SDK 1.10.0](https://registry.npmjs.org/@openfeature%2fweb-sdk/1.10.0), [Flagsmith 12.4.0](https://registry.npmjs.org/@flagsmith%2fflagsmith/12.4.0).
- .NET Provider source blob checks: `FlagsmithProvider.cs` is `c830dcd3006a99e2c7439984733d97f75aa0ec68`; the csproj is `96c7f11307f25ffe393f39ae3f5cd39ca58f9559`. These are file blob identifiers, not package signatures or repository-wide commit IDs.

## 3. Flagsmith private deployment

| ID | Official source | Evidence |
| --- | --- | --- |
| D01 | [Self-hosting overview](https://docs.flagsmith.com/deployment-self-hosting/) | Self-hosted product and deployment options |
| D02 | [Kubernetes and OpenShift](https://docs.flagsmith.com/deployment-self-hosting/hosting-guides/kubernetes-openshift) | Helm, external PostgreSQL, Django key, probes, resources, and replicas |
| D03 | [Helm repository](https://github.com/Flagsmith/flagsmith-charts), [values](https://github.com/Flagsmith/flagsmith-charts/blob/main/charts/flagsmith/values.yaml), [published index](https://flagsmith.github.io/flagsmith-charts/index.yaml) | Actual field names, versions, Secret references, workers, and optional components |
| D04 | [API environment template](https://github.com/Flagsmith/flagsmith-charts/blob/main/charts/flagsmith/templates/_api_environment.yaml) | `TASK_RUN_METHOD`, shared Secrets, default Host configuration, and duplicate environment-variable risk |
| D05 | [Asynchronous Task Processor](https://docs.flagsmith.com/deployment-self-hosting/scaling-and-performance/asynchronous-task-processor) | PostgreSQL task storage, separate task database, health, and task statistics |
| D06 | [Environment variables](https://docs.flagsmith.com/deployment-self-hosting/core-configuration/environment-variables) | API and Dashboard URLs, keys, registration, and observability configuration |
| D07 | [Caching strategies](https://docs.flagsmith.com/deployment-self-hosting/core-configuration/caching-strategies) | Caching is not unconditionally enabled by default, plus centralized caching and environment-document freshness |
| D08 | [Edge Proxy architecture](https://docs.flagsmith.com/performance/edge-proxy), [deployment configuration](https://docs.flagsmith.com/deployment-self-hosting/edge-proxy) | Upstream server key, downstream client key, polling, no trait persistence, and readiness staleness policy |
| D09 | [Enterprise Edition](https://docs.flagsmith.com/deployment-self-hosting/enterprise-edition) | Paid image, license, and edition boundaries for SAML, LDAP, workflows, and related features |
| D10 | [Flagsmith on Flagsmith](https://docs.flagsmith.com/deployment-self-hosting/core-configuration/running-flagsmith-on-flagsmith) | Private address for management-console flags and protection from hidden SaaS dependencies |
| D11 | [Initial setup](https://docs.flagsmith.com/deployment-self-hosting/core-configuration/initial-setup), [upgrade and rollback](https://docs.flagsmith.com/deployment-self-hosting/administration-and-maintenance/upgrades-and-rollbacks) | Administrator initialization, upgrades, and data recovery |
| D12 | [Flagsmith project and source](https://github.com/Flagsmith/flagsmith) | Product components, deployment, and licensing; the business .NET application does not change the control-plane stack |

## 4. Cloud platforms

| ID | Official source | Evidence |
| --- | --- | --- |
| C01 | [Private AKS clusters](https://learn.microsoft.com/en-us/azure/aks/private-clusters) | Private Kubernetes API networking, DNS, and private registry connectivity; regional capabilities still require confirmation |
| C02 | [Azure PostgreSQL reliability](https://learn.microsoft.com/en-us/azure/reliability/reliability-database-postgresql) | Database HA, fault domains, and recovery responsibilities |
| C03 | [AKS Key Vault CSI](https://learn.microsoft.com/en-us/azure/aks/csi-secrets-store-driver) | Secret mounting and synchronization, rotation limits, identity, and network requirements |
| C04 | [China Telecom eSurfing Cloud CCE](https://www.ctyun.cn/products/cce) | The official product name is Cloud Container Engine CCE; resource-pool capabilities require confirmation |
| C05 | [China Telecom eSurfing Cloud PostgreSQL](https://www.ctyun.cn/products/postgresql) | Native managed PostgreSQL product entry; do not infer that every region provides it |
| C06 | [China Telecom eSurfing Cloud CRS](https://www.ctyun.cn/products/crs) | Container registry product entry |
| C07 | [China Telecom eSurfing Cloud ELB](https://www.ctyun.cn/products/elb) | Elastic load-balancing product entry |
| C08 | [China Telecom eSurfing Cloud ZOS](https://www.ctyun.cn/products/zos) | Object storage product entry; tool protocol and resource-pool capabilities require separate verification |

## 5. Items this document does not claim to have verified

No cloud account resources were created, no production Flagsmith instance was connected, no real database migration was run, no production identity system was tested, no business throughput was measured, and no RPO or RTO drill was performed. This document does not use third-party performance examples as capacity commitments, and it does not invent eSurfing Cloud load-balancer annotations, secrets CSI adapters, or managed PostgreSQL SLAs.

Go-live gate: complete the target business application's build and contract tests, license confirmation, regional availability review, image scanning, Helm rendering and policy review, authentication and tenant negative tests, and network-outage and recovery drills before signing off production acceptance.
