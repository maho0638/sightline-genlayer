import json


def test_receipt_duplicate_id_rejected(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/receipt_attestor.py")
    direct_vm.sender = direct_alice
    direct_vm.mock_llm(r"(?s).*You verify one receipt image.*", json.dumps({
        "verdict": "MATCH", "confidence": 90, "actual_amount": "1.00",
        "actual_merchant": "Shop", "actual_date": "2026-09-28"
    }))
    c.attest("dup-r", "ref", b"img", "Shop", "1.00", "2026-09-28")
    with direct_vm.expect_revert("Result already exists"):
        c.attest("dup-r", "ref2", b"img2", "Shop", "1.00", "2026-09-28")


def test_damage_duplicate_id_rejected(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/damage_severity_oracle.py")
    direct_vm.sender = direct_alice
    direct_vm.mock_llm(r"(?s).*Assess visible physical damage.*", json.dumps({
        "severity": "NONE", "confidence": 90, "summary": "No damage."
    }))
    c.assess("dup-d", "ref", b"img", "box")
    with direct_vm.expect_revert("Result already exists"):
        c.assess("dup-d", "ref2", b"img2", "box")


def test_before_after_duplicate_id_rejected(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/before_after_verifier.py")
    direct_vm.sender = direct_alice
    direct_vm.mock_llm(r"(?s).*Image 1 is BEFORE and image 2 is AFTER.*", json.dumps({
        "verdict": "SUPPORTED", "materiality": 80, "confidence": 90, "rationale": "Changed."
    }))
    c.verify("dup-ba", "Changed.", b"before", b"after")
    with direct_vm.expect_revert("Result already exists"):
        c.verify("dup-ba", "Changed again.", b"before2", b"after2")


def test_rubric_duplicate_id_rejected(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/visual_rubric_gate.py")
    direct_vm.sender = direct_alice
    direct_vm.mock_llm(r"(?s).*Evaluate the visual deliverable against this frozen rubric.*", json.dumps({
        "verdict": "PASS", "score": 90, "confidence": 90, "reason": "Pass."
    }))
    c.evaluate("dup-g", "Must show requested state.", b"img")
    with direct_vm.expect_revert("Result already exists"):
        c.evaluate("dup-g", "Another rubric.", b"img2")


def test_chart_duplicate_id_rejected(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/chart_claim_verifier.py")
    direct_vm.sender = direct_alice
    direct_vm.mock_llm(r"(?s).*Inspect this chart or dashboard image.*", json.dumps({
        "verdict": "SUPPORTED", "confidence": 90,
        "extracted_fact": "Value 120.", "rationale": "Visible."
    }))
    c.verify("dup-chart", "Value exceeds 100.", b"chart")
    with direct_vm.expect_revert("Result already exists"):
        c.verify("dup-chart", "Other claim.", b"chart2")


def test_ui_duplicate_id_rejected(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/ui_state_attestor.py")
    direct_vm.sender = direct_alice
    direct_vm.mock_llm(r"(?s).*Inspect this application screenshot.*", json.dumps({
        "visible": True, "blocked": False, "confidence": 90, "note": "Visible."
    }))
    c.attest("dup-ui", "success state", b"screen")
    with direct_vm.expect_revert("Result already exists"):
        c.attest("dup-ui", "other state", b"screen2")


def test_document_duplicate_id_rejected(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/document_field_attestor.py")
    direct_vm.sender = direct_alice
    direct_vm.mock_llm(r"(?s).*FIELD TO CHECK.*", json.dumps({
        "observed_value": "INV-1", "verdict": "MATCH", "confidence": 90
    }))
    c.attest("dup-doc", "invoice number", "INV-1", b"doc")
    with direct_vm.expect_revert("Result already exists"):
        c.attest("dup-doc", "invoice number", "INV-2", b"doc2")


def test_decision_duplicate_id_rejected(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/visual_decision_receipt.py")
    direct_vm.sender = direct_alice
    direct_vm.mock_llm(r"(?s).*Answer this bounded question using only the visual evidence.*", json.dumps({
        "decision": "YES", "confidence": 90, "rationale": "Yes."
    }))
    c.decide("dup-vd", "Is it visible?", "ref", b"img")
    with direct_vm.expect_revert("Receipt already exists"):
        c.decide("dup-vd", "Is something else visible?", "ref2", b"img2")
