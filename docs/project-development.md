# Project development registration

Project-owned registration of the downstream business application and its open items. The scaffold's maintenance tools, creation prerequisites, and document checks stay in the [development guide](development.md).

<a id="project-registration"></a>
## Subproject location and command registration

This section registers only the **downstream business application**, which is still not configured; the maintenance tools in the [development guide](development.md#maintenance-tools) are not an application subproject. After a real project is created or onboarded, copy the registration tables below for each subproject. One set is one project, and working directories must not be mixed between commands. Record local locations as repository-root-relative paths, resolve and confirm them in the current workspace before running, and do not record personal absolute paths.

| Project information | Current value |
|---|---|
| Subproject name or identifier | Not configured |
| Subproject relative location | Not configured |
| Native layout (actual locations of source, tests, and configuration) | Not configured |
| Tech stack, tools, and versions | Not configured; to be selected by the user |
| Environment prerequisites and dependency sources | Not configured; do not record credentials |
| Basis for the task/user selection and its scope | TBD |

| Operation | Actual command | Actual working directory (repository-relative path) | Raw report/output location | Applicability conditions and limitations |
|---|---|---|---|---|
| Install dependencies | Not configured | Not configured | Not configured | No project yet; do not run |
| Build | Not configured | Not configured | Not configured | No application yet; not applicable to the current documentation task |
| Run | Not configured | Not configured | Not configured | No application yet; do not run |
| Test | Not configured | Not configured | Not configured | No application yet; a planned behavior VT stays `not-run` |

These "Not configured" values are not executable commands; do not use empty scripts, commands that only print success, or commands without real checks as placeholders. Before filling them in, confirm the command, cwd, report location, and purpose against the real project. A zero exit code does not mean acceptance passed; record the check scope, discovered, executed, and skipped counts, and the actual result according to the [verification guide](../verification/README.md#execution).

A report location points only to actual output or an authorized report entry point; if none exists yet, write "To be configured". Add ignore rules for files produced by project tools according to their real locations; never ignore formal requirements, verification documents, or development logs.

<a id="troubleshooting"></a>
## Missing items and troubleshooting

| Missing item or problem | Known basis and impact | Inputs to add or next step |
|---|---|---|
| Business application environment and commands not configured | No business application yet; the maintenance-tool environment is listed separately, so documentation tasks are not blocked | After the user decides to create an actual project, complete the business application registration; do not reuse the tool stack to choose the application on the user's behalf |
| Other issues | TBD | TBD |

When a command is unavailable, inputs conflict, or environment requirements are unmet, report the specific reason; do not silently switch tools or record a not-run item as success. After a command, project, or acceptance baseline changes, reassess result applicability, and keep pending re-review and not-run items in the [log](../logs/README.md).
