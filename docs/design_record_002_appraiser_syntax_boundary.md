# Design Record 002: Appraiser/Syntax Boundary

Dicta's current kernel appraises structured Datum, not source text.

A parser, when added later, will only be one producer of structured Datum. The
semantic layer must remain independent from syntax.

## 1. What Has Been Proven

The current kernel can mechanically produce Program chains for:

- Accepted evaluation
- Refused evaluation
- Accepted Revision
- Refused Revision
- Accepted effect
- Refused effect
- Supervised recovery

This proves that structured Datum can be appraised into the semantic chain:

Datum -> Dictum -> Qualification -> Concept -> Purpose -> Disparity -> Inference
-> Outcome -> Revision -> Program

## 2. What Has Not Been Proven

No source syntax exists yet.

No parser exists yet.

No compiler exists yet.

No VM exists yet.

No lowering exists yet.

No real IO occurs.

No real process supervision occurs.

No general interpreter exists yet.

## 3. Why This Boundary Matters

If syntax is added too early, Dicta risks becoming another surface-language
experiment.

The foundation is semantic appraisal. Syntax should feed the semantic layer, not
define it.

## 4. Future Parser Rule

A future parser must produce structured Datum that appraisers can consume.

It must not bypass Datum, Dictum, Qualification, Concept, Purpose, Disparity,
Inference, Outcome, Revision, and Program.

## 5. Future Syntax Rule

Surface syntax must stay simple, but its meaning must lower into explicit
semantic records.

For example, future source like:

```text
3 + 4
```

should become structured arithmetic Datum before appraisal.

Future source like:

```text
counter = counter + 1
```

should become structured counter-revision Datum before appraisal.

## 6. No-Costume Warning

The semantic vocabulary should not be forced onto every surface expression.

Users should not have to write Datum, Dictum, Qualification, Concept, Purpose,
Disparity, Inference, Outcome, Revision, and Program in normal code.

Those are the kernel's semantic records, not mandatory surface ceremony.

## 7. Next Implementation Direction

Before parser work, add a small Datum normalization layer or structured Datum
registry only if the current appraisers need it.

Do not implement source syntax until there is a clear mapping from source forms
to structured Datum.

## Structured Datum Routing

Routing is not parsing.

`appraise_structured_datum()` receives already-structured Datum and dispatches
it to the matching mechanical appraiser.

A future parser may produce these structured Datum forms, but parser work
remains deferred. The router does not read source text, infer syntax, compile,
lower, or execute.
