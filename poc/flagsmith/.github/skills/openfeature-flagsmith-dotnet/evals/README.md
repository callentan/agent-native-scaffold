# Evaluating this Skill

Use [scenarios.json](scenarios.json) to test application behavior, not keyword recall. This Skill combines implementation references with operational guardrails; it is not a general discipline-enforcement Skill.

## Fresh-context comparison

1. Give a fresh agent the `microtest.task` without the Skill. Do not let the control inspect repository references or inherit a prior review. Run five independent controls.
2. Give five fresh agents the same task with the Skill entry point and its relevant references/examples available. Do not supply a reviewer-written answer.
3. Preserve responses verbatim in the session's artifact store. Score each rubric item by reading actual code/algorithms, not by counting words such as "safe" or "generation".
4. Record missing code, invented APIs, unhandled states, and inconsistent choices. A correct plan is evidence about guidance, not proof that generated code compiles.
5. If the controls do not show a proposed failure, do not add speculative rules for it. For demonstrated gaps, edit the smallest relevant route/reference, then repeat the affected application scenario.

Keep the task wording, permitted tools, model selection, and output constraints consistent between variants. Record any limitation rather than presenting a small sample as a statistical benchmark. Do not call external model APIs or send private project code to third parties.

## Executable checks

The repository's `scripts\Test-Examples.ps1` runs the compiled .NET SDK regression harness, Angular TypeScript/service tests, and structure/language/link checks. It accepts an explicit repository root and an optional restore step. The example dependency lockfiles are part of this Skill.

These checks complement rather than replace the fresh-context comparison:

| Check | Establishes | Does not establish |
| --- | --- | --- |
| .NET synthetic transport | No remote fallback, local hot path, Details, logger filtering | Live Flagsmith, target business identity, throughput, deterministic SDK polling teardown |
| Angular service tests | Binding, degradation, cancellation, TTL, hydration state | Real templates, interceptor credentials, full SSR transport, live browser provider |
| Structural validator | English text, frontmatter, local links/anchors, shell labels, supporting files | Agent compliance or runtime behavior |
| Application scenarios | Whether guidance leads to the required implementation choices | Production readiness |

For a release, also run the target application's own build/tests, staging contract checks, authorization negative tests, and outage/recovery exercises relevant to the selected route. Do not modify production flags during an evaluation.

## Reporting evidence

Record the date, variant, scenario, runtime-selected agent/model when available, response artifact location, rubric verdicts with short verbatim evidence, executable results, and untested boundaries. `results.json` records this repository's observed optimization run; it is an audit record, not an input that future test agents should read.
