# Official sources and compatibility evidence

Reviewed on 2026-10-16. Keep this file with the Skill so copied installations do not depend on repository-level documentation. Online pages and `main` branches move; verify target package metadata, lockfiles, source revisions, and application builds.

| ID | Source | Purpose |
| --- | --- | --- |
| S01 | [Flagsmith OpenFeature](https://docs.flagsmith.com/integrating-with-flagsmith/openfeature) | Integration boundary and provider selection |
| S02 | [OpenFeature .NET](https://openfeature.dev/docs/reference/sdks/server/dotnet/) | Initialization, invocation context, Details, shutdown |
| S03 | [.NET Flagsmith provider](https://github.com/open-feature/dotnet-sdk-contrib/tree/main/src/OpenFeature.Contrib.Providers.Flagsmith) | Constructor, flat traits, Boolean/value and disabled behavior |
| S04 | [Flagsmith .NET v9.0.0 client](https://github.com/Flagsmith/flagsmith-dotnet-client/blob/v9.0.0/Flagsmith.FlagsmithClient/FlagsmithClient.cs) | Document-error handling, remote fallback, Information-level document logging, polling lifecycle |
| S05 | [OpenFeature Web](https://openfeature.dev/docs/reference/sdks/client/web/) | Synchronous evaluation, asynchronous context, events |
| S06 | [Browser provider release metadata](https://registry.npmjs.org/@openfeature%2fflagsmith-client-provider/0.3.0) | Exact peers, release integrity, and source `gitHead` |
| S07 | [Browser provider at the release revision](https://github.com/open-feature/js-sdk-contrib/blob/cf5d541f90423a84009ad3a957e010043ef5ff7b/libs/providers/flagsmith-client/src/lib/flagsmith-client-provider.ts) | `FlagsmithClientProvider`, nested traits, context changes, events |
| S08 | [Flagsmith JavaScript](https://docs.flagsmith.com/integrating-with-flagsmith/sdks/client-side-sdks/javascript) | Explicit API, cache, refresh, and SSR state |
| S09 | [Flagsmith security](https://docs.flagsmith.com/administration-and-security/governance-and-compliance/security) | Untrusted client traits and persistence controls |
| S10 | [Official Helm chart](https://github.com/Flagsmith/flagsmith-charts) | Self-hosted settings, external PostgreSQL, Secrets |
| S11 | [Edge Proxy](https://docs.flagsmith.com/deployment-self-hosting/edge-proxy) | Upstream/downstream keys and document refresh |
| S12 | [Web in-memory provider](https://github.com/open-feature/js-sdk/blob/main/packages/web/src/provider/in-memory-provider/in-memory-provider.ts) | Demo/test component, not an application TTL or identity policy |
| S13 | [Angular initialization](https://angular.dev/api/core/provideAppInitializer) | Completing Promise/Observable and legacy `APP_INITIALIZER` |
| S14 | [Angular SSR](https://angular.dev/guide/ssr) | Browser API boundary, request-owned rendering, hydration |
| S15 | [.NET logging](https://learn.microsoft.com/en-us/dotnet/core/extensions/logging/overview) | Category filtering and structured diagnostics |
| S16 | [HTTP message handlers](https://learn.microsoft.com/en-us/aspnet/web-api/overview/advanced/httpclient-message-handlers) | `DelegatingHandler` request boundaries |

## Reference versions

| Component | Pinned reference | Dependency evidence |
| --- | --- | --- |
| OpenFeature .NET | `2.14.1` | [NuGet](https://www.nuget.org/packages/OpenFeature/2.14.1) |
| .NET provider | `0.3.1` | [NuGet](https://www.nuget.org/packages/OpenFeature.Contrib.Providers.Flagsmith/0.3.1); OpenFeature `[2.0,3.0)`, Flagsmith `[8.0.1,10.0)` |
| Flagsmith .NET | `9.0.0` | [NuGet](https://www.nuget.org/packages/Flagsmith/9.0.0); source release tag in S04 |
| Web SDK | `1.10.0` | [npm](https://registry.npmjs.org/@openfeature%2fweb-sdk/1.10.0) |
| Browser provider | `0.3.0` | S06; peers Web SDK `^1.0.0`, Flagsmith JS `^12.1.2` |
| Flagsmith JS | `12.4.0` | [npm](https://registry.npmjs.org/@flagsmith%2fflagsmith/12.4.0) |
| Angular example | `20.3.0` | Runtime/common/compiler pinned together; target application keeps its supported version |

The example projects include lockfiles and executable local checks. Their results do not certify a target business application, identity integration, live Flagsmith environment, cloud deployment, or production throughput.

The .NET provider README can lag behind its project/package dependency constraints. Prefer published metadata and restore results; do not infer compatibility from README text alone.
