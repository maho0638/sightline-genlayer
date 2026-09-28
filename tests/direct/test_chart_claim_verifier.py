import json

def test_chart_claim_supported(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/chart_claim_verifier.py")
    direct_vm.sender = direct_alice
    direct_vm.mock_llm(
        r"(?s).*Inspect this chart or dashboard image.*",
        json.dumps({
            "verdict": "SUPPORTED",
            "confidence": 95,
            "extracted_fact": "September revenue is 120.",
            "rationale": "The bar labeled September reaches 120.",
        }),
    )
    c.verify("c1", "September revenue is at least 100.", b"chart")
    r = c.get_result("c1")
    assert r.verdict == "SUPPORTED"
    assert "120" in r.extracted_fact

def test_chart_claim_low_confidence_abstains(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/chart_claim_verifier.py")
    direct_vm.sender = direct_alice
    direct_vm.mock_llm(
        r"(?s).*Inspect this chart or dashboard image.*",
        json.dumps({
            "verdict": "SUPPORTED",
            "confidence": 35,
            "extracted_fact": "Axis is unclear.",
            "rationale": "Units cannot be read.",
        }),
    )
    c.verify("c2", "Value exceeds 100.", b"chart")
    assert c.get_result("c2").verdict == "UNDETERMINED"
