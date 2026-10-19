# Activate Flagsmith Enterprise on a local deployment

Review date: 2026-10-16. This guide describes the official activation path for the [local Docker Compose deployment](local-development.md), which uses Flagsmith 2.285.0 as its reference version. It does not activate Enterprise, purchase a subscription, or change the running instance.

Self-hosting does not automatically include Enterprise features. The supported activation path requires **an approved Enterprise image and a valid organisation licence with its signature**. Changing a UI flag, an environment variable, or a SaaS subscription is not a substitute for this process.

## 1. Obtain a licence and image access

Contact Flagsmith to purchase Self-hosted Enterprise or request a POC trial. Confirm the following before changing the installation:

| Required item | What to confirm |
| --- | --- |
| Deployment entitlement | Self-hosted Enterprise, not only a subscription to the hosted SaaS service |
| Image access | Exact private registry and repository, approved tag or digest, and the account permitted to pull it |
| Image layout | A unified Dashboard and API image compatible with the current Compose layout, plus the supported migration and Task Processor commands |
| Version compatibility | Prefer a vendor-approved Enterprise release matching 2.285.0; otherwise obtain the supported upgrade and migration procedure |
| Licence file | Authorised organisation, project and seat limits, validity period, and trial or production scope |
| Signature file | The matching cryptographic signature supplied by Flagsmith |
| Feature scope | The required SSO, RBAC, workflows, scheduling, realtime, database, and support capabilities |

Official documentation describes different Enterprise image variants with different extensions. Do not guess the image address or assume every variant includes the required frontend and integrations. Use the image reference supplied for your contract or trial, and do not silently substitute `latest`.

## 2. Back up and preserve the local installation

Take a consistent PostgreSQL backup and verify that it can be restored. Preserve the following local configuration outside Git:

| Item | Reason to retain it |
| --- | --- |
| `%LOCALAPPDATA%\FlagsmithDev\compose.yaml` | Base services, network binding, database settings, and migration dependency |
| `compose.mirror.json` | Current image references; keep a copy before editing |
| `compose.runtime.json` | Local Console project configuration, including its client-side key |
| `.env` | Database password and the fixed `DJANGO_SECRET_KEY` |
| Administrator and SDK credential recovery material | Access to the existing accounts and business environments |
| `flagsmith-local_pgdata` | Existing database volume; do not delete it during the change |

A named volume is not a backup, and copying live PostgreSQL data files without a supported backup mechanism is not a consistent database backup.

Do not run the helper's `Reset` action, delete the database volume, rerun `Init`, or regenerate the Django key. Upgrading the edition should preserve the installation rather than initialise a new database.

## 3. Authenticate to the approved private registry

Use the vendor-approved registry authentication process and Docker's credential storage. Do not commit registry credentials, licences, signatures, or administrator passwords to this repository or put passwords in command-line arguments.

**Do not route private Enterprise images or credentials through `docker.1ms.run` or another public image accelerator.** The public mirror in the local guide was selected for public open-source images only.

If the private registry cannot be reached from the workstation, use a vendor-approved delivery method or an approved enterprise registry. Confirm that the agreement permits the proposed internal mirroring, and retain the approved image digests and provenance.

## 4. Replace all Flagsmith image references

Edit `%LOCALAPPDATA%\FlagsmithDev\compose.mirror.json`. Replace the Flagsmith image reference for all three services:

| Service | Required image |
| --- | --- |
| `migrate-db` | Approved Enterprise image compatible with the `migrate` command |
| `flagsmith` | Matching unified Enterprise image serving the API and Dashboard |
| `flagsmith-task-processor` | Matching Enterprise image compatible with `run-task-processor` |

Use the same approved release for these services. For a vendor-approved unified image supporting all three commands, the override has this shape:

```json
{
  "services": {
    "postgres": {
      "image": "docker.1ms.run/library/postgres:15-alpine"
    },
    "migrate-db": {
      "image": "<approved-enterprise-unified-image-reference>"
    },
    "flagsmith": {
      "image": "<approved-enterprise-unified-image-reference>"
    },
    "flagsmith-task-processor": {
      "image": "<approved-enterprise-unified-image-reference>"
    }
  }
}
```

Replace every placeholder with the complete approved registry, repository, and tag or digest. Keep the existing PostgreSQL image if it differs from the example; changing the edition does not require changing the database image or PostgreSQL major version.

The local helper loads the base YAML, then `compose.mirror.json`, then the optional `compose.runtime.json`. Preserve that runtime file's environment settings and check that it does not override the selected Enterprise image.

**Do not run `ConfigureMirror` after this change.** Its current implementation rewrites `compose.mirror.json` with the public open-source images. It is not an Enterprise image configuration action.

## 5. Validate, pull, and update the containers

Run the following actions one at a time from PowerShell 7. The helper sets its working directory to its own directory and uses explicit Compose paths.

Validate the configuration:

```powershell
pwsh.exe -NoLogo -NoProfile -NonInteractive -File "$env:LOCALAPPDATA\FlagsmithDev\Invoke-LocalFlagsmith.ps1" -Action Check
```

Pull the approved images using the configured private registry access:

```powershell
pwsh.exe -NoLogo -NoProfile -NonInteractive -File "$env:LOCALAPPDATA\FlagsmithDev\Invoke-LocalFlagsmith.ps1" -Action Pull
```

Only after a successful pull and completed backup, update the deployment:

```powershell
pwsh.exe -NoLogo -NoProfile -NonInteractive -File "$env:LOCALAPPDATA\FlagsmithDev\Invoke-LocalFlagsmith.ps1" -Action Start
```

Inspect the services and migration result:

```powershell
pwsh.exe -NoLogo -NoProfile -NonInteractive -File "$env:LOCALAPPDATA\FlagsmithDev\Invoke-LocalFlagsmith.ps1" -Action Status
```

The Compose dependency runs migration before the API and worker start. Confirm migration exited with code `0`, all three Flagsmith services use the intended Enterprise release, and the long-running services are healthy. Allow for a local service interruption; this is not a zero-downtime upgrade procedure.

Recheck the browser's sign-in page and local Console configuration as well as container health. If migration fails, investigate before continuing. Do not remove the dependency or reset the database to hide the failure.

## 6. Apply the licence to the target organisation

1. Open `http://localhost:8000/login` and sign in as an administrator of the target organisation.
2. Select **teamplay** for the business organisation used in this local setup.
3. Open **Organisation Settings > Licensing**.
4. Select the vendor-provided **Licence File**.
5. Select its matching **Signature File**.
6. Click **Upload Licensing Files** and confirm the success notification.

The licence is applied to an organisation. Do not accidentally upload the business licence to the separate Console configuration organisation or assume that one upload licenses every organisation in the instance.

The official workflow also supports an API upload for automation. Use that documented endpoint with an organisation administrator's token and both files; do not include real tokens or licence contents in repository examples.

## 7. Confirm entitlements and configure the features

| Check | Expected result |
| --- | --- |
| Edition | Running images are the approved Enterprise variants, not just an Enterprise label in the UI |
| Licence | Valid signature, intended organisation, correct validity period and authorised limits |
| Projects and seats | Organisation limits reflect the licence; Enterprise does not necessarily mean unlimited |
| Existing data | Accounts, projects, environments, keys, and flag values remain available |
| Feature evaluation | Existing SDK or local smoke-test requests still return the expected result |
| Console | Local feature-configuration requests succeed and the Dashboard does not show Maintenance |
| Purchased features | Relevant capabilities are present and their end-to-end setup is completed |

A successful licence upload does not configure an identity provider, enable SMTP, deploy SSE, or create an experimentation warehouse. SSO, workflows, realtime updates, and other extensions still require their own supported configuration and, where applicable, additional infrastructure.

## Troubleshooting and rollback

| Symptom | What to check |
| --- | --- |
| Licensing tab is missing | Verify the API and Dashboard are actually running the required Enterprise image, then reload the browser |
| Private image pull fails | Check registry entitlement, Docker authentication, proxy, and CA trust; do not send private credentials to a public accelerator or disable TLS verification |
| Image unexpectedly reverts to open source | Check whether `ConfigureMirror` rewrote the override, and review all three image references |
| Signature validation fails | Use the matching licence and signature pair supplied by Flagsmith; contact the account team if verification still fails |
| No permission to upload | Use an organisation administrator account for the intended organisation |
| One-project restriction remains | Check the organisation receiving the licence, its status, and the project limit actually authorised |
| SSO or another feature is unavailable | Confirm the contracted feature, required image variant, and its separate configuration |
| Application downgrade is being considered | Check schema compatibility and the vendor's rollback procedure; changing the image does not reverse migrations |

For an incompatible migration, use the verified database recovery or forward-fix procedure. A database restore can lose changes after the backup point. Do not assume that restoring the previous image reference alone restores the previous installation state.

## Official references

- [Enterprise Edition and image variants](https://docs.flagsmith.com/deployment-self-hosting/enterprise-edition).
- [Enterprise licence, signature, Dashboard and API upload](https://docs.flagsmith.com/deployment-self-hosting/core-configuration/licence).
- [Upgrades and rollbacks](https://docs.flagsmith.com/deployment-self-hosting/administration-and-maintenance/upgrades-and-rollbacks).
- [Local deployment guide](local-development.md) and [deployment directory](README.md).
