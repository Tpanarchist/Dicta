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

## First Mechanical Appraisal

The earlier demos were hand-authored semantic records. They proved that the
chain could be represented, but not that a Program could produce the chain from
structured input.

The first arithmetic appraiser is a deliberately tiny next step. It accepts a
structured Datum, such as `ArithmeticDatum(left=3, operator="+", right=4)`,
consults a Concept containing operand and operator Dicta, and produces the
Disparity, Inference, Outcome, Revision, and final Program Concept
mechanically.

This is still not syntax. It does not parse source text, and it is not a
general interpreter.

## Mechanical Refusal

The success appraiser proved that structured Datum can produce a valid semantic
chain mechanically.

The invalid arithmetic appraiser proves the negative twin. A structured Datum
such as `ArithmeticDatum(left=3, operator="+", right="cat")` can produce
qualified operand Dicta, reveal a type Disparity, derive refusal, witness a
refused Outcome, and record a Revision without first becoming a host-language
exception.

This matters because invalidity belongs inside Dicta's semantic motion. Python
exceptions remain an implementation boundary for unsupported appraiser shapes,
not the primary representation of appraised invalid arithmetic.

## Appraisal Result Shape

The first appraisers produced Program records directly. That remains the public
Program-facing behavior for callers that only need the semantic chain.

`AppraisalResult` preserves the produced Program while also making the
mechanical acceptance status explicit. It carries whether the appraisal was
accepted, a short summary, and direct links to the Disparity, Outcome, and
Revision that were produced.

This shape is for future checkers, agents, and CLIs that need to inspect
acceptance or refusal without unpacking Program history manually. It is still
not syntax, not lowering, and not a full interpreter.

## Mechanical Counter Revision

The arithmetic appraisers proved mechanical success and refusal.

The counter appraiser proves that structured Datum can produce an applied
Revision. The final Program Concept is projected from the Revision: it preserves
`counter is Number`, replaces `counter is 0` with `counter is 1`, and does not
keep the old current-value Dictum as live Concept state.

The Revision also carries a structured `replace_dictum` operation so future
checkers can inspect the state change without parsing the prose change note.

This is still not syntax and not a general interpreter.

## Mechanical Counter Refusal

The accepted counter appraiser proved that structured Datum can produce an
applied Revision.

The refused counter appraiser proves the negative rule: structured Datum can
also refuse Revision when the current Concept does not qualify under Purpose.
For `counter = "cat"; counter = counter + 1`, the Program preserves
`counter is Text` and `counter is "cat"` instead of inventing `counter is 1`.

Mutation is therefore not automatically allowed. Mutation is allowed only when
it qualifies.

## Appraisal Helper Extraction

After mechanical success and refusal for arithmetic and counter revision, the
shared appraisal shape was extracted into small helpers. The helpers classify
narrow values, build typed Dicta, and wrap accepted or refused appraisal results
without forcing each appraiser to repeat that boilerplate.

This is still not syntax, not a general interpreter, and not a rule engine.

## Mechanical File Write Appraisal

The arithmetic and counter appraisers covered evaluation and Revision.

The file write appraiser covers the effect boundary. It can mechanically accept
`write report.txt "hello"` by recording Permission, intended Disk change, and
the resulting file-content Dictum. It can also refuse
`write protected/report.txt "hello"` by recording Permission Disparity and
preserving Disk unchanged.

This proves a world-changing operation can be accepted or refused mechanically
without performing the real effect. It is still not syntax, not a runtime
engine, and not actual IO.

## Mechanical Supervision Appraisal

The arithmetic, counter, and file-write appraisers covered evaluation, Revision,
and effect boundaries.

The supervision appraiser covers Program-to-Program appraisal. A child Program's
failed Outcome becomes Datum for a parent Program. The parent Program detects
Disparity, infers restart from a known-good Concept, witnesses the restart
Outcome, and revises its Concept so the worker is Alive again.

This is still not multiprocessing, not a runtime supervisor, and not a
state-machine framework.

## Reference Direction

Truth-maintenance systems are relevant because they preserve justifications for
belief changes. Toulmin-style qualifier, warrant, and backing terminology is
also relevant because Dicta Qualification records basis, conditions, timing, and
strength.

These are design references, not runtime dependencies.
