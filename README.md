# Sightline — Visual Consensus Primitives for GenLayer

Sightline is a catalog of 12 standalone GenLayer Intelligent Contracts that turn visual evidence into small, auditable on-chain decisions.

The project deliberately focuses on the Vision surface of GenLayer rather than rebuilding text-only web verification. Each primitive accepts visual evidence as raw image bytes or a bounded live-web proof, keeps nondeterminism inside a constrained semantic judgment, asks validators to independently re-check the decisive fields, and writes only compact structured results to storage.

## Why GenLayer

Traditional smart contracts cannot inspect a receipt photo, compare before/after images, judge visible damage, read a chart, determine whether a UI screenshot satisfies a written acceptance criterion, or evaluate a rendered webpage screenshot semantically. GenLayer can pass these inputs through vision-capable validator execution and reach consensus over bounded structured judgments.

## Catalog

1. `ReceiptAttestor` — verifies merchant / amount / date against an expected receipt claim.
2. `DamageSeverityOracle` — classifies visible damage and explicitly supports `UNDETERMINED`.
3. `BeforeAfterVerifier` — judges whether two images support a claimed material change.
4. `VisualRubricGate` — checks a visual deliverable against a frozen natural-language rubric.
5. `ChartClaimVerifier` — verifies whether a chart or dashboard image supports a numerical/textual claim.
6. `VisualQuorum` — evaluates three independent images and applies deterministic 2-of-3 aggregation.
7. `UIStateAttestor` — proves a named UI state from a screenshot using fixed boolean flags and blocker precedence.
8. `DocumentFieldAttestor` — verifies one named field from a photographed/scanned document.
9. `ChallengeableVisualClaim` — gives a visual judgment one fresh challenge/re-review before finalization.
10. `VisualDecisionReceipt` — stores a compact auditable receipt tying a question, evidence reference and consensus result together.
11. `WebScreenshotAttestor` — screenshots a live HTTPS page and attests a visual criterion.
12. `VisualMilestoneEscrow` — locks native GEN behind a visual milestone and releases/refunds after consensus judgment.

## Safety design

- AI output is treated as an untrusted nondeterministic observation;
- raw caller-supplied image bytes are SHA-256 bound to the resulting state;
- image bytes themselves are not stored;
- decisive outputs are reduced to bounded fields;
- validators independently re-run decisive vision judgments;
- low-confidence or malformed results fail closed to `UNDETERMINED` / `ABSTAIN`;
- validators compare the final thresholded settlement status inside consensus, so tolerated score/confidence drift cannot cross an economic decision boundary;
- duplicate result IDs are rejected;
- VisualQuorum rejects duplicate evidence hashes and aggregates three independent classifications;
- UI blocker state deterministically overrides visible success;
- challengeable mechanisms enforce a one-hour initial challenge window;
- economic settlement is deterministic and terminal state prevents double settlement;
- live-web screenshot consensus is semantic, because independent renders need not be pixel-identical.

See `docs/THREAT_MODEL.md` for explicit limitations.

## Current verification snapshot

Sightline is live-verified on Studionet:

- 58 direct tests PASS;
- 12 / 12 contracts pass GenVM lint;
- canonical CI run: https://github.com/maho0638/sightline-genlayer/actions/runs/36456868314
- canonical full Studionet run: https://github.com/maho0638/sightline-genlayer/actions/runs/36456231411
- live commit: `c5c89b43d27be0fd5393a4a099e09608d05d04fb`
- core lifecycle: 4 / 4 PASS;
- expanded catalog: 8 / 8 PASS;
- total: 12 / 12 primitives deployed and exercised with live transactions and read/assertion checks.

The live workflow pins SHA-256 hashes of all 12 contract sources. Contract addresses, transaction hashes, source hashes, evidence hashes, and observed results are in `docs/PROOF_MANIFEST.json`.

## Reviewer path

1. Read `CONTRACTS.md`.
2. Read `docs/THREAT_MODEL.md` and `DECISIONS.md`.
3. Inspect `docs/PROOF_MANIFEST.json`.
4. Follow `docs/REVIEWER_GUIDE.md` for direct and Studionet reproduction.
5. Use `SUBMISSION_DRAFT.md` as the Portal-facing technical summary.
