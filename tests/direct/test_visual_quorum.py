import json

def test_three_image_support_quorum(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/visual_quorum.py")
    direct_vm.sender = direct_alice
    direct_vm.mock_llm(
        r"(?s).*Judge this ONE visual evidence item.*",
        json.dumps({"verdict": "SUPPORTED", "confidence": 90}),
    )
    c.verify("q1", "The package is visibly sealed.", b"a", b"b", b"c")
    r = c.get_result("q1")
    assert r.verdict == "SUPPORTED"
    assert r.support_count == 3
    assert r.contradict_count == 0

def test_three_image_contradiction_quorum(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/visual_quorum.py")
    direct_vm.sender = direct_alice
    direct_vm.mock_llm(
        r"(?s).*Judge this ONE visual evidence item.*",
        json.dumps({"verdict": "CONTRADICTED", "confidence": 91}),
    )
    c.verify("q2", "The indicator is green.", b"a", b"b", b"c")
    r = c.get_result("q2")
    assert r.verdict == "CONTRADICTED"
    assert r.contradict_count == 3
