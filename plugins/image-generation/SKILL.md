---
name: image-generation
description: Generate or edit images with the MaaS OpenAI-compatible gpt-image-2 API, including structured prompts, reference images, and common aspect ratios.
version: 2.0.0
required_env:
  - GPT_IMAGE_API_KEY
optional_env:
  - GPT_IMAGE_BASE_URL
  - GPT_IMAGE_MODEL
credentials:
  - key: GPT_IMAGE_API_KEY
    label: GPT Image API Key
    required: true
    secret: true
---

# Image Generation

Generate new images from text prompts or edit images using one or more references. Use the bundled script rather than hand-writing HTTP requests or curl commands.

## Configuration

- `GPT_IMAGE_API_KEY` is required.
- `GPT_IMAGE_BASE_URL` is optional and defaults to `http://47.104.0.249:28088/v1`.
- `GPT_IMAGE_MODEL` is optional and defaults to `gpt-image-2`.

`GPT_IMAGE_BASE_URL` is the complete API base. A trailing slash is removed, but configured paths such as `/v1` are preserved.

The script uses the OpenAI-compatible endpoints below:

- No reference images: `POST {base}/images/generations` with JSON.
- One or more reference images: `POST {base}/images/edits` with multipart form data. One reference uses `image`; multiple references use OpenAI-compatible `image[]` fields.

## Workflow

1. Understand the requested subject, style, composition, lighting, and output shape.
2. Write an English prompt to a UTF-8 text or JSON file in the current workspace.
3. Resolve the script path relative to this `SKILL.md`: `scripts/generate.py`.
4. Invoke the script with an output path appropriate for the current runtime.
5. Present the generated file and iterate when requested.

Do not assume fixed `/mnt/skills` or `/mnt/user-data` paths. Use paths available in the current environment. JSON prompt files are supported; the complete file contents are sent as the prompt.

## Script Invocation

From this skill directory:

```bash
python scripts/generate.py \
  --prompt-file /path/to/prompt.json \
  --output-file /path/to/outputs/generated-image.png \
  --aspect-ratio 16:9
```

With references:

```bash
python scripts/generate.py \
  --prompt-file /path/to/prompt.json \
  --reference-images /path/to/ref1.png /path/to/ref2.jpg \
  --output-file /path/to/outputs/edited-image.png \
  --aspect-ratio portrait
```

If invoking from another directory, construct the path to `scripts/generate.py` from the installed skill directory instead of hard-coding a machine-specific location.

## Parameters

- `--prompt-file`: Required UTF-8 prompt file path.
- `--reference-images`: Optional space-separated image paths. Supplying any reference selects the edits endpoint.
- `--output-file`: Required output file path. Missing parent directories are created automatically.
- `--aspect-ratio`: Optional; defaults to `16:9`.

Supported aspect ratios and output sizes:

- `1:1` or `square`: `1024x1024`
- `portrait`, `9:16`, or `2:3`: `1024x1792`
- `landscape`, `16:9`, or `3:2`: `1792x1024`

## Python Entry Point

The script also exposes:

```python
generate_image(prompt_file, reference_images, output_file, aspect_ratio="16:9")
```

It returns a success message containing the absolute output path. Failures raise actionable exceptions; CLI failures are written to stderr and exit with status 1.

## Prompt Guidance

- Prefer English prompts for consistent model behavior.
- Describe the subject, setting, style, composition, lighting, color palette, and exclusions.
- Structured JSON is useful for complex scenes, but plain text is also accepted.
- Refer to supplied images clearly, such as `[Image 1]` and `[Image 2]`, in the same order as `--reference-images`.

Example prompt file:

```json
{
  "subject": "A woman in 1990s Tokyo street fashion walking through Shibuya after rain",
  "style": "35mm documentary street photography, natural film grain",
  "composition": "medium shot, subject off-center, layered city background",
  "lighting": "neon storefront reflections on wet pavement",
  "color_palette": "muted warm skin tones with cyan and red accents",
  "negative_prompt": "studio lighting, selfie angle, oversaturated colors, distorted hands"
}
```

## Output And Errors

The API may return either `data[0].b64_json` or `data[0].url`; the script saves both forms to `--output-file` using a same-directory temporary file and atomic replacement. A failed save cleans up the temporary file and preserves an existing output. Provider error text is redacted and bounded before it is reported. If generation fails, report the script's error rather than claiming an image was created. Common actionable errors include missing credentials, missing input files, unsupported aspect ratios, HTTP failures, and malformed provider responses.

## Specific Templates

Read a template only when it matches the request:

- [Doraemon Comic](templates/doraemon.md)
