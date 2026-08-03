# Worked execution shapes

## Contents

1. [How to use these](#how-to-use-these)
2. [Focused bug fix](#focused-bug-fix)
3. [Ticket or behavior closure](#ticket-or-behavior-closure)
4. [POC completion](#poc-completion)
5. [Experiment-gated round](#experiment-gated-round)
6. [Migration](#migration)
7. [Long program round](#long-program-round)
8. [Shape selection check](#shape-selection-check)

## How to use these

These are non-exhaustive presets, not round types or validator schemas. Copy a
shape only after confirming the product criterion, authority, risk, evidence
level, and actual dependency boundaries. Add, remove, or reorder units when
the product earns it.

## Focused bug fix

Profile:

- one concrete reproduced failure;
- existing product surface and proof path;
- no new external authority;
- achieved stop;
- usually no conditional module.

Typical earned boundaries:

1. reproduce and pin the failure with the smallest relevant existing test/flow;
2. implement the product repair;
3. run one integrated qualification after the final mutation.

Do not add a general retry/fallback/diagnostic framework unless the reproduced
failure establishes that need.

## Ticket or behavior closure

Profile:

- several independently judgeable requested behaviors;
- existing architecture largely remains;
- proof maps one-to-one or many-to-one to the closure items;
- external ticket changes require `authority`; they do not trigger `deploy`
  unless an actual deployment/release is also in scope.

Use one obligation per behavior that can independently close. Build execution
units by dependency/integration, not by ticket count. Update external trackers
only with current authority and after the corresponding evidence closes.

## POC completion

Profile:

- finish, measure, and decide the fate of a bounded proof of concept;
- minimal permanent architecture;
- fixed trial envelope;
- `experiment` and possibly `verified-live` modules.

Keep the POC fence explicit. Success includes the named completion/decision,
not an implied production replatform. Refusal/removal is valid only if defined
and evidenced.

## Experiment-gated round

Profile:

- hypothesis may pass or conservatively refuse;
- fixed baseline/sample/acceptance bounds;
- later work/action locked behind a gate;
- `experiment`, `performance`, and/or `gate` modules.

Typical earned boundaries:

1. establish vocabulary/baseline on the named existing path;
2. run the fixed experiment;
3. evaluate pass/refusal/inconclusive without moving the oracle;
4. perform only the action authorized by the result.

Record unanswered ideas in the future-experiment ledger instead of silently
expanding trials.

## Migration

Profile:

- durable data/schema/format changes;
- preservation, collision, rollback, ordering, and partial-failure risks;
- `migration`, plus `authority` for external mutation, often `deploy`, and
  sometimes `verified-live`.

Typical earned boundaries follow safety dependencies: preflight/collision
policy, reversible transformation, application compatibility where current
states require it, post-state proof, deployment/rollback, and smallest live
verification. Feature-first means earliest safely usable migrated product, not
reckless behavior before data safety.

## Long program round

Profile:

- broad product outcome with multiple independently owned surfaces;
- shared contracts must freeze before parallel writers;
- gates/checkpoints based on material integration or authority events, not an
  elapsed timer;
- `delegation` plus risk modules selected per surface.

The lead owns the global obligation/evidence map and integration. Delegates
receive exact revision, bounded ownership, return schema, verification, and
stop conditions. Use per-unit, per-integration, or per-gate provenance so the
large execution remains reconstructable. Do not equate a large rider, proof
program, diff, or agent count with drift.

## Shape selection check

Before using a preset, answer:

- What user-visible/system-visible product state defines success?
- Which prerequisites prevent a named safety/authority failure?
- What existing proof path is shortest and valid?
- What evidence authority does each obligation require?
- Which work is semantically independent rather than merely separable by file?
- What is the truthful non-success stop state?

If the preset adds an item that cannot answer one of those questions, remove
it. If none fits, author a new profile directly.
