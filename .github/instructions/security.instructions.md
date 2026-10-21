---
applyTo: "src/**,app/**,apps/**,lib/**,packages/**,services/**"
---

# Security boundaries in implementation

Apply these rules to implementation code and configuration. Use the project's actual policies and security mechanisms, and do not claim a security result without evidence.

## Scope of these rules

- These are reading rules for a limited set of paths, not an ACL, a security scanner, or proof of an audit.
- Read them explicitly even when the actual code or configuration sits in a path that does not match `applyTo`.
- Real permissions are determined by the client, operating system, and platform configuration.

## Secrets and credentials

- **Do not store secrets or credentials in source code, configuration, fixtures, or reports.**
- Use the project's existing, approved secret-injection mechanism.
- If that configuration is missing, stop the corresponding operation. Do not create a usable default password or write sensitive values to logs instead.

## Input, commands, and existing content

- Validate external input at trust boundaries.
- Use the actual language/framework's safety mechanisms for databases, commands, paths, and output encoding, respectively.
- Do not build commands by concatenating input, and do not bypass scope checks.
- A generation task does not grant permission to overwrite existing user content or read-only sources.

## Authentication and authorization

- Treat authentication and authorization as separate responsibilities.
- Check principal, resource, and action against the actual policy, and enforce decisions at the established trusted boundary.
- Without a policy, do not assume anonymous access, an all-powerful role, or frontend-only checks.
- Do not claim permissions are configured just because a rule exists.

## Errors, logs, and auditing

- Record only the diagnostics needed in errors and logs. Do not expose secrets, personal data, raw sensitive input, or internal details.
- Handle auditing, retention periods, and correlation identifiers according to the actual project's conventions. For unknown rules, ask the accountable owner to confirm.

## Cryptography, dependencies, and external actions

- Reuse the chosen framework's cryptography and dependency-management mechanisms.
- Do not invent cryptographic algorithms, disable certificate or authentication checks, or silently add dependencies.
- External scans, installs, data transmission, and service calls each need separate authorization.

## Evidence

- Map relevant rejection paths, input boundaries, and leakage risks to actual acceptance criteria and tests.
- Without tools, objects, or evidence, record them as not run or pending review.
- Do not claim an audit passed by ticking a security checklist, pointing to test file names, or writing Approved into content.
