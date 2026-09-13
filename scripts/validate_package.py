from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Sequence


PLUGIN_NAME = "no-slop"
PLUGIN_ROOT = Path("plugins/no-slop")
SKILL_ROOT = PLUGIN_ROOT / "skills/no-slop"
SEMVER_PATTERN = re.compile(
    r"^(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)"
    r"(?:-(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)(?:\.(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
MARKDOWN_LINK_PATTERN = re.compile(r"(?<!\!)\[[^\]]*\]\(([^)]+)\)")
REQUIRED_SKILL_RESOURCES = (
    Path("SKILL.md"),
    Path("agents/openai.yaml"),
    Path("references/rules.md"),
    Path("references/genres.md"),
    Path("references/comprehension.md"),
)
REQUIRED_CODEX_INTERFACE_FIELDS = (
    "displayName",
    "shortDescription",
    "longDescription",
    "developerName",
    "category",
    "capabilities",
    "defaultPrompt",
)


def validate_package(root: Path | str) -> list[str]:
    """Return deterministic package-contract violations for ``root``.

    The validator intentionally checks only JSON, Markdown links, and filesystem
    invariants. It requires the OpenAI YAML resource to exist but does not parse
    YAML, whose full grammar is outside this distribution check.
    """

    root = Path(root)
    errors: list[str] = []

    claude_manifest = _load_json(
        root / PLUGIN_ROOT / ".claude-plugin/plugin.json", "Claude manifest", errors
    )
    codex_manifest = _load_json(
        root / PLUGIN_ROOT / ".codex-plugin/plugin.json", "Codex manifest", errors
    )

    claude_version = _validate_manifest(claude_manifest, "Claude", errors)
    codex_version = _validate_manifest(codex_manifest, "Codex", errors, codex=True)
    if claude_version is not None and codex_version is not None and claude_version != codex_version:
        errors.append("Claude and Codex manifest versions must match")

    _validate_license(root / "LICENSE", errors)
    _validate_skill_resources(root, errors)
    return errors


def _load_json(path: Path, label: str, errors: list[str]) -> dict[str, Any] | None:
    try:
        content = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append(f"{label} is missing: {path}")
        return None
    except (OSError, UnicodeError) as exc:
        errors.append(f"{label} cannot be read: {exc}")
        return None

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        errors.append(f"{label} contains invalid JSON: {exc.msg}")
        return None

    if not isinstance(parsed, dict):
        errors.append(f"{label} JSON must be an object")
        return None
    return parsed


def _validate_manifest(
    manifest: dict[str, Any] | None, label: str, errors: list[str], *, codex: bool = False
) -> str | None:
    if manifest is None:
        return None

    if manifest.get("name") != PLUGIN_NAME:
        errors.append(f"{label} manifest name must be {PLUGIN_NAME!r}")

    version = manifest.get("version")
    if not isinstance(version, str) or not SEMVER_PATTERN.fullmatch(version):
        errors.append(f"{label} manifest version must be a valid semantic version")
        version = None

    author = manifest.get("author")
    if not isinstance(author, dict) or not isinstance(author.get("name"), str) or not author["name"].strip():
        errors.append(f"{label} manifest author.name is required")

    if manifest.get("license") != "MIT":
        errors.append(f"{label} manifest license must be MIT")

    if codex:
        _validate_codex_fields(manifest, errors)

    return version


def _validate_codex_fields(manifest: dict[str, Any], errors: list[str]) -> None:
    if manifest.get("skills") != "./skills/":
        errors.append("Codex manifest skills must be './skills/'")

    interface = manifest.get("interface")
    if not isinstance(interface, dict):
        errors.append("Codex manifest interface is required")
        return

    for field in REQUIRED_CODEX_INTERFACE_FIELDS:
        value = interface.get(field)
        if isinstance(value, str):
            valid = bool(value.strip())
        elif field in {"capabilities", "defaultPrompt"}:
            valid = isinstance(value, list) and bool(value) and all(
                isinstance(item, str) and item.strip() for item in value
            )
        else:
            valid = False
        if not valid:
            errors.append(f"Codex manifest interface.{field} is required")

    if interface.get("category") != "Productivity":
        errors.append("Codex manifest interface category must be 'Productivity'")




def _validate_license(path: Path, errors: list[str]) -> None:
    try:
        license_text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append("MIT LICENSE is missing")
        return
    except (OSError, UnicodeError) as exc:
        errors.append(f"MIT LICENSE cannot be read: {exc}")
        return

    required_phrases = (
        "MIT License",
        "Permission is hereby granted, free of charge",
        'THE SOFTWARE IS PROVIDED "AS IS"',
    )
    if not all(phrase in license_text for phrase in required_phrases):
        errors.append("MIT LICENSE does not contain the required MIT terms")


def _validate_skill_resources(root: Path, errors: list[str]) -> None:
    skill_root = root / SKILL_ROOT
    for relative_path in REQUIRED_SKILL_RESOURCES:
        resource = skill_root / relative_path
        if not resource.is_file():
            errors.append(f"required skill resource is missing: {SKILL_ROOT / relative_path}")

    if not (skill_root / "SKILL.md").is_file():
        return

    for markdown_file in sorted(skill_root.rglob("*.md")):
        _validate_markdown_links(markdown_file, skill_root, errors)


def _validate_markdown_links(markdown_file: Path, skill_root: Path, errors: list[str]) -> None:
    try:
        contents = markdown_file.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"skill resource cannot be read: {markdown_file}: {exc}")
        return

    editable_contents = _editable_markdown(contents)
    if "\N{EM DASH}" in editable_contents:
        errors.append(f"editable skill prose contains an em dash: {markdown_file}")

    for match in MARKDOWN_LINK_PATTERN.finditer(editable_contents):
        destination = match.group(1).strip().strip("<>")
        destination = destination.split(maxsplit=1)[0].split("#", 1)[0]
        if not destination or "://" in destination or destination.startswith(("mailto:", "/", "#")):
            continue

        resolved = (markdown_file.parent / destination).resolve()
        if not _is_relative_to(resolved, skill_root.resolve()) or not resolved.is_file():
            errors.append(f"unresolved skill reference in {markdown_file}: {destination}")


def _editable_markdown(contents: str) -> str:
    editable_lines: list[str] = []
    fence_character: str | None = None
    fence_length = 0

    for line in contents.splitlines():
        fence = re.match(r" {0,3}(`{3,}|~{3,})", line)
        if fence_character is not None:
            closing = re.match(
                rf" {{0,3}}{re.escape(fence_character)}{{{fence_length},}}\s*$", line
            )
            if closing:
                fence_character = None
                fence_length = 0
            continue
        if fence:
            delimiter = fence.group(1)
            fence_character = delimiter[0]
            fence_length = len(delimiter)
            continue
        if line.lstrip().startswith(">"):
            continue

        editable = re.sub(r"`+[^`\n]*`+", "", line)
        editable = re.sub(r'"(?:\\.|[^"\\])*"', "", editable)
        editable = re.sub(r"“[^”\n]*”", "", editable)
        editable_lines.append(editable)

    return "\n".join(editable_lines)




def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the no-slop package contract.")
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)

    errors = validate_package(args.root)
    if errors:
        print("Package validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Package validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
