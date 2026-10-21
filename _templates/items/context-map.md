---
schemaVersion: 1
id: CM-NNN
kind: context-map
scope: PROJECT/CTX-NNN
contentState: draft
upstream: []
targets: []
---
# CM-NNN: TBD context map notes

> Optional relationship description; it requires neither a diagram nor splitting services. First read the [directed exchanges](../../domain-model/README.md#exchanges) and the [metadata conventions](../../domain-model/README.md#artifact-metadata). Copy it to `domain-model/CM-NNN-<slug>.md` only when needed; confirm the `PROJECT/CTX-NNN` this record belongs to, replace the ID, title, and anchors, fix relative links, keep any existing relationships, and then delete this hint.

<a id="basis"></a>
## Sources and knowledge boundaries

- Known contexts and fact ownership with source location, date, or version: TBD.
- Derived candidates and the basis for deriving them: TBD.
- Open questions and who needs to confirm them: TBD.

Upstream declarations of the participating artifacts belong in the frontmatter; the sections below record direction, term meaning, and responsibility, and are not a second machine-readable relationship table.

<a id="relations"></a>
## Directed relationships

Record each direction separately; do not infer two-way reads and writes from an undirected line.

| Provider → consumer | Information or capability and fact owner | Relationship type and the basis for choosing it | Consumption boundary and dependencies |
|---|---|---|---|
| TBD | TBD | Not decided | TBD |

The relationship type can be an evidence-based Partnership or Customer-Supplier relationship, or it can remain undecided. Choose patterns such as ACL, Open Host Service, Shared Kernel, or Separate Ways only when there is a real need and a source; this table does not mandate them.

<a id="translation"></a>
## Translation and collaboration agreements

| Collaboration information | Content |
|---|---|
| Term differences between the two sides and translation responsibility | TBD; do not assume terms mean the same thing |
| Allowed dependencies and explicitly forbidden cross-boundary changes | TBD |
| Navigation to the Published Interface / partner description | Not provided; if one exists, link to the original owner |
| Source of version and compatibility agreements | Not provided |
| Business boundaries for timeliness, failure, and interruption | Not provided; do not assume retry or degradation |
| Owner and approval boundary for jointly maintained content (if applicable) | Not decided; do not assume a Shared Kernel |

<a id="questions"></a>
## Changes and gaps

- Unclear direction, ownership, pattern, or translation, and their impact: TBD.
- Who needs to supply what, and related BLs: TBD.
- Old and new baselines of relationship changes and impact on consumers: TBD; notifications and cross-repository changes still require separate authorization.
