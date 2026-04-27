#!/usr/bin/env python3
import json
import sys
from pathlib import Path

REQUIRED = {
    "id",
    "created_at",
    "observed_window_start_utc",
    "observed_window_end_utc",
    "thread_id",
    "session_title",
    "cwd",
    "category",
    "confidence",
    "summary",
    "evidence",
    "proposed_destination",
    "verification_needed",
    "status",
    "notes",
}

OPTIONAL_REVIEW_FIELDS = {
    "reviewed_at",
    "reviewed_by",
    "decision",
    "destination",
    "reason",
    "superseded_by",
}

ALLOWED_CATEGORIES = {
    "active_work",
    "completed_work",
    "durable_fact",
    "possible_action",
    "possible_decision",
    "project_status",
    "system_learning",
    "needs_verification",
    "noise",
}

ALLOWED_DESTINATIONS = {
    "ignore",
    "cos_review",
    "action_ledger",
    "decision_queue",
    "domain_note",
    "project_note",
    "knowledge",
    "skill_update",
    "source_verification",
}

ALLOWED_CONFIDENCE = {"high", "medium", "low"}
ALLOWED_STATUS = {
    "new",
    "promoted",
    "dismissed",
    "superseded",
    "needs_verification",
    "ignored_noise",
}
ALLOWED_DECISION = ALLOWED_STATUS - {"new"}


def validate_candidate(line_no: int, obj: dict) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED - set(obj))
    if missing:
        errors.append(f"line {line_no}: missing fields: {', '.join(missing)}")

    extra = sorted(set(obj) - REQUIRED - OPTIONAL_REVIEW_FIELDS)
    if extra:
        errors.append(f"line {line_no}: unexpected fields: {', '.join(extra)}")

    if obj.get("category") not in ALLOWED_CATEGORIES:
        errors.append(f"line {line_no}: invalid category {obj.get('category')!r}")
    if obj.get("proposed_destination") not in ALLOWED_DESTINATIONS:
        errors.append(
            f"line {line_no}: invalid proposed_destination {obj.get('proposed_destination')!r}"
        )
    if obj.get("confidence") not in ALLOWED_CONFIDENCE:
        errors.append(f"line {line_no}: invalid confidence {obj.get('confidence')!r}")
    if obj.get("verification_needed") is not True and obj.get("verification_needed") is not False:
        errors.append(f"line {line_no}: verification_needed must be boolean")
    if obj.get("status") not in ALLOWED_STATUS:
        errors.append(f"line {line_no}: invalid status {obj.get('status')!r}")
    if obj.get("status") != "new":
        if obj.get("decision") not in ALLOWED_DECISION:
            errors.append(f"line {line_no}: reviewed candidates need a lifecycle decision")
        if not obj.get("reviewed_at"):
            errors.append(f"line {line_no}: reviewed candidates need reviewed_at")
        if not obj.get("reviewed_by"):
            errors.append(f"line {line_no}: reviewed candidates need reviewed_by")
        if not obj.get("reason"):
            errors.append(f"line {line_no}: reviewed candidates need reason")
    evidence = obj.get("evidence")
    if not isinstance(evidence, list) or not all(isinstance(item, str) for item in evidence):
        errors.append(f"line {line_no}: evidence must be a list of strings")
    return errors


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        Path.home() / "LifeOps" / "vault/Operations/.machine/codex-session-harvest/outbox.jsonl"
    )
    errors: list[str] = []
    for line_no, raw in enumerate(path.read_text().splitlines(), 1):
        if not raw.strip():
            continue
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"line {line_no}: invalid JSON: {exc}")
            continue
        if obj.get("type") == "system":
            continue
        errors.extend(validate_candidate(line_no, obj))

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("codex-session-harvest outbox ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
