import json

def test_rubric_pass(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/visual_rubric_gate.py"); direct_vm.sender=direct_alice
    direct_vm.mock_llm(r"(?s).*Evaluate the visual deliverable against this frozen rubric.*",json.dumps({"verdict":"PASS","score":88,"confidence":90,"reason":"All required visual elements are present."}))
    c.evaluate("g1","Must show title, chart, and legend.",b"img"); r=c.get_result("g1"); assert r.verdict=="PASS"; assert r.score==88

def test_rubric_score_floor(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/visual_rubric_gate.py"); direct_vm.sender=direct_alice
    direct_vm.mock_llm(r"(?s).*Evaluate the visual deliverable against this frozen rubric.*",json.dumps({"verdict":"PASS","score":55,"confidence":92,"reason":"Only part of rubric met."}))
    c.evaluate("g2","Must satisfy all items.",b"img"); assert c.get_result("g2").verdict=="FAIL"
