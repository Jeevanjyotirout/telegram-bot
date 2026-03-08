"""
GuardBot Utility Helpers
"""

import re
from typing import Optional


def sanitize_text(text: str) -> str:
    """Remove control characters and trim whitespace."""
    return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text).strip()


def truncate(text: str, max_len: int = 200) -> str:
    """Truncate a string for storage / display."""
    return text[:max_len] + "…" if len(text) > max_len else text


def user_mention_md(user_id: int, display: str) -> str:
    """Return a Markdown-safe inline mention."""
    return f"[{display}](tg://user?id={user_id})"


def format_violations_summary(violations: list) -> str:
    if not violations:
        return "No violations recorded."
    lines = []
    for v in violations[:10]:  # Show last 10
        lines.append(
            f"• {v.violation_date.strftime('%Y-%m-%d')} | "
            f"{v.violation_type} | {v.action_taken or 'N/A'}"
        )
    return "\n".join(lines)
