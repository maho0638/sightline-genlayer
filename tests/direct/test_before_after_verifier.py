import hashlib
import json


def test_before_after_supported(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/before_after_verifier.py")
    direct_vm.sender = direct_alice
    direct_vm.mock_llm(
        r"(?s).*Image 1 is BEFORE and image 2 is AFTER.*",
        json.dumps({"verdict": "SUPPORTED", "materiality": 88, "confidence": 92, "rationale": "The requested element is visibly added."}),
    )
    before = b"before"
    after = b"after"
    c.verify("b1", "A safety railing was installed.", before, after)
    r = c.get_result("b1")
    assert r.verdict == "SUPPORTED"
    assert r.materiality == 88
    assert r.before_hash == hashlib.sha256(before).hexdigest()
    assert r.after_hash == hashlib.sha256(after).hexdigest()


def test_before_after_low_confidence_undetermined(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/before_after_verifier.py")
    direct_vm.sender = direct_alice
    direct_vm.mock_llm(
        r"(?s).*Image 1 is BEFORE and image 2 is AFTER.*",
        json.dumps({"verdict": "SUPPORTED", "materiality": 70, "confidence": 45, "rationale": "Perspective differs."}),
    )
    c.verify("b2", "The damaged area was repaired.", b"before", b"after")
    assert c.get_result("b2").verdict == "UNDETERMINED"


def test_before_after_rejects_identical_evidence(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/before_after_verifier.py")
    direct_vm.sender = direct_alice
    with direct_vm.expect_revert("Before and after images must differ"):
        c.verify("b3", "Something changed.", b"same", b"same")
