import json
import os
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEMO_PATH = os.path.join(
    REPO_ROOT,
    "plugins",
    "huiping-incremental-evaluator",
    "skills",
    "huiping-incremental-evaluator",
    "references",
    "demo-visualization-payload.json",
)
SKILL_PATH = os.path.join(
    REPO_ROOT,
    "plugins",
    "huiping-incremental-evaluator",
    "skills",
    "huiping-incremental-evaluator",
    "SKILL.md",
)
RADAR_RENDERER_PATH = os.path.join(
    REPO_ROOT,
    "plugins",
    "huiping-incremental-evaluator",
    "skills",
    "huiping-incremental-evaluator",
    "references",
    "scripts",
    "render_radar_svg.py",
)


class TestMingxueVisualSkills(unittest.TestCase):
    def load_demo_payload(self):
        with open(DEMO_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def test_demo_payload_has_all_visual_modules(self):
        payload = self.load_demo_payload()
        visualization = payload["visualization_payload"]

        self.assertIn("material_check", visualization)
        self.assertIn("draft_delta_map", visualization)
        self.assertIn("six_dimension_scores", visualization)
        self.assertIn("expert_panel", visualization)
        self.assertIn("growth_evidence_chain", visualization)
        self.assertIn("evaluation_report", visualization)

    def test_demo_scores_are_consistent(self):
        payload = self.load_demo_payload()
        scores = payload["visualization_payload"]["six_dimension_scores"]

        for dimension in scores["dimensions"]:
            self.assertEqual(
                dimension["final"] - dimension["initial"],
                dimension["delta"],
                dimension["name"],
            )
            self.assertGreaterEqual(dimension["initial"], 0)
            self.assertLessEqual(dimension["final"], 100)

        self.assertEqual(
            scores["overall"]["final"] - scores["overall"]["initial"],
            scores["overall"]["delta"],
        )

    def test_incremental_evaluator_references_demo_payload(self):
        with open(SKILL_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("references/demo-visualization-payload.json", content)

    def test_radar_renderer_creates_svg_from_demo_payload(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "radar.svg")
            result = subprocess.run(
                [
                    sys.executable,
                    RADAR_RENDERER_PATH,
                    DEMO_PATH,
                    output_path,
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(os.path.exists(output_path))

            with open(output_path, "r", encoding="utf-8") as f:
                svg = f.read()

            self.assertIn("<svg", svg)
            self.assertIn("初稿", svg)
            self.assertIn("终稿", svg)
            self.assertIn("数据分析深度", svg)
            self.assertIn("polyline", svg)

    def test_incremental_evaluator_references_radar_renderer(self):
        with open(SKILL_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("references/scripts/render_radar_svg.py", content)

    def test_incremental_evaluator_is_single_file_install_safe(self):
        with open(SKILL_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("Single-File Allo Install Compatibility", content)
        self.assertIn("cat > render_radar_svg.py <<'PY'", content)
        self.assertIn("def render_svg(payload, dimensions, overall):", content)
        self.assertIn('"visualization_payload"', content)
        self.assertIn('"six_dimension_scores"', content)

    def test_visual_skill_suite_uses_huiping_names(self):
        expected = {
            "huiping-incremental-evaluator",
            "huiping-report-review",
            "huiping-data-analysis-coach",
            "huiping-literature-guide",
            "huiping-topic-advisor",
        }
        marketplace_path = os.path.join(REPO_ROOT, "marketplace.json")
        with open(marketplace_path, "r", encoding="utf-8") as f:
            marketplace = json.load(f)

        plugin_names = {plugin["name"] for plugin in marketplace["plugins"]}
        self.assertTrue(expected.issubset(plugin_names))

        deprecated = {
            "mingxue-incremental-evaluator",
            "mingxue-report-review",
            "mingxue-data-analysis-coach",
            "mingxue-literature-guide",
            "mingxue-topic-advisor",
        }
        self.assertTrue(plugin_names.isdisjoint(deprecated))


if __name__ == "__main__":
    unittest.main()
