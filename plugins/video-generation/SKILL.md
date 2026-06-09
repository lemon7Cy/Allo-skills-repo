---
name: video-generation
description: Use this skill when the user requests to generate, create, or imagine videos. Supports structured prompts and reference image for guided generation.
---

# Video Generation Skill


## Runtime Paths

The Agent context should provide the absolute path to this `SKILL.md`. Derive bundled files from that path instead of using fixed virtual mount paths:

```bash
SKILL_DIR="$(cd "$(dirname "$SKILL_MD_PATH")" && pwd)"
WORKSPACE_DIR="${WORKSPACE_DIR:-$PWD/workspace}"
OUTPUT_DIR="${OUTPUT_DIR:-$PWD/outputs}"
UPLOAD_DIR="${UPLOAD_DIR:-$PWD/uploads}"
```

Use `$SKILL_DIR/scripts/generate.py` for the bundled generator. Use Agent-provided workspace, output, and upload paths for user files; create output directories if needed.

## Overview

This skill generates high-quality videos using structured prompts and a Python script. The workflow includes creating JSON-formatted prompts and executing video generation with optional reference image.

## Core Capabilities

- Create structured JSON prompts for AIGC video generation
- Support reference image as guidance or the first/last frame of the video
- Generate videos through automated Python script execution

## Workflow

### Step 1: Understand Requirements

When a user requests video generation, identify:

- Subject/content: What should be in the image
- Style preferences: Art style, mood, color palette
- Technical specs: Aspect ratio, composition, lighting
- Reference image: Any image to guide generation
- Use Agent-provided workspace, upload, and output paths; do not assume any fixed virtual mount directory

### Step 2: Create Structured Prompt

Generate a structured JSON file in `$WORKSPACE_DIR/` with naming pattern: `{descriptive-name}.json`

### Step 3: Create Reference Image (Optional when image-generation skill is available)

Generate reference image for the video generation.

- If only 1 image is provided, use it as the guided frame of the video

### Step 3: Execute Generation

Call the Python script:
```bash
python "$SKILL_DIR/scripts/generate.py" \
  --prompt-file $WORKSPACE_DIR/prompt-file.json \
  --reference-images /path/to/ref1.jpg \
  --output-file $OUTPUT_DIR/generated-video.mp4 \
  --aspect-ratio 16:9
```

Parameters:

- `--prompt-file`: Absolute path to JSON prompt file (required)
- `--reference-images`: Absolute paths to reference image (optional)
- `--output-file`: Absolute path to output image file (required)
- `--aspect-ratio`: Aspect ratio of the generated image (optional, default: 16:9)

[!NOTE]
Do NOT read the python file, instead just call it with the parameters.

## Video Generation Example

User request: "Generate a short video clip depicting the opening scene from "The Chronicles of Narnia: The Lion, the Witch and the Wardrobe"

Step 1: Search for the opening scene of "The Chronicles of Narnia: The Lion, the Witch and the Wardrobe" online

Step 2: Create a JSON prompt file with the following content:

```json
{
  "title": "The Chronicles of Narnia - Train Station Farewell",
  "background": {
    "description": "World War II evacuation scene at a crowded London train station. Steam and smoke fill the air as children are being sent to the countryside to escape the Blitz.",
    "era": "1940s wartime Britain",
    "location": "London railway station platform"
  },
  "characters": ["Mrs. Pevensie", "Lucy Pevensie"],
  "camera": {
    "type": "Close-up two-shot",
    "movement": "Static with subtle handheld movement",
    "angle": "Profile view, intimate framing",
    "focus": "Both faces in focus, background soft bokeh"
  },
  "dialogue": [
    {
      "character": "Mrs. Pevensie",
      "text": "You must be brave for me, darling. I'll come for you... I promise."
    },
    {
      "character": "Lucy Pevensie",
      "text": "I will be, mother. I promise."
    }
  ],
  "audio": [
    {
      "type": "Train whistle blows (signaling departure)",
      "volume": 1
    },
    {
      "type": "Strings swell emotionally, then fade",
      "volume": 0.5
    },
    {
      "type": "Ambient sound of the train station",
      "volume": 0.5
    }
  ]
}
```

Step 3: Use the image-generation skill to generate the reference image

Load the image-generation skill and generate a single reference image `narnia-farewell-scene-01.jpg` according to the skill.

Step 4: Use the generate.py script to generate the video
```bash
python "$SKILL_DIR/scripts/generate.py" \
  --prompt-file $WORKSPACE_DIR/narnia-farewell-scene.json \
  --reference-images $OUTPUT_DIR/narnia-farewell-scene-01.jpg \
  --output-file $OUTPUT_DIR/narnia-farewell-scene-01.mp4 \
  --aspect-ratio 16:9
```
> Do NOT read the python file, just call it with the parameters.

## Output Handling

After generation:

- Videos are typically saved in `$OUTPUT_DIR/`
- Share generated videos (come first) with user as well as generated image if applicable, using `present_files` tool
- Provide brief description of the generation result
- Offer to iterate if adjustments needed

## Notes

- Always use English for prompts regardless of user's language
- JSON format ensures structured, parsable prompts
- Reference image enhance generation quality significantly
- Iterative refinement is normal for optimal results
