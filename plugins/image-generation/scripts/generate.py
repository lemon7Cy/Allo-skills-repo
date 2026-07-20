import argparse
import base64
import binascii
import mimetypes
import os
import re
import sys
import tempfile
from contextlib import ExitStack
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

REQUEST_TIMEOUT = (10, 120)
DEFAULT_BASE_URL = "http://47.104.0.249:28088/v1"
DEFAULT_MODEL = "gpt-image-2"
ASPECT_RATIO_SIZES = {
    "1:1": "1024x1024",
    "square": "1024x1024",
    "portrait": "1024x1792",
    "9:16": "1024x1792",
    "2:3": "1024x1792",
    "landscape": "1792x1024",
    "16:9": "1792x1024",
    "3:2": "1792x1024",
}
MAX_PROVIDER_ERROR_LENGTH = 2000
SECRET_FIELD_NAMES = (
    "api[_-]?key|access[_-]?token|token|key|signature|sig|password|authorization"
)

_ROOT_DIR = Path(__file__).resolve().parents[4]
load_dotenv(_ROOT_DIR / ".env")
load_dotenv(_ROOT_DIR / "backend/.env", override=True)


def _load_config() -> tuple[str, str, str]:
    api_key = os.getenv("GPT_IMAGE_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "GPT_IMAGE_API_KEY is required. Set it before running image generation."
        )

    base_url = os.getenv("GPT_IMAGE_BASE_URL", DEFAULT_BASE_URL).strip().rstrip("/")
    if not base_url:
        raise RuntimeError("GPT_IMAGE_BASE_URL cannot be empty.")

    model = os.getenv("GPT_IMAGE_MODEL", DEFAULT_MODEL).strip()
    if not model:
        raise RuntimeError("GPT_IMAGE_MODEL cannot be empty.")
    return api_key, base_url, model


def _size_for_aspect_ratio(aspect_ratio: str) -> str:
    normalized = aspect_ratio.strip().lower()
    try:
        return ASPECT_RATIO_SIZES[normalized]
    except KeyError as exc:
        supported = ", ".join(ASPECT_RATIO_SIZES)
        raise ValueError(
            f"Unsupported aspect ratio '{aspect_ratio}'. Supported values: {supported}."
        ) from exc


def _require_file(path_value: str, kind: str) -> Path:
    path = Path(path_value).expanduser()
    if not path.is_file():
        raise FileNotFoundError(f"The {kind} file does not exist: {path}")
    return path


def _sanitize_provider_text(text: str, api_key: str) -> str:
    sanitized = text.replace(api_key, "[REDACTED]") if api_key else text
    sanitized = re.sub(
        rf"(?i)(?P<key_quote>[\"'])(?P<key>{SECRET_FIELD_NAMES})(?P=key_quote)(?P<separator>\s*:\s*)(?P<value_quote>[\"'])(?P<value>.*?)(?P=value_quote)",
        lambda match: (
            f"{match.group('key_quote')}{match.group('key')}{match.group('key_quote')}{match.group('separator')}{match.group('value_quote')}[REDACTED]{match.group('value_quote')}"
        ),
        sanitized,
    )
    sanitized = re.sub(
        r"(?i)(\bauthorization\s*:\s*)(?:(?:basic|bearer|digest|negotiate|token)\s+)?[^\s,;\"'}\]]+",
        r"\1[REDACTED]",
        sanitized,
    )
    sanitized = re.sub(
        rf"(?i)([?&](?:{SECRET_FIELD_NAMES})=)[^&\s\"']+",
        r"\1[REDACTED]",
        sanitized,
    )
    if len(sanitized) > MAX_PROVIDER_ERROR_LENGTH:
        return f"{sanitized[:MAX_PROVIDER_ERROR_LENGTH]}... [truncated]"
    return sanitized


def _request_error(
    action: str, exc: requests.RequestException, api_key: str
) -> RuntimeError:
    details = _sanitize_provider_text(str(exc), api_key)
    return RuntimeError(f"{action}: {details}" if details else action)


def _raise_for_status(response: requests.Response, action: str, api_key: str) -> None:
    try:
        response.raise_for_status()
    except requests.RequestException as exc:
        details = _sanitize_provider_text(response.text.strip(), api_key)
        suffix = f" Provider response: {details}" if details else ""
        raise RuntimeError(
            f"Image API {action} failed with HTTP {response.status_code}.{suffix}"
        ) from exc


def _response_item(response: requests.Response) -> dict[str, Any]:
    try:
        payload = response.json()
    except (ValueError, requests.JSONDecodeError) as exc:
        raise RuntimeError("Image API returned invalid JSON.") from exc

    try:
        item = payload["data"][0]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(
            "Image API response must contain a non-empty data array."
        ) from exc
    if not isinstance(item, dict):
        raise RuntimeError("Image API data[0] must be an object.")
    return item


def _image_bytes(response: requests.Response, api_key: str) -> bytes:
    item = _response_item(response)
    encoded = item.get("b64_json")
    if encoded:
        try:
            return base64.b64decode(encoded, validate=True)
        except (binascii.Error, TypeError, ValueError) as exc:
            raise RuntimeError(
                "Image API returned invalid b64_json image data."
            ) from exc

    image_url = item.get("url")
    if image_url:
        try:
            download = requests.get(image_url, timeout=REQUEST_TIMEOUT)
        except requests.RequestException as exc:
            raise _request_error(
                "Failed to download generated image URL", exc, api_key
            ) from exc
        _raise_for_status(download, "image download", api_key)
        if not download.content:
            raise RuntimeError("Generated image URL returned an empty response body.")
        return download.content

    raise RuntimeError("Image API data[0] must contain b64_json or url.")


def _post_generation(
    base_url: str,
    api_key: str,
    model: str,
    prompt: str,
    size: str,
) -> requests.Response:
    return requests.post(
        f"{base_url}/images/generations",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": model,
            "prompt": prompt,
            "size": size,
            "response_format": "b64_json",
        },
        timeout=REQUEST_TIMEOUT,
    )


def _post_edit(
    base_url: str,
    api_key: str,
    model: str,
    prompt: str,
    size: str,
    reference_paths: list[Path],
) -> requests.Response:
    with ExitStack() as stack:
        files = []
        image_field = "image" if len(reference_paths) == 1 else "image[]"
        for path in reference_paths:
            content_type = (
                mimetypes.guess_type(path.name)[0] or "application/octet-stream"
            )
            file_object = stack.enter_context(path.open("rb"))
            files.append((image_field, (path.name, file_object, content_type)))
        return requests.post(
            f"{base_url}/images/edits",
            headers={"Authorization": f"Bearer {api_key}"},
            data={
                "model": model,
                "prompt": prompt,
                "size": size,
                "response_format": "b64_json",
            },
            files=files,
            timeout=REQUEST_TIMEOUT,
        )


def _atomic_write(output_path: Path, image_bytes: bytes) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=output_path.parent,
            prefix=f".{output_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            temporary_file.write(image_bytes)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
        os.replace(temporary_path, output_path)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def generate_image(
    prompt_file: str,
    reference_images: list[str],
    output_file: str,
    aspect_ratio: str = "16:9",
) -> str:
    api_key, base_url, model = _load_config()
    prompt_path = _require_file(prompt_file, "prompt")
    reference_paths = [
        _require_file(reference_image, "reference image")
        for reference_image in reference_images
    ]
    prompt = prompt_path.read_text(encoding="utf-8")
    if not prompt.strip():
        raise ValueError(f"The prompt file is empty: {prompt_path}")
    size = _size_for_aspect_ratio(aspect_ratio)

    try:
        if reference_paths:
            response = _post_edit(
                base_url,
                api_key,
                model,
                prompt,
                size,
                reference_paths,
            )
        else:
            response = _post_generation(base_url, api_key, model, prompt, size)
    except requests.RequestException as exc:
        raise _request_error("Could not reach the image API", exc, api_key) from exc

    _raise_for_status(response, "request", api_key)
    image_bytes = _image_bytes(response, api_key)
    output_path = Path(output_file).expanduser()
    _atomic_write(output_path, image_bytes)
    return f"Successfully generated image to {output_path.resolve()}"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate images using a MaaS OpenAI-compatible image API"
    )
    parser.add_argument(
        "--prompt-file",
        required=True,
        help="Path to a UTF-8 prompt file",
    )
    parser.add_argument(
        "--reference-images",
        nargs="*",
        default=[],
        help="Paths to reference images (space-separated)",
    )
    parser.add_argument(
        "--output-file",
        required=True,
        help="Output path for the generated image",
    )
    parser.add_argument(
        "--aspect-ratio",
        default="16:9",
        help="Output ratio: 1:1, portrait, landscape, 16:9, 9:16, 2:3, or 3:2",
    )
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    try:
        result = generate_image(
            args.prompt_file,
            args.reference_images,
            args.output_file,
            args.aspect_ratio,
        )
    except Exception as exc:
        print(f"Image generation failed: {exc}", file=sys.stderr)
        return 1
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
