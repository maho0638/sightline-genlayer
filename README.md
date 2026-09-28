# Sightline — Visual Consensus Primitives for GenLayer

Sightline is a catalog of standalone GenLayer Intelligent Contracts that turn visual evidence into small, auditable on-chain decisions.

The project deliberately focuses on the Vision surface of GenLayer rather than rebuilding text-only web verification. Each primitive accepts visual evidence as raw image bytes, keeps nondeterminism inside a bounded vision judgment, asks validators to independently re-check the decisive fields, and writes only compact structured results to storage.

## Why GenLayer

Traditional smart contracts cannot inspect a receipt photo, compare before/after images, judge visible damage, read a chart, or determine whether a UI screenshot satisfies a written acceptance criterion. GenLayer can pass images to vision-capable validators and reach consensus over the resulting structured judgment.

## Catalog

1. `ReceiptAttestor` — verifies merchant / amount / date against an expected receipt claim.
2. `DamageSeverityOracle` — classifies visible damage and explicitly supports `UNDETERMINED`.
3. `BeforeAfterVerifier` — judges whether two images support a claimed material change.
4. `VisualRubricGate` — checks a visual deliverable against a frozen natural-language rubric.
5. `ChartClaimVerifier` — verifies whether a chart or dashboard image supports a numerical/textual claim.
6. `VisualQuorum` — evaluates three independent images and requires a deterministic support threshold.
7. `UIStateAttestor` — proves a named UI state from a screenshot using fixed boolean flags.
8. `DocumentFieldAttestor` — extracts and verifies a small set of expected fields from a photographed/scanned document.
9. `ChallengeableVisualClaim` — gives a visual judgment one fresh challenge/re-review before finalization.
10. `VisualDecisionReceipt` — stores a compact auditable receipt tying a question, evidence reference and consensus result together.
11. `WebScreenshotAttestor` — screenshots a live HTTPS page and attests a visual criterion.
12. `VisualMilestoneEscrow` — locks native GEN behind a visual milestone and releases/refunds after consensus judgment.

## Safety design

- image bytes are evaluated but not stored;
- callers supply a short evidence reference for auditability;
- all results are reduced to bounded discrete fields;
- validator logic independently re-runs the vision judgment;
- low-confidence or malformed results fail closed to `UNDETERMINED` / `ABSTAIN`;
- deterministic thresholds are applied after consensus;
- duplicate IDs are rejected;
- no production claim is made until live Studionet proof exists.

## Verification gates before Portal submission

1. all direct tests green;
2. every contract passes GenVM lint;
3. at least three flagship primitives are deployed and exercised on Studionet;
4. transaction hashes and addresses are pinned in a machine-readable proof manifest;
5. reviewer reproduction steps are written from scratch;
6. only then is the Intelligent Contracts contribution prepared.
