# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from dataclasses import dataclass
from genlayer import *

@allow_storage
@dataclass
class QuorumResult:
    id: str
    claim: str
    verdict: str
    support_count: u256
    confidence: u256

class VisualQuorum(gl.Contract):
    results: TreeMap[str, QuorumResult]

    def __init__(self): pass

    def _judge(self,images:list[bytes],claim:str)->dict:
        def leader_fn()->dict:
            out=gl.nondet.exec_prompt(f"""
You receive three visual evidence items for this claim: {claim}
Judge each image independently, then aggregate. Return JSON only:
{{"verdict":"SUPPORTED"|"CONTRADICTED"|"UNDETERMINED","support_count":0|1|2|3,"confidence":0-100}}
Do not count the same visible fact twice merely because wording repeats.
""",images=images,response_format="json")
            verdict=str(out.get("verdict","UNDETERMINED")).upper()
            if verdict not in ("SUPPORTED","CONTRADICTED","UNDETERMINED"): verdict="UNDETERMINED"
            return {"verdict":verdict,"support_count":max(0,min(3,int(out.get("support_count",0)))),"confidence":max(0,min(100,int(out.get("confidence",0))))}
        def validator_fn(leader_result)->bool:
            if not isinstance(leader_result,gl.vm.Return): return False
            try:
                check=leader_fn(); lead=leader_result.calldata
                return str(lead.get("verdict",""))==check["verdict"] and int(lead.get("support_count",-1))==check["support_count"] and abs(int(lead.get("confidence",0))-check["confidence"])<=15
            except Exception:return False
        return gl.vm.run_nondet_unsafe(leader_fn,validator_fn)

    @gl.public.write
    def verify(self,result_id:str,claim:str,image_a:bytes,image_b:bytes,image_c:bytes)->None:
        result_id=result_id.strip(); claim=claim.strip()
        if not result_id or not claim: raise gl.vm.UserError("Missing ID or claim")
        if result_id in self.results: raise gl.vm.UserError("Result already exists")
        out=self._judge([image_a,image_b,image_c],claim)
        verdict=str(out["verdict"]); support=int(out["support_count"]); confidence=int(out["confidence"])
        if verdict!="UNDETERMINED" and (support<2 or confidence<65): verdict="UNDETERMINED"
        self.results[result_id]=QuorumResult(result_id,claim[:1200],verdict,u256(support),u256(confidence))

    @gl.public.view
    def get_result(self,result_id:str)->QuorumResult:
        if result_id not in self.results: raise gl.vm.UserError("Result not found")
        return self.results[result_id]
