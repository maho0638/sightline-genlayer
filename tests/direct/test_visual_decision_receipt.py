import json

def test_visual_decision_yes(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/visual_decision_receipt.py")
    direct_vm.sender = direct_alice
    direct_vm.mock_llm(
        r"(?s).*Answer this bounded question using only the visual evidence.*",
        json.dumps({"decision": "YES", "confidence": 91, "rationale": "The required seal is visible."}),
    )
    c.decide("v1", "Is the required seal visible?", "photo://seal-1", b"image")
    r = c.get_receipt("v1")
    assert r.decision == "YES"
    assert r.evidence_ref == "photo://seal-1"

def test_visual_decision_low_confidence_abstains(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/visual_decision_receipt.py")
    direct_vm.sender = direct_alice
    direct_vm.mock_llm(
        r"(?s).*Answer this bounded question using only the visual evidence.*",
        json.dumps({"decision": "YES", "confidence": 40, "rationale": "Image is blurry."}),
    )
    c.decide("v2", "Is the required seal visible?", "photo://seal-2", b"image")
    assert c.get_receipt("v2").decision == "ABSTAIN"
