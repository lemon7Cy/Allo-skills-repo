#!/usr/bin/env bash
# Setup script for huiping-html-deck skill
# Downloads template assets from upstream guizang-ppt-skill repo
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
UPSTREAM_REPO="https://github.com/op7418/guizang-ppt-skill.git"
TMP_DIR=$(mktemp -d)

echo "=== huiping-html-deck setup ==="
echo "Cloning upstream: $UPSTREAM_REPO"
git clone --depth 1 "$UPSTREAM_REPO" "$TMP_DIR/guizang-ppt-skill"

echo "Copying template assets..."
mkdir -p "$SKILL_DIR/assets/screenshot-backgrounds"
mkdir -p "$SKILL_DIR/references"
mkdir -p "$SKILL_DIR/scripts"

cp "$TMP_DIR/guizang-ppt-skill/assets/template.html" "$SKILL_DIR/assets/"
cp "$TMP_DIR/guizang-ppt-skill/assets/template-swiss.html" "$SKILL_DIR/assets/"
cp "$TMP_DIR/guizang-ppt-skill/assets/motion.min.js" "$SKILL_DIR/assets/"
cp -r "$TMP_DIR/guizang-ppt-skill/assets/screenshot-backgrounds/"* "$SKILL_DIR/assets/screenshot-backgrounds/"
cp "$TMP_DIR/guizang-ppt-skill/references/"*.md "$SKILL_DIR/references/"
cp "$TMP_DIR/guizang-ppt-skill/scripts/validate-swiss-deck.mjs" "$SKILL_DIR/scripts/"

echo "Cleaning up..."
rm -rf "$TMP_DIR"

echo "=== Setup complete ==="
echo "Assets installed to: $SKILL_DIR"
echo "  assets/template.html         (Style A - magazine)"
echo "  assets/template-swiss.html   (Style B - Swiss)"
echo "  references/                  (layouts, themes, checklist)"
echo "  scripts/                     (Swiss deck validator)"
