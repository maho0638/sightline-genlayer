import json

def test_document_field_match(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/document_field_attestor.py")
    direct_vm.sender = direct_alice
    direct_vm.mock_llm(
        r"(?s).*FIELD TO CHECK.*",
        json.dumps({"observed_value": "INV-2026-1007", "verdict": "MATCH", "confidence": 97}),
    )
    c.attest("f1", "invoice number", "INV-2026-1007", b"document")
    r = c.get_result("f1")
    assert r.verdict == "MATCH"
    assert r.observed_value == "INV-2026-1007"

def test_document_field_requires_expected_value(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/document_field_attestor.py")
    direct_vm.sender = direct_alice
    with direct_vm.expect_revert("Missing ID, field name, or expected value"):
        c.attest("f2", "invoice number", "", b"document")
