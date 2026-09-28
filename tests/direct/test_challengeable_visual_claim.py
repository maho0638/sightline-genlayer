import json

def test_one_challenge(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/challengeable_visual_claim.py"); direct_vm.sender=direct_alice
    direct_vm.mock_llm(r"(?s).*Does the visual evidence support this claim.*",json.dumps({"verdict":"SUPPORTED","confidence":90}))
    c.open_claim("v1","package delivered intact",b"img1"); c.challenge("v1",b"img2"); r=c.get_claim("v1"); assert r.challenged is True; assert r.final_verdict=="SUPPORTED"
    with direct_vm.expect_revert("Challenge already used"):
        c.challenge("v1",b"img3")

def test_finalize_blocks_challenge(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/challengeable_visual_claim.py"); direct_vm.sender=direct_alice
    direct_vm.mock_llm(r"(?s).*Does the visual evidence support this claim.*",json.dumps({"verdict":"SUPPORTED","confidence":90}))
    c.open_claim("v2","claim",b"img"); c.finalize("v2")
    with direct_vm.expect_revert("Claim already finalized"):
        c.challenge("v2",b"img")
