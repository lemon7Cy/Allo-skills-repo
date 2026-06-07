---
name: image-generation
description: Use this skill when the user requests to generate, create, imagine, or visualize images including characters, scenes, products, or any visual content. Supports text-to-image and image editing via MaaS platform gpt-image-2 API.
tools: []
version: "2.0.0"
author: allo-official
required_env:
  - GPT_IMAGE_API_KEY
optional_env: []
credentials:
  - key: GPT_IMAGE_API_KEY
    label: GPT Image 2 API Key
    description: 用于调用 MaaS 平台 gpt-image-2 生图和编辑接口的认证 key。
    required: true
    secret: true
---

# Image Generation Skill

## Overview

Generate or edit images via the MaaS platform using `gpt-image-2`. Supports text-to-image generation and image editing with reference images.

## Runtime Paths

The Agent context should provide the absolute path to this `SKILL.md`. Derive bundled files from that path instead of using fixed virtual mount paths:

```bash
SKILL_DIR="$(cd "$(dirname "$SKILL_MD_PATH")" && pwd)"
WORKSPACE_DIR="${WORKSPACE_DIR:-$PWD/workspace}"
OUTPUT_DIR="${OUTPUT_DIR:-$PWD/outputs}"
UPLOAD_DIR="${UPLOAD_DIR:-$PWD/uploads}"
```

Create output directories if needed.

## API Reference

| Operation | Endpoint | Method |
|-----------|----------|--------|
| Generate | `http://221.0.79.251:8080/v1/images/generations` | `POST` |
| Edit | `http://221.0.79.251:8080/v1/images/edits` | `POST` |

| Parameter | Description | Values |
|-----------|-------------|--------|
| `model` | Model name | `gpt-image-2` (required) |
| `prompt` | Text prompt | Required |
| `n` | Number of images | Default `1` |
| `size` | Image dimensions | `1024x1024`, `1024x1792`, `1792x1024` |
| `response_format` | Return format | `b64_json` (default), `url` |
| `quality` | Quality level | `standard`, `hd` |
| `style` | Style | `vivid`, `natural` |
| `stream` | Streaming | `true`, `false` |

## Workflow

### Step 1: Understand Requirements

When a user requests image generation, identify:

- Subject/content: What should be in the image
- Style preferences: Art style, mood, color palette
- Technical specs: Aspect ratio, composition, lighting
- Reference images: Any images to guide generation (use edit endpoint)
- Size: Match the content type (portrait → `1024x1792`, landscape → `1792x1024`)

### Step 2: Generate Image

```bash
curl -s http://221.0.79.251:8080/v1/images/generations \
  -H "Authorization: Bearer $GPT_IMAGE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-image-2",
    "prompt": "YOUR_PROMPT_HERE",
    "n": 1,
    "size": "1024x1024",
    "response_format": "b64_json",
    "quality": "standard",
    "style": "vivid"
  }'
```

### Step 3: Edit Image (with reference)

```bash
curl -s http://221.0.79.251:8080/v1/images/edits \
  -H "Authorization: Bearer $GPT_IMAGE_API_KEY" \
  -F "image=@$UPLOAD_DIR/input.png" \
  -F "prompt=YOUR_EDIT_PROMPT" \
  -F "model=gpt-image-2"
```

### Step 4: Save Output

Decode `b64_json` response and save:

```bash
RESPONSE=$(curl -s http://221.0.79.251:8080/v1/images/generations \
  -H "Authorization: Bearer $GPT_IMAGE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-image-2","prompt":"A cute cat","response_format":"b64_json"}')

echo "$RESPONSE" | python3 -c "
import sys, json, base64
data = json.load(sys.stdin)
img = base64.b64decode(data['data'][0]['b64_json'])
with open('$OUTPUT_DIR/generated.png', 'wb') as f:
    f.write(img)
"
```

## Prompt Engineering Tips

- Always write prompts in English for best results
- Be specific about style, lighting, composition
- Include negative concepts by describing what you DON'T want
- Use `quality: "hd"` for detailed or professional images
- Use `style: "natural"` for realistic photos, `vivid` for artistic

## Common Scenarios

**Character Design**: Describe gender, age, ethnicity, clothing, pose, expression, setting

**Scene/Environment**: Describe location, time of day, weather, mood, atmosphere, focal points

**Product Visualization**: Describe product details, materials, lighting, background, presentation angle

**Illustration/Art**: Specify art style (watercolor, oil painting, digital art, anime), color palette, composition

## Output Handling

After generation:

- Images are saved to `$OUTPUT_DIR/`
- Share generated images with user using `present_files` tool
- Provide brief description of the generation result
- Offer to iterate if adjustments needed
- `revised_prompt` in response shows how the model interpreted your prompt

## Common Mistakes

- Forgetting `response_format` — defaults to `b64_json`, not `url`
- Using unsupported sizes — stick to `1024x1024`, `1024x1792`, `1792x1024`
- Missing `model` field — it's required
- Writing prompts in non-English — always use English for best quality
- Using generation endpoint for edits — use `/v1/images/edits` when modifying existing images
