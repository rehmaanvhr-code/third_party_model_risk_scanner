"""Walk a code base, find third party AI models and APIs, and score each one
against a short third party model risk checklist.

    python scanner.py                 scans sample_project/
    python scanner.py path/to/repo
"""

import json
import os
import re
import sys

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "outputs")

AI_PACKAGES = ["openai", "anthropic", "transformers", "sentence_transformers",
               "huggingface_hub", "langchain", "langchain_community", "langchain_openai",
               "cohere", "vertexai", "google.generativeai", "boto3", "torch", "mistralai"]

MODEL_FILE_EXT = (".pkl", ".pickle", ".joblib", ".pt", ".pth", ".h5", ".onnx", ".safetensors", ".bin")

# model id patterns that appear as string literals in code
MODEL_ID_PATTERNS = [
    r"model\s*=\s*['\"]([^'\"]+)['\"]",
    r"modelId\s*=\s*['\"]([^'\"]+)['\"]",
    r"SentenceTransformer\(\s*['\"]([^'\"]+)['\"]",
    r"from_pretrained\(\s*['\"]([^'\"]+)['\"]",
    r"torch\.hub\.load\(\s*['\"]([^'\"]+)['\"]",
    r"pipeline\([^)]*model\s*=\s*['\"]([^'\"]+)['\"]",
]

IMPORT_RE = re.compile(r"^\s*(?:from\s+([\w\.]+)\s+import|import\s+([\w\.]+))", re.M)


def load_json(name):
    with open(os.path.join(HERE, "data", name)) as f:
        return json.load(f)


def parse_requirements(root):
    """Return {package: pinned_version_or_None} from any requirements file."""
    pins = {}
    for dirpath, _, files in os.walk(root):
        for fn in files:
            if fn.startswith("requirements") and fn.endswith(".txt"):
                for line in open(os.path.join(dirpath, fn)):
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    m = re.match(r"([A-Za-z0-9_.\-]+)\s*(==|>=|<=|~=|>|<)?\s*([^\s;#]*)", line)
                    if m:
                        name = m.group(1).lower().replace("-", "_")
                        pins[name] = m.group(3) if m.group(2) == "==" else None
    return pins


def scan_file(path):
    """Return (imports, model_ids) found in one python file."""
    try:
        text = open(path, encoding="utf8", errors="ignore").read()
    except OSError:
        return [], []
    imports = []
    for a, b in IMPORT_RE.findall(text):
        mod = a or b
        top = ".".join(mod.split(".")[:2]) if mod.startswith("google.") else mod.split(".")[0]
        if top in AI_PACKAGES or mod in AI_PACKAGES:
            imports.append(mod if mod in AI_PACKAGES else top)
    model_ids = []
    for pat in MODEL_ID_PATTERNS:
        model_ids.extend(re.findall(pat, text))
    if "bedrock" in text and "boto3" in text:
        imports = [i for i in imports if i != "boto3"] + ["boto3 bedrock"]
    return sorted(set(imports)), sorted(set(model_ids))


def build_inventory(root):
    pins = parse_requirements(root)
    rows = []
    for dirpath, dirnames, files in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and d not in ("__pycache__", "node_modules", "venv")]
        for fn in files:
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, root)
            if fn.endswith(".py"):
                imports, model_ids = scan_file(path)
                for imp in imports:
                    pkg = imp.split(" ")[0]
                    rows.append({"file": rel, "kind": "package", "name": imp,
                                 "pinned": pins.get(pkg) is not None, "version": pins.get(pkg)})
                for mid in model_ids:
                    rows.append({"file": rel, "kind": "model_id", "name": mid,
                                 "pinned": bool(re.search(r"\d{8}|v\d|:\d", mid)), "version": None})
            elif fn.lower().endswith(MODEL_FILE_EXT):
                rows.append({"file": rel, "kind": "model_file", "name": fn,
                             "pinned": bool(re.search(r"v\d+", fn)), "version": None})
    df = pd.DataFrame(rows, columns=["file", "kind", "name", "pinned", "version"])
    return df.drop_duplicates().reset_index(drop=True)


def score_dependency(row, known, checklist):
    info = known["models"].get(row["name"], {})
    checks = {
        "provenance": bool(info.get("provenance", False)),
        "license": bool(info.get("license_known", False)) and not info.get("license_restrictive", False),
        "model_card": bool(info.get("model_card", False)),
        "version_pinned": bool(row["pinned"]),
        "data_residency": bool(info.get("data_residency_confirmed", False)),
        "evaluation": bool(info.get("evaluated_internally", False)),
        "incident_process": bool(info.get("incident_process", False)),
    }
    if row["kind"] == "model_file":
        # an in house artifact: provenance is whoever trained it, license is not a question
        checks["provenance"] = False
        checks["license"] = True
        checks["model_card"] = False
        checks["data_residency"] = True
    if row["kind"] == "package":
        # a package import on its own tells you a vendor is in play, not which model
        checks["provenance"] = True
        checks["license"] = True
        checks["model_card"] = False
    total = sum(i["weight"] for i in checklist["items"])
    got = sum(i["weight"] for i in checklist["items"] if checks[i["id"]])
    score = got / total
    bands = checklist["bands"]
    band = "low" if score >= bands["low"] else "medium" if score >= bands["medium"] else "high"
    return checks, round(score, 3), band, info


def score_inventory(df, known, checklist):
    records = []
    for _, row in df.iterrows():
        checks, score, band, info = score_dependency(row, known, checklist)
        rec = dict(row)
        rec.update(checks)
        rec["vendor"] = info.get("vendor", "")
        rec["license_text"] = info.get("license", "")
        rec["score"] = score
        rec["risk_band"] = band
        records.append(rec)
    return pd.DataFrame(records)


def write_report(scored, checklist, root, path):
    L = ["# Third party AI model risk report", "",
         "Scanned: %s. %d dependencies found across %d files." % (root, len(scored), scored["file"].nunique()), ""]
    counts = scored["risk_band"].value_counts()
    L.append("Risk bands: " + ", ".join("%s %d" % (b, counts.get(b, 0)) for b in ["high", "medium", "low"]) + ".")
    L.append("")
    L.append("## Checklist")
    L.append("")
    for item in checklist["items"]:
        L.append("%s (weight %d). %s Source: %s." % (item["name"], item["weight"], item["question"], item["source"]))
        L.append("")
    L.append("## Findings")
    L.append("")
    for band in ["high", "medium", "low"]:
        part = scored[scored["risk_band"] == band].sort_values("score")
        if part.empty:
            continue
        L.append("### %s risk" % band.capitalize())
        L.append("")
        for _, r in part.iterrows():
            failed = [i["name"] for i in checklist["items"] if not r[i["id"]]]
            L.append("%s (%s) in %s. Score %.2f. Vendor: %s. License: %s."
                     % (r["name"], r["kind"], r["file"], r["score"], r["vendor"] or "unknown", r["license_text"] or "unknown"))
            if failed:
                L.append("Open items: " + "; ".join(failed) + ".")
            L.append("")
    L.append("## What to do with this")
    L.append("")
    L.append("Items marked data residency, evaluation and incident process cannot be inferred from code. Set them to true in data/known_models.json once the organisation has confirmed them with the vendor, then rerun. A pickled model file with no documentation nearby is a sign the model is not in the inventory at all.")
    with open(path, "w") as f:
        f.write("\n".join(L))


def plot_scores(scored, path):
    s = scored.sort_values("score")
    colors = {"high": "#c0392b", "medium": "#e67e22", "low": "#27ae60"}
    fig, ax = plt.subplots(figsize=(8, 0.4 * len(s) + 1.5))
    ax.barh(range(len(s)), s["score"], color=[colors[b] for b in s["risk_band"]])
    ax.set_yticks(range(len(s)))
    ax.set_yticklabels([n[:45] for n in s["name"]])
    ax.set_xlim(0, 1)
    ax.set_xlabel("checklist score (1 is fully covered)")
    ax.set_title("Third party AI dependencies by checklist coverage")
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def main(root):
    known = load_json("known_models.json")
    checklist = load_json("checklist.json")
    df = build_inventory(root)
    scored = score_inventory(df, known, checklist)
    os.makedirs(OUT, exist_ok=True)
    scored.to_csv(os.path.join(OUT, "inventory.csv"), index=False)
    write_report(scored, checklist, root, os.path.join(OUT, "risk_report.md"))
    plot_scores(scored, os.path.join(OUT, "risk_scores.png"))
    print(scored[["file", "kind", "name", "score", "risk_band"]].to_string(index=False))
    print("wrote outputs/inventory.csv, risk_report.md, risk_scores.png")
    return scored


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "sample_project")
    main(target)
