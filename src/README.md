# Project placement guide

Currently `src/` contains only this guide: no application, dependencies, preset tech stack, or fixed test directory. Do not create a project automatically just to make the skeleton "runnable".

Once the user has explicitly chosen and authorized it, a new project can go directly in `src/` or in `src/<project>/`. An existing project keeps its original path and its native source, test, and configuration layout; it is not required to migrate or to create `src/tests/`.

Before creating or onboarding a project, check the target directory and the required inputs. Afterwards, fill in the real relative location, native layout, environment and dependencies, install/build/run/test commands, actual working directory, report location, and applicable conditions in the [subproject registration of the development guide](../docs/development.md#project-registration).

While the development inputs are not yet determined, leave them unconfigured. When there is no application, application builds and tests are not applicable to documentation tasks; planned business or software behavior VTs remain `not-run`, and a document check cannot be reported as the application passing.
