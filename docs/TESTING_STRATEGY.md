# ONE LINE — Testing Strategy

## Objective

Prevent regressions and establish evidence that the game behaves according to specification.

## Testing Layers

### Layer 1 — Unit Tests

Test isolated:

* graph operations;
* path validation;
* completion;
* scoring;
* level validation;
* serialization;
* save migration.

### Layer 2 — Integration Tests

Test:

* level loading;
* progression;
* save/load;
* gameplay state transitions;
* settings persistence.

### Layer 3 — Automated Playtesting

Run the solver against every final level.

Verify:

* a solution exists;
* the runtime accepts the solution;
* no unexpected rule mismatch exists.

### Layer 4 — Regression

Every important defect receives a regression test.

### Layer 5 — Build

Verify that the project can build/export using the intended configuration.

### Layer 6 — Device

Where actual devices are available, test:

* touch;
* screen sizes;
* safe areas;
* lifecycle;
* performance;
* audio;
* installation;
* upgrade behavior.

## Test Status

Use:

PASS
FAIL
UNVERIFIED
HUMAN ACTION REQUIRED

## Rule

No test result may be fabricated.
