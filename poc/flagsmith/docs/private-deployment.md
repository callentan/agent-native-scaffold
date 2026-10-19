# Flagsmith private deployment design: Azure and China Telecom eSurfing Cloud

Review date: 2026-10-16. This document is an implementation design and go-live checklist, **not a completed cloud deployment**. In this document, China Telecom Cloud means China Telecom eSurfing Cloud. If the target is a dedicated cloud or government resource pool, remap the design to the services that resource pool actually provides. See the [official sources](sources.md).

## 1. Overall design and non-goals

Deploy the official containers and official Helm chart to Kubernetes. Business systems use the OpenFeature SDK; **do not deploy a separate OpenFeature server**. Existing .NET microservices do not need to change their hosting model. Whether they run on AKS, CCE, VMs, or another container platform, they only need network connectivity to the private evaluation API.

Recommended first-phase components:

| Component | Production role | Required |
| --- | --- | --- |
| Flagsmith API | Management, environment configuration, rule documents, and SDK remote evaluation | Yes, at least 3 replicas |
| Flagsmith Dashboard | Operations and development management UI, not the business front end | Yes, at least 2 replicas |
| PostgreSQL | Authoritative configuration and identity data, plus the task queue | Yes, a separate managed HA instance |
| Task Processor | Official asynchronous task processing | Recommended in production, at least 2 replicas |
| Edge Proxy | Fetch rules and perform remote evaluation closer to clients | Optional, use for high remote-evaluation volume, at least 2 replicas |
| Redis / SSE | Selected caching strategy or real-time update path | Not required for the baseline; enable according to the official version capabilities |
| InfluxDB, Kafka, and experimentation data pipeline | Analytics and experimentation extensions | Not required for the baseline; do not introduce them for ordinary feature releases |
| Image registry, secrets service, monitoring, and backups | Delivery and operational support | Yes, reuse enterprise platforms |

**The Task Processor uses PostgreSQL for task storage by default. Celery and Redis are not required.** When the chart's `taskProcessor.enabled` is enabled, the template sets `TASK_RUN_METHOD=TASK_PROCESSOR`. If a separate task database is required, configure the officially supported task-database variables for both the API and the worker. Do not change only one side.

The first phase does not build cross-cloud database active-active replication, fetch rules through a cross-border public network, promise a zero-latency kill switch, or introduce a complete experimentation analytics platform. All capacity, SLO, and recovery targets are **design targets pending load tests and drills**.

## 2. Deployment and data-domain choices

By default, Azure and eSurfing Cloud each get a complete Flagsmith instance that serves its own data domain. Projects, secrets, databases, identities, and audit records remain independent. Business applications select the private API for their own domain through configuration. One business process must not treat the two data sets as one environment.

Supporting two clouds does not mean active-active operation across the clouds. For centralized management, use one controlled pipeline to publish declarative flag contracts and environment differences. Apply them through each Management API with credentials isolated by domain, and retain approvals and change records. Importing or rebuilding an environment can change IDs and percentage buckets. Verify the result rather than assuming that percentage splits will be identical.

For regional disaster recovery, first build a single-writer primary and standby **within the same data-residency and licensing boundary**. Define PostgreSQL replication or backup, primary fencing, split-brain prevention, and recovery order. Do not combine two Flagsmith installations with bidirectional database replication, and do not use DNS round-robin to send management writes to two independent primary databases.

## 3. Cloud resource mapping

| Capability | Azure | China Telecom eSurfing Cloud |
| --- | --- | --- |
| Compute | Private AKS; an existing managed Kubernetes platform is also acceptable | Cloud Container Engine CCE; Kubernetes provided by a dedicated resource pool |
| Images and Chart | Private ACR registry; internal OCI or Chart registry | Container Registry Service CRS; internal Harbor or Chart registry |
| Database | Azure Database for PostgreSQL, using an HA mode supported in the selected region | Managed PostgreSQL service; confirm the resource pool, version, and primary/standby capabilities |
| Network | VNet, private subnets, NSGs, private DNS, VPN or ExpressRoute | VPC, subnets, security groups, private DNS, VPN or private circuit |
| Traffic entry | Existing Gateway or Ingress plus internal LB; enterprise WAF when required | Existing Gateway or Ingress plus ELB; enterprise WAF when required |
| Secrets | Key Vault plus AKS Workload Identity and CSI, or an existing secrets synchronizer | Secrets service supported by the resource pool plus a supported synchronizer; otherwise enterprise Vault |
| Backups | Native PostgreSQL backup and restore; approved exports may be stored in Blob when necessary | Native PostgreSQL backup and restore; enterprise object storage or ZOS for approved backups |
| Observability | Enterprise OTel and Prometheus; Azure Monitor is optional | Enterprise OTel and Prometheus plus eSurfing Cloud monitoring and logging |

The existence of a product does not mean that the target region, resource pool, version, and SKU are available. The names of eSurfing Cloud CCE, CRS, PostgreSQL, ELB, and ZOS were checked against the official product pages, but **no SLA or purchasable region for a particular customer account was verified**.

For Azure regions operated by 21Vianet in China, use the corresponding cloud environment, domains, image sources, and regional availability list. Do not apply the global Azure identity endpoints or service coverage without checking them. This document does not assume that Defender, a particular Gateway implementation, or every Workload Identity capability is available in the China regions.

## 4. Network, security, and access matrix

Use separate domains and access surfaces:

| Entry point | Allowed users | Permitted content |
| --- | --- | --- |
| `flags-admin.internal.example.com` | Administrators on the corporate VPN or private circuit, subject to enterprise access control | Dashboard and controlled management API |
| `flags-api.internal.example.com` | Approved business services, workers, and Proxy | Private SDK evaluation and environment documents; restrict management endpoints separately |
| `flags-public.example.com`, only for the direct-connect route | Business browsers with rate limiting and abuse prevention | Only the paths and methods required for SDK evaluation; do not expose management, environment documents, health, or metrics |

For the BFF route, **do not create a public Flagsmith endpoint**. The browser talks only to the business BFF. A Dashboard user's browser must also be able to resolve and reach the management API address configured for the Dashboard. Do not put a Pod-only Service DNS name in a URL that a browser must use.

Key traffic flows:

| Source to destination | Protocol and port | Constraint |
| --- | --- | --- |
| Browser to business Gateway or BFF | HTTPS 443 | Reuse authentication, session protection, tenant authorization, and rate limiting |
| Administrator to private management endpoint | HTTPS 443 | VPN or private circuit, MFA, and controlled identity; block anonymous access |
| Business service to Flagsmith API | HTTPS 443; platform-dependent 8000 inside the cluster | Local mode polls rules and does not send a per-user evaluation |
| Business service or browser to Edge Proxy | HTTPS 443; container port 8000 | Client key; expose only the required SDK endpoints |
| API or worker to PostgreSQL | PostgreSQL 5432 with TLS | Dedicated account, connection limits, and no public endpoint |
| Proxy to Core API | HTTPS over a protected private network | Server key, used only to fetch environment documents |
| Pod to image registry, secrets, DNS, OTel, or SMTP | As approved by the enterprise platform | Egress allowlist; SMTP is only for invitations and notifications |

Kubernetes should enable a default-deny NetworkPolicy and explicitly allow DNS, probes, and the proxy exceptions. Internal HTTP is not encrypted merely because it stays on a private network. If a Service uses HTTP, protect sensitive keys and documents with mesh mTLS or an equivalent mechanism. Restrict public SDK API CORS to the specific business origins; do not use a broad wildcard as a security boundary.

Management access should use the RBAC and SSO features supported by the purchased edition, together with enterprise entry-point protection. Verify Flagsmith licensing for SAML, LDAP, approval workflows, and similar features. Gateway SSO does not provide Flagsmith's internal user permissions, and setting a UI flag does not enable an enterprise edition.

## 5. Azure implementation steps

1. Decide between global Azure and Azure operated by 21Vianet in China, then confirm the region, data residency, subscription, and quotas for AKS, PostgreSQL HA, Key Vault, ACR, and networking.
2. Reuse or create a private AKS cluster. Separate system and business node pools. Production should have at least 3 schedulable worker nodes, spread across availability zones when available. A private AKS cluster protects the Kubernetes API only; it does not automatically make the application endpoint private.
3. Put PostgreSQL on a private network. Enable HA, TLS, backup retention, and recovery capabilities supported by the selected SKU. Do not treat an ordinary read replica as automatic failover.
4. Import approved Flagsmith API, frontend, and Proxy images and the Chart into ACR or an internal registry. Lock versions and digests. Give the AKS pull identity only the permissions it needs.
5. Store the database URL, fixed Django key, SDK keys, management token, and mail credentials in Key Vault. Map them to Kubernetes Secrets through verified Workload Identity and CSI integration or an approved secrets synchronizer.
6. Expose the management domain and private SDK API through the enterprise Gateway or Ingress. Configure certificates, DNS, private circuits, and routes together. Select an existing supported controller rather than binding the design to a deprecated implementation.
7. Deploy with the shared values and environment overlay files. Initialize administrators and projects, verify SDK modes and rollback, then connect the .NET services and front end.

CSI Secret synchronization usually depends on a Pod mounting the `SecretProviderClass`. Creating the class alone does not make a chart's `secretKeyRef` work automatically. Ensure that the target Secret exists first. After rotating a secret read through environment variables, perform a controlled Pod rollout or rebuild the SDK. Changing the value in Vault does not refresh process environment variables automatically.

## 6. China Telecom eSurfing Cloud implementation steps

1. Identify the public cloud, dedicated cloud, or specified government resource pool. Have that resource pool confirm CCE, native PostgreSQL, CRS, ELB, object storage, secrets services, and cross-availability-zone capabilities.
2. Prefer a supported CCE Kubernetes version. Verify the CNI, NetworkPolicy, CSI, LoadBalancer Controller, private API, and node-failure migration. Start with 3 nodes and distribute them across the available fault domains.
3. Prefer a native PostgreSQL primary/standby service. **Do not treat MySQL or another domestic database that is PostgreSQL-compatible as an interchangeable replacement for open-source Flagsmith.** If no suitable managed service exists, have DBAs operate native PostgreSQL HA on dedicated VMs or a verified operator. Do not reduce the design to one Pod with a PVC and still label it highly available.
4. Import container images, Helm packages, and dependencies into CRS or Harbor before deployment. Use internal NuGet and npm artifact proxies. Production must not depend on temporary access to GitHub, Docker Hub, or an overseas CDN.
5. Use the secrets injection method supported by the resource pool. If no cloud secrets adapter has been verified, use enterprise Vault or controlled Secret delivery. Do not assume that Azure CSI is natively compatible with eSurfing Cloud.
6. Connect ELB to the existing Gateway. Let the product determine internal or public load balancers, TLS termination, certificates, health checks, source addresses, and billing capabilities. Do not copy Service annotations from another cloud.
7. Back up through the data domain's native restore mechanism or the enterprise backup system. Store backups in ZOS or approved object storage when required. Verify the endpoint, tool compatibility, retention locks, and restore procedure. Do not assume that one object store supports every S3 option.

If a restricted environment has no Kubernetes, deploy the same official containers on at least two application VMs behind an internal LB, while keeping the database on an independent HA service. Run the Task Processor separately. You must provide process management, configuration release, health checks, rolling upgrades, and fault-domain distribution. Docker Compose is suitable for a POC, not as a substitute for production HA.

## 7. Helm release baseline

Reference lock: **Chart 0.84.0 and appVersion 2.285.0**, verified against the published index. This does not require a new production release to use a version published yesterday. Run enterprise security scanning and staging validation first. An older validated version is also acceptable, but check the values against that Chart version.

The shared starting point is [values.common.yaml](../deploy/helm/values.common.yaml). It disables the built-in development database, enables an external database Secret, pins the Django key reference, enables the worker, and disables SSE and experimentation extensions. **It is not a complete production deployment file**: it does not configure the cloud entry point, private image registry, network policies, fault domains, database resources, or cloud permissions.

Have the secrets-management process create these Secrets in advance. Do not put their values in Git or in Helm `--set` arguments:

| Secret | Key | Content |
| --- | --- | --- |
| `flagsmith-runtime` | `DATABASE_URL` | PostgreSQL URL with a URL-encoded password and TLS enabled; in production, prefer verified server certificates |
| `flagsmith-runtime` | `DJANGO_SECRET_KEY` | Long random value shared by every API and worker and retained across reinstalls |
| Business service's own Secret | `FeatureFlags__EnvironmentKey` | The business environment key; do not confuse it with a management token |
| `flagsmith-edge`, if enabled | Environment key pairs or configuration | Proxy server key mapped to the corresponding client key |

`sslmode=require` provides encryption semantics only; it is not full server identity verification. Select `verify-full` based on the managed database CA and the image's mounted path. Database least privilege must still account for migrations. Allow a dedicated migration account to perform DDL, grant the runtime account only the permissions it needs, and test the result.

The following examples target PowerShell on Windows and use the locked Chart version:

```powershell
helm repo add flagsmith 'https://flagsmith.github.io/flagsmith-charts/'
helm repo update
helm show values flagsmith/flagsmith --version '0.84.0'
helm template flagsmith flagsmith/flagsmith --version '0.84.0' `
  --namespace flagsmith -f 'deploy\helm\values.common.yaml' `
  -f 'C:\secure\path\values.environment.yaml' > 'C:\secure\path\rendered.yaml'
```

The platform team supplies `values.environment.yaml` with non-sensitive overrides for the internal image registry and approved tags, certificate names, private domains, scheduling rules, and external entry-point resources. The Secrets themselves come through the secrets-management process. Treat rendered output as sensitive infrastructure information.

**Known points to check when reviewing the rendered output:**

- The Chart uses `api.replicacount`, not `replicaCount`; the development database switch is `devPostgresql.enabled`. A different Chart version may rename them.
- Version 0.84.0's API environment template generates `DJANGO_ALLOWED_HOSTS=*`. Adding the same name in `api.extraEnv` creates duplicate environment entries. In production, replace it with one explicit allowed Host in a reviewed internal Chart patch or structured post-renderer, then verify the Helm upgrade. Do not rely on the order in which duplicate variables happen to be applied.
- Verify trusted proxy headers, CSRF trusted origins, CORS, and cookie settings for the selected application version. Adding an arbitrary Django variable does not mean the image reads it. The entry point must remove untrusted `X-Forwarded-*` headers and rebuild them only from trusted proxies.
- This example uses the default API probe path. Confirm that the restricted Host policy does not block kubelet probes. Verify worker probes against the actual image. API Pod health does not prove that tasks are being processed.
- Do not allow `api.enableMigrateDbInitContainer` and an independent migration Job to run concurrent migrations during scaling. The process below runs migration once in the pipeline and then leaves init migration disabled.
- When `frontend.apiProxy.enabled=false`, `FLAGSMITH_API_URL` must be reachable from the administrator's browser.
- Add PDBs and topology spread or anti-affinity for the Task Processor separately. The Chart does not expose identical scheduling and PDB switches for every component. API and frontend PDBs cannot replace real fault-domain scheduling.

Production release order:

1. Create the namespace, certificates, network policies, image-pull permissions, Secrets, and database. Back up the database, then freeze management changes for this release.
2. Run **one** `migrate` Job with the same image and verified environment configuration. Wait for success. If the new version fails, do not continue scaling. On the first installation, run migration before initializing administrators.
3. Release the application. This example leaves the chart's built-in init migration and migration Job disabled because the pipeline manages migration separately:

```powershell
helm upgrade --install flagsmith flagsmith/flagsmith --version '0.84.0' `
  --namespace flagsmith --create-namespace `
  -f 'deploy\helm\values.common.yaml' -f 'C:\secure\path\values.environment.yaml' `
  --wait --timeout '10m'
```

4. Use the official initial setup process to initialize or invite administrators, organizations, and projects. Do not set a public default administrator password. After setup, disable unneeded CLI bootstrap and public registration, then verify invitations and SMTP.
5. Configure "Flagsmith on Flagsmith" to use the private project and URL. Check browser Network activity and egress logs to confirm that the self-hosted console does not unexpectedly connect to SaaS, external analytics, or chat services.
6. Create a smoke-test flag, server key, and required client keys. Verify local, remote, and BFF results, error handling, and network access surfaces separately, then roll out gradually.

For production isolation, use an approved offline Chart package or OCI address rather than running `helm repo update` at the site. Do not run destructive `helm test` tests against a real environment.

## 8. Capacity, update freshness, and high availability

Starting resource suggestions, **not upstream performance commitments**:

| Component | Starting replicas | Requests and limits per replica | Scaling signals |
| --- | --- | --- | --- |
| API | 3 | 500m / 512Mi; 1 CPU / 2Gi | Document and remote-evaluation latency, CPU, and database connections |
| Dashboard | 2 | 100m / 256Mi; 500m / 512Mi | Management access and release activity |
| Task Processor | 2 | 250m / 512Mi; 1 CPU / 2Gi | Queue backlog, oldest task age, and failure rate |
| Optional Edge Proxy | 2 | Configure from rule size and load tests | Remote-evaluation concurrency, memory, and update freshness |
| PostgreSQL | Primary and standby | Start load testing with candidate sizes from 2-4 vCPU and 8-16 GiB | Data volume, IOPS, connections, backup, and HA limits |

Estimate local-evaluation capacity by **SDK instance count**, not business request count. For example, 120 processes polling every 30 seconds produce about 4 pulls per second on average; 1,200 processes produce about 40. Startup storms, document size, synchronization timers, workers, and background tasks increase the peak. Use jitter, rate limiting, and capacity headroom.

Remote mode may fetch the complete flag set for every flag call. Do not assume that one business request equals one provider request. Load-test the real call path. Add request-level memoization or an Edge Proxy when necessary to avoid excessive polling of Core.

Example release-freshness targets: server polling every 30 seconds, BFF successful refresh every 15 seconds, and snapshot TTL of 30 seconds. Measure end-to-end p95 and worst-case windows, including configuration caches, network behavior, retries, and browser background throttling. Do not promise delivery within exactly 30 seconds or immediate emergency disablement.

Spread API, worker, and Dashboard Pods across nodes, and keep at least 3 API replicas under the HPA. Check the remaining CPU, memory, and database connection budget after a complete node failure. A PDB protects voluntary eviction only; it does not guarantee availability after hardware or availability-zone failure. Database HA, backups, and rule caching address different failures and cannot replace one another.

## 9. Backups, disaster recovery, upgrades, and rollback

Suggested targets: **RPO ≤ 15 minutes and RTO ≤ 60 minutes** for a single-region failure or operator error. These targets require continuous backup or replication supported by the selected database and a real recovery drill. A daily dump is not enough to claim that the targets are met.

Back up PostgreSQL, the fixed Django key, encrypted recovery material for SDK and management credentials, Chart and values files, the enterprise license, the identity-mapping design, and the operations runbook. Data exports can support migration and review, but **they are not a complete disaster-recovery backup of every identity, history, audit record, and key**. Redis, browser caches, and rules held in business processes are not authoritative backups.

Run the following drills every quarter and before major upgrades:

1. Restore to a target point in an isolated environment. Restore the Secrets and corresponding application version, then verify projects, environments, permissions, identities, and rules.
2. Use a fixed set of test identities to verify on and off states, segmentation, percentage buckets, and tenant isolation. If keys must change, update every SDK and Proxy.
3. Verify management writes, worker processing, BFF and front-end results, and error monitoring. Record the actual RPO and RTO.
4. Fence the old primary before failover and switch controlled private DNS. After recovery, define whether and how to fail back to avoid two primaries.

Before upgrading, read the official migration and breaking-change notes and validate the release in staging with restored backup data. Reverting an application image is safe only when the database schema remains backward compatible. **Helm rollback does not reverse a database migration.** An incompatible migration needs a maintenance window and a database restore or forward-fix plan. Restoring data loses management changes made after the recovery point, so the business must approve that impact.

## 10. Operational acceptance and alerts

| Category | Acceptance or alert |
| --- | --- |
| Service availability | Probe the API, Dashboard, and worker separately; simulate one Pod and one node exiting |
| Rule freshness | Monitor the last successful SDK or Proxy pull, stale thresholds, and a cold-start offline drill |
| Task processing | Monitor queue length, oldest task age, and failed tasks; execute a real test task |
| Business evaluation | Monitor error rate, default rate, and latency; distinguish a normal off result from an error fallback |
| Database | Monitor connections, space, IOPS, replication lag, backup success, and restore verification |
| Security | Confirm that browsers receive no `ser.` key or rule document; ensure public endpoints cannot reach management APIs; run negative authorization tests |
| Egress | After disconnecting public internet access, verify ordinary evaluation and console behavior; investigate hidden SaaS and analytics requests |
| Release governance | Record owners, approvals, environment isolation, expiry cleanup, and emergency-disable drills |
| Cost | Track QPS by evaluation mode, persisted identity volume, document size, log volume, and storage growth |

Flagsmith 2.170.0 and later provide native Prometheus metrics, but verify the metric names and labels against the locked version. Do not describe custom business metrics as vendor-provided features.

See [scenarios and diagrams](architecture.md) for architecture, sequence, and deployment topologies. See the [integration Skill](../.github/skills/openfeature-flagsmith-dotnet/SKILL.md) for application implementation.
