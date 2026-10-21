---
applyTo: "src/**,app/**,apps/**,lib/**,packages/**,services/**"
---

# Security boundaries in implementation

These are reading rules for a limited set of paths, not an ACL, a security scanner, or proof of an audit. Read them explicitly even when the actual code or configuration sits in a path that does not match; real permissions are determined by the client, operating system, and platform configuration.

- Do not store secrets or credentials in source code, configuration, fixtures, or reports. Use the project's existing, approved secret-injection mechanism; if configuration is missing, stop the corresponding operation instead of creating a usable default password or writing sensitive values to logs.
- Validate external input at trust boundaries, and use the actual language/framework's safety mechanisms for databases, commands, paths, and output encoding respectively. Do not build commands by concatenating input or bypass scope checks; a generation task does not grant permission to overwrite existing user content or read-only sources.
- Authentication and authorization are separate responsibilities. Check principal, resource, and action against the actual policy, and enforce decisions at the established trusted boundary. Without a policy, do not assume anonymous access, an all-powerful role, or frontend-only checks, and do not claim permissions are configured just because a rule exists.
- Errors and logs record only the diagnostics needed; do not expose secrets, personal data, raw sensitive input, or internal details. Handle auditing, retention periods, and correlation identifiers according to the actual project's conventions; for unknown rules, ask the accountable owner to confirm.
- Reuse the chosen framework's cryptography and dependency-management mechanisms. Do not invent cryptographic algorithms, disable certificate or authentication checks, or silently add dependencies. External scans, installs, data transmission, and service calls each need separate authorization.
- Map relevant rejection paths, input boundaries, and leakage risks to actual acceptance criteria and tests. Without tools, objects, or evidence, record them as not run or pending review; do not claim an audit passed by ticking a security checklist, pointing to test file names, or writing Approved into content.
