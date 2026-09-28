def test_requires_https(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/web_screenshot_attestor.py"); direct_vm.sender=direct_alice
    with direct_vm.expect_revert("URL must use HTTPS"):
        c.attest("s1","http://example.com","Page shows operational status")

def test_requires_criterion(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/web_screenshot_attestor.py"); direct_vm.sender=direct_alice
    with direct_vm.expect_revert("Missing ID or criterion"):
        c.attest("s2","https://example.com","")
