# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from dataclasses import dataclass
from genlayer import *

@allow_storage
@dataclass
class UIStateResult:
    id: str
    target_state: str
    verdict: str
    visible: bool
    blocked: bool
    confidence: u256
    note: str

class UIStateAttestor(gl.Contract):
    """Attest a named application/UI state from a screenshot with explicit blockers."""
    results: TreeMap[str, UIStateResult]

    def __init__(self):
        pass

    def _judge(self, image_data: bytes, target_state: str) -> dict:
        def leader_fn() -> dict:
            out = gl.nondet.exec_prompt(
                f"""
Inspect this application screenshot.
TARGET STATE: {target_state}
Return JSON only:
{{"visible":true|false,"blocked":true|false,"confidence":0-100,"note":"under 220 chars"}}
visible=true only when the target state is clearly shown.
blocked=true when an error, modal, loading state, access gate, or contradictory UI prevents the target state from being established.
""",
                images=[image_data],
                response_format="json",
            )
            return {
                "visible": bool(out.get("visible", False)),
                "blocked": bool(out.get("blocked", False)),
                "confidence": max(0, min(100, int(out.get("confidence", 0)))),
                "note": str(out.get("note", ""))[:220],
            }

        def validator_fn(leader_result) -> bool:
            if not isinstance(leader_result, gl.vm.Return):
                return False
            try:
                check = leader_fn()
                lead = leader_result.calldata
                return (
                    bool(lead.get("visible", False)) == check["visible"]
                    and bool(lead.get("blocked", False)) == check["blocked"]
                    and abs(int(lead.get("confidence", 0)) - check["confidence"]) <= 15
                )
            except Exception:
                return False

        return gl.vm.run_nondet_unsafe(leader_fn, validator_fn)

    @gl.public.write
    def attest(self, result_id: str, target_state: str, image_data: bytes) -> None:
        result_id = result_id.strip()
        target_state = target_state.strip()
        if not result_id or not target_state:
            raise gl.vm.UserError("Missing ID or target state")
        if result_id in self.results:
            raise gl.vm.UserError("Result already exists")
        out = self._judge(image_data, target_state)
        confidence = int(out["confidence"])
        if confidence < 65:
            verdict = "UNDETERMINED"
        elif bool(out["blocked"]):
            verdict = "BLOCKED"
        elif bool(out["visible"]):
            verdict = "PRESENT"
        else:
            verdict = "ABSENT"
        self.results[result_id] = UIStateResult(
            id=result_id,
            target_state=target_state[:1000],
            verdict=verdict,
            visible=bool(out["visible"]),
            blocked=bool(out["blocked"]),
            confidence=u256(confidence),
            note=str(out["note"]),
        )

    @gl.public.view
    def get_result(self, result_id: str) -> UIStateResult:
        if result_id not in self.results:
            raise gl.vm.UserError("Result not found")
        return self.results[result_id]
