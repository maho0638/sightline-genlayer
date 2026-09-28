import hashlib
import json


def test_damage_binds_exact_image(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/damage_severity_oracle.py")
    direct_vm.sender = direct_alice
    image = b"damage-evidence"
    direct_vm.mock_llm(r"(?s).*Assess visible physical damage.*", json.dumps({
        "severity": "MODERATE", "confidence": 90, "summary": "Visible damage."
    }))
    c.assess("bind-damage", "ref", image, "box")
    assert c.get_result("bind-damage").evidence_hash == hashlib.sha256(image).hexdigest()


def test_chart_binds_exact_image(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/chart_claim_verifier.py")
    direct_vm.sender = direct_alice
    image = b"chart-evidence"
    direct_vm.mock_llm(r"(?s).*Inspect this chart or dashboard image.*", json.dumps({
        "verdict": "SUPPORTED", "confidence": 90,
        "extracted_fact": "Value 120.", "rationale": "Visible."
    }))
    c.verify("bind-chart", "Value is 120.", image)
    assert c.get_result("bind-chart").evidence_hash == hashlib.sha256(image).hexdigest()


def test_ui_binds_exact_image(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/ui_state_attestor.py")
    direct_vm.sender = direct_alice
    image = b"ui-evidence"
    direct_vm.mock_llm(r"(?s).*Inspect this application screenshot.*", json.dumps({
        "visible": True, "blocked": False, "confidence": 90, "note": "Visible."
    }))
    c.attest("bind-ui", "success state", image)
    assert c.get_result("bind-ui").evidence_hash == hashlib.sha256(image).hexdigest()


def test_document_binds_exact_image(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/document_field_attestor.py")
    direct_vm.sender = direct_alice
    image = b"document-evidence"
    direct_vm.mock_llm(r"(?s).*FIELD TO CHECK.*", json.dumps({
        "observed_value": "INV-1", "verdict": "MATCH", "confidence": 90
    }))
    c.attest("bind-doc", "invoice number", "INV-1", image)
    assert c.get_result("bind-doc").evidence_hash == hashlib.sha256(image).hexdigest()


def test_decision_receipt_binds_exact_image(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/visual_decision_receipt.py")
    direct_vm.sender = direct_alice
    image = b"decision-evidence"
    direct_vm.mock_llm(r"(?s).*Answer this bounded question using only the visual evidence.*", json.dumps({
        "decision": "YES", "confidence": 90, "rationale": "Visible."
    }))
    c.decide("bind-decision", "Is it visible?", "ref", image)
    assert c.get_receipt("bind-decision").evidence_hash == hashlib.sha256(image).hexdigest()
