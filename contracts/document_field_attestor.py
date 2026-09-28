# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import hashlib
from dataclasses import dataclass
from genlayer import *

@allow_storage
@dataclass
class FieldResult:
    id: str
    field_name: str
    expected_value: str
    evidence_hash: str
    observed_value: str
    verdict: str
    confidence: u256

class DocumentFieldAttestor(gl.Contract):
    """Verify one named field from a photographed/scanned document without broad OCR."""
    results: TreeMap[str, FieldResult]

    def __init__(self):
        pass

    def _judge(self, image_data: bytes, field_name: str, expected_value: str) -> dict:
        def leader_fn() -> dict:
            out = gl.nondet.exec_prompt(
                f"""
Inspect this document image.
FIELD TO CHECK: {field_name}
EXPECTED VALUE: {expected_value}
Extract only the requested field. Do not infer missing text.
Return JSON only:
{{"observed_value":"under 180 chars","verdict":"MATCH"|"MISMATCH"|"UNDETERMINED","confidence":0-100}}
Use UNDETERMINED if the field is unreadable or ambiguous.
""",
                images=[image_data],
                response_format="json",
            )
            verdict = str(out.get("verdict", "UNDETERMINED")).upper()
            if verdict not in ("MATCH", "MISMATCH", "UNDETERMINED"):
                verdict = "UNDETERMINED"
            return {
                "observed_value": str(out.get("observed_value", ""))[:180],
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
                    and str(lead.get("observed_value", "")) == check["observed_value"]
                    and abs(int(lead.get("confidence", 0)) - check["confidence"]) <= 12
                )
            except Exception:
                return False

        return gl.vm.run_nondet_unsafe(leader_fn, validator_fn)

    @gl.public.write
    def attest(
        self,
        result_id: str,
        field_name: str,
        expected_value: str,
        image_data: bytes,
    ) -> None:
        result_id = result_id.strip()
        field_name = field_name.strip()
        expected_value = expected_value.strip()
        if not result_id or not field_name or not expected_value:
            raise gl.vm.UserError("Missing ID, field name, or expected value")
        if result_id in self.results:
            raise gl.vm.UserError("Result already exists")
        if not image_data:
            raise gl.vm.UserError("Image data is empty")
        evidence_hash = hashlib.sha256(image_data).hexdigest()
        out = self._judge(image_data, field_name, expected_value)
        verdict = str(out["verdict"])
        confidence = int(out["confidence"])
        if confidence < 65:
            verdict = "UNDETERMINED"
        self.results[result_id] = FieldResult(
            id=result_id,
            field_name=field_name[:180],
            expected_value=expected_value[:240],
            evidence_hash=evidence_hash,
            observed_value=str(out["observed_value"]),
            verdict=verdict,
            confidence=u256(confidence),
        )

    @gl.public.view
    def get_result(self, result_id: str) -> FieldResult:
        if result_id not in self.results:
            raise gl.vm.UserError("Result not found")
        return self.results[result_id]
