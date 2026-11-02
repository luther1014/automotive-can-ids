# Decision log

## ADR-001: Keep the author's test folders intact
Reason: enables evaluation of unfamiliar vehicles and attack types and avoids contamination.

## ADR-002: Begin with stateless frame-level features
Reason: small understandable baseline; later temporal features will be tested under causal constraints.

## ADR-003: Uniform row sampling is for exploration only
Reason: labels are naturally imbalanced. Full-trace held-out results will be required later.

## ADR-004: Hold out complete CSV captures for internal validation
Reason: row-level random splits can mix near-identical frames from the same capture.
