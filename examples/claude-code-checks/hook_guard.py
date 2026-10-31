"""PreToolUse fixture: allow only Read. It never executes the requested tool.

This is a teaching allowlist, not a complete production security boundary.
It is intentionally NOT installed into Claude Code automatically.
"""
import json
import sys


def main():
    try:
        payload = json.load(sys.stdin)
        if not isinstance(payload, dict) or not isinstance(payload.get("tool_input"), dict):
            raise ValueError("invalid event")
        if payload.get("tool_name") == "Read":
            return 0
        print("Teaching guard: only Read is allowed; no requested action was executed.", file=sys.stderr)
        return 2
    except (ValueError, TypeError):
        print("Teaching guard: malformed input; request blocked.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
