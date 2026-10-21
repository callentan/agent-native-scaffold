---
applyTo: "architecture/**/*.md,src/**,app/**,apps/**,lib/**,packages/**,services/**"
---

# Source-backed architecture boundaries

These are a limited set of initial path patterns; they do not prescribe project locations or code layering. When actual code lives in other directories, or the client does not load this file, whoever makes the change must still read these rules explicitly. Adjust the match patterns to the real project; do not move code just to make it match.

- First read the actual task, domain responsibilities, SR, applicable ABB/ADR/QAS, and the [development registration](../../docs/development.md#project-registration). Constrain only the architecture this project actually adopts; do not assume four layers, service decomposition, a language, a cloud platform, containers, or dedicated endpoints by default.
- Where a layered or ports-and-adapters architecture is already adopted, domain rules and business control logic depend inward; do not let infrastructure details dictate domain meaning in reverse. Only an explicit composition root or startup wiring location may reference concrete adapters to assemble dependencies; the wiring does not own business rules.
- This exception does not extend to every controller: a boundary entry point must not use wiring as a pretext to bypass use-case/domain constraints or to write business state directly without an agreed contract. Any existing project exception, such as a read-only projection, needs an actual scope or decision basis; do not infer a general permission to access the database from it.
- Distinguish, by source, fact owners from consumers, and logical dependencies from runtime message direction. Where an explicit asynchronous integration or event-consumption contract exists, keep its boundary; a conceptual exchange between contexts is not enough to infer service calls, transport, retries, or delivery guarantees.
- Constraints on dependency versions, interface compatibility, failure/concurrency, runtime/deployment, and observability need an actual source; when they are unknown, raise items to be confirmed instead of filling in common SLAs or infrastructure. Take real trade-offs back to an [ADR](../../architecture/README.md#decisions); domain sources are not written back automatically.
- Record each real deviation with its path/location, the source of the constraint, and the rationale. A configured dependency check or native test proves only what it actually checks; semantics, wiring boundaries, and trade-offs still need review, and the rule file itself can neither run nor approve anything.
