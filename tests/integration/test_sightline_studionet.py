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
    return (
        signature
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )


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

    result_id = "solid-red-rubric-v2"
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
    evidence_hash = str(_field(result, "evidence_hash"))
    print(f"SIGHTLINE_RUBRIC_VERDICT={verdict}", flush=True)
    print(f"SIGHTLINE_RUBRIC_SCORE={score}", flush=True)
    print(f"SIGHTLINE_RUBRIC_CONFIDENCE={confidence}", flush=True)
    print(f"SIGHTLINE_RUBRIC_EVIDENCE_HASH={evidence_hash}", flush=True)

    assert verdict == "PASS"
    assert score >= 70
    assert confidence >= 65
    assert len(evidence_hash) == 64


@pytest.mark.integration
def test_web_screenshot_attestor_negative_live_studionet(default_account):
    """Use a deliberately false criterion so the negative vision path is reproducible."""
    factory = get_contract_factory("WebScreenshotAttestor")
    contract = factory.deploy(
        account=default_account,
        consensus_max_rotations=4,
    )
    print(f"SIGHTLINE_SCREENSHOT_CONTRACT={contract.address}", flush=True)

    result_id = "example-domain-no-red-alert-v1"
    tx = contract.attest(
        args=[
            result_id,
            "https://example.com",
            "The screenshot shows a full-screen bright red emergency banner with the exact text SYSTEM DOWN repeated many times.",
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
    note = str(_field(result, "note"))
    print(f"SIGHTLINE_SCREENSHOT_VERDICT={verdict}", flush=True)
    print(f"SIGHTLINE_SCREENSHOT_CONFIDENCE={confidence}", flush=True)
    print(f"SIGHTLINE_SCREENSHOT_NOTE={note}", flush=True)

    assert verdict == "FAIL"
    assert confidence >= 65


@pytest.mark.integration
def test_challengeable_visual_claim_live_studionet(default_account):
    factory = get_contract_factory("ChallengeableVisualClaim")
    contract = factory.deploy(
        account=default_account,
        consensus_max_rotations=4,
    )
    print(f"SIGHTLINE_CHALLENGE_CONTRACT={contract.address}", flush=True)

    claim_id = "predominantly-red-v2"
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
    print(
        f"SIGHTLINE_CHALLENGE_DEADLINE={int(_field(initial, 'challenge_deadline'))}",
        flush=True,
    )
    assert str(_field(initial, "initial_verdict")) == "SUPPORTED"
    assert int(_field(initial, "challenge_deadline")) > int(_field(initial, "opened_at"))
    assert contract.is_finalization_ready(args=[claim_id]).call() is False

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
    print(
        f"SIGHTLINE_CHALLENGE_INITIAL_HASH={_field(final, 'initial_evidence_hash')}",
        flush=True,
    )
    print(
        f"SIGHTLINE_CHALLENGE_EVIDENCE_HASH={_field(final, 'challenge_evidence_hash')}",
        flush=True,
    )

    assert bool(_field(final, "challenged")) is True
    assert str(_field(final, "final_verdict")) == "CONTRADICTED"
    assert contract.is_finalization_ready(args=[claim_id]).call() is True

    finalize_tx = contract.finalize(args=[claim_id]).transact(
        wait_interval=10000,
        wait_retries=50,
    )
    assert tx_execution_succeeded(finalize_tx)
    print(f"SIGHTLINE_CHALLENGE_FINALIZE_TX={finalize_tx.get('hash', '')}", flush=True)

    finalized = contract.get_claim(args=[claim_id]).call()
    assert bool(_field(finalized, "finalized")) is True


@pytest.mark.integration
def test_visual_milestone_escrow_negative_refund_live_studionet(
    default_account,
    accounts,
):
    """Exercise escrow, screenshot judgment, challenge re-resolution, and refund."""
    assert len(accounts) >= 2
    worker_account = accounts[1]
    worker_address = worker_account.address

    factory = get_contract_factory("VisualMilestoneEscrow")
    contract = factory.deploy(
        account=default_account,
        consensus_max_rotations=4,
    )
    print(f"SIGHTLINE_ESCROW_CONTRACT={contract.address}", flush=True)
    print(f"SIGHTLINE_ESCROW_WORKER={worker_address}", flush=True)

    creator = contract.connect(account=default_account)
    worker = contract.connect(account=worker_account)

    milestone_id = "false-red-alert-milestone-v1"
    reward = 1_000_000_000_000
    rubric = (
        "Approve only if the proof page visibly shows a full-screen bright red "
        "emergency banner with the exact text SYSTEM DOWN repeated many times."
    )

    create_tx = creator.create_milestone(
        args=[milestone_id, worker_address, rubric]
    ).transact(
        value=reward,
        wait_interval=10000,
        wait_retries=50,
    )
    assert tx_execution_succeeded(create_tx)
    print(f"SIGHTLINE_ESCROW_CREATE_TX={create_tx.get('hash', '')}", flush=True)

    submit_tx = worker.submit_proof(
        args=[milestone_id, "https://example.com"]
    ).transact(
        wait_interval=10000,
        wait_retries=50,
    )
    assert tx_execution_succeeded(submit_tx)
    print(f"SIGHTLINE_ESCROW_SUBMIT_TX={submit_tx.get('hash', '')}", flush=True)

    resolve_tx = creator.resolve(args=[milestone_id]).transact(
        consensus_max_rotations=4,
        wait_interval=10000,
        wait_retries=60,
    )
    assert tx_execution_succeeded(resolve_tx)
    print(f"SIGHTLINE_ESCROW_RESOLVE_TX={resolve_tx.get('hash', '')}", flush=True)

    first = contract.get_milestone(args=[milestone_id]).call()
    first_status = str(_field(first, "status"))
    print(f"SIGHTLINE_ESCROW_INITIAL_STATUS={first_status}", flush=True)
    print(f"SIGHTLINE_ESCROW_INITIAL_SCORE={int(_field(first, 'score'))}", flush=True)
    print(
        f"SIGHTLINE_ESCROW_INITIAL_CONFIDENCE={int(_field(first, 'confidence'))}",
        flush=True,
    )
    print(f"SIGHTLINE_ESCROW_INITIAL_REASON={_field(first, 'reason')}", flush=True)

    assert first_status in {"REJECTED", "UNDETERMINED"}
    assert int(_field(first, "resolution_round")) == 1
    assert contract.is_settlement_ready(args=[milestone_id]).call() is False
    assert contract.get_challenge_deadline(args=[milestone_id]).call() > 0

    challenge_tx = creator.challenge_resolution(
        args=[
            milestone_id,
            "The negative decision should be re-checked before funds are returned.",
        ]
    ).transact(
        wait_interval=10000,
        wait_retries=50,
    )
    assert tx_execution_succeeded(challenge_tx)
    print(f"SIGHTLINE_ESCROW_CHALLENGE_TX={challenge_tx.get('hash', '')}", flush=True)

    reresolve_tx = creator.resolve_challenge(args=[milestone_id]).transact(
        consensus_max_rotations=4,
        wait_interval=10000,
        wait_retries=60,
    )
    assert tx_execution_succeeded(reresolve_tx)
    print(
        f"SIGHTLINE_ESCROW_RERESOLVE_TX={reresolve_tx.get('hash', '')}",
        flush=True,
    )

    second = contract.get_milestone(args=[milestone_id]).call()
    second_status = str(_field(second, "status"))
    print(f"SIGHTLINE_ESCROW_FINAL_DECISION_STATUS={second_status}", flush=True)
    print(
        f"SIGHTLINE_ESCROW_RESOLUTION_ROUND={int(_field(second, 'resolution_round'))}",
        flush=True,
    )
    print(
        f"SIGHTLINE_ESCROW_CHALLENGE_COUNT={int(_field(second, 'challenge_count'))}",
        flush=True,
    )

    assert second_status in {"REJECTED", "UNDETERMINED"}
    assert int(_field(second, "resolution_round")) == 2
    assert int(_field(second, "challenge_count")) == 1
    assert contract.is_settlement_ready(args=[milestone_id]).call() is True

    refund_tx = creator.refund(args=[milestone_id]).transact(
        wait_interval=10000,
        wait_retries=50,
    )
    assert tx_execution_succeeded(refund_tx)
    print(f"SIGHTLINE_ESCROW_REFUND_TX={refund_tx.get('hash', '')}", flush=True)

    settled = contract.get_milestone(args=[milestone_id]).call()
    assert str(_field(settled, "status")) == "REFUNDED"
    assert bool(_field(settled, "settled")) is True
    print("SIGHTLINE_ESCROW_FINAL_STATUS=REFUNDED", flush=True)
