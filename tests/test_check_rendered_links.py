from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "check_rendered_links.py"
SPEC = importlib.util.spec_from_file_location("check_rendered_links", SCRIPT)
assert SPEC and SPEC.loader
CHECKER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECKER
SPEC.loader.exec_module(CHECKER)


class RenderedLinkCheckerTests(unittest.TestCase):
    def run_check(self, files: dict[str, str], base_url: str) -> list[str]:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative, content in files.items():
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
            _, failures = CHECKER.check_output(root, base_url)
            return failures

    def test_missing_page_and_asset_fail(self) -> None:
        failures = self.run_check({"index.html": '<a href="missing/">x</a><img src="nope.png">'}, "https://example.invalid/")
        self.assertEqual(2, len(failures))

    def test_valid_and_missing_anchors(self) -> None:
        files = {"index.html": '<a href="docs/#good">yes</a><a href="docs/#bad">no</a>', "docs/index.html": '<h1 id="good">Docs</h1><a name="named"></a>'}
        failures = self.run_check(files, "https://example.invalid/")
        self.assertEqual(1, len(failures))
        self.assertIn("#bad", failures[0])

    def test_nested_relative_and_directory_index(self) -> None:
        files = {"docs/guide/index.html": '<a href="../">Docs</a><img src="../../assets/a%20b.png">', "docs/index.html": "docs", "assets/a b.png": "asset"}
        self.assertEqual([], self.run_check(files, "https://example.invalid/"))

    def test_root_and_absolute_same_origin_urls(self) -> None:
        files = {"index.html": '<a href="/docs/">one</a><a href="https://example.invalid/docs/">two</a><a href="//example.invalid/docs/">three</a>', "docs/index.html": "docs"}
        self.assertEqual([], self.run_check(files, "https://example.invalid/"))

    def test_subpath_rejects_prefix_escape(self) -> None:
        files = {"index.html": '<a href="/docs/">bad</a><a href="https://example.invalid/nagumix-check/docs/">good</a>', "docs/index.html": "docs"}
        failures = self.run_check(files, "https://example.invalid/nagumix-check/")
        self.assertEqual(1, len(failures))
        self.assertIn("escapes deployment prefix", failures[0])

    def test_external_and_non_http_targets_are_ignored(self) -> None:
        files = {"index.html": '<a href="https://outside.invalid/path">x</a><a href="mailto:hello@example.invalid">m</a><img src="data:image/png;base64,AA==">'}
        self.assertEqual([], self.run_check(files, "https://example.invalid/"))
