# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import hashlib
from dataclasses import dataclass
from genlayer import *


@allow_storage
@dataclass
class QuorumResult:
    id: str
    claim: str
    image_hash_a: str
    image_hash_b: str
    image_hash_c: str
    verdict: str
    support_count: u256
    contradict_count: u256
    confidence: u256


class VisualQuorum(gl.Contract):
    """Three distinct visual observations aggregated with a deterministic 2-of-3 rule."""
    results: TreeMap[str, QuorumResult]

    def __init__(self):
        pass

    def _judge(
        self,
        image_a: bytes,
        image_b: bytes,
        image_c: bytes,
        claim: str,
    ) -> dict:
        def classify_one(image_data: bytes) -> dict:
            out = gl.nondet.exec_prompt(
                f"""
Judge this ONE visual evidence item against the claim below.
CLAIM: {claim}
Return JSON only:
{{"verdict":"SUPPORTED"|"CONTRADICTED"|"UNDETERMINED","confidence":0-100}}
Use only what is visibly established. Do not infer hidden facts.
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

        def leader_fn() -> dict:
            a = classify_one(image_a)
            b = classify_one(image_b)
            c = classify_one(image_c)
            rows = [a, b, c]

            support = sum(
                1
                for row in rows
                if row["verdict"] == "SUPPORTED" and row["confidence"] >= 60
            )
            contradict = sum(
                1
                for row in rows
                if row["verdict"] == "CONTRADICTED" and row["confidence"] >= 60
            )
            confidence = min(a["confidence"], b["confidence"], c["confidence"])

            if support >= 2 and contradict == 0:
                verdict = "SUPPORTED"
            elif contradict >= 2 and support == 0:
                verdict = "CONTRADICTED"
            else:
                verdict = "UNDETERMINED"

            return {
                "verdict": verdict,
                "support_count": support,
                "contradict_count": contradict,
                "confidence": confidence,
            }

        def validator_fn(leader_result) -> bool:
            if not isinstance(leader_result, gl.vm.Return):
                return False
            try:
                check = leader_fn()
                lead = leader_result.calldata
                return (
                    str(lead.get("verdict", "")) == check["verdict"]
                    and int(lead.get("support_count", -1)) == check["support_count"]
                    and int(lead.get("contradict_count", -1)) == check["contradict_count"]
                )
            except Exception:
                return False

        return gl.vm.run_nondet_unsafe(leader_fn, validator_fn)

    @gl.public.write
    def verify(
        self,
        result_id: str,
        claim: str,
        image_a: bytes,
        image_b: bytes,
        image_c: bytes,
    ) -> None:
        result_id = result_id.strip()
        claim = claim.strip()
        if not result_id or not claim:
            raise gl.vm.UserError("Missing ID or claim")
        if result_id in self.results:
            raise gl.vm.UserError("Result already exists")
        if not image_a or not image_b or not image_c:
            raise gl.vm.UserError("Three non-empty images are required")

        hashes = [
            hashlib.sha256(image_a).hexdigest(),
            hashlib.sha256(image_b).hexdigest(),
            hashlib.sha256(image_c).hexdigest(),
        ]
        if len(set(hashes)) != 3:
            raise gl.vm.UserError("Visual quorum requires three distinct images")

        out = self._judge(image_a, image_b, image_c, claim)
        self.results[result_id] = QuorumResult(
            id=result_id,
            claim=claim[:1200],
            image_hash_a=hashes[0],
            image_hash_b=hashes[1],
            image_hash_c=hashes[2],
            verdict=str(out["verdict"]),
            support_count=u256(int(out["support_count"])),
            contradict_count=u256(int(out["contradict_count"])),
            confidence=u256(int(out["confidence"])),
        )

    @gl.public.view
    def get_result(self, result_id: str) -> QuorumResult:
        if result_id not in self.results:
            raise gl.vm.UserError("Result not found")
        return self.results[result_id]
