# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from dataclasses import dataclass
from genlayer import *

@allow_storage
@dataclass
class VisualClaim:
    id: str
    claim: str
    initial_verdict: str
    final_verdict: str
    confidence: u256
    challenged: bool
    finalized: bool

class ChallengeableVisualClaim(gl.Contract):
    claims: TreeMap[str, VisualClaim]

    def __init__(self): pass

    def _judge(self,image_data:bytes,claim:str)->dict:
        def leader_fn()->dict:
            out=gl.nondet.exec_prompt(f"""
Does the visual evidence support this claim: {claim}
Return JSON only:
{{"verdict":"SUPPORTED"|"CONTRADICTED"|"UNDETERMINED","confidence":0-100}}
Use only what is visible.
""",images=[image_data],response_format="json")
            verdict=str(out.get("verdict","UNDETERMINED")).upper()
            if verdict not in ("SUPPORTED","CONTRADICTED","UNDETERMINED"): verdict="UNDETERMINED"
            return {"verdict":verdict,"confidence":max(0,min(100,int(out.get("confidence",0))))}
        def validator_fn(leader_result)->bool:
            if not isinstance(leader_result,gl.vm.Return): return False
            try:
                check=leader_fn(); lead=leader_result.calldata
                return str(lead.get("verdict",""))==check["verdict"] and abs(int(lead.get("confidence",0))-check["confidence"])<=15
            except Exception:return False
        return gl.vm.run_nondet_unsafe(leader_fn,validator_fn)

    @gl.public.write
    def open_claim(self,claim_id:str,claim:str,image_data:bytes)->None:
        claim_id=claim_id.strip(); claim=claim.strip()
        if not claim_id or not claim: raise gl.vm.UserError("Missing ID or claim")
        if claim_id in self.claims: raise gl.vm.UserError("Claim already exists")
        out=self._judge(image_data,claim); verdict=str(out["verdict"]); confidence=int(out["confidence"])
        if confidence<65: verdict="UNDETERMINED"
        self.claims[claim_id]=VisualClaim(claim_id,claim[:1200],verdict,verdict,u256(confidence),False,False)

    @gl.public.write
    def challenge(self,claim_id:str,image_data:bytes)->None:
        if claim_id not in self.claims: raise gl.vm.UserError("Claim not found")
        record=self.claims[claim_id]
        if record.finalized: raise gl.vm.UserError("Claim already finalized")
        if record.challenged: raise gl.vm.UserError("Challenge already used")
        out=self._judge(image_data,record.claim); verdict=str(out["verdict"]); confidence=int(out["confidence"])
        if confidence<65: verdict="UNDETERMINED"
        record.challenged=True; record.final_verdict=verdict; record.confidence=u256(confidence)
        self.claims[claim_id]=record

    @gl.public.write
    def finalize(self,claim_id:str)->None:
        if claim_id not in self.claims: raise gl.vm.UserError("Claim not found")
        record=self.claims[claim_id]
        if record.finalized: raise gl.vm.UserError("Claim already finalized")
        record.finalized=True; self.claims[claim_id]=record

    @gl.public.view
    def get_claim(self,claim_id:str)->VisualClaim:
        if claim_id not in self.claims: raise gl.vm.UserError("Claim not found")
        return self.claims[claim_id]
