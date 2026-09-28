"""Canonical live Studionet verification for Sightline visual-consensus primitives."""

import binascii
import struct
import zlib

import pytest
from gltest import get_contract_factory
from gltest.assertions import tx_execution_succeeded


def _field(value, name):
    if isinstance(value, dict):
        return value.get(name)
    return getattr(value, name)


def _solid_png(red: int, green: int, blue: int, size: int = 64) -> bytes:
    """Generate a deterministic RGB PNG using only the Python standard library."""
    signature = b"\x89PNG\r\n\x1a\n"

    def chunk(kind: bytes, payload: bytes) -> bytes:
        return (
            struct.pack(">I", len(payload))
            + kind
            + payload
            + struct.pack(">I", binascii.crc32(kind + payload) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)
    pixel = bytes([red, green, blue])
    raw = b"".join(b"\x00" + pixel * size for _ in range(size))
    return signature + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")


RED_PNG = _solid_png(255, 0, 0)
GREEN_PNG = _solid_png(0, 255, 0)


@pytest.mark.integration
def test_visual_rubric_gate_live_studionet(default_account):
    factory = get_contract_factory("VisualRubricGate")
    contract = factory.deploy(
        account=default_account,
        consensus_max_rotations=4,
    )
    print(f"SIGHTLINE_RUBRIC_CONTRACT={contract.address}", flush=True)

    result_id = "solid-red-rubric-v1"
    tx = contract.evaluate(
        args=[
            result_id,
            "Pass if the image is predominantly red. Fail if another color clearly dominates.",
            RED_PNG,
        ]
    ).transact(
        consensus_max_rotations=4,
        wait_interval=10000,
        wait_retries=60,
    )
    assert tx_execution_succeeded(tx)
    print(f"SIGHTLINE_RUBRIC_TX={tx.get('hash', '')}", flush=True)

    result = contract.get_result(args=[result_id]).call()
    verdict = str(_field(result, "verdict"))
    score = int(_field(result, "score"))
    confidence = int(_field(result, "confidence"))
    print(f"SIGHTLINE_RUBRIC_VERDICT={verdict}", flush=True)
    print(f"SIGHTLINE_RUBRIC_SCORE={score}", flush=True)
    print(f"SIGHTLINE_RUBRIC_CONFIDENCE={confidence}", flush=True)

    assert verdict == "PASS"
    assert score >= 70
    assert confidence >= 65


@pytest.mark.integration
def test_web_screenshot_attestor_live_studionet(default_account):
    factory = get_contract_factory("WebScreenshotAttestor")
    contract = factory.deploy(
        account=default_account,
        consensus_max_rotations=4,
    )
    print(f"SIGHTLINE_SCREENSHOT_CONTRACT={contract.address}", flush=True)

    result_id = "example-domain-heading-v1"
    tx = contract.attest(
        args=[
            result_id,
            "https://example.com",
            "The screenshot visibly contains the heading 'Example Domain'.",
        ]
    ).transact(
        consensus_max_rotations=4,
        wait_interval=10000,
        wait_retries=60,
    )
    assert tx_execution_succeeded(tx)
    print(f"SIGHTLINE_SCREENSHOT_TX={tx.get('hash', '')}", flush=True)

    result = contract.get_result(args=[result_id]).call()
    verdict = str(_field(result, "verdict"))
    confidence = int(_field(result, "confidence"))
    print(f"SIGHTLINE_SCREENSHOT_VERDICT={verdict}", flush=True)
    print(f"SIGHTLINE_SCREENSHOT_CONFIDENCE={confidence}", flush=True)

    assert verdict == "PASS"
    assert confidence >= 65


@pytest.mark.integration
def test_challengeable_visual_claim_live_studionet(default_account):
    factory = get_contract_factory("ChallengeableVisualClaim")
    contract = factory.deploy(
        account=default_account,
        consensus_max_rotations=4,
    )
    print(f"SIGHTLINE_CHALLENGE_CONTRACT={contract.address}", flush=True)

    claim_id = "predominantly-red-v1"
    open_tx = contract.open_claim(
        args=[
            claim_id,
            "The image is predominantly red.",
            RED_PNG,
        ]
    ).transact(
        consensus_max_rotations=4,
        wait_interval=10000,
        wait_retries=60,
    )
    assert tx_execution_succeeded(open_tx)
    print(f"SIGHTLINE_CHALLENGE_OPEN_TX={open_tx.get('hash', '')}", flush=True)

    initial = contract.get_claim(args=[claim_id]).call()
    print(f"SIGHTLINE_CHALLENGE_INITIAL={_field(initial, 'initial_verdict')}", flush=True)
    assert str(_field(initial, "initial_verdict")) == "SUPPORTED"

    challenge_tx = contract.challenge(
        args=[claim_id, GREEN_PNG]
    ).transact(
        consensus_max_rotations=4,
        wait_interval=10000,
        wait_retries=60,
    )
    assert tx_execution_succeeded(challenge_tx)
    print(f"SIGHTLINE_CHALLENGE_TX={challenge_tx.get('hash', '')}", flush=True)

    final = contract.get_claim(args=[claim_id]).call()
    print(f"SIGHTLINE_CHALLENGE_FINAL={_field(final, 'final_verdict')}", flush=True)
    print(f"SIGHTLINE_CHALLENGED={bool(_field(final, 'challenged'))}", flush=True)

    assert bool(_field(final, "challenged")) is True
    assert str(_field(final, "final_verdict")) == "CONTRADICTED"

    finalize_tx = contract.finalize(args=[claim_id]).transact(
        wait_interval=10000,
        wait_retries=50,
    )
    assert tx_execution_succeeded(finalize_tx)
    print(f"SIGHTLINE_CHALLENGE_FINALIZE_TX={finalize_tx.get('hash', '')}", flush=True)

    finalized = contract.get_claim(args=[claim_id]).call()
    assert bool(_field(finalized, "finalized")) is True
