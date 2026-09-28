# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import hashlib
from dataclasses import dataclass
from genlayer import *

@allow_storage
@dataclass
class DecisionReceipt:
    id: str
    question: str
    evidence_ref: str
    evidence_hash: str
    decision: str
    confidence: u256
    rationale: str

class VisualDecisionReceipt(gl.Contract):
    """Create a compact auditable yes/no/abstain receipt from visual evidence."""
    receipts: TreeMap[str, DecisionReceipt]

    def __init__(self):
        pass

    def _judge(self, image_data: bytes, question: str) -> dict:
        def leader_fn() -> dict:
            out = gl.nondet.exec_prompt(
                f"""
Answer this bounded question using only the visual evidence:
QUESTION: {question}
Return JSON only:
{{"decision":"YES"|"NO"|"ABSTAIN","confidence":0-100,"rationale":"under 240 chars"}}
Use ABSTAIN if the image does not clearly establish YES or NO.
""",
                images=[image_data],
                response_format="json",
            )
            decision = str(out.get("decision", "ABSTAIN")).upper()
            if decision not in ("YES", "NO", "ABSTAIN"):
                decision = "ABSTAIN"
            return {
                "decision": decision,
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
                    str(lead.get("decision", "")) == check["decision"]
                    and abs(int(lead.get("confidence", 0)) - check["confidence"]) <= 15
                )
            except Exception:
                return False

        return gl.vm.run_nondet_unsafe(leader_fn, validator_fn)

    @gl.public.write
    def decide(
        self,
        receipt_id: str,
        question: str,
        evidence_ref: str,
        image_data: bytes,
    ) -> None:
        receipt_id = receipt_id.strip()
        question = question.strip()
        evidence_ref = evidence_ref.strip()
        if not receipt_id or not question or not evidence_ref:
            raise gl.vm.UserError("Missing ID, question, or evidence reference")
        if receipt_id in self.receipts:
            raise gl.vm.UserError("Receipt already exists")
        if not image_data:
            raise gl.vm.UserError("Image data is empty")
        evidence_hash = hashlib.sha256(image_data).hexdigest()
        out = self._judge(image_data, question)
        decision = str(out["decision"])
        confidence = int(out["confidence"])
        if confidence < 65:
            decision = "ABSTAIN"
        self.receipts[receipt_id] = DecisionReceipt(
            id=receipt_id,
            question=question[:1200],
            evidence_ref=evidence_ref[:240],
            evidence_hash=evidence_hash,
            decision=decision,
            confidence=u256(confidence),
            rationale=str(out["rationale"]),
        )

    @gl.public.view
    def get_receipt(self, receipt_id: str) -> DecisionReceipt:
        if receipt_id not in self.receipts:
            raise gl.vm.UserError("Receipt not found")
        return self.receipts[receipt_id]
