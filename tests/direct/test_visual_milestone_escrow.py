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


def _prepare_resolvable_milestone(direct_vm, direct_deploy, milestone_id):
    import json

    c, alice, bob, _ = _deploy_with_accounts(direct_vm, direct_deploy)
    direct_vm.sender = alice
    direct_vm.value = 10**18
    c.create_milestone(
        milestone_id,
        bob,
        "Approve only when the visual proof clearly satisfies the frozen rubric.",
    )

    direct_vm.value = 0
    direct_vm.sender = bob
    c.submit_proof(milestone_id, "https://example.com/proof")

    direct_vm.mock_web(
        r"https://example\.com/.*",
        {"status": 200, "body": "proof"},
    )
    return c, alice, json


def test_validator_rejects_score_tolerance_that_crosses_approval_threshold(
    direct_vm,
    direct_deploy,
):
    c, alice, json = _prepare_resolvable_milestone(
        direct_vm,
        direct_deploy,
        "m-score-boundary",
    )
    pattern = r"(?s).*Judge this visual milestone proof against the frozen rubric below.*"
    direct_vm.mock_llm(
        pattern,
        json.dumps({
            "verdict": "PASS",
            "score": 72,
            "confidence": 80,
            "reason": "Leader sees the milestone above the approval score floor.",
        }),
    )

    direct_vm.sender = alice
    c.resolve("m-score-boundary")

    direct_vm.clear_mocks()
    direct_vm.mock_web(
        r"https://example\.com/.*",
        {"status": 200, "body": "proof"},
    )
    direct_vm.mock_llm(
        pattern,
        json.dumps({
            "verdict": "PASS",
            "score": 68,
            "confidence": 80,
            "reason": "Validator sees the same verdict below the score floor.",
        }),
    )

    assert direct_vm.run_validator() is False


def test_validator_rejects_confidence_tolerance_that_crosses_fail_closed_floor(
    direct_vm,
    direct_deploy,
):
    c, alice, json = _prepare_resolvable_milestone(
        direct_vm,
        direct_deploy,
        "m-confidence-boundary",
    )
    pattern = r"(?s).*Judge this visual milestone proof against the frozen rubric below.*"
    direct_vm.mock_llm(
        pattern,
        json.dumps({
            "verdict": "PASS",
            "score": 90,
            "confidence": 70,
            "reason": "Leader is above both settlement thresholds.",
        }),
    )

    direct_vm.sender = alice
    c.resolve("m-confidence-boundary")

    direct_vm.clear_mocks()
    direct_vm.mock_web(
        r"https://example\.com/.*",
        {"status": 200, "body": "proof"},
    )
    direct_vm.mock_llm(
        pattern,
        json.dumps({
            "verdict": "PASS",
            "score": 90,
            "confidence": 60,
            "reason": "Validator falls below the confidence floor.",
        }),
    )

    assert direct_vm.run_validator() is False


def test_validator_accepts_numeric_drift_when_settlement_outcome_is_unchanged(
    direct_vm,
    direct_deploy,
):
    c, alice, json = _prepare_resolvable_milestone(
        direct_vm,
        direct_deploy,
        "m-same-outcome",
    )
    pattern = r"(?s).*Judge this visual milestone proof against the frozen rubric below.*"
    direct_vm.mock_llm(
        pattern,
        json.dumps({
            "verdict": "PASS",
            "score": 78,
            "confidence": 82,
            "reason": "Leader sees a clear approved outcome.",
        }),
    )

    direct_vm.sender = alice
    c.resolve("m-same-outcome")

    direct_vm.clear_mocks()
    direct_vm.mock_web(
        r"https://example\.com/.*",
        {"status": 200, "body": "proof"},
    )
    direct_vm.mock_llm(
        pattern,
        json.dumps({
            "verdict": "PASS",
            "score": 75,
            "confidence": 79,
            "reason": "Validator differs slightly but remains approved.",
        }),
    )

    assert direct_vm.run_validator() is True
