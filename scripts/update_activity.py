"""
Refresh the "Recent public activity" block in README.md from the GitHub events API.

    GITHUB_TOKEN=... python scripts/update_activity.py

Runs daily from .github/workflows/update-readme.yml. Stdlib only.
"""
import json
import os
import re
import urllib.request
from datetime import datetime
from pathlib import Path

USER = "Rohit-rockan"
README = Path(__file__).resolve().parent.parent / "README.md"
MAX_ITEMS = 6
SKIP_REPOS = {f"{USER}/{USER}"}  # the profile repo's own bot commits


def fetch_events() -> list[dict]:
    req = urllib.request.Request(f"https://api.github.com/users/{USER}/events/public?per_page=50")
    req.add_header("Accept", "application/vnd.github+json")
    if token := os.environ.get("GITHUB_TOKEN"):
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.load(resp)


def describe(event: dict) -> str | None:
    payload, kind = event["payload"], event["type"]
    if kind == "PushEvent":
        n = payload.get("size") or len(payload.get("commits", [])) or 1
        return f"pushed {n} commit{'s' if n != 1 else ''} to"
    if kind == "CreateEvent":
        return "created a repository" if payload.get("ref_type") == "repository" else f"created a {payload.get('ref_type')} in"
    if kind == "PullRequestEvent":
        return f"{payload.get('action')} a pull request in"
    if kind == "IssuesEvent":
        return f"{payload.get('action')} an issue in"
    if kind == "ReleaseEvent":
        return "published a release in"
    if kind == "WatchEvent":
        return "starred"
    if kind == "ForkEvent":
        return "forked"
    return None


def main():
    lines = []
    for event in fetch_events():
        repo = event["repo"]["name"]
        action = describe(event)
        if not action or repo in SKIP_REPOS:
            continue
        date = datetime.strptime(event["created_at"], "%Y-%m-%dT%H:%M:%SZ")
        line = f"- {date:%b} {date.day}, {date.year}: {action} [{repo}](https://github.com/{repo})."
        if line not in lines:
            lines.append(line)
        if len(lines) == MAX_ITEMS:
            break

    block = "\n".join(lines) or "- Nothing public yet this month."
    text = README.read_text(encoding="utf-8")
    new = re.sub(
        r"(<!-- AUTO:ACTIVITY:START -->\n).*?(<!-- AUTO:ACTIVITY:END -->)",
        lambda m: f"{m.group(1)}{block}\n{m.group(2)}",
        text,
        flags=re.S,
    )
    if new != text:
        README.write_text(new, encoding="utf-8")
        print("README updated")
    else:
        print("no change")


if __name__ == "__main__":
    main()
