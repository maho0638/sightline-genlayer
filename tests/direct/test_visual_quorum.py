import hashlib
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
    assert r.image_hash_a == hashlib.sha256(b"a").hexdigest()
    assert r.image_hash_b == hashlib.sha256(b"b").hexdigest()
    assert r.image_hash_c == hashlib.sha256(b"c").hexdigest()


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


def test_quorum_rejects_duplicate_images(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/visual_quorum.py")
    direct_vm.sender = direct_alice
    with direct_vm.expect_revert("Visual quorum requires three distinct images"):
        c.verify("q3", "A claim.", b"same", b"same", b"other")
