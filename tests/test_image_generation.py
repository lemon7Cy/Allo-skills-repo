import base64
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "plugins" / "image-generation"
SKILL_PATH = SKILL_DIR / "SKILL.md"
SCRIPT_PATH = SKILL_DIR / "scripts" / "generate.py"
MARKETPLACE_PATH = REPO_ROOT / "marketplace.json"


def load_generate_module():
    spec = importlib.util.spec_from_file_location("marketplace_image_generation", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load image-generation script")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestImageGenerationSkill(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_generate_module()

    def test_skill_requires_generation_and_presentation_proof(self):
        content = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("Do not call `image_search` for a generation request", content)
        self.assertIn("Successfully generated image to <absolute path>", content)
        self.assertIn("Call `present_files`", content)
        self.assertIn("Successfully presented files", content)
        self.assertIn("only after `present_files`", content)

    def test_marketplace_uses_dfcode_gateway_credentials(self):
        marketplace = json.loads(MARKETPLACE_PATH.read_text(encoding="utf-8"))
        entry = next(
            plugin
            for plugin in marketplace["plugins"]
            if plugin["name"] == "image-generation"
        )

        self.assertEqual(entry["version"], "4.0.1")
        self.assertEqual(entry["required_env"], ["IMAGE_GATEWAY_KEY"])
        self.assertEqual(
            entry["optional_env"],
            ["IMAGE_GATEWAY_BASE_URL", "IMAGE_GENERATION_MODEL"],
        )
        self.assertEqual(entry["credentials"][0]["key"], "IMAGE_GATEWAY_KEY")

    def test_script_has_no_third_party_runtime_dependency(self):
        content = SCRIPT_PATH.read_text(encoding="utf-8")

        self.assertNotIn("import requests", content)
        self.assertNotIn("from dotenv", content)
        self.assertIn("import urllib.request", content)

    def test_default_configuration_targets_shared_gateway(self):
        with patch.dict(os.environ, {"IMAGE_GATEWAY_KEY": "test-key"}, clear=True):
            self.assertEqual(
                self.module._load_config(),
                (
                    "test-key",
                    "http://221.0.79.252:18120/v1",
                    "grok-imagine-image",
                ),
            )

    def test_configuration_rejects_unknown_models(self):
        with patch.dict(
            os.environ,
            {
                "IMAGE_GATEWAY_KEY": "test-key",
                "IMAGE_GENERATION_MODEL": "unknown-image-model",
            },
            clear=True,
        ):
            with self.assertRaisesRegex(ValueError, "Unsupported image generation model"):
                self.module._load_config()

    def test_reference_images_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "does not support image editing"):
            self.module.generate_image(
                "prompt.txt",
                ["reference.png"],
                "output.jpg",
                "1:1",
            )

    def test_generation_writes_non_empty_output_and_returns_absolute_path(self):
        jpeg_bytes = b"\xff\xd8\xff\xe0generated-jpeg"
        response_body = json.dumps(
            {"data": [{"b64_json": base64.b64encode(jpeg_bytes).decode("ascii")}]}
        ).encode("utf-8")

        with tempfile.TemporaryDirectory() as temp_dir:
            prompt_path = Path(temp_dir) / "prompt.txt"
            output_path = Path(temp_dir) / "generated.jpg"
            prompt_path.write_text("A blue circle on a white background", encoding="utf-8")

            with (
                patch.dict(os.environ, {"IMAGE_GATEWAY_KEY": "test-key"}, clear=True),
                patch.object(self.module, "_post_generation", return_value=response_body),
            ):
                result = self.module.generate_image(
                    str(prompt_path),
                    [],
                    str(output_path),
                    "1:1",
                )

            self.assertEqual(output_path.read_bytes(), jpeg_bytes)
            self.assertEqual(
                result,
                f"Successfully generated image to {output_path.resolve()}",
            )

    def test_prompt_length_is_bounded_before_network_request(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            prompt_path = Path(temp_dir) / "prompt.txt"
            output_path = Path(temp_dir) / "generated.jpg"
            prompt_path.write_text("x" * 10_001, encoding="utf-8")

            with patch.dict(os.environ, {"IMAGE_GATEWAY_KEY": "test-key"}, clear=True):
                with self.assertRaisesRegex(ValueError, "exceeds the maximum length"):
                    self.module.generate_image(
                        str(prompt_path),
                        [],
                        str(output_path),
                        "1:1",
                    )


if __name__ == "__main__":
    unittest.main()
