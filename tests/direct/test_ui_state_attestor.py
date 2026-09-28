import json

def test_ui_state_present(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/ui_state_attestor.py")
    direct_vm.sender = direct_alice
    direct_vm.mock_llm(
        r"(?s).*Inspect this application screenshot.*",
        json.dumps({"visible": True, "blocked": False, "confidence": 93, "note": "Success state is clearly visible."}),
    )
    c.attest("u1", "payment success state", b"screen")
    assert c.get_result("u1").verdict == "PRESENT"

def test_ui_blocker_overrides_visible(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/ui_state_attestor.py")
    direct_vm.sender = direct_alice
    direct_vm.mock_llm(
        r"(?s).*Inspect this application screenshot.*",
        json.dumps({"visible": True, "blocked": True, "confidence": 94, "note": "An error modal blocks completion."}),
    )
    c.attest("u2", "payment success state", b"screen")
    r = c.get_result("u2")
    assert r.verdict == "BLOCKED"
    assert r.blocked is True
