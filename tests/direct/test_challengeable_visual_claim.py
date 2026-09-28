import hashlib
import json


def _mock_supported(direct_vm):
    direct_vm.mock_llm(
        r"(?s).*Does the visual evidence support this claim.*",
        json.dumps({"verdict": "SUPPORTED", "confidence": 90}),
    )


def test_one_fresh_challenge_then_finalize(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/challengeable_visual_claim.py")
    direct_vm.sender = direct_alice
    _mock_supported(direct_vm)

    c.open_claim("v1", "package delivered intact", b"img1")
    c.challenge("v1", b"img2")
    r = c.get_claim("v1")
    assert r.challenged is True
    assert r.final_verdict == "SUPPORTED"
    assert r.initial_evidence_hash == hashlib.sha256(b"img1").hexdigest()
    assert r.challenge_evidence_hash == hashlib.sha256(b"img2").hexdigest()
    assert c.is_finalization_ready("v1") is True

    c.finalize("v1")
    assert c.get_claim("v1").finalized is True

    with direct_vm.expect_revert("Claim already finalized"):
        c.challenge("v1", b"img3")


def test_finalize_locked_during_challenge_window(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/challengeable_visual_claim.py")
    direct_vm.sender = direct_alice
    _mock_supported(direct_vm)

    c.open_claim("v2", "claim", b"img")
    assert c.is_finalization_ready("v2") is False
    with direct_vm.expect_revert("Challenge window is still open"):
        c.finalize("v2")


def test_challenge_requires_different_evidence(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/challengeable_visual_claim.py")
    direct_vm.sender = direct_alice
    _mock_supported(direct_vm)

    c.open_claim("v3", "claim", b"same-image")
    with direct_vm.expect_revert("Challenge must provide different evidence"):
        c.challenge("v3", b"same-image")
