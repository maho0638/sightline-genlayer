import json


def _swap_llm(direct_vm, pattern, payload):
    direct_vm.clear_mocks()
    direct_vm.mock_llm(pattern, json.dumps(payload))


def test_receipt_validator_rejects_changed_verdict(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/receipt_attestor.py")
    direct_vm.sender = direct_alice
    pattern = r"(?s).*You verify one receipt image.*"
    direct_vm.mock_llm(pattern, json.dumps({
        "verdict": "MATCH", "confidence": 92,
        "actual_amount": "42.50", "actual_merchant": "Shop", "actual_date": "2026-09-28"
    }))
    c.attest("cg-r", "ref", b"receipt", "Shop", "42.50", "2026-09-28")
    _swap_llm(direct_vm, pattern, {
        "verdict": "MISMATCH", "confidence": 92,
        "actual_amount": "99.00", "actual_merchant": "Shop", "actual_date": "2026-09-28"
    })
    assert direct_vm.run_validator() is False


def test_damage_validator_rejects_changed_severity(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/damage_severity_oracle.py")
    direct_vm.sender = direct_alice
    pattern = r"(?s).*Assess visible physical damage.*"
    direct_vm.mock_llm(pattern, json.dumps({
        "severity": "SEVERE", "confidence": 91, "summary": "Large crack."
    }))
    c.assess("cg-d", "ref", b"damage", "box")
    _swap_llm(direct_vm, pattern, {
        "severity": "MINOR", "confidence": 91, "summary": "Small scuff."
    })
    assert direct_vm.run_validator() is False


def test_before_after_validator_rejects_changed_verdict(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/before_after_verifier.py")
    direct_vm.sender = direct_alice
    pattern = r"(?s).*Image 1 is BEFORE and image 2 is AFTER.*"
    direct_vm.mock_llm(pattern, json.dumps({
        "verdict": "SUPPORTED", "materiality": 90, "confidence": 92, "rationale": "Visible change."
    }))
    c.verify("cg-ba", "A railing was added.", b"before", b"after")
    _swap_llm(direct_vm, pattern, {
        "verdict": "CONTRADICTED", "materiality": 90, "confidence": 92, "rationale": "No change."
    })
    assert direct_vm.run_validator() is False


def test_rubric_validator_rejects_changed_score(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/visual_rubric_gate.py")
    direct_vm.sender = direct_alice
    pattern = r"(?s).*Evaluate the visual deliverable against this frozen rubric.*"
    direct_vm.mock_llm(pattern, json.dumps({
        "verdict": "PASS", "score": 90, "confidence": 91, "reason": "Meets rubric."
    }))
    c.evaluate("cg-g", "Must visibly satisfy the requested state.", b"image")
    _swap_llm(direct_vm, pattern, {
        "verdict": "PASS", "score": 40, "confidence": 91, "reason": "Low score."
    })
    assert direct_vm.run_validator() is False


def test_chart_validator_accepts_non_decisive_wording_drift(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/chart_claim_verifier.py")
    direct_vm.sender = direct_alice
    pattern = r"(?s).*Inspect this chart or dashboard image.*"
    direct_vm.mock_llm(pattern, json.dumps({
        "verdict": "SUPPORTED", "confidence": 93,
        "extracted_fact": "September is 120.", "rationale": "Visible bar."
    }))
    c.verify("cg-chart", "September exceeds 100.", b"chart")
    _swap_llm(direct_vm, pattern, {
        "verdict": "SUPPORTED", "confidence": 93,
        "extracted_fact": "September value reads 120.", "rationale": "Same visible result."
    })
    assert direct_vm.run_validator() is True


def test_ui_validator_rejects_blocker_disagreement(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/ui_state_attestor.py")
    direct_vm.sender = direct_alice
    pattern = r"(?s).*Inspect this application screenshot.*"
    direct_vm.mock_llm(pattern, json.dumps({
        "visible": True, "blocked": False, "confidence": 94, "note": "Success visible."
    }))
    c.attest("cg-ui", "payment success", b"screen")
    _swap_llm(direct_vm, pattern, {
        "visible": True, "blocked": True, "confidence": 94, "note": "Modal blocks."
    })
    assert direct_vm.run_validator() is False


def test_document_validator_rejects_changed_observed_value(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/document_field_attestor.py")
    direct_vm.sender = direct_alice
    pattern = r"(?s).*FIELD TO CHECK.*"
    direct_vm.mock_llm(pattern, json.dumps({
        "observed_value": "INV-100", "verdict": "MATCH", "confidence": 96
    }))
    c.attest("cg-doc", "invoice number", "INV-100", b"document")
    _swap_llm(direct_vm, pattern, {
        "observed_value": "INV-999", "verdict": "MISMATCH", "confidence": 96
    })
    assert direct_vm.run_validator() is False


def test_decision_validator_rejects_yes_no_disagreement(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/visual_decision_receipt.py")
    direct_vm.sender = direct_alice
    pattern = r"(?s).*Answer this bounded question using only the visual evidence.*"
    direct_vm.mock_llm(pattern, json.dumps({
        "decision": "YES", "confidence": 92, "rationale": "Visible."
    }))
    c.decide("cg-vd", "Is the seal visible?", "ref", b"image")
    _swap_llm(direct_vm, pattern, {
        "decision": "NO", "confidence": 92, "rationale": "Not visible."
    })
    assert direct_vm.run_validator() is False


def test_quorum_validator_rejects_aggregate_flip(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/visual_quorum.py")
    direct_vm.sender = direct_alice
    pattern = r"(?s).*Judge this ONE visual evidence item.*"
    direct_vm.mock_llm(pattern, json.dumps({
        "verdict": "SUPPORTED", "confidence": 90
    }))
    c.verify("cg-q", "The package is sealed.", b"a", b"b", b"c")
    _swap_llm(direct_vm, pattern, {
        "verdict": "CONTRADICTED", "confidence": 90
    })
    assert direct_vm.run_validator() is False


def test_challengeable_validator_rejects_verdict_flip(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/challengeable_visual_claim.py")
    direct_vm.sender = direct_alice
    pattern = r"(?s).*Does the visual evidence support this claim.*"
    direct_vm.mock_llm(pattern, json.dumps({
        "verdict": "SUPPORTED", "confidence": 90
    }))
    c.open_claim("cg-c", "The image is red.", b"red")
    _swap_llm(direct_vm, pattern, {
        "verdict": "CONTRADICTED", "confidence": 90
    })
    assert direct_vm.run_validator() is False


def test_rubric_validator_rejects_score_threshold_crossing(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/visual_rubric_gate.py")
    direct_vm.sender = direct_alice
    pattern = r"(?s).*Evaluate the visual deliverable against this frozen rubric.*"
    direct_vm.mock_llm(pattern, json.dumps({"verdict":"PASS","score":72,"confidence":90,"reason":"Above threshold."}))
    c.evaluate("cg-g-boundary", "Must satisfy the rubric.", b"image")
    _swap_llm(direct_vm, pattern, {"verdict":"PASS","score":68,"confidence":90,"reason":"Below threshold."})
    assert direct_vm.run_validator() is False


def test_rubric_validator_accepts_same_final_outcome_drift(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/visual_rubric_gate.py")
    direct_vm.sender = direct_alice
    pattern = r"(?s).*Evaluate the visual deliverable against this frozen rubric.*"
    direct_vm.mock_llm(pattern, json.dumps({"verdict":"PASS","score":78,"confidence":82,"reason":"Pass."}))
    c.evaluate("cg-g-stable", "Must satisfy the rubric.", b"image")
    _swap_llm(direct_vm, pattern, {"verdict":"PASS","score":75,"confidence":79,"reason":"Still pass."})
    assert direct_vm.run_validator() is True


def test_before_after_validator_rejects_confidence_threshold_crossing(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/before_after_verifier.py"); direct_vm.sender = direct_alice
    pattern = r"(?s).*Image 1 is BEFORE and image 2 is AFTER.*"
    direct_vm.mock_llm(pattern, json.dumps({"verdict":"SUPPORTED","materiality":80,"confidence":70,"rationale":"Visible."}))
    c.verify("cg-ba-boundary", "A railing was added.", b"before", b"after")
    _swap_llm(direct_vm, pattern, {"verdict":"SUPPORTED","materiality":80,"confidence":60,"rationale":"Less certain."})
    assert direct_vm.run_validator() is False


def test_challengeable_validator_rejects_confidence_threshold_crossing(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/challengeable_visual_claim.py"); direct_vm.sender = direct_alice
    pattern = r"(?s).*Does the visual evidence support this claim.*"
    direct_vm.mock_llm(pattern, json.dumps({"verdict":"SUPPORTED","confidence":70}))
    c.open_claim("cg-c-boundary", "The image is red.", b"red")
    _swap_llm(direct_vm, pattern, {"verdict":"SUPPORTED","confidence":60})
    assert direct_vm.run_validator() is False


def test_damage_validator_rejects_confidence_threshold_crossing(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/damage_severity_oracle.py"); direct_vm.sender = direct_alice
    pattern = r"(?s).*Assess visible physical damage.*"
    direct_vm.mock_llm(pattern, json.dumps({"severity":"SEVERE","confidence":65,"summary":"Large crack."}))
    c.assess("cg-d-boundary", "ref", b"damage", "box")
    _swap_llm(direct_vm, pattern, {"severity":"SEVERE","confidence":55,"summary":"Same crack."})
    assert direct_vm.run_validator() is False


def test_document_validator_rejects_confidence_threshold_crossing(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/document_field_attestor.py"); direct_vm.sender = direct_alice
    pattern = r"(?s).*FIELD TO CHECK.*"
    direct_vm.mock_llm(pattern, json.dumps({"observed_value":"INV-100","verdict":"MATCH","confidence":70}))
    c.attest("cg-doc-boundary", "invoice number", "INV-100", b"document")
    _swap_llm(direct_vm, pattern, {"observed_value":"INV-100","verdict":"MATCH","confidence":60})
    assert direct_vm.run_validator() is False


def test_receipt_validator_rejects_confidence_threshold_crossing(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/receipt_attestor.py"); direct_vm.sender = direct_alice
    pattern = r"(?s).*You verify one receipt image.*"
    direct_vm.mock_llm(pattern, json.dumps({"verdict":"MATCH","confidence":70,"actual_amount":"42.50","actual_merchant":"Shop","actual_date":"2026-09-28"}))
    c.attest("cg-r-boundary", "ref", b"receipt", "Shop", "42.50", "2026-09-28")
    _swap_llm(direct_vm, pattern, {"verdict":"MATCH","confidence":60,"actual_amount":"42.50 USD","actual_merchant":"Shop","actual_date":"2026-09-28"})
    assert direct_vm.run_validator() is False


def test_ui_validator_rejects_confidence_threshold_crossing(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/ui_state_attestor.py"); direct_vm.sender = direct_alice
    pattern = r"(?s).*Inspect this application screenshot.*"
    direct_vm.mock_llm(pattern, json.dumps({"visible":True,"blocked":False,"confidence":70,"note":"Visible."}))
    c.attest("cg-ui-boundary", "payment success", b"screen")
    _swap_llm(direct_vm, pattern, {"visible":True,"blocked":False,"confidence":60,"note":"Less certain."})
    assert direct_vm.run_validator() is False


def test_decision_validator_rejects_confidence_threshold_crossing(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/visual_decision_receipt.py"); direct_vm.sender = direct_alice
    pattern = r"(?s).*Answer this bounded question using only the visual evidence.*"
    direct_vm.mock_llm(pattern, json.dumps({"decision":"YES","confidence":70,"rationale":"Visible."}))
    c.decide("cg-vd-boundary", "Is the seal visible?", "ref", b"image")
    _swap_llm(direct_vm, pattern, {"decision":"YES","confidence":60,"rationale":"Less certain."})
    assert direct_vm.run_validator() is False
