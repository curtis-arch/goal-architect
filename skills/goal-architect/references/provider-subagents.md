# Provider subagents and evidence receipts

## Contents

1. [Purpose](#purpose)
2. [Independence test](#independence-test)
3. [Main-agent responsibilities](#main-agent-responsibilities)
4. [Assignment packet](#assignment-packet)
5. [Receipt contract](#receipt-contract)
6. [Citation integrity](#citation-integrity)
7. [Claude Code execution](#claude-code-execution)
8. [Codex execution](#codex-execution)
9. [Writes, worktrees, and permissions](#writes-worktrees-and-permissions)
10. [Compilation and reconciliation](#compilation-and-reconciliation)
11. [Failure and stop conditions](#failure-and-stop-conditions)
12. [Examples](#examples)

## Purpose

Parallel discovery should remove high-volume reading from the main context
without fragmenting product judgment. Workers return small, mechanically
grounded receipts. One main agent owns the question, resolves conflicts, and
authors the cohesive goal/rider pair.

The receipt compiler is deliberately lossless and unintelligent. It can prove
that a cited byte range still matches a receipt. It cannot prove that a fact is
relevant, correctly interpreted, sufficient, or current outside that source.

## Independence test

Delegate only when at least two assignments can proceed without consuming the
other's unpublished interpretation. Before spawning, answer yes to all:

- Does each assignment have one distinct question?
- Can its input roots and sources be named now?
- Can its result be expressed as cited facts, conflicts, and open decisions?
- Can workers finish without editing the same file or mutable checkout?
- Can the main agent reconcile the results without replaying every transcript?
- Does parallel work save meaningful elapsed time or main-context volume?

Good independent slices include:

- affected code and architectural substrate;
- exact rider/goal history and its source revisions;
- scoped session-history evidence for prior drift;
- current tests, fixtures, and real-boundary proof paths;
- migration/data constraints;
- provider/runtime documentation; and
- independent competing failure hypotheses.

Do not parallelize a small scan, an evolving product decision, final scope,
obligation/evidence design, tightly coupled same-file reasoning, final prose,
or completion judgment. If one worker must wait for another's conclusions, the
work is sequential even if the tools permit concurrency.

## Main-agent responsibilities

Before delegation, the main agent fixes:

- the user's literal product criterion and current failure/absence;
- the execution root and source revision;
- current user-owned dirty-state facts;
- external and irreversible authority;
- the questions worth answering;
- allowed roots and writes; and
- the reconciliation and stop conditions.

The main agent remains responsible for checking repository instructions,
choosing relevant prior pairs rider-first, rechecking material conflicts,
designing O/E/U mappings, authoring both normative files, validating them, and
truthfully reporting unresolved decisions.

Do not outsource ambiguity by asking a worker to “figure out the goal.”

## Assignment packet

Use this bounded shape in the native spawn/delegation prompt:

```text
assignment_id: A-code-surface
objective: Map the existing code paths and shortest proof substrate for <one question>.
source_revision: <git SHA or stable non-git identifier>
execution_root: /absolute/project
read_roots:
  - /absolute/project/src/relevant
inputs:
  - src/relevant/entry.ts
excluded:
  - unrelated packages
allowed_writes:
  - docs/goals/evidence/<pair-id>/A-code-surface.receipt.json
actions:
  implementation: forbidden
  external: forbidden
  irreversible: forbidden
return: receipt schema v1 with cited facts, conflicts, and open decisions
verify: validate every cited path/range at source_revision before returning
stop_if: revision changed, required source is outside roots, or authority is unclear
```

Use exact paths and real constraints. “Inspect the repo” is not a bounded
assignment. `allowed_writes` normally contains one receipt path inside the
project's designated artifact directory. Do not use `/tmp` or an unrelated
private folder.

Workers are not alone in the repository. They preserve user-owned changes and
do not revert, delete, overwrite, deploy, send messages, modify remote state,
or install dependencies unless the assignment explicitly authorizes the exact
action and target.

## Receipt contract

Read [research-receipt.schema.json](research-receipt.schema.json) when creating
or debugging a receipt. A receipt contains:

- `schema_version`;
- stable `receipt_id`, packet `assignment_id`, and `source_revision`;
- `status` plus exact `limitations` (`partial`/`blocked` requires at least one);
- `scope.roots` and `scope.sources`;
- exact `facts` with source citations;
- `conflicts` that the main agent must resolve;
- `open_decisions` that evidence cannot decide; and
- `actions.implementation`, `actions.writes`, and `actions.external`.

All three action arrays remain empty. The only permitted write is emitting the
receipt itself to the packet's exact `allowed_writes` path; do not record that
artifact emission as a research action. Any implementation, external action,
or other write invalidates the receipt. An empty action array is a claim about
what the worker did, not retroactive permission.

Facts are narrow observations, not prescriptions or summaries. Prefer:

```text
`parseConfig` calls `loadDefaults` before applying workspace overrides.
```

Avoid:

```text
The configuration architecture is good and should probably be preserved.
```

Every material fact has at least one citation. Put disagreement between
sources in `conflicts`; do not silently choose one. Put decisions requiring
product or authority judgment in `open_decisions`; do not convert them into a
worker recommendation presented as fact.

The receipt `source_revision` must exactly match the packet's stable revision.
Use `limitations` for the precise obstacle, unavailable source, or bounded
claim the main agent must retain. A `complete` receipt has no limitations;
`partial` and `blocked` receipts require at least one and cannot hide the reason
in a worker transcript.

## Citation integrity

A citation names a path relative to the compiler `--root`, inclusive
`line_start` and `line_end`, and `exact_sha256` for the exact cited line bytes.
The compiler rejects paths escaping the root, invalid ranges, missing sources,
and stale hashes.

Generate hashes using the same inclusive-byte convention implemented by
`<goal-architect-root>/scripts/compile_receipts.py`; do not normalize or
paraphrase before hashing.
Keep ranges as small as the fact permits. A hash proves source identity, not
interpretation.

Use repository-relative source paths in citations even when the assignment
packet uses absolute roots. Generated receipts and dossiers must not cite one
another as evidence for product behavior.

When a source is not line-addressable—runtime UI, deployed endpoint, database,
or external API—do not invent a file citation. The worker returns the bounded
source limitation or points to a project-native immutable capture explicitly
authorized for the task. Required real-boundary or verified-live proof remains
an evidence obligation for execution, not a research-receipt claim.

## Claude Code execution

Prefer Claude Code native subagents for focused assignments that report back
to the lead. Each subagent has its own context, so include all packet fields
and do not assume it sees the lead's unstated reasoning.

Use an experimental agent team only when workers need direct communication,
shared task coordination, or deliberate cross-review. Teams have higher token
and coordination cost and are a poor fit for sequential work, same-file edits,
or independent receipts that only the lead must reconcile.

Do not launch `claude -p` as a substitute for native delegation by default.
Headless execution is appropriate only for explicitly requested automation or
a harness that intentionally manages independent processes, permissions,
streaming output, and session lifecycle.

Permissions remain those of the session. Auto mode does not expand the packet
or product authority. The lead checks a permission request against the exact
action and target before allowing it.

## Codex execution

Prefer Codex native subagents for independent exploration, tests, triage, log
analysis, and bounded source review. Give each agent the complete packet,
explicit output ownership, and an instruction to return only narrow findings
with exact citations.

Codex guidance favors read-heavy parallel work because multiple write-heavy
agents can conflict and add integration cost. Use exclusive files or isolated
worktrees for the rare independent write assignment, then make the main agent
integrate and verify the result.

Do not launch `codex exec` as a hidden subagent by default. Use it for explicit
non-interactive automation with an intentional output/session contract. The
main Codex thread still owns decisions, integration, pair prose, and evidence.

If provider or project instructions disallow delegation, use the direct
workflow. Parallelism is an optimization, not part of product completion.

## Writes, worktrees, and permissions

Read-only workers may share a checkout when their commands cannot mutate it.
For writes, require either:

- exclusive ownership of disjoint files in the shared project; or
- separate Git worktrees based on the declared source revision.

Never give two workers overlapping files. Do not use broad globs or unresolved
environment variables as write ownership. Keep artifacts under a named
project directory so the user can inspect and retain them.

Workers do not create speculative tests, harnesses, mocks, process code, or
implementation while gathering authoring evidence. If discovery reveals that
such work may be required later, it is an open decision or candidate obligation
for the main agent to evaluate under the feature-first admission rule.

Before approving permissions, verify the exact target belongs to the current
assignment and the action is reversible or explicitly authorized. Stop and
return the issue for deletion, overwrite, deployment, credential use, messages,
or external mutation outside the packet.

## Compilation and reconciliation

Compile receipts with:

```bash
python3 <goal-architect-root>/scripts/compile_receipts.py \
  --root /absolute/project \
  --output docs/goals/evidence/<pair-id>/evidence-dossier.json \
  docs/goals/evidence/<pair-id>/*.receipt.json
```

The dossier schema is documented by
[evidence-dossier.schema.json](evidence-dossier.schema.json). Compilation:

- validates each receipt;
- rejects duplicate receipt or assignment identities;
- rejects unstable or mixed source revisions and retains the shared revision;
- re-reads every citation under the root;
- verifies its exact line hash;
- records deterministic input identities;
- sorts and deduplicates only exact duplicate facts; and
- preserves status, limitations, and conflict/open-decision provenance.

Compilation does not summarize, rewrite, infer, rank, adjudicate, or certify.
The main agent then:

1. reads every conflict and open decision;
2. follows citations for material or disputed claims;
3. checks stale-revision or runtime-sensitive facts;
4. resolves what evidence can resolve;
5. asks only for decisions that materially change product or authority;
6. derives one cohesive obligation/evidence ledger; and
7. authors the rider and goal itself.

The dossier is an authoring input. It does not belong in the normative pair and
does not close execution evidence `E*` unless the rider explicitly defines a
source-analysis obligation that this level of evidence can actually prove.

The receipt and dossier schemas are fixed benchmark contracts. Change one only
for a named failing benchmark fixture or validator defect, keep the failure as
a regression test, and bump the schema version when compatibility changes. Do
not add narrative, recommendation, winner, or correctness fields.

## Failure and stop conditions

Stop or reissue an assignment when:

- the source revision or scoped file changes during the read;
- a required path lies outside allowed roots;
- repository instructions contradict the packet;
- a citation cannot be made stable;
- the worker needs implementation or external mutation to answer;
- another worker owns the required mutable file;
- user-owned changes would be overwritten; or
- product/authority judgment is required.

Do not broaden scope autonomously. Return the exact obstacle, checked evidence,
and smallest packet change needed. The main agent decides whether to amend,
sequence, perform direct inspection, or proceed with an explicit uncertainty.

## Examples

### Appropriate two-worker split

- A-code: map affected symbols, dependencies, existing fixtures, and shortest
  integrated proof path under `src/` and `tests/`.
- A-history: locate exact rider/goal pairs and the scoped session segment that
  shows why earlier execution drifted.

These can return independently and inform different parts of the contract.

### Inappropriate split

- Worker 1 writes the product obligations.
- Worker 2 writes the evidence inventory.
- Worker 3 combines their prose.

The obligations determine sufficient evidence, so these are coupled judgments.
The main agent must author both from reconciled facts.

### Isolated authoring exception

After the product criterion, O/E ledger, shared interfaces, authority, and
module boundaries are frozen, workers may draft disjoint triggered conditional
modules into exclusive fragment files or separate worktrees. They do not draft
the core rider blocks or goal prose. Fragments remain non-normative inputs and
must not be concatenated mechanically into the rider. The lead reconciles and
integrates their meaning, reads the whole rider, resolves conflicts, projects
the goal, and validates the pair.

Parallel implementation is a separate decision expressed by the resulting
rider's `delegation` module. It is not inferred from parallel authoring.
