#!/usr/bin/env python3
"""Validate read-only research receipts and compile a mechanical dossier.

This program deliberately has no product judgment. It preserves exact claims,
declared conflicts, and open decisions; it never resolves, summarizes, ranks,
or turns them into goal/rider prose.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
REFERENCE_DIR = HERE.parent / "references"
RECEIPT_SCHEMA = REFERENCE_DIR / "research-receipt.schema.json"
DOSSIER_SCHEMA = REFERENCE_DIR / "evidence-dossier.schema.json"
UNSTABLE_SOURCE_REVISIONS = frozenset({"latest", "head", "current"})
MISSING_SOURCE_REVISION_PREFIXES = ("none", "unknown", "unavailable")


class ValidationError(ValueError):
    """A receipt, citation, or compiled dossier violates its contract."""


def _without_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> Any:
    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_without_duplicate_keys,
        )
    except OSError as exc:
        raise ValidationError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {path}: {exc}") from exc


def _schema_target(root_schema: dict[str, Any], reference: str) -> dict[str, Any]:
    if not reference.startswith("#/"):
        raise ValidationError(f"unsupported non-local schema reference: {reference}")
    target: Any = root_schema
    for token in reference[2:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        if not isinstance(target, dict) or token not in target:
            raise ValidationError(f"invalid schema reference: {reference}")
        target = target[token]
    if not isinstance(target, dict):
        raise ValidationError(f"schema reference is not an object: {reference}")
    return target


def _is_type(value: Any, expected: str) -> bool:
    return {
        "object": lambda: isinstance(value, dict),
        "array": lambda: isinstance(value, list),
        "string": lambda: isinstance(value, str),
        "integer": lambda: isinstance(value, int) and not isinstance(value, bool),
        "boolean": lambda: isinstance(value, bool),
        "null": lambda: value is None,
    }.get(expected, lambda: False)()


def validate_schema(
    value: Any,
    schema: dict[str, Any],
    root_schema: dict[str, Any] | None = None,
    location: str = "$",
) -> None:
    """Validate the JSON-Schema subset used by the two checked-in schemas."""

    root_schema = root_schema or schema
    if "$ref" in schema:
        validate_schema(
            value,
            _schema_target(root_schema, schema["$ref"]),
            root_schema,
            location,
        )
        return

    for member in schema.get("allOf", []):
        validate_schema(value, member, root_schema, location)

    if "if" in schema:
        try:
            validate_schema(value, schema["if"], root_schema, location)
        except ValidationError:
            conditional_match = False
        else:
            conditional_match = True
        branch = "then" if conditional_match else "else"
        if branch in schema:
            validate_schema(value, schema[branch], root_schema, location)

    if "const" in schema and value != schema["const"]:
        raise ValidationError(f"{location} must equal {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        raise ValidationError(f"{location} is not an allowed value")

    expected = schema.get("type")
    if expected is not None:
        choices = expected if isinstance(expected, list) else [expected]
        if not any(_is_type(value, choice) for choice in choices):
            raise ValidationError(f"{location} has the wrong JSON type")

    if isinstance(value, dict):
        required = schema.get("required", [])
        missing = [key for key in required if key not in value]
        if missing:
            raise ValidationError(f"{location} is missing required keys: {missing}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extras = sorted(set(value) - set(properties))
            if extras:
                raise ValidationError(f"{location} has unexpected keys: {extras}")
        for key, child in properties.items():
            if key in value:
                validate_schema(value[key], child, root_schema, f"{location}.{key}")

    if isinstance(value, list):
        minimum = schema.get("minItems")
        maximum = schema.get("maxItems")
        if minimum is not None and len(value) < minimum:
            raise ValidationError(f"{location} has fewer than {minimum} items")
        if maximum is not None and len(value) > maximum:
            raise ValidationError(f"{location} has more than {maximum} items")
        if schema.get("uniqueItems"):
            encoded = [
                json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                for item in value
            ]
            if len(encoded) != len(set(encoded)):
                raise ValidationError(f"{location} contains duplicate items")
        if "items" in schema:
            for index, child in enumerate(value):
                validate_schema(child, schema["items"], root_schema, f"{location}[{index}]")

    if isinstance(value, str):
        minimum = schema.get("minLength")
        if minimum is not None and len(value) < minimum:
            raise ValidationError(f"{location} is shorter than {minimum} characters")
        pattern = schema.get("pattern")
        if pattern is not None and re.search(pattern, value) is None:
            raise ValidationError(f"{location} does not match {pattern}")

    if isinstance(value, int) and not isinstance(value, bool):
        minimum = schema.get("minimum")
        if minimum is not None and value < minimum:
            raise ValidationError(f"{location} is less than {minimum}")


def _canonical_relative(value: str, *, allow_dot: bool = False) -> str:
    if "\\" in value:
        raise ValidationError(f"path must use POSIX separators: {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part == ".." for part in path.parts):
        raise ValidationError(f"path must remain under the declared root: {value!r}")
    normalized = path.as_posix()
    if normalized != value or (normalized == "." and not allow_dot):
        raise ValidationError(f"path must be canonical and root-relative: {value!r}")
    return normalized


def _resolved_under(root: Path, relative: str) -> Path:
    try:
        resolved = (root / relative).resolve(strict=True)
    except OSError as exc:
        raise ValidationError(f"cited path does not exist: {relative}") from exc
    if resolved != root and root not in resolved.parents:
        raise ValidationError(f"path resolves outside root: {relative}")
    return resolved


def cited_line_digest(path: Path, line_start: int, line_end: int) -> str:
    """Hash inclusive source lines exactly, retaining their original line endings."""

    lines = path.read_bytes().splitlines(keepends=True)
    if line_end < line_start or line_end > len(lines):
        raise ValidationError(
            f"invalid line range {line_start}-{line_end} for {path} ({len(lines)} lines)"
        )
    selected = b"".join(lines[line_start - 1 : line_end])
    return "sha256:" + hashlib.sha256(selected).hexdigest()


def _citation_key(citation: dict[str, Any]) -> tuple[str, int, int, str]:
    return (
        citation["path"],
        citation["line_start"],
        citation["line_end"],
        citation["exact_sha256"],
    )


def _sorted_citations(citations: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key = {_citation_key(item): dict(item) for item in citations}
    return [by_key[key] for key in sorted(by_key)]


def _validate_source_revision(source_revision: str) -> None:
    normalized = source_revision.strip()
    lowered = normalized.casefold()
    if source_revision != normalized or not normalized:
        raise ValidationError("source_revision must be a non-blank exact revision value")
    if lowered in UNSTABLE_SOURCE_REVISIONS or lowered.startswith(
        MISSING_SOURCE_REVISION_PREFIXES
    ):
        raise ValidationError(
            "source_revision must be a stable anchor, not "
            "latest/HEAD/current/none/unknown/unavailable"
        )


def validate_receipt(raw: Any, root: Path, schema: dict[str, Any]) -> dict[str, Any]:
    validate_schema(raw, schema)
    if not isinstance(raw, dict):  # Narrow type for static checkers after validation.
        raise ValidationError("receipt must be an object")

    _validate_source_revision(raw["source_revision"])

    actions = raw["actions"]
    if any(actions[name] for name in ("implementation", "writes", "external")):
        raise ValidationError(
            "research receipts must not contain implementation, write, or external actions"
        )

    scope_roots: list[Path] = []
    for item in raw["scope"]["roots"]:
        relative = _canonical_relative(item, allow_dot=True)
        resolved = _resolved_under(root, relative)
        if not resolved.is_dir():
            raise ValidationError(f"scope root is not a directory: {relative}")
        scope_roots.append(resolved)

    sources: dict[str, Path] = {}
    for item in raw["scope"]["sources"]:
        relative = _canonical_relative(item)
        resolved = _resolved_under(root, relative)
        if not resolved.is_file():
            raise ValidationError(f"scope source is not a regular file: {relative}")
        if not any(resolved == scope_root or scope_root in resolved.parents for scope_root in scope_roots):
            raise ValidationError(f"scope source is outside declared roots: {relative}")
        sources[relative] = resolved

    def verify_citations(items: list[dict[str, Any]], location: str) -> list[dict[str, Any]]:
        checked: list[dict[str, Any]] = []
        for index, citation in enumerate(items):
            relative = _canonical_relative(citation["path"])
            if relative not in sources:
                raise ValidationError(
                    f"{location}[{index}] is not one of the receipt's declared sources: {relative}"
                )
            actual = cited_line_digest(
                sources[relative], citation["line_start"], citation["line_end"]
            )
            if actual != citation["exact_sha256"]:
                raise ValidationError(f"{location}[{index}] has a stale or incorrect line hash")
            checked.append(dict(citation))
        return _sorted_citations(checked)

    fact_ids: set[str] = set()
    facts: list[dict[str, Any]] = []
    for index, fact in enumerate(raw["facts"]):
        if fact["fact_id"] in fact_ids:
            raise ValidationError(f"duplicate fact_id in {raw['receipt_id']}: {fact['fact_id']}")
        fact_ids.add(fact["fact_id"])
        facts.append(
            {
                **fact,
                "citations": verify_citations(
                    fact["citations"], f"facts[{index}].citations"
                ),
            }
        )

    conflict_ids: set[str] = set()
    conflicts: list[dict[str, Any]] = []
    for index, conflict in enumerate(raw["conflicts"]):
        if conflict["conflict_id"] in conflict_ids:
            raise ValidationError(
                f"duplicate conflict_id in {raw['receipt_id']}: {conflict['conflict_id']}"
            )
        conflict_ids.add(conflict["conflict_id"])
        if not set(conflict["fact_refs"]) <= fact_ids:
            raise ValidationError(
                f"conflict {conflict['conflict_id']} references an absent local fact"
            )
        conflicts.append(
            {
                **conflict,
                "fact_refs": sorted(conflict["fact_refs"]),
                "citations": verify_citations(
                    conflict["citations"], f"conflicts[{index}].citations"
                ),
            }
        )

    decision_ids: set[str] = set()
    decisions: list[dict[str, Any]] = []
    for index, decision in enumerate(raw["open_decisions"]):
        if decision["decision_id"] in decision_ids:
            raise ValidationError(
                f"duplicate decision_id in {raw['receipt_id']}: {decision['decision_id']}"
            )
        decision_ids.add(decision["decision_id"])
        decisions.append(
            {
                **decision,
                "citations": verify_citations(
                    decision["citations"], f"open_decisions[{index}].citations"
                ),
            }
        )

    return {
        **raw,
        "limitations": sorted(raw["limitations"]),
        "facts": facts,
        "conflicts": conflicts,
        "open_decisions": decisions,
    }


def _fact_key(subject: str, claim: str) -> str:
    exact = json.dumps(
        [subject, claim], ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(exact).hexdigest()


def compile_receipts(root: Path, receipt_paths: Iterable[Path]) -> dict[str, Any]:
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValidationError(f"root is not a directory: {root}")
    receipt_schema = load_json(RECEIPT_SCHEMA)
    dossier_schema = load_json(DOSSIER_SCHEMA)

    receipts = [validate_receipt(load_json(path), root, receipt_schema) for path in receipt_paths]
    if not receipts:
        raise ValidationError("at least one receipt is required")
    receipt_ids = [item["receipt_id"] for item in receipts]
    if len(receipt_ids) != len(set(receipt_ids)):
        raise ValidationError("receipt_id values must be unique across inputs")
    assignment_ids = [item["assignment_id"] for item in receipts]
    if len(assignment_ids) != len(set(assignment_ids)):
        raise ValidationError(
            "assignment_id values must be unique across inputs; assignment_id is packet identity"
        )
    source_revisions = {item["source_revision"] for item in receipts}
    if len(source_revisions) != 1:
        raise ValidationError("all receipts must have the same source_revision")
    source_revision = next(iter(source_revisions))

    compiled_facts: dict[tuple[str, str], dict[str, Any]] = {}
    conflicts: list[dict[str, Any]] = []
    decisions: list[dict[str, Any]] = []

    for receipt in receipts:
        receipt_id = receipt["receipt_id"]
        for fact in receipt["facts"]:
            identity = (fact["subject"], fact["claim"])
            current = compiled_facts.setdefault(
                identity,
                {
                    "fact_key": _fact_key(*identity),
                    "subject": fact["subject"],
                    "claim": fact["claim"],
                    "citations": {},
                    "origins": set(),
                },
            )
            for citation in fact["citations"]:
                current["citations"][_citation_key(citation)] = citation
            current["origins"].add((receipt_id, fact["fact_id"]))

        for conflict in receipt["conflicts"]:
            conflicts.append(
                {
                    "receipt_id": receipt_id,
                    "conflict_id": conflict["conflict_id"],
                    "description": conflict["description"],
                    "fact_refs": conflict["fact_refs"],
                    "citations": conflict["citations"],
                }
            )
        for decision in receipt["open_decisions"]:
            decisions.append(
                {
                    "receipt_id": receipt_id,
                    "decision_id": decision["decision_id"],
                    "question": decision["question"],
                    "citations": decision["citations"],
                }
            )

    facts: list[dict[str, Any]] = []
    for identity in sorted(compiled_facts):
        item = compiled_facts[identity]
        facts.append(
            {
                "fact_key": item["fact_key"],
                "subject": item["subject"],
                "claim": item["claim"],
                "citations": [item["citations"][key] for key in sorted(item["citations"])],
                "origins": [
                    {"receipt_id": receipt_id, "fact_id": fact_id}
                    for receipt_id, fact_id in sorted(item["origins"])
                ],
            }
        )

    dossier = {
        "schema_version": "1.0",
        "source_revision": source_revision,
        "receipts": sorted(
            (
                {
                    "receipt_id": item["receipt_id"],
                    "assignment_id": item["assignment_id"],
                    "status": item["status"],
                    "limitations": item["limitations"],
                }
                for item in receipts
            ),
            key=lambda item: (item["assignment_id"], item["receipt_id"]),
        ),
        "facts": facts,
        "conflicts": sorted(
            conflicts, key=lambda item: (item["receipt_id"], item["conflict_id"])
        ),
        "open_decisions": sorted(
            decisions, key=lambda item: (item["receipt_id"], item["decision_id"])
        ),
    }
    validate_schema(dossier, dossier_schema)
    return dossier


def render_dossier(dossier: dict[str, Any]) -> str:
    return json.dumps(dossier, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate read-only receipts and compile an exact evidence dossier."
    )
    parser.add_argument("--root", required=True, type=Path, help="citation root")
    parser.add_argument("--output", type=Path, help="write dossier here; otherwise stdout")
    parser.add_argument("receipts", nargs="+", type=Path, help="receipt JSON files")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.output is not None:
            output = args.output.resolve()
            inputs = {path.resolve() for path in args.receipts}
            if output in inputs:
                raise ValidationError("output must not overwrite an input receipt")
        rendered = render_dossier(compile_receipts(args.root, args.receipts))
        if args.output is None:
            sys.stdout.write(rendered)
        else:
            args.output.write_text(rendered, encoding="utf-8")
    except (OSError, ValidationError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
