"""Evaluate a fresh, minimal Codex usage snapshot. No network or file writes."""

import argparse
import json
import math
from pathlib import Path


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def evaluate(usage, state=None, limit_id="codex", *, heartbeat=False,
             expected_thread_id=None, expected_work_id=None, expected_pause_generation=None):
    state = state or {}
    expected = {"thread_id": expected_thread_id, "work_id": expected_work_id,
                "pause_generation": expected_pause_generation}
    if heartbeat:
        if any(not isinstance(value, str) or not value.strip() for value in expected.values()):
            return {"action": "unknown", "reason": "Heartbeat requires all three expected identifiers"}
        if any(state.get(key) != value for key, value in expected.items()):
            return {"action": "ignore", "reason": "Stale or unrelated heartbeat; do not change automation"}
        if state.get("status") != "paused_limit":
            return {"action": "ignore", "reason": "Task is not paused by limit; do not change automation"}
    elif any(value is not None for value in expected.values()):
        return {"action": "unknown", "reason": "Expected identifiers require explicit heartbeat mode"}
    status = state.get("status", "running")
    if status in {"completed", "cancelled", "waiting_user", "paused_user"}:
        return {"action": "inactive", "reason": status}
    if status not in {"running", "preparing", "paused_limit"}:
        return {"action": "unknown", "reason": "Unknown task state"}
    paused = status == "paused_limit"
    if "rateLimitsByLimitId" in usage and usage["rateLimitsByLimitId"] is not None:
        buckets = usage["rateLimitsByLimitId"]
        bucket = buckets.get(limit_id) if isinstance(buckets, dict) else None
    else:
        bucket = usage.get("rateLimits")
        if isinstance(bucket, dict) and bucket.get("limitId", limit_id) != limit_id:
            bucket = None
    if not isinstance(bucket, dict):
        return {"action": "unknown", "reason": "Requested rate-limit bucket unavailable"}
    windows = [bucket[key] for key in ("primary", "secondary") if isinstance(bucket.get(key), dict)]
    five = [window for window in windows if window.get("windowDurationMins") == 300]
    if len(five) != 1:
        return {"action": "unknown", "reason": "Five-hour window missing or ambiguous"}
    current = five[0]
    used = current.get("usedPercent")
    if not number(used) or not 0 <= used <= 100:
        return {"action": "unknown", "reason": "Five-hour usage unavailable or invalid"}
    remaining = 100 - used
    reset = current.get("resetsAt")
    reset = reset if number(reset) and reset > 0 else None
    result = {"limit_id": limit_id, "remaining_percent": remaining, "resets_at": reset}
    blocked = usage.get("ordinaryUsageAllowed") is False or bucket.get("spendControlReached") is True
    other_exhausted = [window for window in windows if window is not current
                       and number(window.get("usedPercent")) and window["usedPercent"] >= 100]
    if blocked or other_exhausted:
        resets = [window.get("resetsAt") for window in other_exhausted]
        if remaining <= 1:
            resets.append(reset)
        known_resets = [value for value in resets if number(value) and value > 0]
        return {**result, "action": "wait" if paused else "pause",
                "reason": "Another limit blocks work", "retry_after": max(known_resets, default=None)}
    if paused:
        old_used = state.get("paused_used_percent")
        old_reset = state.get("paused_resets_at")
        restored = ((number(old_used) and used < old_used)
                    or (number(old_reset) and reset is not None and reset > old_reset))
        if remaining > 5 and restored:
            return {**result, "action": "resume", "reason": "Fresh limits show recovery"}
        return {**result, "action": "wait", "reason": "Recovery not confirmed", "retry_after": reset}
    if remaining <= 1:
        return {**result, "action": "pause", "reason": "One percent or less remains", "retry_after": reset}
    if remaining <= 5:
        return {**result, "action": "prepare", "reason": "Five percent or less remains"}
    return {**result, "action": "continue", "reason": "More than five percent remains"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--usage", type=Path, required=True)
    parser.add_argument("--state", type=Path)
    parser.add_argument("--limit-id", default="codex")
    parser.add_argument("--heartbeat", action="store_true",
                        help="Evaluate a callback only for the expected paused task")
    parser.add_argument("--expected-thread-id")
    parser.add_argument("--expected-work-id")
    parser.add_argument("--expected-pause-generation")
    args = parser.parse_args()
    expected = (args.expected_thread_id, args.expected_work_id, args.expected_pause_generation)
    if args.heartbeat and (not args.state or any(not value or not value.strip() for value in expected)):
        parser.error("--heartbeat requires --state and all three --expected-* identifiers")
    if not args.heartbeat and any(value is not None for value in expected):
        parser.error("--expected-* identifiers require --heartbeat")
    usage = json.loads(args.usage.read_text(encoding="utf-8-sig"))
    state = json.loads(args.state.read_text(encoding="utf-8-sig")) if args.state else {}
    if not isinstance(usage, dict) or not isinstance(state, dict):
        parser.error("Usage and state must be JSON objects")
    result = evaluate(usage, state, args.limit_id, heartbeat=args.heartbeat,
                      expected_thread_id=args.expected_thread_id,
                      expected_work_id=args.expected_work_id,
                      expected_pause_generation=args.expected_pause_generation)
    print(json.dumps(result, ensure_ascii=False, allow_nan=False))


if __name__ == "__main__":
    main()
