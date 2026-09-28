# Sightline architecture

Sightline treats vision AI as an untrusted nondeterministic sensor. Contracts do not accept free-form prose as final authority. Each primitive follows the same boundary:

1. deterministic input validation;
2. bounded vision task using `gl.nondet.exec_prompt(..., images=[...], response_format="json")`;
3. validator-side independent re-execution;
4. agreement on decisive discrete fields, plus bounded numeric tolerance where needed;
5. deterministic fail-closed normalization;
6. compact state write.

The official GenLayer image-processing API currently limits one LLM call to at most two images. `VisualQuorum` deliberately respects that constraint by judging each of three images separately and only then aggregating the three discrete observations with a deterministic 2-of-3 rule.

The project avoids a generic `verify_image(prompt)` abstraction because that would hide the actual product invariants. Receipt matching, damage classification, before/after comparison, UI blocking, quorum aggregation, challenge lifecycle, and escrow settlement are separate mechanisms.
