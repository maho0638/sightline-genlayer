"""Expanded live Studionet coverage for the remaining Sightline catalog primitives."""

from io import BytesIO

import pytest
from PIL import Image, ImageDraw, ImageFont
from gltest import get_contract_factory
from gltest.assertions import tx_execution_succeeded


def _field(value, name):
    if isinstance(value, dict):
        return value.get(name)
    return getattr(value, name)


def _font(size=34):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()


def _png(draw_fn, width=720, height=420, background="white"):
    image = Image.new("RGB", (width, height), background)
    draw = ImageDraw.Draw(image)
    draw_fn(draw, image)
    buf = BytesIO()
    image.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def _receipt_png():
    def draw(draw, image):
        title = _font(44)
        body = _font(34)
        draw.text((50, 35), "RECEIPT", fill="black", font=title)
        draw.text((50, 110), "Example Market", fill="black", font=body)
        draw.text((50, 175), "Amount: 42.50 USD", fill="black", font=body)
        draw.text((50, 240), "Date: 2026-09-28", fill="black", font=body)
        draw.text((50, 315), "PAID", fill="green", font=title)
    return _png(draw)


def _damage_png():
    def draw(draw, image):
        body = _font(34)
        title = _font(44)
        draw.rectangle((120, 80, 600, 330), outline="black", width=8, fill=(210, 170, 110))
        points = [(330, 80), (290, 140), (370, 185), (300, 235), (390, 330)]
        draw.line(points, fill="red", width=18)
        draw.text((155, 20), "SEVERE VISIBLE DAMAGE", fill="red", font=title)
        draw.text((175, 345), "LARGE STRUCTURAL CRACK", fill="black", font=body)
    return _png(draw)


def _before_png():
    def draw(draw, image):
        title = _font(42)
        draw.text((210, 35), "BEFORE", fill="black", font=title)
        draw.rectangle((80, 280, 640, 340), fill=(150, 150, 150))
        draw.text((185, 360), "PLATFORM - NO RAILING", fill="black", font=_font(30))
    return _png(draw)


def _after_png():
    def draw(draw, image):
        title = _font(42)
        draw.text((225, 25), "AFTER", fill="black", font=title)
        draw.rectangle((80, 280, 640, 340), fill=(150, 150, 150))
        for x in (110, 240, 370, 500, 620):
            draw.line((x, 140, x, 280), fill="blue", width=12)
        draw.line((110, 140, 620, 140), fill="blue", width=14)
        draw.line((110, 205, 620, 205), fill="blue", width=10)
        draw.text((135, 355), "BLUE SAFETY RAILING INSTALLED", fill="blue", font=_font(30))
    return _png(draw)


def _chart_png():
    def draw(draw, image):
        title = _font(38)
        body = _font(28)
        draw.text((140, 20), "Monthly Revenue Dashboard", fill="black", font=title)
        base_y = 340
        values = [70, 90, 120]
        labels = ["July 70", "August 90", "September 120"]
        xs = [130, 320, 510]
        for x, value, label in zip(xs, values, labels):
            height = int(value * 2)
            draw.rectangle((x, base_y-height, x+100, base_y), fill="navy")
            draw.text((x-10, 355), label, fill="black", font=body)
        draw.text((430, 80), "September = 120", fill="black", font=body)
    return _png(draw)


def _ui_png():
    def draw(draw, image):
        title = _font(52)
        body = _font(34)
        draw.rectangle((50, 50, 670, 370), outline="green", width=10)
        draw.text((130, 105), "PAYMENT SUCCESS", fill="green", font=title)
        draw.text((190, 205), "Status: COMPLETED", fill="black", font=body)
        draw.text((225, 275), "Order #A-1024", fill="black", font=body)
    return _png(draw)


def _document_png():
    def draw(draw, image):
        title = _font(42)
        body = _font(32)
        draw.text((250, 30), "INVOICE", fill="black", font=title)
        draw.text((60, 115), "Invoice Number: INV-2026-1007", fill="black", font=body)
        draw.text((60, 185), "Customer: Example Labs", fill="black", font=body)
        draw.text((60, 255), "Amount Due: 75.00 USD", fill="black", font=body)
        draw.text((60, 325), "Date: 2026-09-28", fill="black", font=body)
    return _png(draw)


def _decision_png():
    def draw(draw, image):
        title = _font(44)
        draw.ellipse((220, 90, 500, 370), fill="green", outline="black", width=8)
        draw.text((180, 25), "APPROVED GREEN SEAL", fill="green", font=title)
    return _png(draw)


def _sealed_png(photo_number):
    def draw(draw, image):
        title = _font(42)
        body = _font(30)
        draw.rectangle((150, 100, 570, 320), fill=(200, 155, 90), outline="black", width=8)
        draw.line((360, 100, 360, 320), fill="black", width=12)
        draw.rectangle((300, 90, 420, 120), fill="gray")
        draw.text((180, 30), "PACKAGE SEALED", fill="green", font=title)
        draw.text((280, 345), f"PHOTO #{photo_number}", fill="black", font=body)
    return _png(draw)


@pytest.mark.integration
def test_receipt_attestor_live(default_account):
    contract = get_contract_factory("ReceiptAttestor").deploy(
        account=default_account, consensus_max_rotations=4
    )
    print(f"SIGHTLINE_RECEIPT_CONTRACT={contract.address}", flush=True)
    tx = contract.attest(args=[
        "receipt-live-v1", "fixture:receipt-v1", _receipt_png(),
        "Example Market", "42.50 USD", "2026-09-28"
    ]).transact(consensus_max_rotations=4, wait_interval=10000, wait_retries=60)
    assert tx_execution_succeeded(tx)
    print(f"SIGHTLINE_RECEIPT_TX={tx.get('hash', '')}", flush=True)
    r = contract.get_result(args=["receipt-live-v1"]).call()
    print(f"SIGHTLINE_RECEIPT_VERDICT={_field(r, 'verdict')}", flush=True)
    print(f"SIGHTLINE_RECEIPT_HASH={_field(r, 'evidence_hash')}", flush=True)
    assert str(_field(r, "verdict")) == "MATCH"
    assert int(_field(r, "confidence")) >= 65
    assert len(str(_field(r, "evidence_hash"))) == 64


@pytest.mark.integration
def test_damage_oracle_live(default_account):
    contract = get_contract_factory("DamageSeverityOracle").deploy(
        account=default_account, consensus_max_rotations=4
    )
    print(f"SIGHTLINE_DAMAGE_CONTRACT={contract.address}", flush=True)
    tx = contract.assess(args=[
        "damage-live-v1", "fixture:damage-v1", _damage_png(), "shipping box"
    ]).transact(consensus_max_rotations=4, wait_interval=10000, wait_retries=60)
    assert tx_execution_succeeded(tx)
    print(f"SIGHTLINE_DAMAGE_TX={tx.get('hash', '')}", flush=True)
    r = contract.get_result(args=["damage-live-v1"]).call()
    print(f"SIGHTLINE_DAMAGE_SEVERITY={_field(r, 'severity')}", flush=True)
    assert str(_field(r, "severity")) in {"MODERATE", "SEVERE"}
    assert int(_field(r, "confidence")) >= 60


@pytest.mark.integration
def test_before_after_live(default_account):
    contract = get_contract_factory("BeforeAfterVerifier").deploy(
        account=default_account, consensus_max_rotations=4
    )
    print(f"SIGHTLINE_BEFORE_AFTER_CONTRACT={contract.address}", flush=True)
    tx = contract.verify(args=[
        "before-after-live-v1",
        "A blue safety railing was installed along the platform edge.",
        _before_png(),
        _after_png(),
    ]).transact(consensus_max_rotations=4, wait_interval=10000, wait_retries=60)
    assert tx_execution_succeeded(tx)
    print(f"SIGHTLINE_BEFORE_AFTER_TX={tx.get('hash', '')}", flush=True)
    r = contract.get_result(args=["before-after-live-v1"]).call()
    print(f"SIGHTLINE_BEFORE_AFTER_VERDICT={_field(r, 'verdict')}", flush=True)
    print(f"SIGHTLINE_BEFORE_HASH={_field(r, 'before_hash')}", flush=True)
    print(f"SIGHTLINE_AFTER_HASH={_field(r, 'after_hash')}", flush=True)
    assert str(_field(r, "verdict")) == "SUPPORTED"
    assert str(_field(r, "before_hash")) != str(_field(r, "after_hash"))


@pytest.mark.integration
def test_chart_claim_live(default_account):
    contract = get_contract_factory("ChartClaimVerifier").deploy(
        account=default_account, consensus_max_rotations=4
    )
    print(f"SIGHTLINE_CHART_CONTRACT={contract.address}", flush=True)
    tx = contract.verify(args=[
        "chart-live-v1", "The September value shown is 120.", _chart_png()
    ]).transact(consensus_max_rotations=4, wait_interval=10000, wait_retries=60)
    assert tx_execution_succeeded(tx)
    print(f"SIGHTLINE_CHART_TX={tx.get('hash', '')}", flush=True)
    r = contract.get_result(args=["chart-live-v1"]).call()
    print(f"SIGHTLINE_CHART_VERDICT={_field(r, 'verdict')}", flush=True)
    print(f"SIGHTLINE_CHART_FACT={_field(r, 'extracted_fact')}", flush=True)
    assert str(_field(r, "verdict")) == "SUPPORTED"
    assert int(_field(r, "confidence")) >= 65


@pytest.mark.integration
def test_ui_state_live(default_account):
    contract = get_contract_factory("UIStateAttestor").deploy(
        account=default_account, consensus_max_rotations=4
    )
    print(f"SIGHTLINE_UI_CONTRACT={contract.address}", flush=True)
    tx = contract.attest(args=[
        "ui-live-v1", "payment success state", _ui_png()
    ]).transact(consensus_max_rotations=4, wait_interval=10000, wait_retries=60)
    assert tx_execution_succeeded(tx)
    print(f"SIGHTLINE_UI_TX={tx.get('hash', '')}", flush=True)
    r = contract.get_result(args=["ui-live-v1"]).call()
    print(f"SIGHTLINE_UI_VERDICT={_field(r, 'verdict')}", flush=True)
    print(f"SIGHTLINE_UI_BLOCKED={_field(r, 'blocked')}", flush=True)
    assert str(_field(r, "verdict")) == "PRESENT"
    assert bool(_field(r, "blocked")) is False


@pytest.mark.integration
def test_document_field_live(default_account):
    contract = get_contract_factory("DocumentFieldAttestor").deploy(
        account=default_account, consensus_max_rotations=4
    )
    print(f"SIGHTLINE_DOCUMENT_CONTRACT={contract.address}", flush=True)
    tx = contract.attest(args=[
        "document-live-v1", "invoice number", "INV-2026-1007", _document_png()
    ]).transact(consensus_max_rotations=4, wait_interval=10000, wait_retries=60)
    assert tx_execution_succeeded(tx)
    print(f"SIGHTLINE_DOCUMENT_TX={tx.get('hash', '')}", flush=True)
    r = contract.get_result(args=["document-live-v1"]).call()
    print(f"SIGHTLINE_DOCUMENT_VERDICT={_field(r, 'verdict')}", flush=True)
    print(f"SIGHTLINE_DOCUMENT_VALUE={_field(r, 'observed_value')}", flush=True)
    assert str(_field(r, "verdict")) == "MATCH"
    assert "INV-2026-1007" in str(_field(r, "observed_value"))


@pytest.mark.integration
def test_visual_decision_receipt_live(default_account):
    contract = get_contract_factory("VisualDecisionReceipt").deploy(
        account=default_account, consensus_max_rotations=4
    )
    print(f"SIGHTLINE_DECISION_CONTRACT={contract.address}", flush=True)
    tx = contract.decide(args=[
        "decision-live-v1",
        "Is the large circular seal visibly green?",
        "fixture:green-seal-v1",
        _decision_png(),
    ]).transact(consensus_max_rotations=4, wait_interval=10000, wait_retries=60)
    assert tx_execution_succeeded(tx)
    print(f"SIGHTLINE_DECISION_TX={tx.get('hash', '')}", flush=True)
    r = contract.get_receipt(args=["decision-live-v1"]).call()
    print(f"SIGHTLINE_DECISION_RESULT={_field(r, 'decision')}", flush=True)
    assert str(_field(r, "decision")) == "YES"
    assert int(_field(r, "confidence")) >= 65


@pytest.mark.integration
def test_visual_quorum_live(default_account):
    contract = get_contract_factory("VisualQuorum").deploy(
        account=default_account, consensus_max_rotations=4
    )
    print(f"SIGHTLINE_QUORUM_CONTRACT={contract.address}", flush=True)
    tx = contract.verify(args=[
        "quorum-live-v1",
        "The package is visibly sealed.",
        _sealed_png(1),
        _sealed_png(2),
        _sealed_png(3),
    ]).transact(consensus_max_rotations=4, wait_interval=10000, wait_retries=80)
    assert tx_execution_succeeded(tx)
    print(f"SIGHTLINE_QUORUM_TX={tx.get('hash', '')}", flush=True)
    r = contract.get_result(args=["quorum-live-v1"]).call()
    print(f"SIGHTLINE_QUORUM_VERDICT={_field(r, 'verdict')}", flush=True)
    print(f"SIGHTLINE_QUORUM_SUPPORT={int(_field(r, 'support_count'))}", flush=True)
    print(f"SIGHTLINE_QUORUM_CONTRADICT={int(_field(r, 'contradict_count'))}", flush=True)
    assert str(_field(r, "verdict")) == "SUPPORTED"
    assert int(_field(r, "support_count")) >= 2
