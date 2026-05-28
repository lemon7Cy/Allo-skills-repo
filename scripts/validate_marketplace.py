#!/usr/bin/env python3
"""Validate that marketplace.json matches the skills repository layout."""

import os
import json


def validate_marketplace(root):
    root = os.path.abspath(root)
    manifest_path = os.path.join(root, "marketplace.json")
    if not os.path.exists(manifest_path):
        return {"ok": False, "errors": ["marketplace.json not found"], "warnings": []}

    errors = []
    warnings = []

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as exc:
        return {
            "ok": False,
            "errors": [f"marketplace.json parse error: {exc}"],
            "warnings": [],
        }

    if "name" not in data:
        errors.append("marketplace.json missing top-level name")
    if "plugins" not in data or not isinstance(data["plugins"], list):
        errors.append("marketplace.json missing plugins list")
        return {"ok": False, "errors": errors, "warnings": warnings}

    seen_names = set()
    manifest_plugins = {}

    for idx, plugin in enumerate(data["plugins"]):
        pos = f"plugins[{idx}]"
        plugin_name = plugin.get("name")
        source = plugin.get("source")
        if not plugin_name:
            errors.append(f"{pos} missing name")
            continue
        if not source:
            errors.append(f"{pos} ({plugin_name}) missing source")
        if plugin_name in seen_names:
            errors.append(f"duplicate plugin name: {plugin_name}")
        seen_names.add(plugin_name)
        manifest_plugins[plugin_name] = plugin

        if source:
            skill_path = os.path.join(root, source, "skills", plugin_name, "SKILL.md")
            if not os.path.exists(skill_path):
                errors.append(
                    f"missing skill entry for {plugin_name}: {os.path.relpath(skill_path, root)}"
                )

    skill_files = []
    plugins_root = os.path.join(root, "plugins")
    if os.path.isdir(plugins_root):
        for dirpath, _, filenames in os.walk(plugins_root):
            if os.path.basename(dirpath) == "skills":
                for skill_dir in sorted(os.listdir(dirpath)):
                    candidate = os.path.join(dirpath, skill_dir, "SKILL.md")
                    if os.path.isfile(candidate):
                        skill_files.append((skill_dir, candidate))

    for skill_name, _ in skill_files:
        if skill_name not in manifest_plugins:
            errors.append(
                f"skill exists but not registered in marketplace.json: {skill_name}"
            )

    return {"ok": len(errors) == 0, "errors": errors, "warnings": warnings}


if __name__ == "__main__":
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    result = validate_marketplace(target)
    if result["ok"]:
        print("MARKETPLACE VALIDATION PASSED")
        if result["warnings"]:
            for w in result["warnings"]:
                print(f"  WARN: {w}")
    else:
        print("MARKETPLACE VALIDATION FAILED")
        for e in result["errors"]:
            print(f"  - {e}")
    raise SystemExit(0 if result["ok"] else 1)
