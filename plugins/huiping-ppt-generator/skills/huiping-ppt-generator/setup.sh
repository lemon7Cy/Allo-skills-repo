#!/usr/bin/env bash
# Setup script for huiping-ppt-generator skill
# Downloads scripts and references from upstream ppt-master repo via GitHub raw
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_URL="https://raw.githubusercontent.com/hugohe3/ppt-master/main/skills/ppt-master"

echo "=== huiping-ppt-generator setup ==="
echo "Downloading from: $BASE_URL"

mkdir -p "$SKILL_DIR/scripts/source_to_md"
mkdir -p "$SKILL_DIR/references"
mkdir -p "$SKILL_DIR/templates"

# Download key scripts
SCRIPTS=(
  "scripts/project_manager.py"
  "scripts/finalize_svg.py"
  "scripts/svg_to_pptx.py"
  "scripts/total_md_split.py"
  "scripts/svg_quality_checker.py"
  "scripts/image_gen.py"
  "scripts/latex_render.py"
  "scripts/analyze_images.py"
  "scripts/update_spec.py"
  "scripts/source_to_md/pdf_to_md.py"
  "scripts/source_to_md/doc_to_md.py"
  "scripts/source_to_md/excel_to_md.py"
  "scripts/source_to_md/ppt_to_md.py"
  "scripts/source_to_md/web_to_md.py"
)

for script in "${SCRIPTS[@]}"; do
  dest="$SKILL_DIR/$script"
  echo "  Fetching $script..."
  curl -fsSL "$BASE_URL/$script" -o "$dest" 2>/dev/null || echo "  Warning: failed to fetch $script"
done

# Download key references
REFERENCES=(
  "references/strategist.md"
  "references/executor-base.md"
  "references/shared-standards.md"
  "references/executor-general.md"
  "references/executor-consultant.md"
  "references/canvas-formats.md"
  "references/image-base.md"
  "references/image-generator.md"
  "references/image-searcher.md"
  "references/animations.md"
)

for ref in "${REFERENCES[@]}"; do
  dest="$SKILL_DIR/$ref"
  echo "  Fetching $ref..."
  curl -fsSL "$BASE_URL/$ref" -o "$dest" 2>/dev/null || echo "  Warning: failed to fetch $ref"
done

echo "Installing Python dependencies..."
pip install -r "$SKILL_DIR/requirements.txt" 2>/dev/null || echo "Warning: pip install failed, run manually: pip install -r $SKILL_DIR/requirements.txt"

echo "=== Setup complete ==="
echo "Resources installed to: $SKILL_DIR"
echo "  scripts/           (PDF/DOCX converters, SVG tools, PPTX export)"
echo "  references/        (strategist, executor role definitions)"
echo ""
echo "For AI image generation, create .env:"
echo "  cp $SKILL_DIR/.env.example $SKILL_DIR/.env"
echo "  # Edit .env to set OPENAI_API_KEY"
