import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import scanner

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE = os.path.join(HERE, "sample_project")


def test_finds_imports_and_model_ids():
    imports, ids = scanner.scan_file(os.path.join(SAMPLE, "services", "chat_service.py"))
    assert "openai" in imports and "anthropic" in imports
    assert "gpt-4o" in ids


def test_bedrock_replaces_plain_boto3():
    imports, ids = scanner.scan_file(os.path.join(SAMPLE, "services", "fraud_rules.py"))
    assert "boto3 bedrock" in imports and "boto3" not in imports
    assert any("claude" in i for i in ids)


def test_inventory_includes_model_files():
    df = scanner.build_inventory(SAMPLE)
    assert (df["kind"] == "model_file").sum() == 2
    assert df.loc[df["name"] == "openai", "pinned"].iloc[0]
    assert not df.loc[df["name"] == "anthropic", "pinned"].iloc[0]


def test_restrictive_license_lowers_score():
    known = scanner.load_json("known_models.json")
    checklist = scanner.load_json("checklist.json")
    df = scanner.build_inventory(SAMPLE)
    scored = scanner.score_inventory(df, known, checklist)
    yolo = scored[scored["name"] == "ultralytics/yolov5"].iloc[0]
    mini = scored[scored["name"] == "sentence-transformers/all-MiniLM-L6-v2"].iloc[0]
    assert yolo["score"] < mini["score"]
    assert set(scored["risk_band"]) <= {"low", "medium", "high"}
