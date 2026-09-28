# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from genlayer import *


CHALLENGE_WINDOW_SECONDS = 60 * 60


@allow_storage
@dataclass
class VisualClaim:
    id: str
    claim: str
    opener: str
    challenger: str
    initial_evidence_hash: str
    challenge_evidence_hash: str
    initial_verdict: str
    final_verdict: str
    confidence: u256
    opened_at: u256
    challenge_deadline: u256
    challenged_at: u256
    challenged: bool
    finalized: bool


class ChallengeableVisualClaim(gl.Contract):
    """Visual attestation with a guaranteed one-hour challenge window."""
    claims: TreeMap[str, VisualClaim]

    def __init__(self):
        pass

    def _now(self) -> int:
        return int(datetime.now(timezone.utc).timestamp())

    def _judge(self, image_data: bytes, claim: str) -> dict:
        def leader_fn() -> dict:
            out = gl.nondet.exec_prompt(
                f"""
Does the visual evidence support this claim: {claim}
Return JSON only:
{{"verdict":"SUPPORTED"|"CONTRADICTED"|"UNDETERMINED","confidence":0-100}}
Use only what is visible.
""",
                images=[image_data],
                response_format="json",
            )
            verdict = str(out.get("verdict", "UNDETERMINED")).upper()
            if verdict not in ("SUPPORTED", "CONTRADICTED", "UNDETERMINED"):
                verdict = "UNDETERMINED"
            return {
                "verdict": verdict,
                "confidence": max(0, min(100, int(out.get("confidence", 0)))),
            }

        def validator_fn(leader_result) -> bool:
            if not isinstance(leader_result, gl.vm.Return):
                return False
            try:
                check = leader_fn()
                lead = leader_result.calldata
                return (
                    str(lead.get("verdict", "")) == check["verdict"]
                    and abs(int(lead.get("confidence", 0)) - check["confidence"]) <= 15
                )
            except Exception:
                return False

        return gl.vm.run_nondet_unsafe(leader_fn, validator_fn)

    @gl.public.write
    def open_claim(self, claim_id: str, claim: str, image_data: bytes) -> None:
        claim_id = claim_id.strip()
        claim = claim.strip()
        if not claim_id or not claim:
            raise gl.vm.UserError("Missing ID or claim")
        if claim_id in self.claims:
            raise gl.vm.UserError("Claim already exists")
        if not image_data:
            raise gl.vm.UserError("Image data is empty")

        evidence_hash = hashlib.sha256(image_data).hexdigest()
        out = self._judge(image_data, claim)
        verdict = str(out["verdict"])
        confidence = int(out["confidence"])
        if confidence < 65:
            verdict = "UNDETERMINED"

        now = self._now()
        self.claims[claim_id] = VisualClaim(
            id=claim_id,
            claim=claim[:1200],
            opener=str(gl.message.sender_address),
            challenger="",
            initial_evidence_hash=evidence_hash,
            challenge_evidence_hash="",
            initial_verdict=verdict,
            final_verdict=verdict,
            confidence=u256(confidence),
            opened_at=u256(now),
            challenge_deadline=u256(now + CHALLENGE_WINDOW_SECONDS),
            challenged_at=u256(0),
            challenged=False,
            finalized=False,
        )

    @gl.public.write
    def challenge(self, claim_id: str, image_data: bytes) -> None:
        if claim_id not in self.claims:
            raise gl.vm.UserError("Claim not found")
        record = self.claims[claim_id]
        if record.finalized:
            raise gl.vm.UserError("Claim already finalized")
        if record.challenged:
            raise gl.vm.UserError("Challenge already used")
        if self._now() > int(record.challenge_deadline):
            raise gl.vm.UserError("Challenge window has closed")
        if not image_data:
            raise gl.vm.UserError("Challenge image is empty")

        challenge_hash = hashlib.sha256(image_data).hexdigest()
        if challenge_hash == record.initial_evidence_hash:
            raise gl.vm.UserError("Challenge must provide different evidence")

        out = self._judge(image_data, record.claim)
        verdict = str(out["verdict"])
        confidence = int(out["confidence"])
        if confidence < 65:
            verdict = "UNDETERMINED"

        record.challenged = True
        record.challenger = str(gl.message.sender_address)
        record.challenge_evidence_hash = challenge_hash
        record.final_verdict = verdict
        record.confidence = u256(confidence)
        record.challenged_at = u256(self._now())
        self.claims[claim_id] = record

    @gl.public.write
    def finalize(self, claim_id: str) -> None:
        if claim_id not in self.claims:
            raise gl.vm.UserError("Claim not found")
        record = self.claims[claim_id]
        if record.finalized:
            raise gl.vm.UserError("Claim already finalized")
        if not record.challenged and self._now() <= int(record.challenge_deadline):
            raise gl.vm.UserError("Challenge window is still open")
        record.finalized = True
        self.claims[claim_id] = record

    @gl.public.view
    def get_claim(self, claim_id: str) -> VisualClaim:
        if claim_id not in self.claims:
            raise gl.vm.UserError("Claim not found")
        return self.claims[claim_id]

    @gl.public.view
    def get_challenge_deadline(self, claim_id: str) -> u256:
        if claim_id not in self.claims:
            raise gl.vm.UserError("Claim not found")
        return self.claims[claim_id].challenge_deadline

    @gl.public.view
    def is_finalization_ready(self, claim_id: str) -> bool:
        if claim_id not in self.claims:
            raise gl.vm.UserError("Claim not found")
        record = self.claims[claim_id]
        return record.challenged or self._now() > int(record.challenge_deadline)
