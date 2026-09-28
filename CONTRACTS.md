# Sightline contract catalog

Sightline is one contribution composed of 12 standalone Intelligent Contract primitives. The contracts share a vision-consensus safety boundary but expose different state machines and failure semantics.

## 1. ReceiptAttestor
Purpose: verify that a receipt image matches expected merchant, amount and date. Consensus compares the decisive verdict and amount; low confidence becomes `UNDETERMINED`.

## 2. DamageSeverityOracle
Purpose: convert visible damage into `NONE`, `MINOR`, `MODERATE`, `SEVERE` or `UNDETERMINED`. It explicitly refuses to infer hidden damage.

## 3. BeforeAfterVerifier
Purpose: compare two images and decide whether they establish a claimed material change. Materiality is bounded and confidence fails closed.

## 4. VisualRubricGate
Purpose: score one visual deliverable against a frozen natural-language rubric. Deterministic post-processing prevents a sub-threshold PASS.

## 5. ChartClaimVerifier
Purpose: decide whether a chart or dashboard visibly supports a claim and preserve the short extracted fact that drove the decision.

## 6. VisualQuorum
Purpose: aggregate three separate visual observations without exceeding GenLayer's two-image-per-prompt limit. Each image is classified independently, then a deterministic 2-of-3 rule decides support/contradiction/undetermined.

## 7. UIStateAttestor
Purpose: attest whether an application screenshot visibly establishes a named UI state. `blocked=true` deterministically overrides `visible=true`.

## 8. DocumentFieldAttestor
Purpose: verify one named field from a scanned/photographed document. It intentionally avoids unconstrained OCR and refuses to infer missing fields.

## 9. ChallengeableVisualClaim
Purpose: provide one fresh visual re-review before a claim can be finalized. Initial and final verdicts remain auditable.

## 10. VisualDecisionReceipt
Purpose: answer a bounded yes/no/abstain question and store a compact receipt containing the question, evidence reference, decision, confidence and rationale.

## 11. WebScreenshotAttestor
Purpose: capture a live webpage screenshot inside GenLayer and verify a visual criterion. This composes web access with vision consensus.

## 12. VisualMilestoneEscrow
Purpose: attach an economic consequence to visual evidence. A sponsor escrows native GEN, a designated worker submits an HTTPS proof URL, validators inspect the screenshot against the frozen rubric, and deterministic state gates claim or refund.

## Shared safety boundary

- image bytes are inputs to vision evaluation but are not stored;
- free-form model text is never the sole authority;
- decisive outputs are discrete/bounded fields;
- validators independently re-run the vision judgment;
- low confidence fails closed;
- duplicate IDs are rejected;
- economic transfers happen only after deterministic state checks.

## Non-goal

Sightline is not twelve renamed prompts around one generic verifier. Each contract has a different public API, state representation, deterministic invariant, and failure path.
