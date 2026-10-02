# Sightline — Visual Consensus Primitives for GenLayer

## Submission status

READY FOR FINAL PORTAL REVIEW

Sightline has completed its direct-test, GenVM lint, and live Studionet verification gates. The contribution is intentionally packaged as one high-quality Intelligent Contracts submission containing 12 distinct visual-consensus state machines, not as 12 near-duplicate submissions.

## Short summary

Sightline is a reusable catalog of 12 GenLayer Intelligent Contracts that turn receipts, photos, before/after evidence, screenshots, charts, scanned documents, live webpage screenshots, and visual milestone proofs into bounded consensus-backed on-chain decisions.

The suite includes exact evidence binding, fail-closed confidence gates, 2-of-3 visual quorum, challenge/re-review mechanics, and a native-GEN visual milestone escrow with a guaranteed one-hour challenge window.

## Why it is distinct

Sightline is not a renamed text-verification contribution and it is not one generic prompt copied across contracts. The 12 primitives expose different public APIs, state layouts, deterministic invariants, and failure semantics:

- receipt field matching;
- visible damage classification;
- before/after material-change verification;
- visual rubric scoring;
- chart-claim verification;
- three-image quorum;
- UI-state attestation with blocker precedence;
- bounded document-field verification;
- challengeable visual claims;
- compact visual decision receipts;
- live HTTPS screenshot attestation;
- native-GEN visual milestone escrow.

## Why GenLayer is necessary

The decisive inputs are visual and semantic. A conventional deterministic smart contract cannot inspect a receipt photo, compare before/after images, judge visible physical damage, read a chart, interpret a UI screenshot, or evaluate a rendered webpage against a natural-language visual rubric.

Sightline uses GenLayer's vision-capable nondeterministic execution for the bounded semantic judgment, asks validators to independently re-evaluate the decisive fields, then applies deterministic contract rules before storage or economic settlement.

## Security model

Sightline treats AI output as untrusted observation rather than trusted state.

Key controls:

- low confidence resolves to UNDETERMINED / ABSTAIN;
- invalid labels are normalized;
- deterministic score and confidence floors, with thresholded final outcomes compared inside validator consensus across the affected primitives;
- duplicate result IDs are blocked;
- duplicate image evidence is blocked where quorum requires distinct observations;
- caller-supplied raw images are bound to exact SHA-256 digests;
- live web screenshots use semantic consensus rather than requiring validator pixel hashes to match;
- visible webpage/image text is explicitly treated as evidence, not instruction;
- validator disagreement is tested adversarially;
- nondeterministic calls do not directly mutate economic state;
- challengeable mechanisms enforce a one-hour initial challenge window;
- challenge evidence must be fresh where applicable;
- settlement remains locked during the initial challenge period;
- terminal settlement prevents double claim/refund.

## Live verification

### Direct and lint

- 67 direct tests: PASS
- 12 / 12 GenVM contract lints: PASS
- Canonical CI run: https://github.com/maho0638/sightline-genlayer/actions/runs/37062146230

The direct suite covers happy paths, fail-closed paths, duplicate-ID invariants, exact SHA-256 evidence binding, challenge-window rules, distinct-evidence rules, adversarial validator disagreement, and score/confidence threshold-crossing regressions.

### Canonical Studionet proof

- Canonical run: https://github.com/maho0638/sightline-genlayer/actions/runs/37062146333
- Live code commit: `160992edf63803a49e14e6642f94329aa4e9e016`
- Core lifecycle suite: 4 / 4 PASS
- Expanded catalog suite: 8 / 8 PASS
- Total: 12 / 12 primitives deployed and exercised on Studionet

The workflow pins SHA-256 hashes of every contract source before live execution. The machine-readable addresses, transaction hashes, source hashes, evidence hashes, and observed results are recorded in `docs/PROOF_MANIFEST.json`.

## Deep lifecycle evidence

### ChallengeableVisualClaim

Live flow:

initial evidence -> SUPPORTED -> one-hour challenge window -> distinct challenge evidence -> CONTRADICTED -> finalize

This demonstrates that an initial AI-supported decision cannot simply bypass the configured re-review path.

### VisualMilestoneEscrow

Live native-GEN flow:

create -> worker proof submission -> visual resolution -> challenge -> fresh re-resolution -> sponsor refund

Canonical live outcome:

- initial decision: REJECTED
- resolution round: 2
- challenge count: 1
- final settlement: REFUNDED

This is an economic state machine, not only a vision demo: consensus outcome gates native GEN settlement, with challenge and double-settlement protections.

## Evidence identity

Caller-supplied raw visual evidence is committed to state with SHA-256 so the evaluated bytes are auditable.

Live webpage screenshots are different: validators render independently and pixel bytes can legitimately differ. Sightline therefore records the leader screenshot digest as an audit snapshot while consensus is taken over bounded semantic output.

## Reproducibility

Reviewer steps are in `docs/REVIEWER_GUIDE.md`.

Direct verification:

```bash
python -m pip install -r requirements.txt
pytest tests/direct -v
for f in contracts/*.py; do genvm-lint check "$f"; done
```

Live Studionet verification:

```bash
gltest tests/integration/test_sightline_studionet.py -v -s --network studionet
gltest tests/integration/test_sightline_catalog_studionet.py -v -s --network studionet
```

## Reviewer map

- `README.md` — project overview and current verification snapshot
- `CONTRACTS.md` — purpose and invariant of each primitive
- `DECISIONS.md` — engineering decisions and live-observation-driven changes
- `docs/THREAT_MODEL.md` — explicit security model and limitations
- `docs/REVIEWER_GUIDE.md` — reproduction path
- `docs/PROOF_MANIFEST.json` — machine-readable live proof

## Final claim

Sightline demonstrates reusable visual consensus primitives with deterministic safety boundaries, real Studionet state transitions, source-hash pinning, adversarial consensus tests, and a live native-GEN settlement lifecycle.

The submission does not claim that AI is infallible, that images are authentic/recent/geolocated, or that live webpage pixels are identical across validators. Those limitations are explicit in the threat model.
