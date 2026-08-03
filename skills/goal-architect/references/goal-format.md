# Goal format

## Contents

1. [Purpose](#purpose)
2. [Filename](#filename)
3. [Required form](#required-form)
4. [Section rules](#section-rules)
5. [Stop shapes](#stop-shapes)
6. [Headroom and trimming](#headroom-and-trimming)
7. [Condensed examples](#condensed-examples)

## Purpose

The goal is the compact completion condition repeatedly seen by the executing
lead/evaluator. It carries stable product obligations, material authority and
constraints, evidence mappings, and truthful stop semantics. Execution detail
lives in the rider.

Claude documents a 4,000-character `/goal` bound. This package enforces at most
4,000 UTF-8 bytes as a conservative cross-harness contract, including when the
condition contains non-ASCII text. It is not a target for rider size.

## Filename

```text
<project>/docs/goals/<YYYY-MM-DD>-<HHMM>-<project>-<topic>-goal.md
```

The rider uses the identical stem with `-rider.md`. Reserve the stem before
writing either file. Use the project's established goal directory when it has
one; otherwise ask or use `docs/goals/`.

## Required form

Use these exact bold labels so the validator and evaluator can locate the
contract. Replace every angle-bracket marker; shipped pairs contain no template
markers, `TODO`, or `TBD`.

```markdown
GOAL: <current concrete absence/failure -> one observable product end state>.

**Pair and read first.**

- `<absolute path to exact sibling rider>`
- `<other load-bearing existing path, only when needed>`

**Product obligations.**

- `O1` — <observable product behavior>.
- `O2` — <observable product behavior>.

**Boundaries and authority.** Preserve: <behavior that must survive>. External actions:
<allowed action + exact target + gate/recovery, or `none authorized`>. Withheld:
<specific actions, or `none`>.

**Execution constraint.** Land the earliest usable integrated slice. Reuse the
named proof path. Add support machinery or proof only for a named active
obligation or concrete reproduced defect the existing path cannot establish.

**Evidence.**

- `O1 -> E1, E2`
- `O2 -> E3`

Surface the named results after the final relevant behavior/configuration
change.

**Stop when** every active obligation has its mapped evidence at the required
authority and no withheld action was taken. <Optional accepted-refusal clause.>
At <turn/time bound>, report delivered and missing obligations; do not call the
goal complete.
```

## Section rules

### GOAL

State the user's product outcome and the observed current gap. Do not substitute
tests, files, phases, documentation, coverage, or process for the product.

### Pair and read first

Always cite the exact rider by absolute path. Add only sources the executing
lead must retain on every continuation. Longer research and source inventories
belong in the rider.

Every listed read-first path must already exist. Expected outputs belong in the
rider and are marked `create`; do not put nonexistent outputs here.

### Product obligations

Use plain sequential IDs: `O1`, `O2`, ... . An obligation describes one
observable behavior or required product decision. It is not a phase or test.

Keep the set sufficient, not artificially small. Split an obligation when its
parts can independently pass/fail or require different proof authority.

### Boundaries and authority

State only material constraints under the explicit `Preserve:` label. Replace
boilerplate `No git push` with current
authority: exact action, target, gate, recovery, and what remains withheld.
User authorization can change between rounds; do not inherit it implicitly.

### Execution constraint

Keep this compact drift control in the goal. Detailed admission and proof rules
live in the rider. It prevents optional scaffolding from becoming the product.

### Evidence

Map every `O*` to one or more rider `E*` entries. Detail such as commands,
fixtures, environments, and expected observations stays in the rider.

The evaluator needs transcript-visible results. A path, manifest, successful
edit, worker summary, deploy command, or `done` assertion is not evidence by
itself.

### Stop when

Success requires every active obligation and named evidence. Separate a spend
bound from success. If the bound fires, report partial state rather than
manufacturing completion.

## Stop shapes

### Achieved

Use for ordinary feature/migration/closure rounds:

```text
Stop when O1-O4 have E1-E7, the deployed claim has verified-live E7, and no
withheld action occurred. At 20 turns report remaining obligations without
calling complete.
```

### Accepted refusal

Use only when conservative refusal is itself an intended result:

```text
Stop when either the experiment satisfies O1-O3 with E1-E5 or the refusal gate
records the specified unsafe/insufficient signal as E6 and leaves production
unchanged.
```

The refusal evidence and safe state must be precise. `Could not finish` is not
accepted refusal.

### Bounded incomplete

Use when external state or spend must bound the run:

```text
At 15 turns, stop further work and report achieved obligations, missing
obligations, exact evidence absent, and the authority/state change needed.
Do not mark the goal complete unless the achieved condition already holds.
```

## Headroom and trimming

The validator reports bytes and remaining headroom. IDs must remain plain and
short. Provenance narration, ticket lists, reviewer transcripts, status,
measurements, phase text, and design prose never colonize the goal.

Trim in this order:

1. descriptions of read-first paths;
2. explanation already present in the rider;
3. repeated boundary prose;
4. evidence detail beyond `O -> E` mappings.

Do not trim product obligations, material authority, or truthful stop
semantics. If those do not fit, the product round may require a scoped split.

## Condensed examples

### Feature with real-boundary proof

```markdown
GOAL: Make flight-import recovery return the user to an actionable itinerary
without losing already recovered legs; today a partial provider response can
strand the flow.

**Pair and read first.**
- `/repo/docs/goals/2026-08-02-1540-app-flight-recovery-rider.md`
- `/repo/src/import/recover.ts`

**Product obligations.**
- `O1` — A partial response preserves every recovered leg and labels the gap.
- `O2` — Retry resumes from the unresolved provider boundary without duplicate legs.
- `O3` — The existing staging journey completes recovery on a real provider sample.

**Boundaries and authority.** Preserve: provider ordering and current schema.
External actions: deploy the named staging worker after local evidence. Withheld:
production deploy and schema mutation.

**Execution constraint.** Land the earliest usable integrated slice. Reuse the
named staging journey. Add support machinery or proof only for an active
obligation or reproduced defect the existing path cannot establish.

**Evidence.**
- `O1 -> E1`
- `O2 -> E2, E3`
- `O3 -> E4`

**Stop when** O1-O3 have E1-E4 after the final staging mutation and no withheld
action occurred. At 12 turns report missing obligations without calling complete.
```

### Why size is not the control

A security round may have four obligations and ninety distinct threat-mapped
evidence entries in the rider. A bug fix may have one obligation and two
entries. Both are valid. The goal stays compact because it maps the product,
not because the rider or proof program is small.
