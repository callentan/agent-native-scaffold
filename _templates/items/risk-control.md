---
schemaVersion: 1
id: RC-NNN
kind: risk-control
scope: PROJECT/CTX-NNN
contentState: draft
---
# RC-NNN: TBD risk control reference

> Optional reference to external risk material; not a risk analysis or acceptance authority. Read the [governance boundaries](../../docs/governance.md#intended-use) and [source field conventions](../../docs/governance.md#source-views) first. Copy to `domain-model/RC-NNN-<slug>.md` as needed, replace placeholders, fix links, then delete this notice. Add only real upstream relationships; do not fabricate requirements, VTs, or risk levels to complete an export.

<a id="analysis"></a>
## External risk analysis source

| Analysis information | Content |
|---|---|
| External analysis text, section, and baseline | Not provided: an actual source is required; do not copy the full external analysis |
| Accessibility, check date, and limitations | Not provided: if unreadable, keep the location clues and the specific gap |
| Analysis owner and applicable basis of responsibility | Not provided: this repository does not become the authority on external risk |
| Pre-mitigation risk | Not provided: only cite a conclusion already given externally and its location; do not calculate or prefill a level |

<a id="control"></a>
## Control and implementation basis

| Control information | Content |
|---|---|
| Control text, scope of application, and baseline | Not provided: an actual control source is required |
| Control owner and implementation responsibility | Not provided: a sourced responsibility arrangement is required |
| Reading entry points for requirements, design, and tests | TBD: actual REQ/SR, design, VT/raw report; do not copy relationship or result tables |
| Known implementation limitations and evidence gaps | TBD; missing tests do not mean the control is already effective |

<a id="residual"></a>
## Residual risk and actual decision reference

| Decision information | Content |
|---|---|
| Residual risk | Not provided: only cite the original external conclusion; do not estimate a score or infer risk acceptance |
| Acceptance/rejection decision text, date, and baseline | Not provided: a form field cannot substitute for a missing approval |
| Named decision maker and source of responsibility/authority | Not provided: a Reviewed-by string cannot authenticate anyone |
| Objects, scope, and limitations the decision applies to | Not provided: do not extrapolate to other uses or versions |

When the source is unavailable or the decision is missing, keep it unknown and stop the affected acceptance/compliance statements; do not fill in a default severity, residual risk score, or legal compliance. The frontmatter alone holds contentState and confirmation; neither means the external risk has been accepted.

<a id="follow-up"></a>
## Remaining gaps and recheck

- Missing/unreadable sources, blocked judgments, and who must supply what: TBD.
- Changes to the use, requirements, controls, or object baselines, and the original artifacts to re-review: TBD.
- Preserved entry points to old sources/decisions/VTs, next steps, and their authorization prerequisites: TBD.

The model only references sources and baselines; keep `partial` for incomplete fields and `unverified` for an unreadable optional source. Do not fabricate values, reverse relationships, or decisions to complete an export, and do not overwrite external sources or historical results.
