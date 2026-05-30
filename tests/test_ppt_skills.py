import json
import os
import unittest


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HTML_DECK_SKILL_PATH = os.path.join(
    REPO_ROOT,
    "plugins",
    "huiping-html-deck",
    "skills",
    "huiping-html-deck",
    "SKILL.md",
)
HTML_DECK_ASSETS_PATH = os.path.join(
    REPO_ROOT,
    "plugins",
    "huiping-html-deck",
    "skills",
    "huiping-html-deck",
    "assets",
)
HTML_DECK_SETUP_PATH = os.path.join(
    REPO_ROOT,
    "plugins",
    "huiping-html-deck",
    "skills",
    "huiping-html-deck",
    "setup.sh",
)

PPT_GEN_SKILL_PATH = os.path.join(
    REPO_ROOT,
    "plugins",
    "huiping-ppt-generator",
    "skills",
    "huiping-ppt-generator",
    "SKILL.md",
)
PPT_GEN_SETUP_PATH = os.path.join(
    REPO_ROOT,
    "plugins",
    "huiping-ppt-generator",
    "skills",
    "huiping-ppt-generator",
    "setup.sh",
)
PPT_GEN_ENV_PATH = os.path.join(
    REPO_ROOT,
    "plugins",
    "huiping-ppt-generator",
    "skills",
    "huiping-ppt-generator",
    ".env.example",
)
PPT_GEN_REQ_PATH = os.path.join(
    REPO_ROOT,
    "plugins",
    "huiping-ppt-generator",
    "skills",
    "huiping-ppt-generator",
    "requirements.txt",
)

PDF2MD_SKILL_PATH = os.path.join(
    REPO_ROOT,
    "plugins",
    "pdf-to-markdown",
    "skills",
    "pdf-to-markdown",
    "SKILL.md",
)

DONGFANG_SKILL_PATH = os.path.join(
    REPO_ROOT,
    "plugins",
    "dongfang-enterprise-kb-query",
    "skills",
    "dongfang-enterprise-kb-query",
    "SKILL.md",
)


class TestHuipingHtmlDeck(unittest.TestCase):
    def test_skill_md_exists(self):
        self.assertTrue(os.path.exists(HTML_DECK_SKILL_PATH))

    def test_skill_md_has_frontmatter(self):
        with open(HTML_DECK_SKILL_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertTrue(content.startswith("---"))
        self.assertIn("name: huiping-html-deck", content)

    def test_skill_md_references_templates(self):
        with open(HTML_DECK_SKILL_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("template.html", content)
        self.assertIn("template-swiss.html", content)

    def test_skill_md_references_guizang_upstream(self):
        with open(HTML_DECK_SKILL_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("guizang-ppt-skill", content)
        self.assertIn("op7418", content)

    def test_setup_script_exists(self):
        self.assertTrue(os.path.exists(HTML_DECK_SETUP_PATH))

    def test_template_assets_exist(self):
        self.assertTrue(os.path.exists(HTML_DECK_ASSETS_PATH))
        self.assertTrue(
            os.path.exists(os.path.join(HTML_DECK_ASSETS_PATH, "template.html"))
        )
        self.assertTrue(
            os.path.exists(os.path.join(HTML_DECK_ASSETS_PATH, "template-swiss.html"))
        )

    def test_template_html_is_valid(self):
        template_path = os.path.join(HTML_DECK_ASSETS_PATH, "template.html")
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("<!DOCTYPE html>", content)
        self.assertIn("SLIDES_HERE", content)

    def test_references_exist(self):
        refs_path = os.path.join(
            REPO_ROOT,
            "plugins",
            "huiping-html-deck",
            "skills",
            "huiping-html-deck",
            "references",
        )
        self.assertTrue(os.path.exists(refs_path))
        expected_files = ["layouts.md", "themes.md", "checklist.md", "components.md"]
        for f in expected_files:
            self.assertTrue(
                os.path.exists(os.path.join(refs_path, f)),
                f"Missing reference: {f}",
            )

    def test_skill_registered_in_marketplace(self):
        marketplace_path = os.path.join(REPO_ROOT, "marketplace.json")
        with open(marketplace_path, "r", encoding="utf-8") as f:
            marketplace = json.load(f)
        plugin_names = {p["name"] for p in marketplace["plugins"]}
        self.assertIn("huiping-html-deck", plugin_names)


class TestHuipingPptGenerator(unittest.TestCase):
    def test_skill_md_exists(self):
        self.assertTrue(os.path.exists(PPT_GEN_SKILL_PATH))

    def test_skill_md_has_frontmatter(self):
        with open(PPT_GEN_SKILL_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertTrue(content.startswith("---"))
        self.assertIn("name: huiping-ppt-generator", content)

    def test_skill_md_references_ppt_master(self):
        with open(PPT_GEN_SKILL_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("ppt-master", content)
        self.assertIn("hugohe3", content)

    def test_skill_md_has_pipeline_steps(self):
        with open(PPT_GEN_SKILL_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Step 1", content)
        self.assertIn("Step 7", content)
        self.assertIn("svg_to_pptx", content)
        self.assertIn("finalize_svg", content)

    def test_setup_script_exists(self):
        self.assertTrue(os.path.exists(PPT_GEN_SETUP_PATH))

    def test_env_example_exists(self):
        self.assertTrue(os.path.exists(PPT_GEN_ENV_PATH))
        with open(PPT_GEN_ENV_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("OPENAI_API_KEY", content)

    def test_requirements_txt_exists(self):
        self.assertTrue(os.path.exists(PPT_GEN_REQ_PATH))
        with open(PPT_GEN_REQ_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("python-pptx", content)

    def test_skill_registered_in_marketplace(self):
        marketplace_path = os.path.join(REPO_ROOT, "marketplace.json")
        with open(marketplace_path, "r", encoding="utf-8") as f:
            marketplace = json.load(f)
        plugin_names = {p["name"] for p in marketplace["plugins"]}
        self.assertIn("huiping-ppt-generator", plugin_names)

    def test_skill_md_mentions_setup(self):
        with open(PPT_GEN_SKILL_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("setup.sh", content)

    def test_skill_md_mentions_api_keys(self):
        with open(PPT_GEN_SKILL_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn(".env", content)


class TestPdfToMarkdown(unittest.TestCase):
    def test_skill_md_exists(self):
        self.assertTrue(os.path.exists(PDF2MD_SKILL_PATH))

    def test_skill_md_has_frontmatter(self):
        with open(PDF2MD_SKILL_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertTrue(content.startswith("---"))
        self.assertIn("name: pdf-to-markdown", content)

    def test_skill_md_has_api_config(self):
        with open(PDF2MD_SKILL_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("PDF_PARSE_BASE_URL", content)
        self.assertIn("PDF_PARSE_TOKEN", content)

    def test_skill_md_has_endpoints(self):
        with open(PDF2MD_SKILL_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("/pdf/markdown", content)
        self.assertIn("/pdf/jobs", content)
        self.assertIn("/archive", content)

    def test_skill_registered_in_marketplace(self):
        marketplace_path = os.path.join(REPO_ROOT, "marketplace.json")
        with open(marketplace_path, "r", encoding="utf-8") as f:
            marketplace = json.load(f)
        plugin_names = {p["name"] for p in marketplace["plugins"]}
        self.assertIn("pdf-to-markdown", plugin_names)


class TestDongfangKbQuery(unittest.TestCase):
    def test_skill_md_exists(self):
        self.assertTrue(os.path.exists(DONGFANG_SKILL_PATH))

    def test_skill_md_has_frontmatter(self):
        with open(DONGFANG_SKILL_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertTrue(content.startswith("---"))
        self.assertIn("name: dongfang-enterprise-kb-query", content)

    def test_skill_md_has_query_command(self):
        with open(DONGFANG_SKILL_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("DONGFANG_API_URL", content)

    def test_skill_md_has_dataset_info(self):
        with open(DONGFANG_SKILL_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("DONGFANG_API_TOKEN", content)

    def test_skill_registered_in_marketplace(self):
        marketplace_path = os.path.join(REPO_ROOT, "marketplace.json")
        with open(marketplace_path, "r", encoding="utf-8") as f:
            marketplace = json.load(f)
        plugin_names = {p["name"] for p in marketplace["plugins"]}
        self.assertIn("dongfang-enterprise-kb-query", plugin_names)


class TestPptSkillsInMarketplace(unittest.TestCase):
    def test_all_ppt_skills_present(self):
        expected = {
            "huiping-html-deck",
            "huiping-ppt-generator",
            "guizang-ppt-skill",
        }
        marketplace_path = os.path.join(REPO_ROOT, "marketplace.json")
        with open(marketplace_path, "r", encoding="utf-8") as f:
            marketplace = json.load(f)
        plugin_names = {p["name"] for p in marketplace["plugins"]}
        self.assertTrue(expected.issubset(plugin_names))

    def test_marketplace_has_no_duplicate_names(self):
        marketplace_path = os.path.join(REPO_ROOT, "marketplace.json")
        with open(marketplace_path, "r", encoding="utf-8") as f:
            marketplace = json.load(f)
        names = [p["name"] for p in marketplace["plugins"]]
        self.assertEqual(len(names), len(set(names)))

    def test_all_huiping_skills_present(self):
        expected = {
            "huiping-incremental-evaluator",
            "huiping-report-review",
            "huiping-data-analysis-coach",
            "huiping-literature-guide",
            "huiping-topic-advisor",
            "huiping-html-deck",
            "huiping-ppt-generator",
        }
        marketplace_path = os.path.join(REPO_ROOT, "marketplace.json")
        with open(marketplace_path, "r", encoding="utf-8") as f:
            marketplace = json.load(f)
        plugin_names = {p["name"] for p in marketplace["plugins"]}
        self.assertTrue(expected.issubset(plugin_names))


if __name__ == "__main__":
    unittest.main()
