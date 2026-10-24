# Portable candidate scope

This guide describes the file-level candidate, not a release. The sole inventory and component ownership map is [distribution-manifest.json](distribution-manifest.json). Each listed path is an explicit file copied byte-for-byte; directory names and patterns are never copy instructions. The manifest is included so a recipient can inspect the same inventory.

## Ownership and exclusions

The `component` on each manifest entry identifies the file's delivery owner. Component descriptions and the exact excluded paths are maintained only in the manifest.

The candidate includes reusable project guides, blank forms, shared methods, local maintenance tools with their contracts and lock, and the actual validate-artifacts workflow. It deliberately omits populated business instances and maker evidence, including research/reference material, internal design or execution plans, real session or development logs, verification results, exercise fixtures, test code or runners, proposal/fan-out workflows, Git objects/history, environments, caches, session artifacts, and personal or credential data. `logs/README.md` is an explicitly included blank guide and does not bring along the other files under `logs/`.

The maker-side copy and verification operation is not part of the candidate. It uses portable Python file operations to export exactly the manifest and compare missing, extra, or changed files, keeping ordinary path-scope checks and exclusive creation. It provides no native handle auditing and no protection against hostile concurrent filesystem replacement. Copy and verification reports are exclusive-new files under explicitly authorized output roots, outside the source tree and candidate; overlapping destinations are refused. An existing destination is an ownership conflict, not permission to replace or skip content. The copy has no installer, application scaffold, publisher, Git initialization, history transfer, hook installation, or implicit output location. A local receipt records the exact source commit and dirty scope, per-file raw-byte hashes, excluded source paths, and authorized output roots; it is maker evidence and is not copied downstream.

## Runtime and optional capabilities

- Reading guides and copying blank forms does not require Python or a maintenance-tool install.
- The optional maintenance tools target Windows, Linux, and macOS using Python 3.11+ and the included dependency manifests. Paths are explicit inputs or project-relative resources, never a personal directory, drive, or fixed virtual-environment layout. The downstream project must choose and maintain its own application stack and commands; `src/` remains only a guide.
- Hooks are optional files. Copying or importing them does not install hooks, change Git configuration, create a hosted check, or configure permissions.
- Local-source setup is explicit and local. Offline extraction does not fetch sources or send data. No audio provider, model, SDK, or transcription adapter is selected.
- The local template-update utility is a read-only proposal tool. Its maintainer-only proposal workflow and any fan-out/target checkout are excluded.
- JSON, SVG, and HTML rendering are included, including the parameterized presentation capability. PDF/PPTX remain unavailable; the renderer manifest does not select an engine.
- The interaction ledger accepts only caller-provided records. Read-only summaries do not create lock files. Writes use portable local-process locking and require caller attestation of local, non-synchronized storage; this is not OS/storage-provider verification or a cross-host guarantee.
- The included validation workflow references candidate runtime files, contracts, and the lock. Its presence is not evidence of a hosted run, required-check configuration, or platform approval.

## Status boundary

This candidate is not a release, complete parity claim, business or software acceptance result, application, or proof of client-native discovery. Human/App use, a real application, hosted CI/platform behavior, publication, actual audio, PDF/PPTX, and provider/billing usage remain separate gates. Their absence is not converted to success by copying or local document/tool checks.

For the shared task and authorization entry point, read [AGENTS.md](../AGENTS.md) and the [README activity navigation](../README.md#activities). Project setup and unconfigured application inputs remain in [development.md](development.md); verification layers and `not-run` rules remain in [verification/README.md](../verification/README.md).
