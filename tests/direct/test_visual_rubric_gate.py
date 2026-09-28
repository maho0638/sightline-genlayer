import hashlib
import json


def test_rubric_pass(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/visual_rubric_gate.py")
    direct_vm.sender = direct_alice
    direct_vm.mock_llm(
        r"(?s).*Evaluate the visual deliverable against this frozen rubric.*",
        json.dumps({"verdict": "PASS", "score": 88, "confidence": 90, "reason": "All required visual elements are present."}),
    )
    image = b"rubric-image"
    c.evaluate("g1", "Must show title, chart, and legend.", image)
    r = c.get_result("g1")
    assert r.verdict == "PASS"
    assert r.score == 88
    assert r.evidence_hash == hashlib.sha256(image).hexdigest()


def test_rubric_score_floor(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/visual_rubric_gate.py")
    direct_vm.sender = direct_alice
    direct_vm.mock_llm(
        r"(?s).*Evaluate the visual deliverable against this frozen rubric.*",
        json.dumps({"verdict": "PASS", "score": 55, "confidence": 92, "reason": "Only part of rubric met."}),
    )
    c.evaluate("g2", "Must satisfy all items.", b"img")
    assert c.get_result("g2").verdict == "FAIL"


def test_rubric_rejects_empty_image(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/visual_rubric_gate.py")
    direct_vm.sender = direct_alice
    with direct_vm.expect_revert("Image data is empty"):
        c.evaluate("g3", "Must show a red square.", b"")
