---
name: goal-architect
description: Architect a compact /goal objective and detailed rider for substantial autonomous coding work by grounding the user's product criterion in repository evidence, closing every obligation with proportionate proof, and using bounded native subagents only for semantically independent research. Use when the user asks to create, draft, revise, validate, or hand off a Claude Code or Codex goal/rider pair. Do not use to implement the feature itself or for a tiny change that does not need a durable execution contract.
---

# Goal Architect

Create two normative files for one substantial round:

- a goal of at most 4,000 bytes containing the product completion condition;
- an unbounded rider containing the execution contract and closed evidence.

Goal Architect accelerates evidence gathering, not judgment or prose. One lead
owns the product criterion, resolves conflicts, authors both files, validates
the pair, and remains accountable for every claim. Better does not mean
smaller; retain detail serving an obligation, material risk, authority boundary,
or necessary proof.

Resolve the skill root as the directory containing this `SKILL.md`. Invoke
bundled scripts from that root; never assume the user's project is the skill
directory.

## Read the bundled contract

Read these before authoring:

1. [references/goal-format.md](references/goal-format.md)
2. [references/rider-format.md](references/rider-format.md)
3. [references/worked-shapes.md](references/worked-shapes.md)
4. [references/provider-subagents.md](references/provider-subagents.md)

Read [references/risk-modules.md](references/risk-modules.md) only for modules
triggered by the round's risk/profile. Read
[references/harness-behavior.md](references/harness-behavior.md) before
handoff or whenever the user asks how Claude, Codex, or a coordinator should
run the pair. Read the receipt schemas only when preparing or diagnosing
machine-readable receipts.

## 1. Establish the product criterion in the main context

Before delegation, state one observable product end state and the concrete
current absence or failure. Preserve the user's criterion; do not replace it
with test count, coverage, file count, documentation, or process completion.

Record the current user authority and the decisions that cannot be delegated.
Ask only when a missing decision materially changes the product, authority, or
irreversible outcome. Otherwise inspect and proceed.

## 2. Find prior pairs rider-first

Find `*-rider.md` first. Treat a file as prior output of this skill only when
the exact same directory and filename stem has its sibling `*-goal.md`. Ignore
naked goals and generated benchmark copies unless the user places them in
scope.

Read the most relevant exact pairs. When inheriting behavior, name the source
pair and carried invariant categories and explicitly retire or override
conflicts. Never delegate “find some prior goals” without the rider-first and
exact-sibling rule.

## 3. Decide whether parallel discovery is earned

Use parallel discovery only when at least two bounded investigations are both:

- semantically independent until their receipts return;
- read-heavy or isolated to exclusive output files/worktrees;
- grounded in named roots, sources, and a shared revision;
- useful to distinct product, risk, architecture, history, or proof questions;
  and
- cheap to reconcile through exact citations.

Good examples are independent code-surface mapping, relevant goal/session
history, external/provider constraints, current test/proof substrate, and
migration/runtime risk. Keep work direct when the task is small, sequential,
same-file, or depends on a single evolving interpretation. Parallelism is not
a completeness or agent-count requirement.

Do not delegate the product criterion, final scope, obligation/evidence design,
authority decision, final goal/rider prose, or completion judgment.

## 4. Dispatch bounded native subagents

Use the current provider's native subagent tools. Do not start headless Claude
or Codex processes unless the user explicitly requests non-interactive
automation or native delegation is unavailable and the user authorizes the
alternative.

Each assignment packet must name:

- `assignment_id` and one concrete question;
- execution/source revision and allowed read roots;
- specific inputs/sources and excluded areas;
- allowed writes and exact exclusive output path, normally only one receipt;
- prohibited external, irreversible, or implementation actions;
- required fact/citation and conflict/open-decision return shape;
- verification the worker must perform; and
- a `stop_if` condition for stale state, contradiction, or missing authority.

Use [references/provider-subagents.md](references/provider-subagents.md) for
the packet and receipt forms. Workers write inside the designated project
directory, not `/tmp`, and preserve user-owned changes. Two workers never own
the same file or mutable checkout.

## 5. Compile receipts without interpretation

Validate and compile returned receipts deterministically:

```bash
python3 <goal-architect-root>/scripts/compile_receipts.py \
  --root <execution-root> \
  --output <project-artifact-dir>/evidence-dossier.json \
  <receipt-1.json> <receipt-2.json> ...
```

The compiler verifies schemas, a shared frozen source revision, and cited line
hashes; it sorts and deduplicates exact facts and preserves conflicts, limits,
and open decisions with provenance. It does not summarize, choose a winner,
certify truth, or accept a product claim.

The compiler rejects malformed receipts, uncited facts, stale hashes, path
escapes, and recorded actions. During reconciliation, the lead also rejects or
reissues receipts whose declared scope exceeds the original assignment packet;
the compiler cannot authenticate that packet. A worker saying `done` is not
evidence.

Do not grow either receipt schema for convenience. Change a schema only in
response to a named failing benchmark fixture or validator defect, preserve the
failure as a test, and bump its version when compatibility changes.

The lead reads the bounded dossier and only the underlying citations needed to
resolve conflicts, ambiguity, or material decisions. Keep receipts/dossiers
outside the normative pair and outside the main transcript when their raw bulk
does not help judgment.

## 6. Ground one cohesive contract

The lead reconciles the dossier with current repository instructions, dirty
state, architecture, affected symbols/surfaces, runtime/deployment environment,
and user authority. Re-check material facts that conflict, have stale source
revision, or determine an irreversible action.

Inventory existing substrate before proposing new code. Name the shortest
already-valid proof path for every external claim.

Close each material evidence journey before freezing the inventory. Trace the
observable claim across the producer, durable state, transport, consumer, and
external side effects that the proof action actually reaches. Separate evidence
rows do not compose merely because each passes: at least one named flow must
cross every real boundary material to the claim. If current authority cannot
safely cross a required boundary, withhold that composed claim or name its gate
instead of replacing it with a mock. This is not a demand for end-to-end proof
for every obligation; apply it only where correctness depends on the
composition.

Assign plain short IDs:

- `O1`, `O2`, ... for independently judgeable product obligations;
- `E1`, `E2`, ... for evidence at the necessary authority; and
- `U1`, `U2`, ... for earned execution units.

Declare external/irreversible authority, evidence authority, provenance
cadence, semantic independence available during execution, achieved versus
accepted-refusal versus bounded-incomplete stop shape, and only triggered risk
modules.

## 7. Write the rider, then project the goal

Reserve one shared timestamp/stem. Write the rider from the reconciled
obligation/evidence ledger, then write the compact goal as its stable
evaluator-facing projection. The rider may be large and must read as one
contract, not stitched worker prose.

Execution units are earned by product, dependency, authority, integration, or
proof boundaries. Do not generate plumbing, friendliness, documentation, demo,
or CHANGELOG units because a template has room.

If parallel implementation is appropriate, the rider's `delegation` module
names only semantically independent units, exclusive ownership, integration
order, and main-agent proof responsibility. It does not require parallel
execution.

### Optional disjoint module drafting

This is separate from evidence receipts and is never required. Only after the
lead freezes the product criterion, O/E ledger, shared interfaces, authority,
and module boundaries may workers draft disjoint triggered conditional modules
into exclusive fragment files or separate worktrees. Each packet names the
exact required heading, allowed references/exports, output file, and conflicts
that must return to the lead.

Workers do not draft core rider blocks or goal prose. Their fragments remain
non-normative inputs: do not concatenate them mechanically into the rider. The
lead reconciles and integrates their meaning, reads the rider as a whole,
resolves cross-module conflicts, projects the goal, and runs the shared pair
validator.

## 8. Enforce feature-first drift controls

- Land the earliest usable integrated product slice after only necessary
  safety and authority prerequisites.
- Treat measurement as the feature when measurement is the requested product.
- Admit a guard, cache, retry, fallback, alternate mode, abstraction,
  diagnostic surface, test, fixture, mock, harness, simulator, telemetry, or
  process only for a named active obligation or concrete reproduced defect the
  existing path cannot establish.
- Prefer strengthening or replacing existing evidence before adding a proof
  shape.
- Use mocks only for the bounded claim they can prove; never substitute them
  for required real-boundary or live evidence.
- Do not infer a composed producer-to-consumer claim from separate real-state
  and mocked-consumer checks that never traverse the actual handoff.
- Run integrated qualification after the final relevant mutation. Repeat only
  after a later relevant mutation, required environment transition,
  inconclusive/flaky result, or distinct newly discovered obligation.
- During descope or cleanup, retain sufficient evidence at the correct
  authority for every active obligation.

## 9. Validate, freeze, and hand off

Run:

```bash
python3 <goal-architect-root>/scripts/validate_pair.py <goal-file> <rider-file>
```

Fix every failure. Warnings are review prompts. The validator reports goal
headroom and emits a bounded activation manifest; it does not judge product
quality or impose rider, phase, test, file, commit, agent, or duration counts.

The pair may change before activation; revalidate after every edit. Once
activated, its bytes are immutable. A material correction or authority/scope
change creates a timestamped superseding revision updating obligations,
evidence, authority, and stop state together. Receipts, dossiers, status, and
review transcripts remain outside the normative pair.

Before calling a pair activation-ready, reconcile every mandatory evidence flow
with current authority. Obtain the exact action/target authority first or state
that execution is expected to pause at the named gate.

After activation, treat new user permission as an exact authority delta before
the affected action. Quote the current instruction; enumerate the exact action,
target, prerequisites, and which previously withheld actions remain withheld.
A narrow permission that only unlocks an existing gate may live in the
execution transcript. If it changes an obligation, evidence authority, target,
or completion state, create and validate a superseding pair. Never infer Git
push, another provider mutation, or a broader release from permission to deploy
one named target, and never revive permissions from an earlier goal or
compacted history.

Before implementation, the executing lead must read both files, validate and
surface the manifest, check for another active goal, activate the exact revision
using the provider-native form, and retain integration/final-evidence
ownership. Do not activate or implement when the user asked only for authoring.

Return the goal/rider paths, validation result, selected modules, goal
headroom, material conflicts resolved, and unresolved decisions. Do not report
subagent choreography as the result.

## Non-negotiable distinctions

- Authored is not activated.
- Implemented is not tested.
- Tested locally is not deployed.
- Deployed is not verified live.
- A compiled receipt is not an accepted product claim.
- A time/turn bound limits spend; it does not convert partial delivery into
  success.
- A companion skill or reviewer can inform implementation; only named product
  evidence closes an obligation.
