from gltest.direct import create_address


def test_create_requires_reward(direct_vm, direct_deploy):
    c = direct_deploy("contracts/visual_milestone_escrow.py")
    alice = create_address("alice")
    bob = create_address("bob")
    direct_vm.sender = alice
    direct_vm.value = 0

    with direct_vm.expect_revert("Reward must be greater than zero"):
        c.create_milestone(
            "m1",
            bob,
            "Visible dashboard must show all three KPIs",
        )


def test_worker_only_submit(direct_vm, direct_deploy):
    c = direct_deploy("contracts/visual_milestone_escrow.py")
    alice = create_address("alice")
    bob = create_address("bob")
    charlie = create_address("charlie")

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
