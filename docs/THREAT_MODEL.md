# Sightline Threat Model

Sightline treats visual AI output as an untrusted nondeterministic observation. The contracts are designed around bounded consequences rather than assuming a model is always correct.

## Threats and controls

| Threat | Control |
| --- | --- |
| Prompt injection inside an image/webpage | Prompts explicitly treat visible text as evidence only and constrain the task/output. |
| Hallucinated certainty | Every classification has an explicit UNDETERMINED/ABSTAIN path; low confidence fails closed. |
| Evidence swapping after a decision | Raw-image primitives persist SHA-256 digests of the exact evaluated bytes. |
| Duplicate images faking quorum | VisualQuorum rejects repeated SHA-256 digests before consensus. |
| One weak image counted multiple times | Three images are classified independently; deterministic aggregation requires 2-of-3 support with no contradictory vote for a positive result. |
| Model says PASS with a weak score | VisualRubricGate deterministically converts PASS below the score floor to FAIL. |
| UI success hidden by an error/modal | UIStateAttestor gives a blocker flag deterministic priority over visible=true. |
| Validator/model disagreement | Validators independently re-run decisive judgments; adversarial direct tests prove changed results are rejected. |
| Immediate settlement defeating appeal rights | ChallengeableVisualClaim and VisualMilestoneEscrow enforce a one-hour initial challenge window. |
| Reusing the same challenge evidence | ChallengeableVisualClaim requires a different SHA-256 evidence digest. |
| Double settlement | Escrow stores terminal settlement state and rejects a second claim/refund. |
| Arbitrary/unbounded inputs | IDs, rubrics, URLs, result strings, notes, and rationales are bounded; web proof URLs must be HTTPS. |
| Nondeterministic storage mutation | Nondeterministic calls only produce structured results; storage/economic state changes happen afterward in deterministic code. |

## Explicit limitations

Sightline does not prove that a photo is recent, geolocated, camera-authentic, or free of image editing. Those properties require trusted capture/attestation infrastructure outside the present contracts. Sightline only reaches consensus over what supplied visual evidence visibly establishes.

The contracts also do not claim infallible OCR. DocumentFieldAttestor intentionally verifies one named field at a time and can return UNDETERMINED instead of inventing missing content.
