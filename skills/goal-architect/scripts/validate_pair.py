#!/usr/bin/env python3
"""Mechanically validate an evidence-closed goal/rider pair.

The validator deliberately checks references and declared contracts, not how
many phases, tests, files, agents, commits, or hours a round should contain.
On success the CLI prints only the bounded activation manifest to stdout.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Iterable


GOAL_CAP_BYTES = 4_000
GOAL_MARKERS = (
    "GOAL:",
    "**Pair and read first.**",
    "**Product obligations.**",
    "**Boundaries and authority.**",
    "**Execution constraint.**",
    "**Evidence.**",
    "**Stop when**",
)
IDENTITY_LABELS = (
    "Pair-ID",
    "Goal",
    "Execution-root",
    "Source-revision",
    "Provenance",
    "Modules",
    "Supersedes",
)
PROVENANCE_CADENCES = ("per-unit", "per-integration", "per-gate")
MODULE_HEADINGS = {
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
EVIDENCE_LEVELS = {"unit", "integrated", "real-boundary", "deployed", "verified-live"}
EVIDENCE_LEVEL_ORDER = {
    "unit": 0,
    "integrated": 1,
    "real-boundary": 2,
    "deployed": 3,
    "verified-live": 4,
}
EXTERNAL_ACTION = re.compile(
    r"\b(?:push|deploy|release|publish|send|email|message|delete|drop|migrate|mutate)\b",
    re.IGNORECASE,
)
DEPLOY_ACTION = re.compile(r"\b(?:deploy|release|publish|rollout)\b", re.IGNORECASE)
NEW_PROOF_SUPPORT = re.compile(
    r"\b(?:new|create|alternate|disposable)\b.{0,50}\b"
    r"(?:harness|simulator|mock stack|fixture system|telemetry scaffold|fallback)\b",
    re.IGNORECASE,
)
UNRESOLVED = re.compile(
    r"\b(?:TODO|TBD|FIXME)\b|\{\{[^}\n]+\}\}|"
    r"\[\s*(?:PLACEHOLDER|REPLACE[ _-]?ME)[^\]\n]*\]|"
    r"\bREPLACE[ _-]?ME\b|<[^<>\n]{1,160}>|\?\?\?",
    re.IGNORECASE,
)
ID_PATTERN = re.compile(r"\b([OUE]\d+)\b")


def _absolute(path: Path) -> Path:
    """Return an absolute path without requiring the target to exist."""

    return Path(os.path.abspath(os.fspath(path)))


def _natural_id(value: str) -> tuple[str, int]:
    return value[0], int(value[1:])


def _dedupe_sorted(items: Iterable[str]) -> list[str]:
    return sorted(set(items))


def _strip_value(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == "`":
        return value[1:-1].strip()
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest_sha256(manifest: dict[str, object]) -> str:
    """Hash the canonical, compact representation of an activation manifest."""

    payload = json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _read(path: Path, label: str, errors: list[str]) -> str | None:
    if not path.is_file():
        errors.append(f"{label} is missing: {path}")
        return None
    if path.stat().st_size == 0:
        errors.append(f"{label} is empty: {path}")
        return None
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        errors.append(f"{label} is not valid UTF-8: {path}")
        return None


def _goal_sections(text: str, errors: list[str]) -> dict[str, str]:
    """Return bodies for the exact, ordered goal markers."""

    found: list[tuple[str, int, int]] = []
    for marker in GOAL_MARKERS:
        if marker == "GOAL:":
            matches = list(re.finditer(r"^GOAL:\s*", text, re.MULTILINE))
        else:
            matches = list(re.finditer(rf"^{re.escape(marker)}\s*", text, re.MULTILINE))
        if len(matches) != 1:
            errors.append(f"goal must contain exactly one {marker} marker; found {len(matches)}")
            continue
        found.append((marker, matches[0].start(), matches[0].end()))

    if len(found) != len(GOAL_MARKERS):
        return {}
    positions = [item[1] for item in found]
    if positions != sorted(positions):
        errors.append("goal markers are out of order")
    sections: dict[str, str] = {}
    for index, (marker, _start, end) in enumerate(found):
        next_start = found[index + 1][1] if index + 1 < len(found) else len(text)
        body = text[end:next_start].strip()
        sections[marker] = body
        if not body:
            errors.append(f"goal section {marker} is empty")
    return sections


def _identity(text: str, errors: list[str]) -> dict[str, str]:
    first_h2 = re.search(r"^## ", text, re.MULTILINE)
    preamble = text[: first_h2.start()] if first_h2 else text
    values: dict[str, str] = {}
    for label in IDENTITY_LABELS:
        pattern = re.compile(
            rf"^\s*(?:[-*]\s+)?(?:\*\*)?{re.escape(label)}:(?:\*\*)?\s*(.+?)\s*$",
            re.MULTILINE,
        )
        matches = pattern.findall(preamble)
        if len(matches) != 1:
            errors.append(f"rider must declare {label}: exactly once; found {len(matches)}")
            continue
        value = _strip_value(matches[0])
        if not value:
            errors.append(f"rider {label}: declaration is empty")
        else:
            values[label] = value
    return values


def _check_required_semantics(text: str, errors: list[str]) -> None:
    """Check layout-independent rider fields and completion/change semantics."""

    for label in ("Product criterion", "Current state"):
        matches = re.findall(
            rf"^\s*{re.escape(label)}:\s*(\S.*?)\s*$", text, re.MULTILINE
        )
        if len(matches) != 1:
            errors.append(f"rider must declare {label}: exactly once; found {len(matches)}")

    clauses = (
        (r"\bactivat\w*\b.{0,80}\bimmutable\b", "activated bytes must be immutable"),
        (
            r"\b(?:proof|evidence|support)\b.{0,120}\b(?:named\s+(?:gap|active\s+obligation)|reproduced\s+defect)\b",
            "proof additions must require a named gap/obligation or reproduced defect",
        ),
        (
            r"\bqualif\w*\b.{0,100}\bfinal\s+relevant\s+mutation\b",
            "qualification must occur after the final relevant mutation",
        ),
        (
            r"\b(?:descope|cleanup)\b.{0,120}\b(?:proof|evidence)\b.{0,100}\bobligation",
            "descope/cleanup must preserve evidence for retained obligations",
        ),
        (
            r"\bmaterial\b.{0,80}\b(?:scope|authority)\b.{0,100}\b(?:new|supersed\w*)\b.{0,40}\brevision\b",
            "material scope/authority changes must create a superseding revision",
        ),
    )
    for pattern, message in clauses:
        if not re.search(pattern, text, re.IGNORECASE | re.DOTALL):
            errors.append(f"rider change/completion contract must state that {message}")

    final_report = re.search(
        r"\bfinal\s+report(?:ing)?\b.{0,300}", text, re.IGNORECASE | re.DOTALL
    )
    if not final_report or any(
        term not in final_report.group(0).lower()
        for term in ("implemented", "tested", "deployed", "verified-live", "incomplete", "withheld")
    ):
        errors.append(
            "rider final reporting must separate implemented, tested, deployed, "
            "verified-live, incomplete, and withheld states"
        )


def _split_table_row(line: str) -> list[str]:
    """Split a Markdown table row without splitting escaped or inline-code pipes."""

    stripped = line.strip()
    if not stripped.startswith("|"):
        return []
    cells: list[str] = []
    current: list[str] = []
    in_code = False
    escaped = False
    for char in stripped[1:]:
        if escaped:
            current.append(char)
            escaped = False
            continue
        if char == "\\":
            current.append(char)
            escaped = True
            continue
        if char == "`":
            in_code = not in_code
            current.append(char)
            continue
        if char == "|" and not in_code:
            cells.append(_strip_value("".join(current).strip()))
            current = []
            continue
        current.append(char)
    if current:
        cells.append(_strip_value("".join(current).strip()))
    if cells and not cells[-1]:
        cells.pop()
    return cells


def _ledger_rows(
    text: str,
    header: tuple[str, ...],
    row_id_pattern: str,
    label: str,
    errors: list[str],
) -> list[list[str]]:
    """Find one machine-readable ledger by its exact header, independent of H2 layout."""

    lines = text.splitlines()
    matches: list[int] = []
    expected = [item.lower() for item in header]
    for index, line in enumerate(lines):
        cells = _split_table_row(line)
        if [item.lower() for item in cells] == expected:
            matches.append(index)
    if len(matches) != 1:
        errors.append(f"rider must contain exactly one {label} table; found {len(matches)}")
        return []

    rows: list[list[str]] = []
    for line in lines[matches[0] + 1 :]:
        cells = _split_table_row(line)
        if not cells:
            break
        if all(re.fullmatch(r"-+", item) for item in cells):
            continue
        if not re.fullmatch(row_id_pattern, cells[0], re.IGNORECASE):
            break
        rows.append(cells)
    return rows


def _duplicates(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return sorted(duplicates, key=_natural_id)


def _goal_obligations(section: str, errors: list[str]) -> list[str]:
    definitions = re.findall(r"^\s*[-*]\s+`(O\d+)`\s+(?:—|-)\s+\S.*$", section, re.MULTILINE)
    if not definitions:
        errors.append("goal has no product-obligation definitions")
    duplicates = _duplicates(definitions)
    if duplicates:
        errors.append(f"goal has duplicate obligation IDs: {duplicates}")
    return sorted(set(definitions), key=_natural_id)


def _goal_mappings(section: str, errors: list[str]) -> dict[str, list[str]]:
    mappings: dict[str, list[str]] = {}
    occurrences: list[str] = []
    pattern = re.compile(r"\b(O\d+)\b\s*->\s*(.*?)(?=(?:\bO\d+\b\s*->)|[;\n]|$)", re.DOTALL)
    for match in pattern.finditer(section):
        obligation = match.group(1)
        occurrences.append(obligation)
        evidence = sorted(set(re.findall(r"\bE\d+\b", match.group(2))), key=_natural_id)
        if not evidence:
            errors.append(f"goal evidence mapping for {obligation} has no evidence IDs")
        mappings[obligation] = evidence
    duplicates = _duplicates(occurrences)
    if duplicates:
        errors.append(f"goal has duplicate evidence mappings: {duplicates}")
    if not mappings:
        errors.append("goal has no O -> E evidence mappings")
    return mappings


def _unit_blocks(text: str, errors: list[str]) -> dict[str, str]:
    matches = list(re.finditer(r"^### (U\d+)\b[^\n]*$", text, re.MULTILINE))
    identifiers = [match.group(1) for match in matches]
    duplicates = _duplicates(identifiers)
    if duplicates:
        errors.append(f"rider has duplicate execution-unit IDs: {duplicates}")
    if not identifiers:
        errors.append("rider has no U* execution units")
    blocks: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks.setdefault(match.group(1), text[match.end():end])
    return blocks


def _unit_field(block: str, label: str) -> str | None:
    match = re.search(rf"^\s*[-*]\s+{re.escape(label)}:\s*(.*?)\s*$", block, re.MULTILINE)
    return match.group(1).strip() if match else None


def _nearest_git_root(path: Path) -> Path | None:
    current = path.resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return None


def _path_from_cell(cell: str, execution_root: Path) -> Path:
    value = _strip_value(cell)
    path = Path(value)
    return path if path.is_absolute() else execution_root / path


def _check_substrate_paths(
    rider_text: str,
    execution_root: Path,
    errors: list[str],
    warnings: list[str],
) -> None:
    rows = _ledger_rows(
        rider_text,
        ("Status", "Path", "Reuse/current fact", "Used by"),
        r"(?:existing|create)",
        "existing substrate",
        errors,
    )
    for cells in rows:
        if len(cells) < 4:
            errors.append("substrate rows must contain Status, Path, Reuse/current fact, and Used by")
            continue
        status, raw_path = cells[0].lower(), cells[1]
        if not raw_path:
            errors.append(f"{status} substrate row has an empty path")
            continue
        candidate = _path_from_cell(raw_path, execution_root)
        if status == "existing" and not candidate.exists():
            errors.append(f"existing read-first path does not resolve: {candidate}")
        elif status == "create" and not candidate.exists():
            warnings.append(f"declared create path does not yet exist: {candidate}")
        if status == "create" and NEW_PROOF_SUPPORT.search(" ".join(cells[1:])):
            warnings.append(f"new proof-support path requires shortest-valid-proof review: {candidate}")
    if not rows:
        errors.append("existing-substrate section has no existing/create path rows")


def _check_inherited_sources(
    rider_text: str,
    execution_root: Path,
    errors: list[str],
) -> None:
    heading = re.search(r"^## Precedence and inherited obligations\s*$", rider_text, re.MULTILINE)
    if not heading:
        return
    next_heading = re.search(r"^## [^#\n].*$", rider_text[heading.end():], re.MULTILINE)
    end = heading.end() + next_heading.start() if next_heading else len(rider_text)
    section = rider_text[heading.end():end]
    rows = 0
    for line in section.splitlines():
        cells = _split_table_row(line)
        if not cells or cells[0].lower() in {"source", "---", "--"}:
            continue
        if len(cells) < 3:
            continue
        rows += 1
        source, carried, delta = cells[:3]
        if not source or not carried or not delta:
            errors.append("inherited-obligation rows require source, carried categories, and delta")
            continue
        source_path = _path_from_cell(source, execution_root)
        if not source_path.exists():
            errors.append(f"inherited source does not resolve: {source_path}")
        elif not source_path.name.endswith("-rider.md"):
            errors.append(f"inherited source must be a rider file: {source_path}")
        else:
            sibling_goal = source_path.with_name(
                source_path.name.removesuffix("-rider.md") + "-goal.md"
            )
            if not sibling_goal.is_file():
                errors.append(
                    f"inherited rider has no exact sibling goal: {sibling_goal}"
                )
        if re.search(r"\ball\s+(?:historic|prior|previous)\s+invariants?\s+(?:hold|apply)\b", delta, re.I):
            errors.append("inherited-obligation delta is blanket rather than explicit")
    if not rows:
        errors.append("precedence section has no resolvable source/carried-category/delta rows")


def _check_authority(
    goal_sections: dict[str, str],
    rider_text: str,
    modules: set[str],
    errors: list[str],
) -> None:
    boundary = goal_sections.get("**Boundaries and authority.**", "")
    for term in ("preserve", "external actions", "withheld"):
        if not re.search(rf"\b{term}\b", boundary, re.IGNORECASE):
            errors.append(f"goal boundaries and authority must declare {term} state")

    external_match = re.search(
        r"\bExternal actions:\s*(.*?)(?=(?:;|\n)\s*Withheld:|$)",
        boundary,
        re.IGNORECASE | re.DOTALL,
    )
    external_actions = external_match.group(1) if external_match else ""
    external_declared = bool(EXTERNAL_ACTION.search(external_actions)) or bool(
        {"authority", "deploy"} & modules
    )
    if not external_declared:
        return
    if EXTERNAL_ACTION.search(external_actions) and "authority" not in modules:
        errors.append("declared external action requires the authority module")
    if DEPLOY_ACTION.search(external_actions) and "deploy" not in modules:
        errors.append("declared deploy/release action requires the deploy module")
    heading = re.search(r"^## Authority and irreversible actions\s*$", rider_text, re.MULTILINE)
    if not heading:
        errors.append("external/irreversible authority requires ## Authority and irreversible actions")
        return
    following = re.search(r"^## [^#\n].*$", rider_text[heading.end():], re.MULTILINE)
    end = heading.end() + following.start() if following else len(rider_text)
    body = rider_text[heading.end():end]
    rows: list[list[str]] = []
    for line in body.splitlines():
        cells = _split_table_row(line)
        if not cells or cells[0].lower() == "action" or all(re.fullmatch(r"-+", cell) for cell in cells):
            continue
        rows.append(cells)
    if not rows:
        errors.append("authority section has no action/target/scope/gate/recovery/withheld row")
    for index, row in enumerate(rows, start=1):
        if len(row) != 6 or any(not cell for cell in row):
            errors.append(f"authority row {index} must contain six concrete values")


def _check_modules(rider_text: str, raw: str, errors: list[str]) -> list[str]:
    values = [item.strip().lower() for item in re.split(r"\s*,\s*", raw) if item.strip()]
    if not values:
        errors.append("Modules: declaration is empty")
        return []
    if "none" in values and len(values) > 1:
        errors.append("Modules: none cannot be combined with selected modules")
    duplicate_modules = sorted({item for item in values if values.count(item) > 1})
    if duplicate_modules:
        errors.append(f"Modules: contains duplicate declarations: {duplicate_modules}")
    unknown = sorted(set(values) - set(MODULE_HEADINGS) - {"none"})
    if unknown:
        errors.append(f"unknown selected modules: {unknown}")
    selected = sorted(set(values) & set(MODULE_HEADINGS))
    for module, heading in MODULE_HEADINGS.items():
        count = len(re.findall(rf"^## {re.escape(heading)}\s*$", rider_text, re.MULTILINE))
        if module in selected and count != 1:
            errors.append(f"selected module {module} requires exactly one ## {heading}; found {count}")
        elif module in selected:
            match = re.search(rf"^## {re.escape(heading)}\s*$", rider_text, re.MULTILINE)
            assert match is not None
            following = re.search(r"^## [^#\n].*$", rider_text[match.end():], re.MULTILINE)
            end = match.end() + following.start() if following else len(rider_text)
            if not rider_text[match.end():end].strip():
                errors.append(f"selected module {module} has an empty ## {heading} section")
        if module not in selected and count:
            errors.append(f"## {heading} is present but module {module} is not selected")
    if "none" in values and selected:
        errors.append("Modules: none declares a contradictory active module profile")
    if "deploy" in selected and "authority" not in selected:
        errors.append("selected module deploy also requires the authority module")
    return selected


def _check_descope_plan(
    rider_text: str,
    selected_modules: set[str],
    goal_mappings: dict[str, list[str]],
    evidence_levels: dict[str, str],
    errors: list[str],
) -> None:
    if "descope" not in selected_modules:
        return
    rows = _ledger_rows(
        rider_text,
        (
            "Retained obligation",
            "Surviving evidence",
            "Required authority",
            "Removal boundary",
            "Stop if",
        ),
        r"O\d+",
        "descope proof-survival",
        errors,
    )
    identifiers = [row[0] for row in rows]
    duplicates = _duplicates(identifiers)
    if duplicates:
        errors.append(f"descope plan has duplicate obligations: {duplicates}")
    if set(identifiers) != set(goal_mappings):
        errors.append(
            "descope plan must cover every active obligation: "
            f"expected={sorted(goal_mappings, key=_natural_id)}, "
            f"found={sorted(set(identifiers), key=_natural_id)}"
        )
    for row in rows:
        if len(row) != 5 or any(not cell for cell in row):
            errors.append(f"descope row {row[0]} must contain five concrete values")
            continue
        surviving = sorted(set(re.findall(r"\bE\d+\b", row[1])), key=_natural_id)
        if not surviving:
            errors.append(f"descope row {row[0]} has no surviving evidence")
        elif surviving != goal_mappings.get(row[0], []):
            errors.append(
                f"descope row {row[0]} must preserve its mapped evidence: "
                f"expected={goal_mappings.get(row[0], [])}, found={surviving}"
            )
        if row[2].lower() not in EVIDENCE_LEVELS:
            errors.append(
                f"descope row {row[0]} has invalid required authority: {row[2]}"
            )
        elif surviving and all(item in evidence_levels for item in surviving):
            required = max(
                (evidence_levels[item] for item in surviving),
                key=EVIDENCE_LEVEL_ORDER.__getitem__,
            )
            if row[2].lower() != required:
                errors.append(
                    f"descope row {row[0]} authority does not match surviving evidence: "
                    f"expected={required}, found={row[2].lower()}"
                )


def validate_pair(
    goal: Path,
    rider: Path,
    expected_manifest_sha256: str | None = None,
) -> tuple[list[str], list[str], dict[str, object] | None]:
    """Validate a pair and return errors, warnings, and its bounded manifest."""

    goal = _absolute(goal)
    rider = _absolute(rider)
    errors: list[str] = []
    warnings: list[str] = []

    name_match = re.fullmatch(r"(.+)-goal\.md", goal.name)
    pair_id = name_match.group(1) if name_match else ""
    if not name_match:
        errors.append("goal filename must end in -goal.md")
    else:
        expected_rider = goal.with_name(f"{pair_id}-rider.md")
        if rider != expected_rider:
            errors.append(f"rider is not the exact sibling {expected_rider}")

    goal_text = _read(goal, "goal", errors)
    rider_text = _read(rider, "rider", errors)
    if goal_text is None or rider_text is None:
        return _dedupe_sorted(errors), _dedupe_sorted(warnings), None

    goal_bytes = len(goal.read_bytes())
    headroom = GOAL_CAP_BYTES - goal_bytes
    warnings.append(f"goal byte headroom: {headroom} bytes")
    if goal_bytes > GOAL_CAP_BYTES:
        errors.append(f"goal is {goal_bytes} bytes; portable cap is {GOAL_CAP_BYTES}")
    if UNRESOLVED.search(goal_text):
        errors.append("goal contains TODO/TBD or an unresolved template marker")
    if UNRESOLVED.search(rider_text):
        errors.append("rider contains TODO/TBD or an unresolved template marker")

    goal_sections = _goal_sections(goal_text, errors)
    identity = _identity(rider_text, errors)
    _check_required_semantics(rider_text, errors)

    expected_goal_citation = f"`{goal}`"
    expected_rider_citation = f"`{rider}`"
    pair_section = goal_sections.get("**Pair and read first.**", "")
    if expected_rider_citation not in pair_section:
        errors.append(f"goal is missing absolute rider citation {expected_rider_citation}")
    if identity.get("Goal") != str(goal):
        errors.append(f"rider Goal: must be the absolute goal path {goal}")
    if expected_goal_citation not in rider_text:
        errors.append(f"rider is missing absolute goal citation {expected_goal_citation}")
    if pair_id and identity.get("Pair-ID") != pair_id:
        errors.append(f"rider Pair-ID must match sibling stem {pair_id}")

    for code_span in re.findall(r"`([^`\n]+)`", pair_section):
        if code_span == str(rider):
            continue
        read_first = Path(code_span)
        if not read_first.is_absolute():
            errors.append(f"goal read-first path must be absolute: {code_span}")
        elif not read_first.exists():
            errors.append(f"goal read-first path does not resolve: {code_span}")

    execution_root: Path | None = None
    root_value = identity.get("Execution-root")
    if root_value:
        execution_root = Path(root_value)
        if not execution_root.is_absolute():
            errors.append("Execution-root: must be absolute")
        elif not execution_root.is_dir():
            errors.append(f"Execution-root: is not an existing directory: {execution_root}")

    source_revision = identity.get("Source-revision", "")
    if source_revision.lower() in {"latest", "head", "current"}:
        errors.append("Source-revision: must be a stable anchor, not latest/HEAD/current")
    provenance = identity.get("Provenance", "")
    if provenance:
        lower_provenance = provenance.lower()
        if lower_provenance in PROVENANCE_CADENCES:
            pass
        elif lower_provenance.startswith("none") and re.search(r"^none(?:\s*(?:—|-|:|\().+)", provenance, re.I):
            pass
        else:
            errors.append("Provenance: must be per-unit, per-integration, per-gate, or justified none")
    supersedes = identity.get("Supersedes", "")
    if supersedes and pair_id and supersedes.lower() != "none" and supersedes == pair_id:
        errors.append("Supersedes: contradicts the active pair revision")

    selected_modules = _check_modules(rider_text, identity.get("Modules", ""), errors)
    _check_authority(goal_sections, rider_text, set(selected_modules), errors)

    outcome = goal_sections.get("GOAL:", "")
    if outcome and "->" not in outcome:
        errors.append("GOAL: must state current absence/failure -> observable end state")
    constraint = goal_sections.get("**Execution constraint.**", "")
    for pattern, message in (
        (r"\bearliest\b.{0,80}\bintegrated\s+slice\b", "execution constraint must require the earliest integrated slice"),
        (r"\breuse\b.{0,80}\bproof\s+path\b", "execution constraint must require proof-path reuse"),
        (r"\b(?:obligation|concrete reproduced defect)\b", "execution constraint must bind additions to an obligation or reproduced defect"),
    ):
        if constraint and not re.search(pattern, constraint, re.I | re.S):
            errors.append(message)
    stop = goal_sections.get("**Stop when**", "")
    for term in ("obligation", "evidence", "withheld"):
        if stop and not re.search(rf"\b{term}\w*\b", stop, re.I):
            errors.append(f"goal stop semantics are not tied to {term}")

    goal_obligations = _goal_obligations(
        goal_sections.get("**Product obligations.**", ""), errors
    )
    goal_mappings = _goal_mappings(goal_sections.get("**Evidence.**", ""), errors)
    if set(goal_mappings) != set(goal_obligations):
        errors.append(
            "goal evidence mappings must cover exactly the product obligations: "
            f"obligations={goal_obligations}, mappings={sorted(goal_mappings, key=_natural_id)}"
        )
    obligation_rows = _ledger_rows(
        rider_text,
        ("ID", "Observable behavior", "Surfaces", "Evidence", "Explicit exclusions"),
        r"O\d+",
        "obligation ledger",
        errors,
    )
    rider_obligation_ids = [row[0] for row in obligation_rows]
    duplicate_o = _duplicates(rider_obligation_ids)
    if duplicate_o:
        errors.append(f"rider has duplicate obligation IDs: {duplicate_o}")
    if not rider_obligation_ids:
        errors.append("rider obligation ledger has no O* rows")
    if set(rider_obligation_ids) != set(goal_obligations):
        errors.append(
            "goal/rider obligation sets differ: "
            f"goal={goal_obligations}, rider={sorted(set(rider_obligation_ids), key=_natural_id)}"
        )
    for row in obligation_rows:
        if len(row) < 5:
            errors.append(f"{row[0]} obligation row must include behavior, surfaces, boundaries, and evidence")
            continue
        rider_map = sorted(set(re.findall(r"\bE\d+\b", row[3])), key=_natural_id)
        if not rider_map:
            errors.append(f"{row[0]} obligation row has no mapped evidence")
        elif goal_mappings.get(row[0], []) != rider_map:
            errors.append(
                f"{row[0]} goal/rider evidence mappings differ: "
                f"goal={goal_mappings.get(row[0], [])}, rider={rider_map}"
            )

    evidence_rows = _ledger_rows(
        rider_text,
        (
            "ID",
            "Proves",
            "Level",
            "Existing path/environment",
            "Command or flow",
            "Expected observation",
            "Mock boundary",
            "Addition rule",
        ),
        r"E\d+",
        "closed evidence inventory",
        errors,
    )
    rider_evidence_ids = [row[0] for row in evidence_rows]
    duplicate_e = _duplicates(rider_evidence_ids)
    if duplicate_e:
        errors.append(f"rider has duplicate evidence IDs: {duplicate_e}")
    mapped_evidence = sorted(
        {item for values in goal_mappings.values() for item in values}, key=_natural_id
    )
    if not rider_evidence_ids:
        errors.append("rider closed evidence inventory has no E* rows")
    if set(rider_evidence_ids) != set(mapped_evidence):
        errors.append(
            "goal/rider evidence sets differ: "
            f"goal={mapped_evidence}, rider={sorted(set(rider_evidence_ids), key=_natural_id)}"
        )
    evidence_levels: dict[str, str] = {}
    for row in evidence_rows:
        if len(row) != 8:
            errors.append(f"{row[0]} evidence row must have eight columns")
            continue
        proves = sorted(set(re.findall(r"\bO\d+\b", row[1])), key=_natural_id)
        if not proves:
            errors.append(f"{row[0]} evidence row proves no obligations")
        if row[2].lower() not in EVIDENCE_LEVELS:
            errors.append(f"{row[0]} has invalid evidence level: {row[2]}")
        else:
            evidence_levels[row[0]] = row[2].lower()
        for column, label in zip(
            row[3:],
            (
                "existing path/environment",
                "command or flow",
                "expected observation",
                "mock boundary",
                "addition rule",
            ),
        ):
            if not column:
                errors.append(f"{row[0]} evidence row has an empty {label}")
        if NEW_PROOF_SUPPORT.search(" ".join(row[3:])):
            warnings.append(f"{row[0]} proposes new proof support; review shortest-valid-proof justification")
        expected_proves = sorted(
            [obligation for obligation, values in goal_mappings.items() if row[0] in values],
            key=_natural_id,
        )
        if proves != expected_proves:
            errors.append(
                f"{row[0]} proves/mapping obligations differ: row={proves}, goal={expected_proves}"
            )

    _check_descope_plan(
        rider_text,
        set(selected_modules),
        goal_mappings,
        evidence_levels,
        errors,
    )

    units = _unit_blocks(rider_text, errors)
    unit_obligations: set[str] = set()
    unit_evidence: set[str] = set()
    for unit_id, block in sorted(units.items(), key=lambda item: _natural_id(item[0])):
        fields: dict[str, str] = {}
        for label in (
            "Advances",
            "Delivers",
            "Owns",
            "Prerequisite",
            "Evidence closed",
            "Depends on",
            "Provenance",
            "Stop if",
        ):
            value = _unit_field(block, label)
            if value is None or not value:
                errors.append(f"{unit_id} is missing {label}: with a concrete value")
            else:
                fields[label] = value
        advances = set(re.findall(r"\bO\d+\b", fields.get("Advances", "")))
        closes = set(re.findall(r"\bE\d+\b", fields.get("Evidence closed", "")))
        dependencies = set(re.findall(r"\bU\d+\b", fields.get("Depends on", "")))
        if not advances:
            errors.append(f"{unit_id} advances no obligations")
        if not closes:
            errors.append(f"{unit_id} closes no evidence")
        if unit_id in dependencies:
            errors.append(f"{unit_id} depends on itself")
        unit_obligations.update(advances)
        unit_evidence.update(closes)
    if set(goal_obligations) - unit_obligations:
        errors.append(
            "obligations absent from execution units: "
            f"{sorted(set(goal_obligations) - unit_obligations, key=_natural_id)}"
        )
    if set(mapped_evidence) - unit_evidence:
        errors.append(
            "evidence absent from execution-unit closure: "
            f"{sorted(set(mapped_evidence) - unit_evidence, key=_natural_id)}"
        )

    all_definitions = {
        "O": set(rider_obligation_ids),
        "U": set(units),
        "E": set(rider_evidence_ids),
    }
    for source_label, source_text in (("goal", goal_text), ("rider", rider_text)):
        for identifier in sorted(set(ID_PATTERN.findall(source_text)), key=_natural_id):
            if identifier not in all_definitions[identifier[0]]:
                errors.append(f"{source_label} references undefined {identifier}")

    if execution_root and execution_root.is_dir():
        _check_substrate_paths(
            rider_text,
            execution_root,
            errors,
            warnings,
        )
        _check_inherited_sources(rider_text, execution_root, errors)
        git_root = _nearest_git_root(execution_root)
        if git_root and execution_root.resolve() != git_root.resolve():
            warnings.append(f"execution root differs from repository root: {execution_root} != {git_root}")
        if git_root and (
            not source_revision
            or source_revision.lower().startswith(("none", "unknown", "unavailable"))
        ):
            warnings.append("Git project has no source-revision anchor")

    manifest: dict[str, object] | None = None
    if pair_id and source_revision and execution_root:
        manifest = {
            "pair_id": pair_id,
            "goal_sha256": _sha256(goal),
            "rider_sha256": _sha256(rider),
            "goal_bytes": goal_bytes,
            "source_revision": source_revision,
            "execution_root": str(execution_root),
            "obligations": sorted(set(goal_obligations), key=_natural_id),
            "evidence": sorted(set(mapped_evidence), key=_natural_id),
            "selected_modules": selected_modules,
        }
        if expected_manifest_sha256:
            if not re.fullmatch(r"[0-9a-fA-F]{64}", expected_manifest_sha256):
                errors.append("expected manifest SHA-256 must be exactly 64 hexadecimal characters")
            elif manifest_sha256(manifest) != expected_manifest_sha256.lower():
                errors.append("activation manifest SHA-256 does not match expected manifest hash")

    errors = _dedupe_sorted(errors)
    warnings = _dedupe_sorted(warnings)
    return errors, warnings, manifest if not errors else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate an evidence-closed goal/rider pair and emit its activation manifest."
    )
    parser.add_argument("goal", type=Path)
    parser.add_argument("rider", type=Path)
    parser.add_argument(
        "--expected-manifest-sha256",
        metavar="SHA256",
        help="fail unless the canonical activation manifest has this SHA-256",
    )
    args = parser.parse_args(argv)
    errors, warnings, manifest = validate_pair(
        args.goal,
        args.rider,
        expected_manifest_sha256=args.expected_manifest_sha256,
    )
    for warning in warnings:
        print(f"WARN: {warning}", file=sys.stderr)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    assert manifest is not None
    print(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
