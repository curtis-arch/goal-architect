#!/usr/bin/env python3
"""Deterministic positive and adversarial controls for validate_pair.py."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

from validate_pair import manifest_sha256, validate_pair


SCRIPT_DIR = Path(__file__).resolve().parent
VALIDATOR = SCRIPT_DIR / "validate_pair.py"


def _goal_text(goal: Path, rider: Path, existing: Path, obligations: list[str], evidence: list[str], *, external: bool = False) -> str:
    obligation_lines = "\n".join(
        f"- `{obligation}` — Observable behavior for {obligation}." for obligation in obligations
    )
    mappings = "; ".join(
        f"`{obligation} -> {proof}`" for obligation, proof in zip(obligations, evidence)
    )
    allowed = (
        "deploy to production target alpha after its named gate; recovery restores the prior version"
        if external
        else "none authorized"
    )
    return f"""GOAL: missing deterministic behavior -> users observe the requested integrated behavior.

**Pair and read first.** `{rider}`; `{existing}`.

**Product obligations.**
{obligation_lines}

**Boundaries and authority.** Preserve: existing unrelated behavior. External actions: {allowed}; Withheld: every other external mutation, commit, and push.

**Execution constraint.** Land the earliest usable integrated slice. Reuse the named proof path. Add support machinery or proof only for a named active obligation or concrete reproduced defect the existing path cannot establish.

**Evidence.** {mappings}. Surface the named results after the final relevant behavior or configuration change.

**Stop when** every active obligation has its mapped evidence and no withheld action was taken. At any spend bound, report incomplete obligations rather than claiming completion.
"""


def _rider_text(
    goal: Path,
    execution_root: Path,
    existing_rel: str,
    pair_id: str,
    obligations: list[str],
    evidence: list[str],
    units: list[str],
    *,
    modules: tuple[str, ...] = (),
    source_revision: str = "non-git-observation-2026-08-02T1200Z",
    provenance: str = "per-integration",
    extra: str = "",
) -> str:
    obligation_rows = "\n".join(
        f"| {obligation} | Observable behavior for {obligation}. | `src/current.py` | {proof} | Preserve unrelated behavior. |"
        for obligation, proof in zip(obligations, evidence)
    )
    evidence_rows = "\n".join(
        f"| {proof} | {obligation} | integrated | `src/current.py` | `python3 -m unittest` | exits zero and observes {obligation} | none | closed |"
        for obligation, proof in zip(obligations, evidence)
    )
    advances = ", ".join(obligations)
    closes = ", ".join(evidence)
    unit_blocks: list[str] = []
    for index, unit in enumerate(units):
        depends = units[index - 1] if index else "none"
        unit_blocks.append(
            f"""### {unit} — integrated product boundary

- Advances: {advances}
- Delivers: the observable integrated behavior
- Owns: `src/current.py`
- Prerequisite: current source is readable, because it prevents changing the wrong behavior
- Evidence closed: {closes}
- Depends on: {depends}
- Provenance: pair and unit receipt at integration
- Stop if: authority or current behavior contradicts this contract
"""
        )
    module_value = ", ".join(modules) if modules else "none"
    optional_sections: list[str] = []
    heading_map = {
        "migration": "Migration and data integrity",
        "security": "Threat and security",
        "authority": "Authority and irreversible actions",
        "deploy": "Deploy and rollback",
        "experiment": "Experiment and refusal",
        "performance": "Performance",
        "gate": "Gate receipts",
        "mechanical-posture": "Mechanical posture",
        "delegation": "Delegation plan",
        "descope": "Descope plan",
        "verified-live": "Verified-live proof",
    }
    for module in modules:
        if module == "authority":
            action = (
                "deploy integrated feature | production target alpha"
                if "deploy" in modules
                else "update tracker status | tracker item alpha"
            )
            optional_sections.append(
            f"""## Authority and irreversible actions

| Action | Exact target | Authorized by/current scope | Gate | Recovery | Withheld |
|---|---|---|---|---|---|
| {action} | current goal boundary | E1 | restore prior state | every other remote mutation |
"""
            )
        elif module == "descope":
            optional_sections.append(
                """## Descope plan

| Retained obligation | Surviving evidence | Required authority | Removal boundary | Stop if |
|---|---|---|---|---|
| O1 | E1 | integrated | alternate support only | E1 no longer proves O1 |
"""
            )
        else:
            optional_sections.append(
                f"## {heading_map[module]}\n\nThe selected {module} risk has a named claim, boundary, and recovery path."
            )
    optional = "\n\n".join(optional_sections)
    return f"""# Evidence-closed rider

Pair-ID: `{pair_id}`
Goal: `{goal}`
Execution-root: `{execution_root}`
Source-revision: `{source_revision}`
Provenance: `{provenance}`
Modules: `{module_value}`
Supersedes: `none`

## Product criterion and current state

Product criterion: Users observe the requested integrated behavior.

Current state: The requested behavior is absent at the declared source revision, as shown by `src/current.py`.

## Obligations and boundaries

| ID | Observable behavior | Surfaces | Evidence | Explicit exclusions |
|---|---|---|---|---|
{obligation_rows}

## Existing substrate and shortest proof paths

| Status | Path | Reuse/current fact | Used by |
|---|---|---|---|
| existing | `{existing_rel}` | Current implementation and named proof path. | {', '.join(units)} |

## Execution units

{''.join(unit_blocks)}
## Closed evidence inventory

| ID | Proves | Level | Existing path/environment | Command or flow | Expected observation | Mock boundary | Addition rule |
|---|---|---|---|---|---|---|---|
{evidence_rows}

## Change and completion contract

The activated pair remains immutable. A proof addition requires a named gap or reproduced defect. Qualify once after the final relevant mutation. Cleanup retains sufficient proof for every active obligation. A material scope or authority change creates a superseding revision. Final reporting separates implemented, tested, deployed, verified-live, incomplete, and withheld states.

{optional}
{extra}
"""


def make_pair(
    root: Path,
    *,
    pair_id: str = "2026-08-02-1200-evidence-closed",
    obligations: list[str] | None = None,
    evidence: list[str] | None = None,
    units: list[str] | None = None,
    modules: tuple[str, ...] = (),
    source_revision: str = "non-git-observation-2026-08-02T1200Z",
    provenance: str = "per-integration",
    extra: str = "",
    external: bool = False,
) -> tuple[Path, Path, Path]:
    obligations = obligations or ["O1"]
    evidence = evidence or ["E1"]
    units = units or ["U1"]
    docs = root / "docs" / "goals"
    docs.mkdir(parents=True, exist_ok=True)
    source = root / "src" / "current.py"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text("VALUE = 1\n", encoding="utf-8")
    goal = docs / f"{pair_id}-goal.md"
    rider = docs / f"{pair_id}-rider.md"
    goal.write_text(_goal_text(goal, rider, source, obligations, evidence, external=external), encoding="utf-8")
    rider.write_text(
        _rider_text(
            goal,
            root,
            "src/current.py",
            pair_id,
            obligations,
            evidence,
            units,
            modules=modules,
            source_revision=source_revision,
            provenance=provenance,
            extra=extra,
        ),
        encoding="utf-8",
    )
    return goal, rider, source


def assert_valid(goal: Path, rider: Path) -> tuple[list[str], dict[str, object]]:
    errors, warnings, manifest = validate_pair(goal, rider)
    assert not errors, errors
    assert manifest is not None
    return warnings, manifest


def assert_error(goal: Path, rider: Path, needle: str) -> None:
    errors, _warnings, manifest = validate_pair(goal, rider)
    assert manifest is None
    assert any(needle in error for error in errors), (needle, errors)


def rewrite(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    assert old in text, old
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix=".evidence-validator-", dir=SCRIPT_DIR) as temporary:
        workspace = Path(temporary)

        minimal = workspace / "minimal"
        goal, rider, _source = make_pair(minimal)
        warnings, manifest = assert_valid(goal, rider)
        assert any("goal byte headroom" in warning for warning in warnings)
        assert set(manifest) == {
            "pair_id",
            "goal_sha256",
            "rider_sha256",
            "goal_bytes",
            "source_revision",
            "execution_root",
            "obligations",
            "evidence",
            "selected_modules",
        }
        expected_hash = manifest_sha256(manifest)
        assert not validate_pair(goal, rider, expected_hash)[0]
        errors, _, _ = validate_pair(goal, rider, "0" * 64)
        assert any("activation manifest SHA-256" in error for error in errors), errors

        command = [sys.executable, str(VALIDATOR), str(goal), str(rider)]
        first = subprocess.run(command, text=True, capture_output=True, check=False)
        second = subprocess.run(command, text=True, capture_output=True, check=False)
        assert first.returncode == second.returncode == 0, (first.stderr, second.stderr)
        assert first.stdout == second.stdout
        assert first.stderr == second.stderr
        assert json.loads(first.stdout) == manifest
        assert set(json.loads(first.stdout)) == set(manifest)
        checked = subprocess.run(
            command + ["--expected-manifest-sha256", expected_hash],
            text=True,
            capture_output=True,
            check=False,
        )
        assert checked.returncode == 0, checked.stderr

        large = workspace / "large"
        obligations = [f"O{number}" for number in range(1, 40, 2)]
        evidence = [f"E{number}" for number in range(2, 41, 2)]
        large_goal, large_rider, _ = make_pair(
            large,
            pair_id="2026-08-02-1201-large-nonstandard",
            obligations=obligations,
            evidence=evidence,
            units=["U7", "U42"],
            extra="\n## Deep product context\n\n" + ("Distinct retained product fact with direct grounding.\n" * 2_000),
        )
        _large_warnings, large_manifest = assert_valid(large_goal, large_rider)
        assert large_rider.stat().st_size > 80_000
        assert large_manifest["obligations"] == obligations
        assert large_manifest["evidence"] == evidence

        combined = workspace / "combined-layout"
        combined_goal, combined_rider, _ = make_pair(
            combined,
            pair_id="2026-08-02-1206-combined-layout",
        )
        rewrite(
            combined_rider,
            "## Product criterion and current state",
            "## Cohesive execution contract",
        )
        for heading in (
            "## Obligations and boundaries\n",
            "## Existing substrate and shortest proof paths\n",
            "## Execution units\n",
            "## Closed evidence inventory\n",
            "## Change and completion contract\n",
        ):
            rewrite(combined_rider, heading, "")
        assert_valid(combined_goal, combined_rider)

        deploy = workspace / "deploy"
        deploy_goal, deploy_rider, _ = make_pair(
            deploy,
            pair_id="2026-08-02-1202-deploy",
            modules=("authority", "deploy"),
            external=True,
        )
        _deploy_warnings, deploy_manifest = assert_valid(deploy_goal, deploy_rider)
        assert deploy_manifest["selected_modules"] == ["authority", "deploy"]

        authority_only = workspace / "authority-only"
        authority_goal, authority_rider, _ = make_pair(
            authority_only,
            pair_id="2026-08-02-1207-authority-only",
            modules=("authority",),
        )
        rewrite(
            authority_goal,
            "External actions: none authorized",
            "External actions: send one status message to tracker item alpha after E1",
        )
        _authority_warnings, authority_manifest = assert_valid(
            authority_goal, authority_rider
        )
        assert authority_manifest["selected_modules"] == ["authority"]

        descope = workspace / "descope"
        descope_goal, descope_rider, _ = make_pair(
            descope,
            pair_id="2026-08-02-1208-descope",
            modules=("descope",),
        )
        _descope_warnings, descope_manifest = assert_valid(descope_goal, descope_rider)
        assert descope_manifest["selected_modules"] == ["descope"]

        invalid_descope = workspace / "invalid-descope"
        invalid_descope_goal, invalid_descope_rider, _ = make_pair(
            invalid_descope,
            pair_id="2026-08-02-1209-invalid-descope",
            modules=("descope",),
        )
        rewrite(
            invalid_descope_rider,
            "| O1 | E1 | integrated | alternate support only | E1 no longer proves O1 |",
            "| O1 | none | integrated | alternate support only | removal seems fine |",
        )
        assert_error(
            invalid_descope_goal,
            invalid_descope_rider,
            "has no surviving evidence",
        )

        wrong_descope_authority = workspace / "wrong-descope-authority"
        wrong_authority_goal, wrong_authority_rider, _ = make_pair(
            wrong_descope_authority,
            pair_id="2026-08-02-1210-wrong-descope-authority",
            modules=("descope",),
        )
        rewrite(
            wrong_authority_rider,
            "| O1 | E1 | integrated | alternate support only | E1 no longer proves O1 |",
            "| O1 | E1 | verified-live | alternate support only | E1 no longer proves O1 |",
        )
        assert_error(
            wrong_authority_goal,
            wrong_authority_rider,
            "authority does not match surviving evidence",
        )

        cases: list[tuple[str, str]] = []

        missing_root = workspace / "missing-files"
        missing_goal = missing_root / "2026-08-02-1203-missing-goal.md"
        missing_rider = missing_root / "2026-08-02-1203-missing-rider.md"
        assert_error(missing_goal, missing_rider, "goal is missing")

        empty = workspace / "empty"
        empty.mkdir()
        empty_goal = empty / "2026-08-02-1204-empty-goal.md"
        empty_rider = empty / "2026-08-02-1204-empty-rider.md"
        empty_goal.write_text("", encoding="utf-8")
        empty_rider.write_text("", encoding="utf-8")
        assert_error(empty_goal, empty_rider, "goal is empty")

        wrong = workspace / "wrong-sibling"
        wrong_goal, wrong_rider, _ = make_pair(wrong)
        other_rider = wrong_rider.with_name("2026-08-02-1200-other-rider.md")
        other_rider.write_text(wrong_rider.read_text(encoding="utf-8"), encoding="utf-8")
        assert_error(wrong_goal, other_rider, "exact sibling")

        relative = workspace / "relative-read-first"
        relative_goal, relative_rider, relative_source = make_pair(relative)
        rewrite(relative_goal, f"`{relative_source}`", "`src/current.py`")
        assert_error(relative_goal, relative_rider, "read-first path must be absolute")

        mutations: list[tuple[str, str, str, str]] = [
            ("pair-id", "rider", "`2026-08-02-1200-evidence-closed`", "`different-pair`", "Pair-ID must match"),
            ("goal-citation", "goal", "`/", "`/definitely-missing/", "absolute rider citation"),
            ("rider-citation", "rider", "Goal: `", "Goal: `/definitely-missing/", "rider Goal:"),
            ("duplicate-goal-o", "goal", "- `O1` — Observable behavior for O1.", "- `O1` — Observable behavior for O1.\n- `O1` — Duplicated behavior.", "duplicate obligation IDs"),
            ("missing-rider-o", "rider", "| O1 | Observable behavior for O1. | `src/current.py` | E1 | Preserve unrelated behavior. |\n", "", "obligation sets differ"),
            ("unmapped-o", "rider", "| O1 | Observable behavior for O1. | `src/current.py` | E1 | Preserve unrelated behavior. |", "| O1 | Observable behavior for O1. | `src/current.py` | none | Preserve unrelated behavior. |", "has no mapped evidence"),
            ("duplicate-u", "rider", "### U1 — integrated product boundary", "### U1 — integrated product boundary\n\n### U1 — duplicate boundary", "duplicate execution-unit IDs"),
            ("duplicate-e", "rider", "| E1 | O1 | integrated | `src/current.py` | `python3 -m unittest` | exits zero and observes O1 | none | closed |", "| E1 | O1 | integrated | `src/current.py` | `python3 -m unittest` | exits zero and observes O1 | none | closed |\n| E1 | O1 | integrated | `src/current.py` | `python3 -m unittest` | exits zero | none | closed |", "duplicate evidence IDs"),
            ("dangling", "rider", "The activated pair remains immutable.", "The activated pair remains immutable. Undefined O99 is forbidden.", "references undefined O99"),
            ("missing-existing", "rider", "`src/current.py` | Current implementation", "`src/missing.py` | Current implementation", "existing read-first path does not resolve"),
            ("missing-provenance", "rider", "Provenance: `per-integration`\n", "", "declare Provenance:"),
            ("missing-product-criterion", "rider", "Product criterion: Users observe the requested integrated behavior.\n", "", "declare Product criterion:"),
            ("missing-close-once", "rider", "Qualify once after the final relevant mutation.", "Qualification may run repeatedly.", "final relevant mutation"),
            ("bad-provenance", "rider", "`per-integration`", "`none`", "must be per-unit"),
            ("unstable-revision", "rider", "`non-git-observation-2026-08-02T1200Z`", "`latest`", "stable anchor"),
            ("stop", "goal", "every active obligation has its mapped evidence and no withheld action was taken", "the work appears finished", "stop semantics"),
            ("module", "rider", "Modules: `none`", "Modules: `security`", "selected module security requires"),
            ("undeclared-module", "rider", "## Change and completion contract", "## Threat and security\n\nSecurity details.\n\n## Change and completion contract", "module security is not selected"),
            ("todo", "rider", "The activated pair remains immutable.", "TODO: The activated pair remains immutable.", "unresolved template marker"),
            ("template", "goal", "missing deterministic behavior", "<current failure>", "unresolved template marker"),
            ("self-supersedes", "rider", "Supersedes: `none`", "Supersedes: `2026-08-02-1200-evidence-closed`", "contradicts the active pair revision"),
            ("invalid-level", "rider", "| E1 | O1 | integrated |", "| E1 | O1 | proposed |", "invalid evidence level"),
            ("undefined-unit", "rider", "- Depends on: none", "- Depends on: U99", "references undefined U99"),
        ]
        for name, target, old, new, expected in mutations:
            case_root = workspace / f"case-{name}"
            case_goal, case_rider, _ = make_pair(case_root)
            rewrite(case_goal if target == "goal" else case_rider, old, new)
            assert_error(case_goal, case_rider, expected)
            cases.append((name, expected))

        oversized = workspace / "oversized"
        oversized_goal, oversized_rider, _ = make_pair(oversized)
        rewrite(
            oversized_goal,
            "missing deterministic behavior",
            "missing deterministic behavior " + ("without filler resolution " * 220),
        )
        assert oversized_goal.stat().st_size > 4_000
        assert_error(oversized_goal, oversized_rider, "portable cap")

        external_missing = workspace / "external-missing"
        ext_goal, ext_rider, _ = make_pair(
            external_missing,
            modules=("authority", "deploy"),
            external=True,
        )
        rewrite(ext_rider, "## Authority and irreversible actions", "## External action notes")
        assert_error(ext_goal, ext_rider, "Authority and irreversible actions")

        bad_hash_errors, _, _ = validate_pair(goal, rider, "not-a-hash")
        assert any("64 hexadecimal" in error for error in bad_hash_errors)

        create_root = workspace / "create-warning"
        create_goal, create_rider, _ = make_pair(create_root)
        rewrite(
            create_rider,
            "| existing | `src/current.py` | Current implementation and named proof path.",
            "| create | `proof/new-harness.py` | create new alternate harness for proof.",
        )
        create_warnings, _ = assert_valid(create_goal, create_rider)
        assert any("declared create path" in warning for warning in create_warnings)
        assert any("shortest-valid-proof review" in warning for warning in create_warnings)

        git_repo = workspace / "git-warning"
        (git_repo / ".git").mkdir(parents=True)
        nested = git_repo / "packages" / "feature"
        git_goal, git_rider, _ = make_pair(
            nested,
            pair_id="2026-08-02-1205-git-warning",
            source_revision="none",
        )
        git_warnings, _ = assert_valid(git_goal, git_rider)
        assert any("execution root differs" in warning for warning in git_warnings)
        assert any("no source-revision anchor" in warning for warning in git_warnings)

        inherited = workspace / "inherited"
        inherited_goal, inherited_rider, _ = make_pair(inherited)
        with inherited_rider.open("a", encoding="utf-8") as stream:
            stream.write(
                """
## Precedence and inherited obligations

| Source | Carried categories | Delta |
|---|---|---|
| `docs/goals/2026-08-02-1000-missing-rider.md` | product behavior | preserve behavior; retire none |
"""
            )
        assert_error(inherited_goal, inherited_rider, "inherited source does not resolve")

        print(
            "PASS: evidence-closed validator accepted minimal, deploy, and 80KB/noncontiguous pairs; "
            f"rejected {len(cases) + 10} structural/reference/authority/hash defects; "
            "and emitted deterministic bounded manifests plus path/headroom review warnings"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
