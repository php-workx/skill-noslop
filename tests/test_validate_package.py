from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.validate_package import validate_package


MIT_LICENSE = """MIT License

Copyright (c) 2026 No Slop Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the \"Software\"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


class ValidatePackageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.package_root = Path(self.temporary_directory.name)
        self._write_valid_package()

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def _write_valid_package(self) -> None:
        self._write_json(
            "plugins/no-slop/.claude-plugin/plugin.json",
            {
                "name": "no-slop",
                "version": "0.1.0",
                "description": "Make AI-generated prose plain and direct.",
                "author": {"name": "No Slop Contributors"},
                "license": "MIT",
                "keywords": ["writing"],
            },
        )
        self._write_json(
            "plugins/no-slop/.codex-plugin/plugin.json",
            {
                "name": "no-slop",
                "version": "0.1.0",
                "description": "Make AI-generated prose plain and direct.",
                "author": {"name": "No Slop Contributors"},
                "license": "MIT",
                "keywords": ["writing"],
                "skills": "./skills/",
                "interface": {
                    "displayName": "No Slop",
                    "shortDescription": "Make AI prose plain and direct.",
                    "longDescription": "Removes formulaic AI rhetoric.",
                    "developerName": "No Slop Contributors",
                    "category": "Productivity",
                    "capabilities": ["Edit"],
                    "defaultPrompt": ["Use $no-slop to make this prose direct and plain."],
                },
            },
        )
        self._write("LICENSE", MIT_LICENSE)
        self._write(
            "plugins/no-slop/skills/no-slop/SKILL.md",
            "---\nname: no-slop\ndescription: Plain prose.\n---\n\n"
            "Read [rules](references/rules.md), [genres](references/genres.md), and [comprehension](references/comprehension.md).\n",
        )
        self._write(
            "plugins/no-slop/skills/no-slop/agents/openai.yaml",
            "interface:\n  display_name: No Slop\n",
        )
        self._write("plugins/no-slop/skills/no-slop/references/rules.md", "Rules.\n")
        self._write("plugins/no-slop/skills/no-slop/references/genres.md", "Genres.\n")
        self._write("plugins/no-slop/skills/no-slop/references/comprehension.md", "Comprehension.\n")

    def _write_json(self, relative_path: str, content: object) -> None:
        self._write(relative_path, json.dumps(content))

    def _write(self, relative_path: str, content: str) -> None:
        path = self.package_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def _read_json(self, relative_path: str) -> dict[str, object]:
        return json.loads((self.package_root / relative_path).read_text(encoding="utf-8"))

    def _mutate_json(self, relative_path: str, mutate) -> None:
        content = self._read_json(relative_path)
        mutate(content)
        self._write_json(relative_path, content)

    def assert_valid(self) -> None:
        self.assertEqual([], validate_package(self.package_root))

    def assert_rejected(self, expected_error: str) -> None:
        self.assertTrue(
            any(expected_error in error for error in validate_package(self.package_root)),
            f"Expected {expected_error!r} in validation errors",
        )

    def test_accepts_a_complete_valid_package(self) -> None:
        self.assert_valid()

    def test_rejects_malformed_json(self) -> None:
        self._write("plugins/no-slop/.claude-plugin/plugin.json", "{")

        self.assert_rejected("invalid JSON")

    def test_rejects_missing_or_mismatched_plugin_name(self) -> None:
        self._mutate_json(
            "plugins/no-slop/.claude-plugin/plugin.json", lambda manifest: manifest.pop("name")
        )
        self.assert_rejected("Claude manifest name")

        self._write_valid_package()
        self._mutate_json(
            "plugins/no-slop/.codex-plugin/plugin.json",
            lambda manifest: manifest.__setitem__("name", "other-plugin"),
        )
        self.assert_rejected("Codex manifest name")

    def test_rejects_invalid_semver(self) -> None:
        self._mutate_json(
            "plugins/no-slop/.claude-plugin/plugin.json",
            lambda manifest: manifest.__setitem__("version", "0.1"),
        )

        self.assert_rejected("valid semantic version")

    def test_rejects_missing_codex_author_or_interface_fields(self) -> None:
        self._mutate_json(
            "plugins/no-slop/.codex-plugin/plugin.json", lambda manifest: manifest.pop("author")
        )
        self.assert_rejected("Codex manifest author.name")

        self._write_valid_package()
        self._mutate_json(
            "plugins/no-slop/.codex-plugin/plugin.json", lambda manifest: manifest.pop("interface")
        )
        self.assert_rejected("Codex manifest interface")


    def test_rejects_missing_skill_resources(self) -> None:
        (self.package_root / "plugins/no-slop/skills/no-slop/agents/openai.yaml").unlink()

        self.assert_rejected("required skill resource")

    def test_rejects_missing_comprehension_resource(self) -> None:
        (
            self.package_root
            / "plugins/no-slop/skills/no-slop/references/comprehension.md"
        ).unlink()

        self.assert_rejected("required skill resource")

    def test_rejects_unresolved_reference_links(self) -> None:
        (self.package_root / "plugins/no-slop/skills/no-slop/references/rules.md").unlink()

        self.assert_rejected("unresolved skill reference")

    def test_ignores_reference_links_in_protected_markdown(self) -> None:
        path = self.package_root / "plugins/no-slop/skills/no-slop/references/rules.md"
        path.write_text(
            "Rules.\n\n"
            "```markdown\n[example](missing-fenced.md)\n```\n\n"
            "`[example](missing-inline.md)`\n\n"
            "> [Example](missing-quote.md)\n\n"
            "A literal quotation says “[example](missing-literal.md).”\n",
            encoding="utf-8",
        )

        self.assert_valid()

    def test_rejects_em_dash_in_editable_skill_prose(self) -> None:
        path = self.package_root / "plugins/no-slop/skills/no-slop/references/genres.md"
        path.write_text(path.read_text(encoding="utf-8") + "Forbidden — dash.\n", encoding="utf-8")

        self.assert_rejected("em dash")

    def test_reports_markdown_violations_in_path_order(self) -> None:
        references = self.package_root / "plugins/no-slop/skills/no-slop/references"
        rules = references / "rules.md"
        genres = references / "genres.md"
        rules.write_text("Rules — invalid.\n", encoding="utf-8")
        genres.write_text("Genres — invalid.\n", encoding="utf-8")

        with patch.object(Path, "rglob", return_value=[rules, genres]):
            violations = [
                error for error in validate_package(self.package_root) if "em dash" in error
            ]
        self.assertEqual(
            [
                f"editable skill prose contains an em dash: {genres}",
                f"editable skill prose contains an em dash: {rules}",
            ],
            violations,
        )

    def test_allows_em_dash_in_protected_markdown(self) -> None:
        path = self.package_root / "plugins/no-slop/skills/no-slop/references/genres.md"
        path.write_text(
            "Rules.\n\n"
            "```text\nprotected — code\n```\n\n"
            "`protected — inline code`\n\n"
            "> Protected — block quotation.\n\n"
            "A literal quotation says “protected — quotation.”\n",
            encoding="utf-8",
        )

        self.assert_valid()

    def test_rejects_a_missing_mit_license(self) -> None:
        (self.package_root / "LICENSE").unlink()

        self.assert_rejected("MIT LICENSE")

    def test_rejects_unequal_manifest_versions(self) -> None:
        self._mutate_json(
            "plugins/no-slop/.codex-plugin/plugin.json",
            lambda manifest: manifest.__setitem__("version", "0.2.0"),
        )

        self.assert_rejected("manifest versions")


if __name__ == "__main__":
    unittest.main()
