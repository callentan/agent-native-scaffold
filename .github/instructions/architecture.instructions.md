---
applyTo: "architecture/**/*.md,src/**,app/**,apps/**,lib/**,packages/**,services/**"
---

# Source-backed architecture boundaries

Apply these rules when changing architecture documents or code. They tie architecture constraints to what the project actually adopts and to actual sources.

## Scope of these rules

- The `applyTo` patterns are a limited initial set. They do not prescribe project locations or code layering.
- When actual code lives in other directories, or the client does not load this file, whoever makes the change must still read these rules explicitly.
- Adjust the match patterns to the real project. Do not move code just to make it match.

## Read first

- First read the actual task, domain responsibilities, SR, applicable ABB/ADR/QAS, and the [development registration](../../docs/development.md#project-registration).
- Constrain only the architecture this project actually adopts. Do not assume four layers, service decomposition, a language, a cloud platform, containers, or dedicated endpoints by default.

## Dependency direction and wiring

- Where a layered or ports-and-adapters architecture is already adopted, make domain rules and business control logic depend inward. Do not let infrastructure details dictate domain meaning in reverse.
- In that architecture, only an explicit composition root or startup wiring location may reference concrete adapters to assemble dependencies. The wiring does not own business rules.
- This wiring exception does not extend to every controller. A boundary entry point must not use wiring as a pretext to bypass use-case or domain constraints, or to write business state directly without an agreed contract.
- An existing project exception, such as a read-only projection, needs an actual scope or decision basis. Do not infer a general permission to access the database from that exception.

## Integration and runtime constraints

- Use sources to distinguish fact owners from consumers, and logical dependencies from runtime message direction.
- Where an explicit asynchronous integration or event-consumption contract exists, keep its boundary. A conceptual exchange between contexts is not enough to infer service calls, transport, retries, or delivery guarantees.
- Constraints on dependency versions, interface compatibility, failure/concurrency, runtime/deployment, and observability need an actual source. When a constraint is unknown, raise an item to be confirmed; do not fill in common SLAs or infrastructure.
- Record real trade-offs in an [ADR](../../architecture/README.md#decisions). Do not write back to domain sources automatically.

## Deviations and evidence

- Record each real deviation with its path/location, the source of the constraint, and the rationale.
- A configured dependency check or native test proves only what it actually checks. Semantics, wiring boundaries, and trade-offs still need review.
- This rule file can neither run nor approve anything.
