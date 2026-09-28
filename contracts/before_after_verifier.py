# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import hashlib
from dataclasses import dataclass
from genlayer import *


@allow_storage
@dataclass
class ChangeResult:
    id: str
    claim: str
    before_hash: str
    after_hash: str
    verdict: str
    materiality: u256
    confidence: u256
    rationale: str


class BeforeAfterVerifier(gl.Contract):
    """Judge a claimed visual change while binding both source images by hash."""
    results: TreeMap[str, ChangeResult]

    def __init__(self):
        pass

    def _judge(self, before_image: bytes, after_image: bytes, claim: str) -> dict:
        def leader_fn() -> dict:
            out = gl.nondet.exec_prompt(
                f"""
Image 1 is BEFORE and image 2 is AFTER.
Claimed change: {claim}
Judge only visible evidence. Return JSON only:
{{"verdict":"SUPPORTED"|"CONTRADICTED"|"UNDETERMINED","materiality":0-100,"confidence":0-100,"rationale":"under 240 chars"}}
UNDETERMINED means the two images cannot reliably establish the claimed change.
""",
                images=[before_image, after_image],
                response_format="json",
            )
            verdict = str(out.get("verdict", "UNDETERMINED")).upper()
            if verdict not in ("SUPPORTED", "CONTRADICTED", "UNDETERMINED"):
                verdict = "UNDETERMINED"
            return {
                "verdict": verdict,
                "materiality": max(0, min(100, int(out.get("materiality", 0)))),
                "confidence": max(0, min(100, int(out.get("confidence", 0)))),
                "rationale": str(out.get("rationale", ""))[:240],
            }

        def validator_fn(leader_result) -> bool:
            if not isinstance(leader_result, gl.vm.Return):
                return False
            try:
                check = leader_fn()
                lead = leader_result.calldata
                return (
                    str(lead.get("verdict", "")) == check["verdict"]
                    and abs(int(lead.get("materiality", 0)) - check["materiality"]) <= 12
                    and abs(int(lead.get("confidence", 0)) - check["confidence"]) <= 15
                )
            except Exception:
                return False

        return gl.vm.run_nondet_unsafe(leader_fn, validator_fn)

    @gl.public.write
    def verify(
        self,
        result_id: str,
        claim: str,
        before_image: bytes,
        after_image: bytes,
    ) -> None:
        result_id = result_id.strip()
        claim = claim.strip()
        if not result_id or not claim:
            raise gl.vm.UserError("Missing ID or claim")
        if result_id in self.results:
            raise gl.vm.UserError("Result already exists")
        if not before_image or not after_image:
            raise gl.vm.UserError("Both images are required")

        before_hash = hashlib.sha256(before_image).hexdigest()
        after_hash = hashlib.sha256(after_image).hexdigest()
        if before_hash == after_hash:
            raise gl.vm.UserError("Before and after images must differ")

        out = self._judge(before_image, after_image, claim)
        verdict = str(out["verdict"])
        confidence = int(out["confidence"])
        if confidence < 65:
            verdict = "UNDETERMINED"

        self.results[result_id] = ChangeResult(
            id=result_id,
            claim=claim[:1000],
            before_hash=before_hash,
            after_hash=after_hash,
            verdict=verdict,
            materiality=u256(int(out["materiality"])),
            confidence=u256(confidence),
            rationale=str(out["rationale"]),
        )

    @gl.public.view
    def get_result(self, result_id: str) -> ChangeResult:
        if result_id not in self.results:
            raise gl.vm.UserError("Result not found")
        return self.results[result_id]
