#!/usr/bin/env python3
"""Static validator for Dify workflow YAML files."""

import sys, re
import yaml


def main(yml_path):
    with open(yml_path, "r") as f:
        d = yaml.safe_load(f)

    errors = []

    for k in ["app", "kind", "version", "workflow"]:
        if k not in d:
            errors.append(f"missing top-level key: {k}")

    wf = d.get("workflow", {})
    graph = wf.get("graph", {})
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])

    if not isinstance(nodes, list):
        errors.append("nodes is not a list")
    if not isinstance(edges, list):
        errors.append("edges is not a list")

    node_ids = set()
    id_to_node = {}
    for n in nodes:
        nid = n.get("id")
        if not nid:
            errors.append("node missing id")
            continue
        if nid in node_ids:
            errors.append(f"duplicate node id: {nid}")
        node_ids.add(nid)
        id_to_node[nid] = n
        if not n.get("data", {}).get("type"):
            errors.append(f"node {nid} missing data.type")

    for e in edges:
        src = e.get("source")
        tgt = e.get("target")
        if src not in node_ids:
            errors.append(f"edge source {src} not in nodes (target={tgt})")
        if tgt not in node_ids:
            errors.append(f"edge target {tgt} not in nodes (source={src})")
        ed = e.get("data", {})
        src_type = id_to_node.get(src, {}).get("data", {}).get("type", "")
        tgt_type = id_to_node.get(tgt, {}).get("data", {}).get("type", "")
        if ed.get("sourceType") != src_type:
            errors.append(
                f"edge {e['id']}: sourceType={ed.get('sourceType')} != node type={src_type}"
            )
        if ed.get("targetType") != tgt_type:
            errors.append(
                f"edge {e['id']}: targetType={ed.get('targetType')} != node type={tgt_type}"
            )

    def collect_outputs(node):
        outs = set()
        dt = node.get("data", {})
        ntype = dt.get("type", "")
        if ntype == "start":
            for v in dt.get("variables", []):
                outs.add(v.get("variable", ""))
        elif ntype == "llm":
            outs.add("text")
        elif ntype == "code":
            for v in dt.get("variables", []):
                outs.add(v.get("variable", ""))
            for k in dt.get("outputs") or {}:
                outs.add(k)
        elif ntype == "template-transform":
            for v in dt.get("variables", []):
                outs.add(v.get("variable", ""))
            outs.add("output")
        return outs

    for n in nodes:
        nid = n.get("id", "")
        dt = n.get("data", {})
        for v in dt.get("variables", []) or []:
            sel = v.get("value_selector", [])
            if not sel:
                continue
            if len(sel) < 2:
                errors.append(f"node {nid}: bad value_selector {sel}")
                continue
            src_id, var_name = sel[0], sel[1]
            if src_id not in id_to_node:
                errors.append(f"node {nid}: value_selector source {src_id} not found")
                continue
            src_outputs = collect_outputs(id_to_node[src_id])
            if var_name not in src_outputs:
                errors.append(
                    f"node {nid}: variable {var_name} not in source {src_id} outputs {src_outputs}"
                )
        if dt.get("type") == "end":
            for o in dt.get("outputs", []) or []:
                if not isinstance(o, dict):
                    continue
                sel = o.get("value_selector", [])
                if len(sel) < 2:
                    errors.append(f"node {nid}: bad output value_selector {sel}")
                    continue
                src_id, var_name = sel[0], sel[1]
                if src_id not in id_to_node:
                    errors.append(f"node {nid}: output source {src_id} not found")
                    continue
                src_outputs = collect_outputs(id_to_node[src_id])
                if var_name not in src_outputs:
                    errors.append(
                        f"node {nid}: output variable {var_name} not in source {src_id} outputs {src_outputs}"
                    )

    for n in nodes:
        dt = n.get("data", {})
        if dt.get("type") != "code":
            continue
        nid = n.get("id", "")
        code = dt.get("code", "")
        in_vars = [v.get("variable", "") for v in (dt.get("variables") or [])]
        m = re.search(r"def main\(([^)]*)\)", code)
        if m:
            params = [p.strip() for p in m.group(1).split(",") if p.strip()]
            if set(params) != set(in_vars):
                errors.append(
                    f"node {nid}: code params {params} != declared vars {in_vars}"
                )
        out_keys = set((dt.get("outputs") or {}).keys())
        ret_match = re.search(r"return\s+\{([^}]+)\}", code, re.DOTALL)
        if ret_match:
            ret_keys = set(re.findall(r"'(\w+)'\s*:", ret_match.group(1)))
            if ret_keys != out_keys:
                errors.append(
                    f"node {nid}: code return keys {ret_keys} != declared outputs {out_keys}"
                )

    for n in nodes:
        dt = n.get("data", {})
        if dt.get("type") != "template-transform":
            continue
        nid = n.get("id", "")
        tmpl = dt.get("template", "")
        tmpl_vars = re.findall(r"\{\{\s*(\w+)\s*\}\}", tmpl)
        declared = [v.get("variable", "") for v in (dt.get("variables") or [])]
        for tv in tmpl_vars:
            if tv not in declared:
                errors.append(
                    f"node {nid}: template uses {{{{ {tv} }}}} not declared in variables {declared}"
                )

    if errors:
        print("VALIDATION FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1
    else:
        print("VALIDATION PASSED")
        print(f"  Nodes: {len(nodes)}, Edges: {len(edges)}")
        for n in nodes:
            print(f"  Node {n['id']} ({n['data']['type']}): {n['data']['title']}")
        return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 validate_workflow.py <workflow.yml>")
        sys.exit(1)
    sys.exit(main(sys.argv[1]))
