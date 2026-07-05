# Semantic Test Matrix 000

This document records the semantic coverage proven by the current hard-coded
Dicta demos.

## Foundation Chain

A Datum is given.

A Dictum says.

A Qualification tells how the Dictum stands.

A Concept holds qualified Dicta.

A Purpose gives the Concept direction.

A Disparity reveals what does not fit under that Purpose.

An Inference derives what follows.

An Outcome witnesses what actually followed.

A Revision changes what the Program now holds.

A Program carries the whole motion forward.

## Current Demos

| Demo | Command | Scenario | Proves |
| --- | --- | --- | --- |
| Arithmetic success | `dicta demo` | `3 + 4` | Valid Datum can be appraised into qualified Dicta, derive an Inference, witness Outcome, and record Revision. |
| Invalid arithmetic | `dicta invalid-demo` | `3 + "cat"` | A well-received Datum can fail Qualification under Purpose, produce Disparity, and be refused without becoming a host-language exception first. |
| Counter revision | `dicta counter-demo` | `counter = 0; counter = counter + 1` | Mutation can be represented as qualified Revision to a Concept. |
| File write effect | `dicta file-write-demo` | `write report.txt "hello"` | World-changing effects can be represented as intended Outcomes with Permission and Disk-change Dicta without performing the real effect. |
| Refused file write effect | `dicta refused-file-write-demo` | `write protected/report.txt "hello"` | A well-formed effect can be refused because Permission does not qualify, preserving Disk unchanged. |
| Supervised worker failure | `dicta supervised-worker-demo` | worker crashes, supervisor restarts from known-good Concept | Failure can be represented as Outcome becoming Datum for a parent Program, allowing supervised recovery. |
| AI agent edit accepted | `dicta agent-edit-demo` | agent proposes behavior-preserving edit | Agent output enters as Datum and becomes accepted Revision only after Qualification. |
| AI agent edit refused | `dicta refused-agent-edit-demo` | agent proposes behavior-changing edit | Agent output can be refused when it violates Purpose or fails Qualification. |

## Design Conclusion

The first Dicta scaffold proves that the semantic chain can represent success,
invalidity, mutation, effects, permission refusal, supervision, and AI-agent
appraisal before parser or compiler work begins.

These demos are hard-coded semantic proofs, not language syntax. The next
implementation step should preserve this distinction.
