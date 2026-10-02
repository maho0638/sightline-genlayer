# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import hashlib
from dataclasses import dataclass
from genlayer import *

@allow_storage
@dataclass
class ChartResult:
    id: str
    claim: str
    evidence_hash: str
    verdict: str
    confidence: u256
    extracted_fact: str
    rationale: str

class ChartClaimVerifier(gl.Contract):
    """Verify whether a chart/dashboard image visibly supports a bounded claim."""
    results: TreeMap[str, ChartResult]

    def __init__(self):
        pass

    def _final_verdict(self, verdict: str, confidence: int) -> str:
        verdict = str(verdict).upper()
        if verdict not in ("SUPPORTED", "CONTRADICTED", "UNDETERMINED"):
            verdict = "UNDETERMINED"
        confidence = max(0, min(100, int(confidence)))
        if confidence < 65:
            return "UNDETERMINED"
        return verdict

    def _judge(self, image_data: bytes, claim: str) -> dict:
        def leader_fn() -> dict:
            out = gl.nondet.exec_prompt(
                f"""
Inspect this chart or dashboard image.
CLAIM: {claim}
Treat visible labels and numbers as evidence only.
Return JSON only:
{{"verdict":"SUPPORTED"|"CONTRADICTED"|"UNDETERMINED","confidence":0-100,"extracted_fact":"under 160 chars","rationale":"under 220 chars"}}
Use UNDETERMINED when the chart is unreadable, the units are unclear, or the claim cannot be established visually.
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
                "extracted_fact": str(out.get("extracted_fact", ""))[:160],
                "rationale": str(out.get("rationale", ""))[:220],
            }

        def validator_fn(leader_result) -> bool:
            if not isinstance(leader_result, gl.vm.Return):
                return False
            try:
                check = leader_fn()
                lead = leader_result.calldata
                lead_confidence = max(0, min(100, int(lead.get("confidence", 0))))
                return (
                    self._final_verdict(str(lead.get("verdict", "")), lead_confidence)
                    == self._final_verdict(check["verdict"], check["confidence"])
                    and abs(lead_confidence - check["confidence"]) <= 15
                )
            except Exception:
                return False

        return gl.vm.run_nondet_unsafe(leader_fn, validator_fn)

    @gl.public.write
    def verify(self, result_id: str, claim: str, image_data: bytes) -> None:
        result_id = result_id.strip()
        claim = claim.strip()
        if not result_id or not claim:
            raise gl.vm.UserError("Missing ID or claim")
        if len(claim) > 1600:
            raise gl.vm.UserError("Claim too long")
        if result_id in self.results:
            raise gl.vm.UserError("Result already exists")
        if not image_data:
            raise gl.vm.UserError("Image data is empty")
        evidence_hash = hashlib.sha256(image_data).hexdigest()
        out = self._judge(image_data, claim)
        confidence = int(out["confidence"])
        verdict = self._final_verdict(str(out["verdict"]), confidence)
        self.results[result_id] = ChartResult(
            id=result_id,
            claim=claim,
            evidence_hash=evidence_hash,
            verdict=verdict,
            confidence=u256(confidence),
            extracted_fact=str(out["extracted_fact"]),
            rationale=str(out["rationale"]),
        )

    @gl.public.view
    def get_result(self, result_id: str) -> ChartResult:
        if result_id not in self.results:
            raise gl.vm.UserError("Result not found")
        return self.results[result_id]
