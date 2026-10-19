# Flagsmith deployment guide

This directory contains the shared Helm configuration for a private Flagsmith deployment on Azure and China Telecom eSurfing Cloud. Use the official containers and official Helm Chart in a Kubernetes cluster in each data domain.

The current deliverable is a deployment design and configuration starting point, **not a complete package ready for production**. The repository does not provide cloud resource-creation scripts, environment overlay files, a database migration Job, or complete network policies. The platform team must add them for the target environment. See the full [private deployment design](../docs/private-deployment.md).

## Deployment options

| Scenario | Design | Notes |
| --- | --- | --- |
| Azure | Private AKS with external highly available PostgreSQL | Use ACR or an internal registry for images; deliver Secrets through Key Vault or the enterprise's existing process |
| China Telecom eSurfing Cloud | CCE or resource-pool Kubernetes with external highly available PostgreSQL | Use CRS or Harbor for images; determine secrets injection and network capabilities from the target resource pool |
| Restricted environment without Kubernetes | At least two application VMs with an internal LB and external highly available PostgreSQL | Use the same official containers, then add process management, rolling upgrades, and health checks; this directory does not provide that configuration |
| Local development, validation, or POC | Single-machine Docker Compose | See the [local development deployment](local-development.md) for configuration and PowerShell examples; it does not provide production HA |

Deploy a complete instance independently in Azure and eSurfing Cloud by default. Keep the databases, projects, environment keys, and identities separate, with no cross-cloud dual writes. Do not configure the two instances as if they were one Flagsmith environment. For disaster recovery, design a single-writer primary, standby, failover, and recovery process within the applicable data-residency boundary.

OpenFeature is the SDK interface inside the business application. **It does not require a separate OpenFeature server.** Existing .NET microservices do not need to move into these clusters. They only need access to the private Flagsmith API in their own data domain.

## Components and access patterns

| Component | Baseline in the shared configuration | Responsibility |
| --- | --- | --- |
| Flagsmith API | 3 replicas; HPA range 3-10 | Management API, environment rule documents, and SDK remote evaluation |
| Dashboard | 2 replicas | Management console, not the business front end |
| Task Processor | Enabled, 2 replicas | Asynchronous tasks, using a PostgreSQL task queue by default |
| PostgreSQL | Built-in development database disabled; external database Secret referenced | Authoritative configuration and task data; prepare the database separately |
| Edge Proxy | Optional and not included in the shared configuration | Deploy when remote-evaluation volume justifies it |
| SSE and experimentation extensions | Disabled | Not part of the first-phase baseline |

Redis is not required by this baseline. Multiple replicas and PDBs do not by themselves provide high availability. Configure scheduling across nodes and fault domains, provide database HA, and verify remaining capacity after a node failure.

Recommended access patterns:

- Administrators use the corporate VPN or private circuit to reach the private Dashboard and management API. The API address configured for the Dashboard must be resolvable and reachable from the administrator's browser.
- Business services use server keys to access the private API and should prefer SDK local evaluation. The server creates trusted tenant and user context.
- The business browser obtains allowlisted, already evaluated results through the BFF. It does not receive server keys or rule documents. This route does not need a public Flagsmith endpoint.
- Open a restricted SDK evaluation endpoint only when a public, non-sensitive UI flag must be evaluated directly in the browser. Limit paths, configure CORS and rate limiting, and do not expose the management API.

## Directory and version

| File | Purpose |
| --- | --- |
| [Local development deployment](local-development.md) | Workstation Docker Compose setup, domestic image mirror selection, initialization, application connectivity, and reset |
| [Enterprise activation](enterprise-activation.md) | Official image and licence prerequisites, data-preserving local edition switch, organisation activation, and rollback cautions |
| [helm/values.common.yaml](helm/values.common.yaml) | Shared non-sensitive Helm configuration starting point for both clouds |
| [Private deployment design](../docs/private-deployment.md) | Cloud resource mapping, network boundaries, release steps, capacity, and disaster-recovery requirements |
| [Scenarios and diagrams](../docs/architecture.md) | Architecture, call sequences, and dual-cloud deployment topology |
| [Sources and verification record](../docs/sources.md) | Official sources, versions, and compatibility evidence |

The shared configuration targets **Helm Chart 0.84.0 and Flagsmith 2.285.0**. This is a reference version, not an approval to deploy without review. Before changing the Chart or application version, recheck the values fields, templates, and upgrade notes.

## Configuration to provide before deployment

The shared configuration disables Ingress, the built-in database, and automatic migration. Applying only `values.common.yaml` does not produce a complete production environment.

| Area | Environment requirement |
| --- | --- |
| Kubernetes and database | Prepare the namespace, schedulable nodes, external PostgreSQL HA, TLS, connection limits, and backups |
| Images and Chart | Import approved images and Chart packages into an internal registry, lock versions and digests, and configure pull permissions |
| Environment overlay | The platform team supplies `values.environment.yaml` with non-sensitive overrides for image locations, domains, resources, and scheduling. The file is not included in this repository |
| Private entry point | Configure the internal LB, Gateway or Ingress, DNS, and certificates. Replace the `internal.example.com` placeholders in the shared configuration |
| Network boundary | Add NetworkPolicy, egress allowlists, and trusted-proxy configuration. Protect sensitive internal traffic with TLS, mTLS, or an equivalent mechanism |
| Operations | Configure fault-domain distribution, a Task Processor PDB, monitoring and alerts, database recovery, and go-live acceptance |

Before release, use the enterprise secrets process to create these Secrets in the target namespace:

| Secret | Key | Requirement |
| --- | --- | --- |
| `flagsmith-runtime` | `DATABASE_URL` | Points to external PostgreSQL with a URL-encoded password; configure TLS and certificate verification for the database CA |
| `flagsmith-runtime` | `DJANGO_SECRET_KEY` | Fixed long random value shared by the API and worker and retained across upgrades and reinstalls |

Deliver business environment keys, management tokens, and optional Edge Proxy credentials separately. Do not mix them with the runtime Secret above. Do not commit credentials to Git or put them in Helm `--set` arguments. After rotating a secret injected through environment variables, perform a controlled Pod rollout or rebuild the SDK.

The Chart 0.84.0 template generates `DJANGO_ALLOWED_HOSTS=*`. In production, replace it with one explicit Host list through a reviewed internal Chart patch or structured post-renderer. Do not rely on the order of duplicate environment variables. Also verify CSRF and CORS settings, proxy headers, and probe behavior. See the [Helm release baseline](../docs/private-deployment.md#7-helm-release-baseline).

## Release process

1. Confirm the data domain, cloud environment, and region. Establish the cluster, database, image registry, private entry point, and secrets delivery, and verify the capabilities offered by the target resource pool.
2. Prepare the shared configuration and environment overlay. Render the locked Chart version and review the resources. In an isolated environment, use an approved offline package or internal OCI address instead of depending on a public download at release time.
3. Back up the database before the upgrade and freeze management changes as needed. The pipeline must run one independent migration Job with the same image and environment configuration, and it must succeed before the release continues.
4. Install or upgrade Helm with the shared configuration and environment overlay, then wait for the API, Dashboard, and worker to become ready. The shared configuration disables init migration and the Chart migration Job, so do not skip the previous step.
5. For a first installation, follow the official initial setup process to create the administrator, organization, project, and environment. Verify invitations and SMTP. Configure the Dashboard to use the private Flagsmith project and URL, then investigate unexpected SaaS egress.
6. Create a smoke-test flag. Verify local and remote evaluation, BFF results, access restrictions, offline degradation, and worker task processing before gradually connecting business applications.

See the [full deployment design](../docs/private-deployment.md) for rendering and release commands and cloud implementation steps. Complete the environment overlay and migration process first; do not use placeholder paths from the design directly in production.

## Acceptance and rollback

Before go-live, verify the API, Dashboard, and worker separately. Confirm that real tasks are processed, measure rule-update freshness, test SDK cold-start behavior and fallback while offline, and exercise one Pod and one node failure. Browsers must not receive server keys or rule documents, and public endpoints must not reach management APIs.

Backups should include PostgreSQL, the fixed Django key, credential recovery material, and the matching Chart and values files. The full design's RPO ≤ 15 minutes and RTO ≤ 60 minutes are design targets pending recovery drills, not commitments of this delivery.

**Helm rollback does not reverse a database migration.** Revert the application separately only when the schema remains backward compatible. For an incompatible upgrade, prepare a database restore or forward-fix plan in advance. Restoring the database loses management changes made after the recovery point, so confirm the impact beforehand.
