---
name: image-generation
description: Generate new images through the shared DFCode image gateway. Use when the user asks to generate, draw, render, design, or create an image; do not use for image search, editing, or reference-image requests.
version: 4.0.1
required_env:
  - IMAGE_GATEWAY_KEY
optional_env:
  - IMAGE_GATEWAY_BASE_URL
  - IMAGE_GENERATION_MODEL
credentials:
  - key: IMAGE_GATEWAY_KEY
    label: DFCode Image Gateway Key
    required: true
    secret: true
---

# Image Generation

Use this skill when the user asks to generate, draw, render, design, or create a new image. Do not call `image_search` for a generation request. The current gateway supports generation only; it does not support editing or reference images.

## Required Workflow

Follow this order exactly:

1. Write a complete UTF-8 prompt containing the subject, style, composition, lighting, palette, and exclusions.
2. Keep the prompt non-empty and at most 10,000 characters.
3. Save the prompt under the current workspace.
4. Run `scripts/generate.py` from this skill directory.
5. Do not pass `--reference-images`.
6. Prefer a `.jpg` output filename because the default gateway model returns JPEG bytes.
7. Treat generation as successful only if the command exits with code 0, stdout contains `Successfully generated image to <absolute path>`, and that exact output file exists and is non-empty.
8. Call `present_files` with a one-item `filepaths` list containing that exact absolute output path.
9. Claim that the image was generated only after `present_files` returns `Successfully presented files`.

If any check or the `present_files` call fails, report the failure honestly. Never say “已生成”, “生成完成”, “image is ready”, or an equivalent success claim without both generation and presentation proof.

## Invocation

```bash
python3 scripts/generate.py \
  --prompt-file /path/to/workspace/prompt.txt \
  --output-file /path/to/outputs/generated-image.jpg \
  --aspect-ratio 16:9
```

Resolve `scripts/generate.py` relative to this skill directory. Do not hard-code a machine-specific skill path.

## Configuration

- `IMAGE_GATEWAY_KEY` is required and must be injected from secret storage.
- `IMAGE_GATEWAY_BASE_URL` defaults to `http://221.0.79.252:18120/v1`.
- `IMAGE_GENERATION_MODEL` defaults to `grok-imagine-image`.
- Supported models are `gpt-image-2`, `grok-imagine-image`, and `grok-imagine-image-quality`.

## Parameters

- `--prompt-file`: Required UTF-8 prompt file.
- `--output-file`: Required output path; prefer `.jpg` with the default model.
- `--aspect-ratio`: `1:1`, `square`, `portrait`, `9:16`, `2:3`, `landscape`, `16:9`, or `3:2`.
- `--reference-images`: Unsupported. Do not pass this option with any files.

## Failure Contract

If the command fails, the success line is missing, the output file is empty, or `present_files` fails, report the error and do not claim that an image was generated. Do not print Base64 response data or authentication values. Decline reference-image editing requests because the current gateway supports generation only.

For Doraemon-style comics, read `templates/doraemon.md` before composing the prompt.
