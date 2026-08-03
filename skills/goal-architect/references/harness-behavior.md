# Harness behavior

## Contents

1. [Purpose](#purpose)
2. [Shared activation invariant](#shared-activation-invariant)
3. [Claude Code goal body](#claude-code-goal-body)
4. [Codex objective and attachment](#codex-objective-and-attachment)
5. [Dispatched coordinator briefing](#dispatched-coordinator-briefing)
6. [Native subagents before headless sessions](#native-subagents-before-headless-sessions)
7. [Provider-neutral execution briefing](#provider-neutral-execution-briefing)
8. [Completion and interruption](#completion-and-interruption)
9. [Authority changes during execution](#authority-changes-during-execution)
10. [Grounding sources](#grounding-sources)

## Purpose

The goal/rider pair is provider-neutral. Activation is not. Use the provider's
native durable-goal mechanism while preserving the same product obligations,
evidence authority, revision identity, and completion semantics.

Do not weaken the pair to make the harness easier to drive. Adapt the handoff,
not the product criterion.

## Shared activation invariant

The executing lead owns the full pair and remains accountable for integration
and final evidence even when workers contribute. Before any implementation:

1. Read the exact sibling goal and rider plus repository instructions.
2. Verify the named source revision and current dirty state.
3. Resolve the directory containing the installed `SKILL.md`, run
   `python3 <goal-architect-root>/scripts/validate_pair.py <goal> <rider>`,
   and surface its activation manifest.
4. Check whether that session already has an active goal.
5. Activate the exact immutable pair revision through one of the forms below.
6. Keep the main session focused on product decisions, integration, evidence,
   and truthful completion.

Before describing the pair as activation-ready, check that every mandatory
evidence flow is possible at current authority. Obtain the exact action/target
permission or tell the user execution will pause at the named gate.

Activation does not grant permissions. The agent may perform only actions the
user and current environment authorize. A worker or coordinator cannot confer
additional external or irreversible authority.

## Claude Code goal body

Claude Code `/goal` accepts one completion condition of at most 4,000
characters. The command starts a turn immediately and replaces an existing
active goal. Therefore:

1. Run `/goal` without arguments and inspect the current state.
2. Do not replace an unrelated active goal without explicit authority.
3. Read the goal and rider before invoking `/goal`; the goal body is the
   directive for the first turn.
4. Invoke `/goal <exact goal body>`, not merely `/goal <path>`.
5. Keep the absolute rider citation inside that body so the executing model can
   read the detailed contract.
6. Surface named evidence and observations in the transcript because the goal
   evaluator cannot read files or run tools independently.

The evaluator sees the condition and conversation, returns yes/no plus a short
reason, and starts another turn when the condition is not yet demonstrated.
It is not an implementation reviewer. A condition such as “the feature is
done” is too opaque; the compact goal must name the observable end state,
checks, constraints, and stop shape that the transcript can demonstrate.

Auto mode can approve allowed tool calls but does not change completion or
permission semantics. A time/turn clause limits continuation; it does not make
partial work successful. If the bound arrives before the achieved condition,
the transcript must report bounded-incomplete or an explicitly defined
accepted-refusal state.

Use non-interactive `claude -p "/goal ..."` only when the user explicitly wants
automation or an unattended process. Stream output for long runs so lack of
terminal output is not mistaken for inactivity. Interactive native execution
is the default for an already active Claude session.

## Codex objective and attachment

Codex may expose the durable objective as native goal tools rather than a
slash command. Use the actual tools available in the current client; do not
invent a shell wrapper.

1. Read and validate the exact pair in the main Codex thread.
2. Call the native goal-status operation first.
3. If no unrelated objective is active, use the client's native goal-file
   path/attachment form when it retains and injects the exact revision.
   Otherwise create the objective from the exact goal body. In either form,
   retain the absolute rider attachment/citation.
4. Execute from the declared `Execution-root` with current repository
   instructions in force.
5. Mark the objective complete only after every obligation has sufficient
   evidence at its declared authority and no required work remains.

For Codex clients exposing `get_goal`, `create_goal`, and `update_goal`, that
means `get_goal` before `create_goal`. Use `update_goal(status="complete")`
only for actual completion. Do not mark a goal complete because a budget is
low or one worker reported success.

Use `blocked` only under the current goal-tool contract: the same blocking
condition must recur for at least three consecutive goal turns and safe
in-scope alternatives must be exhausted. Until then, report the exact missing
authority, environment, input, or external state and keep making meaningful
progress where possible.

Codex goal evaluation and persistence can vary by client version. The shared
contract does not: the main agent reads both files, activates the exact
revision, owns integration, and maps completion to the closed evidence
inventory. Body condition, native path/attachment, and dispatched briefing are
peer handoff forms. A native path/attachment is preferred when Codex retains
and injects it; it never replaces the main agent reading the sibling rider.
The compact goal body is the portable fallback.

## Dispatched coordinator briefing

Some harnesses dispatch a coordinator instead of keeping the authoring session
as the executing lead. Treat this as a third handoff form, not as a substitute
for a Claude `/goal` evaluator or Codex native goal.

The dispatch packet must contain:

- exact absolute goal and rider paths;
- Pair-ID and source revision;
- execution root and repository-instruction locations;
- the goal body or an instruction to read it before acting;
- allowed write roots and external/irreversible authority;
- required evidence authority and final report states;
- current dirty-state facts that must be preserved; and
- a stop-if condition for contradiction, missing authority, or stale grounding.

The coordinator must confirm it read the pair, validate the revision, check its
own active-goal state, and activate the objective before dispatching workers.
It owns continuation, conflict resolution, integration, and final evidence.
A coordinator's summary is provenance, not proof of an external product claim.

Do not hand workers only the goal file. The rider contains the concrete
boundaries, substrate, execution units, evidence authority, and change rules
that prevent plausible but out-of-scope implementation.

## Native subagents before headless sessions

Use the current harness's native subagent mechanism for focused work. It keeps
delegation visible to the executing lead and avoids creating opaque parallel
sessions.

For Claude Code:

- use native subagents for quick, focused tasks whose results return to the
  lead;
- use experimental agent teams only when workers truly need direct
  communication or shared coordination and the feature is enabled;
- prefer a single lead for sequential work, same-file changes, and tightly
  coupled decisions; and
- use `claude -p` only for explicit non-interactive automation, not as the
  default way to manufacture subagents.

For Codex:

- use native subagents for independent read-heavy exploration, tests, triage,
  or log analysis;
- return narrow findings with file/line or other source grounding;
- use isolated worktrees or exclusive file ownership for independent writes;
  and
- use `codex exec` only for explicit non-interactive automation, not as an
  implicit replacement for native delegation.

Native delegation still costs context and coordination. Use it only when work
is semantically independent and the result can be bounded. The direct variant
does not require parallelism; see the parallel variant when deliberate receipt
compilation is warranted.

## Provider-neutral execution briefing

Use this briefing shape regardless of provider:

```text
Execute Pair-ID <id> from <execution-root>.
Read and validate <absolute goal> and <absolute rider> before implementation.
Preserve source revision and current user-owned changes.
Activate the exact goal body with this harness's native durable-goal form.
Authority: <allowed external/irreversible actions and exact targets>.
Evidence: close O* only through the named E* at the declared authority.
Change: activated bytes are immutable; material scope/authority changes require
a superseding pair. The main executing lead owns integration and final proof.
Stop: <achieved, accepted-refusal, or bounded-incomplete shape>.
```

Do not add provider folklore to the normative rider. If a client needs a
special launch command, permission mode, environment variable, or worktree
setup, put it in the invocation or environment configuration unless it is
itself a product obligation or material execution boundary.

## Completion and interruption

Completion requires the pair's achieved condition and sufficient evidence for
every active obligation. Keep these states separate:

- implemented;
- tested locally;
- deployed;
- verified live;
- accepted refusal; and
- bounded incomplete.

If the user says `stop`, stop goal turns, workers, edits, deploys, and retries,
then report the exact retained state once. If a permission prompt appears,
confirm the requested action is within the pair's authority and exact target;
do not approve unrelated deletion, overwrite, deployment, or external action.

## Authority changes during execution

When the user grants or changes permission after activation, record the exact
delta before the affected action:

1. anchor the current user instruction;
2. enumerate the exact action, target, and necessary prerequisites now allowed;
3. enumerate adjacent previously withheld actions that remain withheld; and
4. decide whether this only unlocks an existing gate or changes an obligation,
   evidence authority, target, or completion state.

An existing-gate unlock may remain transcript authority. A material change in
step 4 requires a timestamped superseding pair and validation before acting.
Permission to deploy one named Worker does not imply creating a separately
withheld database, pushing Git, releasing another service, or mutating another
provider unless those actions and targets are explicit.

After compaction, handoff, or goal resumption, reread the activated pair and the
latest exact authority delta before any external or irreversible action. Ignore
permissions from earlier goals or replacement history when the current pair
does not inherit them.

## Grounding sources

This adapter was derived from provider documentation reviewed during the
skill's design:

- Claude Code: `goal_en_docs.md`, `sub-agents_en_docs.md`,
  `agent-teams_en_docs.md`, and `headless_en_docs.md`.
- Codex: `subagents.md_agent-configuration_codex.md`,
  `git-worktrees.md_environments_codex.md`, and
  `non-interactive-mode.md_codex.md`.

The provider documentation can change. Prefer current native tools and their
actual contract at execution time while preserving the provider-neutral pair
invariants above.
