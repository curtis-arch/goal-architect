# Risk modules

## Contents

1. [Selection rule](#selection-rule)
2. [Migration and data integrity](#migration-and-data-integrity)
3. [Threat and security](#threat-and-security)
4. [Authority and irreversible actions](#authority-and-irreversible-actions)
5. [Deploy and rollback](#deploy-and-rollback)
6. [Experiment and refusal](#experiment-and-refusal)
7. [Performance](#performance)
8. [Gate receipts](#gate-receipts)
9. [Mechanical posture](#mechanical-posture)
10. [Delegation plan](#delegation-plan)
11. [Descope plan](#descope-plan)
12. [Verified-live proof](#verified-live-proof)
13. [Oracle-integrity clauses](#oracle-integrity-clauses)

## Selection rule

Select a module only when its trigger exists. Add its canonical name to the
rider's `Modules:` label and include its exact heading. The validator checks
declared modules, not guessed prose.

| Module | Trigger |
|---|---|
| `migration` | Existing durable data/schema/format changes or rollback/compatibility risk |
| `security` | Authentication, authorization, secrets, untrusted input, isolation, or named threat |
| `authority` | Any external mutation, push, message, deletion, or irreversible action |
| `deploy` | A deploy, release, rollout, or environment transition is in scope |
| `experiment` | Success may legitimately be a measured refusal/no-go decision |
| `performance` | Latency, throughput, resource use, or timing is an obligation |
| `gate` | Later work/actions are forbidden until machine-checkable evidence holds |
| `mechanical-posture` | Scope/shape invariants must be proven against mutation or generated output |
| `delegation` | Two or more semantically independent tasks are intentionally delegated |
| `descope` | Partial delivery, cleanup, or removal could strand a retained obligation without proof |
| `verified-live` | The stop condition requires post-deploy real-world observation |

The list is extensible. A new module must be justified by a recurring material
risk that the core rider cannot express cleanly. Do not add one because a
single pair has unusual prose.

## Migration and data integrity

Use heading `## Migration and data integrity`.

Include:

- source and destination representations;
- preconditions and collision/invalid-data policy;
- forward, rollback, retry/idempotency, and partial-failure semantics;
- exact version/order of schema and application changes;
- preservation invariants and data-loss refusal;
- representative production-shaped fixture or real-boundary proof; and
- post-state queries/observations tied to `E*`.

Do not invent compatibility layers for callers/data that do not exist. Name
the real current states that require compatibility.

## Threat and security

Use heading `## Threat and security`.

Map each security control and evidence entry to a named threat or trust
boundary. Include:

- actors, assets, trust boundaries, and attacker capability;
- allow/deny/refusal matrix;
- authentication/authorization ordering;
- secret handling and logging constraints;
- replay, confused-deputy, cross-tenant, escalation, and fail-open risks when
  applicable; and
- evidence authority required for every threat claim.

Large threat-mapped proof programs are valid. Do not cap them by count. Do not
add generic security scaffolding without a named threat.

## Authority and irreversible actions

Use heading `## Authority and irreversible actions` for any external or
irreversible action, including a repository push, tracker mutation, message,
deletion, data mutation, or deploy. This module grants nothing; it records the
current user authority precisely.

Authority table:

| Action | Exact target | Authorized by/current scope | Gate | Recovery | Withheld |
|---|---|---|---|---|---|
| ... | ... | ... | E... | ... | ... |

Never infer authority from repository access, prior rounds, or another agent's
message. A tracker update or Git push does not trigger deployment machinery.

After activation, a narrow new permission may unlock an already-authored gate
when the transcript records the current instruction, exact action/target and
prerequisites, and every adjacent action still withheld. If the permission
changes an obligation, evidence authority, target, or completion state, create
and validate a superseding pair. A deploy permission never silently includes a
database, Git push, another service, or another provider.

## Deploy and rollback

Use heading `## Deploy and rollback` only for an actual deploy, release,
rollout, or environment transition. Select `authority` as well.

Include exact version provenance, target ordering, preflight,
rollback/recovery, abort thresholds, and separate `deployed` versus
`verified-live` evidence.

## Experiment and refusal

Use heading `## Experiment and refusal`.

Define:

- hypothesis and current baseline;
- fixed sample/trial envelope;
- instrumentation/reuse path;
- acceptance bounds and conservative refusal condition;
- safe state after either outcome;
- evidence that distinguishes pass, refusal, and inconclusive result; and
- a future-experiment ledger for unanswered questions outside this round.

Refusal is success only when the pair defines it and the evidence demonstrates
the named unsafe/insufficient signal. Inconclusive is not refusal.

## Performance

Use heading `## Performance`.

Define timing vocabulary before instrumentation:

- clock boundaries and inclusions/exclusions;
- workload/dataset, concurrency, warmup, and environment;
- baseline and target statistic;
- sample size and aggregation;
- instrumentation overhead budget; and
- regression/abort threshold.

Never label a tiny sample as a percentile it cannot estimate (`n=3` is not
p95). A single happy-path RSS/latency observation does not prove a population
claim.

## Gate receipts

Use heading `## Gate receipts`.

For each gate, state:

- obligations/evidence required;
- machine-checkable lock or exact receipt form;
- actions forbidden before it closes;
- authority after it closes; and
- reset/reopen condition after relevant mutation.

Do not solve a failed gate by emitting synthetic evidence, weakening the
oracle, or skipping the locked action.

## Mechanical posture

Use heading `## Mechanical posture`.

Use when a shape constraint is material enough to prove mechanically. Examples:

- hash/tree baseline for no-edit zones;
- generated-artifact parity;
- allowed-path or dependency boundary;
- data-shape preservation; and
- exact version binding.

State what failure the mechanism prevents. Do not introduce a hash/manifest
system merely to prove the skill's own process.

## Delegation plan

Use heading `## Delegation plan`.

The durable contract names capability and ownership, not provider, pane,
model, or tmux window. Include:

| Task | Semantically independent because | Inputs/revision | Allowed ownership | Return/evidence | Stop if |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... |

Freeze shared interfaces first. Read-heavy discovery can share a checkout;
concurrent writers require disjoint ownership or separate worktrees. The lead
owns integration and final evidence. Headless agents are fallback automation,
not the default when native subagents exist.

## Descope plan

Use heading `## Descope plan` when partial delivery, cleanup, or removal is
plausible enough to strand a retained obligation without adequate proof.

```markdown
| Retained obligation | Surviving evidence | Required authority | Removal boundary | Stop if |
|---|---|---|---|---|
| O1 | E1 | integrated | Remove only the alternate harness | E1 no longer proves O1 |
```

Name the proof coverage that survives before deletion begins. Do not preserve
a numeric test floor; preserve sufficient evidence at the authority of every
retained claim. If cleanup changes the product criterion or removes an active
obligation, create a superseding pair.

## Verified-live proof

Use heading `## Verified-live proof`.

Name:

- exact deployed version and target;
- real account/device/provider/dataset;
- smallest sample/control cases sufficient for the claim;
- expected observation and evidence capture;
- cleanup/recovery; and
- what remains merely deployed or locally tested.

Do not expand live sampling after the fixed cases prove the claim unless a
distinct defect/obligation requires it.

## Oracle-integrity clauses

Select only clauses matching an active risk:

- Never widen or rewrite the oracle merely to make a check pass.
- Tests/evidence are never deleted to manufacture success; during cleanup map
  retained obligations to retained proof first.
- Synthetic events, mocks, or fixtures cannot satisfy a required real-boundary
  claim.
- `n=3` must not be labeled p95.
- A single happy-path resource observation is not population evidence.
- An agent, worker, review, manifest, or tool saying `done` is not evidence.
- Do not narrate agent procedure as if it were product acceptance.

Do not paste every clause into every rider. Untriggered anti-gaming boilerplate
is process noise.
