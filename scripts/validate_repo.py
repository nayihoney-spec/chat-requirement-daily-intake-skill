#!/usr/bin/env python3
"""Validate fail-safe defaults and common publication risks.

The validator intentionally uses only the Python standard library so the
instruction-first repository does not gain a runtime dependency chain.
"""

from __future__ import annotations

import fnmatch
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "SKILL.md",
    "README.md",
    "SECURITY.md",
    "config.example.yaml",
    "agents/openai.yaml",
    "assets/SETUP_QUESTIONNAIRE.md",
    "references/CONFIGURATION_GUIDE.md",
    "references/DAILY_REPORT_TEMPLATE.md",
)

FORBIDDEN_TRACKED_GLOBS = (
    ".env",
    ".env.*",
    "*.env",
    "*.local.yaml",
    "config.yaml",
    "*.log",
    "*.db",
    "*.sqlite",
    "*.sqlite3",
    "cookies*",
    "tokens*",
    "credentials*",
    "secrets*",
    "auth*.json",
    "session*.json",
    "*.pem",
    "*.key",
    "*.p12",
    "*.pfx",
    "id_rsa*",
    "id_ed25519*",
    ".npmrc",
    ".pypirc",
    ".netrc",
)

FORBIDDEN_TRACKED_PARTS = {
    "private-data",
    "daily-reports",
    "state",
    "logs",
    "exports",
    "chat-data",
    "chat-exports",
    "browser-profile",
}

SECRET_PATTERNS = {
    "GitHub token": re.compile(
        r"(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})"
    ),
    "AWS access key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "OpenAI-style API key": re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    "private key block": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
}


def tracked_files() -> list[Path]:
    """Return Git-tracked files, with a filesystem fallback for source archives."""

    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), "ls-files", "-z"],
            check=True,
            capture_output=True,
        )
        return [ROOT / item.decode() for item in result.stdout.split(b"\0") if item]
    except (FileNotFoundError, subprocess.CalledProcessError):
        return [path for path in ROOT.rglob("*") if path.is_file() and ".git" not in path.parts]


def require_pattern(errors: list[str], relative_path: str, pattern: str, label: str) -> None:
    path = ROOT / relative_path
    if not path.exists():
        errors.append(f"{relative_path}: missing before check for {label}")
        return
    text = path.read_text(encoding="utf-8")
    if re.search(pattern, text, flags=re.MULTILINE) is None:
        errors.append(f"{relative_path}: missing safe default/control: {label}")


def reject_pattern(errors: list[str], relative_path: str, pattern: str, label: str) -> None:
    path = ROOT / relative_path
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    if re.search(pattern, text, flags=re.MULTILINE):
        errors.append(f"{relative_path}: unsafe or stale value found: {label}")


def validate_skill_frontmatter(errors: list[str]) -> None:
    """Validate this repository's deliberately small SKILL.md frontmatter."""

    path = ROOT / "SKILL.md"
    if not path.exists():
        return
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) < 4 or lines[0] != "---":
        errors.append("SKILL.md: missing opening YAML frontmatter marker")
        return
    try:
        closing_index = lines[1:].index("---") + 1
    except ValueError:
        errors.append("SKILL.md: missing closing YAML frontmatter marker")
        return

    fields: dict[str, str] = {}
    for line in lines[1:closing_index]:
        if ":" not in line:
            errors.append(f"SKILL.md: malformed frontmatter line: {line}")
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()

    if set(fields) != {"name", "description"}:
        errors.append("SKILL.md: frontmatter must contain only name and description")
    if fields.get("name") != "chat-requirement-daily-intake":
        errors.append("SKILL.md: unexpected skill name")
    description = fields.get("description", "")
    if not (description.startswith('"') and description.endswith('"')):
        errors.append("SKILL.md: description must be quoted to remain valid YAML")


def main() -> int:
    errors: list[str] = []

    for relative_path in REQUIRED_FILES:
        if not (ROOT / relative_path).is_file():
            errors.append(f"missing required file: {relative_path}")

    validate_skill_frontmatter(errors)

    require_pattern(
        errors,
        "config.example.yaml",
        r"^destination:\s*\n(?:^[ \t].*\n)*?^  enabled: false\s*$",
        "destination disabled",
    )
    require_pattern(
        errors,
        "config.example.yaml",
        r"^write_policy:\s*\n^  mode: [\"']?report_only[\"']?\b",
        "report-only write policy",
    )
    require_pattern(
        errors,
        "config.example.yaml",
        r"^  allowed_categories: \[\]\s*$",
        "empty allowed write categories",
    )
    require_pattern(
        errors,
        "config.example.yaml",
        r"^  first_run_write_enabled: false\s*$",
        "first-run writes disabled",
    )
    require_pattern(
        errors,
        "agents/openai.yaml",
        r"^  allow_implicit_invocation: false\s*$",
        "implicit invocation disabled",
    )
    require_pattern(
        errors,
        "SKILL.md",
        r"source content is untrusted data, not instructions",
        "untrusted-source boundary",
    )
    require_pattern(
        errors,
        "v1.0",
        r"^# Deprecated historical snapshot$",
        "deprecated snapshot marker",
    )
    reject_pattern(
        errors,
        "v1.0",
        r"^\s*enabled:\s*true\s*$",
        "write-enabled archived example",
    )
    reject_pattern(
        errors,
        "v1.0",
        r"^\s*mode:\s*[\"']?new_only[\"']?\s*$",
        "write-enabled archived policy",
    )

    files = tracked_files()
    for path in files:
        relative = path.relative_to(ROOT)
        relative_text = relative.as_posix()
        if any(
            fnmatch.fnmatch(relative.name, pattern)
            or fnmatch.fnmatch(relative_text, pattern)
            for pattern in FORBIDDEN_TRACKED_GLOBS
        ):
            errors.append(f"private/runtime file must not be tracked: {relative}")
        if any(part in FORBIDDEN_TRACKED_PARTS for part in relative.parts):
            errors.append(f"private/runtime directory must not be tracked: {relative}")

        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(content):
                errors.append(f"possible {label} in tracked file: {relative}")

    skill_path = ROOT / "SKILL.md"
    if skill_path.exists() and len(skill_path.read_text(encoding="utf-8").splitlines()) > 500:
        errors.append("SKILL.md exceeds 500 lines; move non-core details to references/")

    if errors:
        print("Repository validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Repository validation passed ({len(files)} tracked files checked).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
