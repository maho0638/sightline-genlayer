# Live Studionet verification plan

Portal submission is blocked until the following proof exists.

## Flagship A — VisualRubricGate
Deploy and evaluate a small stable PNG fixture with a frozen rubric. Record deployed address, write tx, finalized state, score and verdict.

## Flagship B — WebScreenshotAttestor
Use a stable public HTTPS page with an obvious visible criterion. The contract captures the screenshot with `gl.nondet.web.render(..., mode="screenshot")`; record address, write tx and stored result.

## Flagship C — VisualMilestoneEscrow
Create a milestone with a small native GEN reward, designate a second account as worker, submit a stable visual proof URL, resolve, and exercise exactly one economic terminal path (`claim` for APPROVED or `refund` for REJECTED/UNDETERMINED). Record every tx and final state.

## Challenge path
Deploy `ChallengeableVisualClaim`, open a claim, run one fresh challenge with second visual evidence, verify `challenged=true`, then finalize.

## Reviewer evidence required
- deployment address for each flagship;
- source links;
- 24/24 direct test result;
- GenVM lint result for all 12 contracts;
- canonical CI run;
- canonical Studionet run;
- exact transaction hashes;
- `docs/PROOF_MANIFEST.json`;
- reproduction commands and expected state.
