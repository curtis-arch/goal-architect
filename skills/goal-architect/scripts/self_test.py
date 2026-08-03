#!/usr/bin/env python3
"""Self-tests for Goal Architect's pair validator and receipt compiler."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from compile_receipts import (
    ValidationError,
    cited_line_digest,
    compile_receipts,
    render_dossier,
)


HERE = Path(__file__).resolve().parent
PAIR_SELF_TEST = HERE / "validator_self_test.py"
COMPILER = HERE / "compile_receipts.py"
SOURCE_REVISION = "git:0123456789abcdef0123456789abcdef01234567"


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def citation(source: Path, relative: str, start: int, end: int) -> dict[str, Any]:
    return {
        "path": relative,
        "line_start": start,
        "line_end": end,
        "exact_sha256": cited_line_digest(source, start, end),
    }


def receipt(
    receipt_id: str,
    assignment_id: str,
    source: Path,
    facts: list[dict[str, Any]],
    *,
    source_revision: str = SOURCE_REVISION,
    status: str = "complete",
    limitations: list[str] | None = None,
    conflicts: list[dict[str, Any]] | None = None,
    decisions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "receipt_id": receipt_id,
        "assignment_id": assignment_id,
        "source_revision": source_revision,
        "status": status,
        "limitations": list(limitations or []),
        "mode": "read-only-research",
        "scope": {"roots": ["."], "sources": [source.name]},
        "facts": facts,
        "conflicts": conflicts or [],
        "open_decisions": decisions or [],
        "actions": {"implementation": [], "writes": [], "external": []},
    }


def expect_rejected(
    root: Path,
    path: Path,
    invalid: dict[str, Any],
    label: str,
) -> None:
    write_json(path, invalid)
    try:
        compile_receipts(root, [path])
    except ValidationError:
        return
    raise AssertionError(f"compiler accepted {label}")


def run_shared_pair_tests() -> str:
    if not PAIR_SELF_TEST.is_file():
        raise AssertionError(f"copied pair-validator self-test is missing: {PAIR_SELF_TEST}")
    result = subprocess.run(
        [sys.executable, "-B", str(PAIR_SELF_TEST)],
        cwd=HERE.parent,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(
            "Pair-validator self-test failed\n"
            + result.stdout
            + ("\n" if result.stdout and result.stderr else "")
            + result.stderr
        )
    return result.stdout.strip() or "passed"


def run_compiler_tests() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix=".receipt-self-test-", dir=HERE) as raw_dir:
        root = Path(raw_dir)
        source = root / "source.txt"
        source.write_bytes(
            b"transport: http\nlimit: 10\nlimit: 20\nretry: disabled\n"
        )
        c1 = citation(source, source.name, 1, 1)
        c2 = citation(source, source.name, 2, 2)
        c3 = citation(source, source.name, 3, 3)
        c4 = citation(source, source.name, 4, 4)

        first = receipt(
            "R-alpha",
            "architecture",
            source,
            [
                {
                    "fact_id": "F1",
                    "subject": "transport",
                    "claim": "The adapter uses HTTP.",
                    "citations": [c1],
                },
                {
                    "fact_id": "F2",
                    "subject": "limit",
                    "claim": "The configured limit is 10.",
                    "citations": [c2],
                },
                {
                    "fact_id": "F3",
                    "subject": "limit",
                    "claim": "The configured limit is 20.",
                    "citations": [c3],
                },
            ],
            conflicts=[
                {
                    "conflict_id": "C1",
                    "description": "Two source lines declare different limits.",
                    "fact_refs": ["F3", "F2"],
                    "citations": [c3, c2],
                }
            ],
            decisions=[
                {
                    "decision_id": "D1",
                    "question": "Which configured limit is authoritative?",
                    "citations": [c2, c3],
                }
            ],
        )
        second = receipt(
            "R-beta",
            "proof-substrate",
            source,
            [
                {
                    "fact_id": "F1",
                    "subject": "transport",
                    "claim": "The adapter uses HTTP.",
                    "citations": [c1],
                },
                {
                    "fact_id": "F2",
                    "subject": "retry",
                    "claim": "Retry is disabled.",
                    "citations": [c4],
                },
            ],
            status="partial",
            limitations=[
                "Runtime behavior was not observed.",
                "External service state was not queried.",
            ],
        )
        first_path = root / "first.json"
        second_path = root / "second.json"
        write_json(first_path, first)
        write_json(second_path, second)

        forward = render_dossier(compile_receipts(root, [first_path, second_path]))
        reverse = render_dossier(compile_receipts(root, [second_path, first_path]))
        assert forward.encode("utf-8") == reverse.encode("utf-8")
        checks += 1  # byte-identical output regardless of receipt order

        permuted_first = copy.deepcopy(first)
        permuted_first["facts"].reverse()
        permuted_first["conflicts"][0]["fact_refs"].reverse()
        permuted_first["conflicts"][0]["citations"].reverse()
        permuted_first["open_decisions"][0]["citations"].reverse()
        permuted_second = copy.deepcopy(second)
        permuted_second["limitations"].reverse()
        write_json(first_path, permuted_first)
        write_json(second_path, permuted_second)
        permuted = render_dossier(compile_receipts(root, [second_path, first_path]))
        assert forward.encode("utf-8") == permuted.encode("utf-8")
        write_json(first_path, first)
        write_json(second_path, second)
        checks += 1  # byte-identical output regardless of fact/reference order

        dossier_path = root / "dossier.json"
        cli_output = subprocess.run(
            [
                sys.executable,
                "-B",
                str(COMPILER),
                "--root",
                str(root),
                "--output",
                str(dossier_path),
                str(second_path),
                str(first_path),
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        assert cli_output.returncode == 0, cli_output.stderr
        assert cli_output.stdout == ""
        assert dossier_path.read_text(encoding="utf-8") == forward
        checks += 1  # output-file CLI writes the deterministic dossier only

        cli_stdout = subprocess.run(
            [
                sys.executable,
                "-B",
                str(COMPILER),
                "--root",
                str(root),
                str(first_path),
                str(second_path),
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        assert cli_stdout.returncode == 0, cli_stdout.stderr
        assert cli_stdout.stdout == forward
        checks += 1  # stdout CLI has identical bytes

        dossier = json.loads(forward)
        assert set(dossier) == {
            "schema_version",
            "source_revision",
            "receipts",
            "facts",
            "conflicts",
            "open_decisions",
        }
        checks += 1  # bounded, non-narrative dossier surface

        assert dossier["source_revision"] == SOURCE_REVISION
        assert dossier["receipts"] == [
            {
                "receipt_id": "R-alpha",
                "assignment_id": "architecture",
                "status": "complete",
                "limitations": [],
            },
            {
                "receipt_id": "R-beta",
                "assignment_id": "proof-substrate",
                "status": "partial",
                "limitations": [
                    "External service state was not queried.",
                    "Runtime behavior was not observed.",
                ],
            },
        ]
        checks += 1  # revision, status, and exact limitations are preserved deterministically

        duplicate = [
            item
            for item in dossier["facts"]
            if item["subject"] == "transport"
            and item["claim"] == "The adapter uses HTTP."
        ]
        assert len(duplicate) == 1
        assert duplicate[0]["origins"] == [
            {"receipt_id": "R-alpha", "fact_id": "F1"},
            {"receipt_id": "R-beta", "fact_id": "F1"},
        ]
        checks += 1  # exact duplicate facts mechanically deduplicate

        limits = [item["claim"] for item in dossier["facts"] if item["subject"] == "limit"]
        assert limits == ["The configured limit is 10.", "The configured limit is 20."]
        assert dossier["conflicts"] == [
            {
                "receipt_id": "R-alpha",
                "conflict_id": "C1",
                "description": "Two source lines declare different limits.",
                "fact_refs": ["F2", "F3"],
                "citations": [c2, c3],
            }
        ]
        checks += 1  # conflicting claims remain separate; declaration is preserved

        assert dossier["open_decisions"] == [
            {
                "receipt_id": "R-alpha",
                "decision_id": "D1",
                "question": "Which configured limit is authoritative?",
                "citations": [c2, c3],
            }
        ]
        checks += 1  # open material decisions are not resolved

        invalid_path = root / "invalid.json"

        missing_citation = copy.deepcopy(first)
        missing_citation["facts"][0]["citations"] = []
        expect_rejected(root, invalid_path, missing_citation, "a fact without citations")
        checks += 1

        bad_citation = copy.deepcopy(first)
        bad_citation["facts"][0]["citations"][0]["exact_sha256"] = "sha256:" + "0" * 64
        expect_rejected(root, invalid_path, bad_citation, "an incorrect exact-line hash")
        checks += 1

        undeclared_source = copy.deepcopy(first)
        undeclared_source["facts"][0]["citations"][0]["path"] = "other.txt"
        expect_rejected(root, invalid_path, undeclared_source, "an undeclared citation path")
        checks += 1

        extra_key = copy.deepcopy(first)
        extra_key["summary"] = "This key would invite semantic composition."
        expect_rejected(root, invalid_path, extra_key, "an unexpected key")
        checks += 1

        wrong_schema = copy.deepcopy(first)
        wrong_schema["schema_version"] = "9.9"
        expect_rejected(root, invalid_path, wrong_schema, "a schema-version mismatch")
        checks += 1

        unstable_revision = copy.deepcopy(first)
        unstable_revision["source_revision"] = "HEAD"
        expect_rejected(root, invalid_path, unstable_revision, "an unstable source revision")
        mixed_revision = copy.deepcopy(second)
        mixed_revision["source_revision"] = (
            "git:fedcba9876543210fedcba9876543210fedcba98"
        )
        write_json(invalid_path, mixed_revision)
        try:
            compile_receipts(root, [first_path, invalid_path])
        except ValidationError:
            pass
        else:
            raise AssertionError("compiler accepted mixed source revisions")
        checks += 1

        blocked_without_limitation = copy.deepcopy(first)
        blocked_without_limitation["status"] = "blocked"
        blocked_without_limitation["limitations"] = []
        expect_rejected(
            root,
            invalid_path,
            blocked_without_limitation,
            "a blocked receipt without an exact limitation",
        )
        checks += 1

        complete_with_limitation = copy.deepcopy(first)
        complete_with_limitation["limitations"] = ["A hidden incomplete boundary."]
        expect_rejected(
            root,
            invalid_path,
            complete_with_limitation,
            "a complete receipt with a limitation",
        )
        checks += 1

        duplicate_assignment = copy.deepcopy(second)
        duplicate_assignment["assignment_id"] = first["assignment_id"]
        write_json(invalid_path, duplicate_assignment)
        try:
            compile_receipts(root, [first_path, invalid_path])
        except ValidationError:
            pass
        else:
            raise AssertionError("compiler accepted duplicate assignment ownership")
        checks += 1

        for action in ("implementation", "writes", "external"):
            attempted_action = copy.deepcopy(first)
            attempted_action["actions"][action] = ["forbidden action"]
            expect_rejected(root, invalid_path, attempted_action, f"a recorded {action} action")
            checks += 1

    return checks


def main() -> int:
    try:
        pair_result = run_shared_pair_tests()
        checks = run_compiler_tests()
    except (AssertionError, OSError, ValidationError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(f"PASS shared pair validator: {pair_result}")
    print(f"PASS Goal Architect receipt compiler: {checks} checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
