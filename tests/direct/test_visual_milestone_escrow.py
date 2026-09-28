from gltest.direct import create_address


def _deploy_with_accounts(direct_vm, direct_deploy):
    c = direct_deploy("contracts/visual_milestone_escrow.py")
    alice = create_address("alice")
    bob = create_address("bob")
    charlie = create_address("charlie")
    return c, alice, bob, charlie


def test_create_requires_reward(direct_vm, direct_deploy):
    c, alice, bob, _ = _deploy_with_accounts(direct_vm, direct_deploy)
    direct_vm.sender = alice
    direct_vm.value = 0

    with direct_vm.expect_revert("Reward must be greater than zero"):
        c.create_milestone(
            "m1",
            bob,
            "Visible dashboard must show all three KPIs",
        )


def test_worker_only_submit(direct_vm, direct_deploy):
    c, alice, bob, charlie = _deploy_with_accounts(direct_vm, direct_deploy)
    direct_vm.sender = alice
    direct_vm.value = 10**18
    c.create_milestone(
        "m2",
        bob,
        "Visible dashboard must show all three KPIs",
    )

    direct_vm.value = 0
    direct_vm.sender = charlie
    with direct_vm.expect_revert("Only the worker can submit proof"):
        c.submit_proof("m2", "https://example.com/proof")


def test_proof_requires_https(direct_vm, direct_deploy):
    c, alice, bob, _ = _deploy_with_accounts(direct_vm, direct_deploy)
    direct_vm.sender = alice
    direct_vm.value = 10**18
    c.create_milestone("m3", bob, "Visible proof must show completion")

    direct_vm.value = 0
    direct_vm.sender = bob
    with direct_vm.expect_revert("Proof URL must use HTTPS"):
        c.submit_proof("m3", "http://example.com/proof")


def test_duplicate_milestone_rejected(direct_vm, direct_deploy):
    c, alice, bob, _ = _deploy_with_accounts(direct_vm, direct_deploy)
    direct_vm.sender = alice
    direct_vm.value = 10**18
    c.create_milestone("m4", bob, "Visible proof must show completion")

    direct_vm.value = 10**18
    with direct_vm.expect_revert("Milestone already exists"):
        c.create_milestone("m4", bob, "Another rubric")


def test_cannot_challenge_before_resolution(direct_vm, direct_deploy):
    c, alice, bob, _ = _deploy_with_accounts(direct_vm, direct_deploy)
    direct_vm.sender = alice
    direct_vm.value = 10**18
    c.create_milestone("m5", bob, "Visible proof must show completion")

    direct_vm.value = 0
    with direct_vm.expect_revert("Milestone has no challengeable resolution"):
        c.challenge_resolution("m5", "The visual result should be re-checked.")
