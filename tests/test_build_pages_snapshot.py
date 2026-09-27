from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "build_pages_snapshot.py"
SPEC = importlib.util.spec_from_file_location("build_pages_snapshot", SCRIPT)
assert SPEC and SPEC.loader
PAGES = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = PAGES
SPEC.loader.exec_module(PAGES)


class PagesSnapshotTests(unittest.TestCase):
    def fake_builder(self, sha: str, requests: list[PAGES.BuildRequest]) -> None:
        for request in requests:
            request.destination.mkdir(parents=True, exist_ok=True)
            (request.destination / "index.html").write_text(
                f"{request.branch}\n{sha}\n{request.base_url}\n",
                encoding="utf-8",
            )

    def test_branch_paths_are_stable_and_resist_readable_slug_collisions(self) -> None:
        first = PAGES.branch_path("Feature/A")
        second = PAGES.branch_path("feature-a")
        self.assertTrue(first.startswith("feature-a-"))
        self.assertTrue(second.startswith("feature-a-"))
        self.assertNotEqual(first, second)
        self.assertEqual(first, PAGES.branch_path("Feature/A"))
        self.assertNotIn("/", first)

    def test_complete_rebuild_updates_tips_and_removes_stale_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "public"
            initial = [
                PAGES.BranchTip("main", "1" * 40),
                PAGES.BranchTip("Feature/A", "2" * 40),
                PAGES.BranchTip("feature-a", "3" * 40),
            ]
            PAGES.build_snapshot(output, "https://pages.example.test", initial, self.fake_builder)
            stale_path = output / "branches" / PAGES.branch_path("feature-a")
            (output / "stale.txt").write_text("stale", encoding="utf-8")

            updated = [
                PAGES.BranchTip("main", "1" * 40),
                PAGES.BranchTip("Feature/A", "4" * 40),
            ]
            PAGES.build_snapshot(output, "https://pages.example.test", updated, self.fake_builder)

            manifest = json.loads((output / "branches" / "snapshot.json").read_text())
            self.assertFalse((output / "stale.txt").exists())
            self.assertFalse(stale_path.exists())
            feature = next(item for item in manifest["branches"] if item["ref"] == "Feature/A")
            self.assertEqual("4" * 40, feature["sha"])
            self.assertEqual("main", manifest["stable"]["ref"])
            self.assertTrue((output / "index.html").is_file())

    def test_failed_rebuild_preserves_previous_complete_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "public"
            tips = [PAGES.BranchTip("main", "1" * 40)]
            PAGES.build_snapshot(output, "https://pages.example.test", tips, self.fake_builder)
            original = (output / "index.html").read_text(encoding="utf-8")

            def fail(_sha: str, _requests: list[PAGES.BuildRequest]) -> None:
                raise RuntimeError("fixture failure")

            with self.assertRaisesRegex(RuntimeError, "fixture failure"):
                PAGES.build_snapshot(output, "https://pages.example.test", tips, fail)
            self.assertEqual(original, (output / "index.html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
