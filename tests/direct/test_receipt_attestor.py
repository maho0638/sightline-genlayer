import hashlib
import json


def test_receipt_match(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/receipt_attestor.py")
    direct_vm.sender = direct_alice
    direct_vm.mock_llm(
        r"(?s).*You verify one receipt image.*",
        json.dumps({
            "verdict": "MATCH",
            "confidence": 94,
            "actual_amount": "42.50",
            "actual_merchant": "Example Market",
            "actual_date": "2026-09-28",
        }),
    )
    image = b"receipt-image"
    c.attest("r1", "ipfs://receipt-1", image, "Example Market", "42.50", "2026-09-28")
    r = c.get_result("r1")
    assert r.verdict == "MATCH"
    assert r.actual_amount == "42.50"
    assert r.evidence_hash == hashlib.sha256(image).hexdigest()
    assert direct_vm.run_validator() is True


def test_receipt_low_confidence_fails_closed(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/receipt_attestor.py")
    direct_vm.sender = direct_alice
    direct_vm.mock_llm(
        r"(?s).*You verify one receipt image.*",
        json.dumps({
            "verdict": "MATCH",
            "confidence": 40,
            "actual_amount": "42.50",
            "actual_merchant": "Example Market",
            "actual_date": "2026-09-28",
        }),
    )
    c.attest("r2", "ipfs://receipt-2", b"image", "Example Market", "42.50", "2026-09-28")
    assert c.get_result("r2").verdict == "UNDETERMINED"


def test_receipt_rejects_empty_image(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/receipt_attestor.py")
    direct_vm.sender = direct_alice
    with direct_vm.expect_revert("Image data is empty"):
        c.attest("r3", "ipfs://receipt-3", b"", "Example Market", "42.50", "2026-09-28")
