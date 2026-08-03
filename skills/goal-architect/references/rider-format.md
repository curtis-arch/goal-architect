# Rider format

## Contents

1. [Purpose](#purpose)
2. [Filename and identity](#filename-and-identity)
3. [Core form](#core-form)
4. [Identity rules](#identity-rules)
5. [Obligations and boundaries](#obligations-and-boundaries)
6. [Existing substrate](#existing-substrate)
7. [Execution units](#execution-units)
8. [Closed evidence](#closed-evidence)
9. [Change and completion](#change-and-completion)
10. [Conditional blocks](#conditional-blocks)
11. [Traceability without ceremony](#traceability-without-ceremony)

## Purpose

The rider is the detailed normative execution contract. It may be as large as
the product and risk require. Every prescription must advance an observable
product obligation, protect a material risk/authority boundary, or establish
necessary evidence.

Mutable status, measurements, receipts, commit lists, and reviewer transcripts
do not belong in the rider. Put them in the execution transcript or an existing
project-native run record.

## Filename and identity

```text
<project>/docs/goals/<YYYY-MM-DD>-<HHMM>-<project>-<topic>-rider.md
```

The exact sibling goal uses the same stem with `-goal.md`. The rider cites it
by absolute path. Do not pair a rider to a similar or nearby goal.

Start with these machine-readable labels:

```markdown
# <Project> — <Product outcome> Rider

Pair-ID: `2026-08-02-1540-project-topic`
Goal: `/absolute/project/docs/goals/2026-08-02-1540-project-topic-goal.md`
Execution-root: `/absolute/project`
Source-revision: `<git SHA or explicit non-git state identifier>`
Provenance: `per-unit`
Modules: `none`
Supersedes: `none`
```

Allowed provenance values are `per-unit`, `per-integration`, `per-gate`, and
`none: <reason>`. Modules are the canonical comma-separated names in
[risk-modules.md](risk-modules.md), or `none`.

## Core form

The six semantic blocks below are required information, not six mandatory
headings. The layout shown is the canonical default because it is easy to read,
but blocks may be combined or headings renamed when that improves cohesion.

Keep the machine-readable identity labels, `Product criterion:` and `Current
state:` lines, O/E table rows, `### U*` unit headings, and `existing`/`create`
substrate rows exact so the validator can find them independent of layout. A
small round can keep each block short; a large round can expand it without a
size target.

```markdown
## Product criterion and current state

Product criterion: <user's observable outcome>.

Current state: <concrete HEAD/runtime observation showing what is absent or
failing, its source of truth, and material uncertainty>.

## Obligations and boundaries

| ID | Observable behavior | Surfaces | Evidence | Explicit exclusions |
|---|---|---|---|---|
| O1 | ... | ... | E1, E2 | ... |

## Existing substrate and shortest proof paths

| Status | Path | Reuse/current fact | Used by |
|---|---|---|---|
| existing | `src/existing.ts` | Reuse current parser | O1 / E1 |
| create | `src/new.ts` | Smallest new product surface | O2 |

## Execution units

### U1 — <product or integration boundary>

- Advances: `O1`
- Delivers: <observable behavior or required decision>
- Owns: `src/existing.ts`
- Prerequisite: <state>, because it prevents <named product/risk failure>
- Evidence closed: `E1`
- Depends on: `none`
- Provenance: `pair-id/U1` under the declared cadence
- Stop if: <authority, contradiction, unsafe state, or invalid assumption>

## Closed evidence inventory

| ID | Proves | Level | Existing path/environment | Command or flow | Expected observation | Mock boundary | Addition rule |
|---|---|---|---|---|---|---|---|
| E1 | O1 ... | integrated | `tests/existing.test.ts` | `npm test -- ...` | ... | none | closed |

## Change and completion contract

- Activated bytes are immutable; material change creates a superseding pair.
- New evidence/support requires a named active obligation or reproduced defect
  the existing path cannot establish.
- Qualify once after the final relevant mutation; rerun only for a named trigger.
- Descope preserves sufficient evidence for every retained obligation.
- Final report separates authored/activated, implemented, tested, deployed,
  verified-live, incomplete, and withheld states.
- A post-activation permission unlocks only its exact action, target, and
  prerequisite; every other withheld action remains withheld.
```

## Identity rules

### Pair and source revision

`Pair-ID` equals the filename stem without `-goal`/`-rider`. `Source-revision`
anchors the facts used during authoring. If the project is not Git-backed, use
a stable explicit identifier such as a release version plus observation time;
do not write `latest`.

### Supersession

Before activation, edit and revalidate normally. After activation, never append
status or rewrite authority in place. Create a new timestamped pair and set:

```text
Supersedes: `2026-08-02-1540-project-topic`
```

The new pair states obligation, evidence, authority, and stop deltas. Preserve
the old bytes for auditability.

### Precedence and inheritance

Include this conditional block only when an older goal/rider pair contributes
active obligations or constraints. Named inheritance is valid and efficient.
Name each exact source file, the carried invariant categories, and an explicit
delta. Enumerate individual clauses only when material or ambiguous. Never
inherit external authority implicitly.

```markdown
## Precedence and inherited obligations

| Source | Carried categories | Delta |
|---|---|---|
| `docs/goals/<prior>-rider.md` | product behavior, compatibility | Retire <conflict>; preserve <named category> |
```

Every source path must resolve under `Execution-root` (or be absolute). If no
older contract matters, omit this block entirely; do not emit a `none` ritual.

## Obligations and boundaries

Each `O*` is independently judgeable. The evidence column maps to existing
`E*` rows. Exclusions stop adjacent work from being inferred; they are not a
dumping ground for every imaginable future idea.

When the product criterion changes materially, revise the pair. When only an
implementation assumption is disproved but the active product obligation
remains stable, use the change/exception rule and the smallest valid repair.

## Existing substrate

The substrate table makes reuse concrete and machine-checkable:

- `existing` paths must exist when the pair is authored;
- `create` paths are expected outputs and may not exist yet;
- relative paths resolve under `Execution-root`;
- absolute paths are allowed when a required environment lives elsewhere;
- use current symbols/paths rather than guessed future architecture.

Name the existing environment, fixture, dataset/account, deployment, or flow
that proves every external claim. Do not create a disposable alternate route
because it seems easier to automate.

## Execution units

A unit is earned by a product, dependency, authority, integration, or proof
boundary. It is not required to equal one commit. The declared provenance
cadence controls attribution:

- `per-unit` — each unit has a traceable commit/receipt;
- `per-integration` — related units land together at a named boundary;
- `per-gate` — experimental/deployment work records gate receipts;
- `none: reason` — only when repository/state constraints make commit
  provenance inapplicable.

Do not create fixed plumbing, friendliness, docs, demo, or cleanup units. Add
one only when it delivers an obligation or prevents a named material failure.

Write named behavioral evidence before implementation when it can meaningfully
fail. Red-first testing is not required for research, documentation,
deployment, or configuration-only units.

## Closed evidence

### Authority levels

- `unit` — bounded function/component behavior;
- `integrated` — product surfaces operating together locally;
- `real-boundary` — a real external provider/service/device boundary;
- `deployed` — exact version successfully deployed;
- `verified-live` — post-deploy product observation on the named version.

The level must match the claim. A mock can prove serialized payload or clock
behavior; it cannot prove a required real provider interaction. A successful
deploy command is not verified-live evidence.

### Admission rule

The authored list is closed. Add evidence or support only when all hold:

1. name the active obligation or concrete reproduced defect;
2. show why the existing inventory cannot establish it;
3. show why strengthening/replacing existing evidence is insufficient; and
4. record the smallest addition and reason outside the immutable pair.

A newly discovered product obligation requires a superseding pair, not an
append-only proof program.

### Close once

Run integrated qualification after the final relevant behavior, configuration,
contract, or deployment mutation. Rerun only after:

- another relevant mutation;
- a required environment transition for a distinct claim;
- an inconclusive or demonstrably flaky result; or
- discovery of a distinct unproved obligation.

State the trigger. Do not reopen evidence for reassurance.

### Evidence-journey closure

When one obligation depends on several product surfaces operating together,
trace the shortest material journey through them before closing the inventory.
Include any secondary external effect necessarily reached by the proof action.

At least one evidence flow must traverse every real handoff material to the
claim. Do not infer compatibility by pairing real producer/storage evidence
with a mocked consumer, or infer a safe mutation by proving only its primary
write while omitting storage, email, queue, webhook, or provider side effects.

This rule is claim-shaped, not a universal end-to-end-test requirement. A mock
remains valid for its declared bounded claim. If a composed journey cannot run
at current authority, name the missing gate and withhold the composed claim.

### Descope and cleanup

Before deleting tests, harnesses, telemetry, or implementation, map every
retained obligation to sufficient retained evidence at the correct authority.
There is no universal numeric floor.

## Change and completion

The final report uses literal states and evidence IDs:

```text
Pair: authored / activated (revision)
Implemented: O1, O2
Tested: O1 -> E1; O2 -> E2
Deployed: version + target, or not deployed
Verified live: O2 -> E3, or not verified live
Incomplete: obligation + missing evidence
Withheld: action not taken
```

A spend bound produces an incomplete report unless the achieved condition
already holds. A valid accepted refusal must be defined by the experiment or
safety module and leave the named safe state.

After activation, record a new user permission before the affected action:

```text
Authority delta: <current user instruction anchor>
Authorized now: <exact action + target + necessary prerequisite>
Still withheld: <every adjacent action not granted>
Pair impact: unlocks existing gate / requires superseding pair
```

A transcript delta is sufficient only when it unlocks an existing gate without
changing obligations, evidence authority, target, or completion. Otherwise
author and validate a timestamped superseding pair.

## Conditional blocks

Set `Modules:` and include the exact corresponding headings:

| Module | Required heading |
|---|---|
| `migration` | `## Migration and data integrity` |
| `security` | `## Threat and security` |
| `authority` | `## Authority and irreversible actions` |
| `deploy` | `## Deploy and rollback` (and select `authority`) |
| `experiment` | `## Experiment and refusal` |
| `performance` | `## Performance` |
| `gate` | `## Gate receipts` |
| `mechanical-posture` | `## Mechanical posture` |
| `delegation` | `## Delegation plan` |
| `descope` | `## Descope plan` |
| `verified-live` | `## Verified-live proof` |

Read [risk-modules.md](risk-modules.md) for the fields and triggers. Do not
include a conditional heading with generic filler.

## Traceability without ceremony

Traceability makes execution ranges reconstructable; commit count does not
prove the product. Use the repository's commit convention plus the pair/unit,
integration, or gate identity. Update CHANGELOG, architecture, tickets, demos,
or review artifacts only when the project or product actually requires them.

Do not write status or commit SHAs back into the activated rider. The transcript
or existing run record holds mutable provenance.
