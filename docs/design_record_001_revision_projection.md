# Design Record 001: Revision Projection

Dicta must distinguish three states in every semantic motion:

1. The Concept before a Disparity is observed.
2. The Outcome produced under Purpose.
3. The Concept after an accepted Revision.

The early demos originally proved that those states could be narrated. The next
standard is stricter: a Disparity must preserve the Concept as it stood when the
gap was revealed, and a final Program Concept must not depend on rewriting that
evidence later.

## Current Rule

Disparity records use snapshot semantics for their Concept. If the live Program
Concept changes after a Disparity is created, the Disparity still points at the
before-state.

Revision remains intentionally small. It still carries human-readable change
notes, but the final Concept in demos may now represent the after-state instead
of carrying superseded state as if it were current meaning.

## Deferred Rule

Future Revision records should carry structured operations, such as adding,
removing, or replacing Dicta. A Concept projection can then be derived by folding
those Revisions over prior state.

That is the event-sourcing shape for Dicta:

- Revision is the appraised event.
- Concept is the projection.
- Disparity is evidence from the before-state.

This remains future work. No parser, compiler, VM, lowering, or appraiser is
introduced by this record.

## Reference Direction

Truth-maintenance systems are relevant because they preserve justifications for
belief changes. Toulmin-style qualifier, warrant, and backing terminology is
also relevant because Dicta Qualification records basis, conditions, timing, and
strength.

These are design references, not runtime dependencies.
