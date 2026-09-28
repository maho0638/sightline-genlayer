# Engineering Decisions and Live Findings

This file records decisions that changed Sightline's implementation after reading current GenLayer documentation or observing real test/runtime behavior. It is an audit trail, not marketing copy.

## 2026-09-28 — VisualQuorum respects the two-image prompt limit

GenLayer's current image-processing API allows at most two images in a single LLM prompt. The first draft of VisualQuorum tried to pass three images together. That design was discarded before release.

The final contract judges each of three distinct images separately inside the same nondeterministic leader execution, reduces each observation to a small verdict/confidence pair, then applies a deterministic 2-of-3 aggregate rule. SHA-256 hashes prove the three supplied images are distinct.

## 2026-09-28 — Exact evidence bytes are bound on-chain

A free-form evidence reference is not enough to prove which uploaded bytes were actually evaluated. ReceiptAttestor, BeforeAfterVerifier, VisualRubricGate, VisualQuorum, and ChallengeableVisualClaim now persist SHA-256 digests of the exact image bytes that drove the decision.

This separates identity from interpretation: the digest is deterministic, while the visual judgment is consensus-backed.

## 2026-09-28 — Direct-mode address fixtures can be raw bytes

The direct-test address fixtures may be created before the contract SDK is loaded and can therefore be raw bytes. Storing one directly in an Address storage field produced an `as_bytes` failure.

Tests now construct Address objects after deployment. The public VisualMilestoneEscrow entry point also normalizes string/int address inputs before persisting them, because external clients commonly pass hex strings.

## 2026-09-28 — Screenshot verification must test observed behavior, not a hoped-for answer

An exploratory live Studionet test asked whether the example.com screenshot visibly contained the heading "Example Domain". The contract finalized a high-confidence FAIL. We did not rewrite or hide that observation.

The canonical screenshot proof instead uses an intentionally false visual criterion: a full-screen bright-red SYSTEM DOWN alert on example.com. This reliably exercises the negative screenshot + vision path and records the model's concrete note.

## 2026-09-28 — Challenges must have an economic/time effect

A challenge method that exists only as metadata does not protect settlement. ChallengeableVisualClaim and VisualMilestoneEscrow therefore use a guaranteed one-hour initial challenge window. Initial decisions cannot be finalized/settled during that window. A used challenge triggers a fresh judgment; after the re-resolution, settlement can proceed immediately.

## 2026-09-28 — Consensus guard tests include disagreement, not only happy paths

Direct tests deliberately replace the leader's mocked visual judgment before executing the captured validator. Validators must return false when verdicts, scores, blockers, extracted facts, or aggregate quorum outcomes change. This checks the consensus boundary itself rather than only testing storage after a mocked successful answer.
