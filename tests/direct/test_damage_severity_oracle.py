import json

def test_damage_severe(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/damage_severity_oracle.py")
    direct_vm.sender = direct_alice
    direct_vm.mock_llm(
        r"(?s).*Assess visible physical damage.*",
        json.dumps({"severity": "SEVERE", "confidence": 93, "summary": "Large visible structural crack."}),
    )
    c.assess("d1", "photo://damage-1", b"image", "shipping box")
    r = c.get_result("d1")
    assert r.severity == "SEVERE"
    assert r.confidence == 93

def test_damage_low_confidence_undetermined(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/damage_severity_oracle.py")
    direct_vm.sender = direct_alice
    direct_vm.mock_llm(
        r"(?s).*Assess visible physical damage.*",
        json.dumps({"severity": "MODERATE", "confidence": 30, "summary": "Image is unclear."}),
    )
    c.assess("d2", "photo://damage-2", b"image", "device")
    assert c.get_result("d2").severity == "UNDETERMINED"
