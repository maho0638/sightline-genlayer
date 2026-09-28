# Reviewer Guide

Sightline is intentionally reviewable as a catalog of standalone mechanisms rather than as a UI demo.

## Fast review

1. Read `CONTRACTS.md` for the purpose and invariant of each of the 12 primitives.
2. Read `docs/THREAT_MODEL.md` for the failure model and fail-closed controls.
3. Read `DECISIONS.md` for implementation changes caused by current GenLayer limits and live observations.
4. Inspect the canonical CI run linked from `docs/PROOF_MANIFEST.json`.
5. Inspect the canonical Studionet run and the Explorer transactions pinned in the manifest.

## Reproduce deterministic tests

```bash
python -m pip install -r requirements.txt
pytest tests/direct -v
for f in contracts/*.py; do genvm-lint check "$f"; done
```

The direct suite covers:
- happy paths and low-confidence fail-closed paths;
- duplicate-ID state invariants;
- exact SHA-256 binding for caller-supplied visual evidence;
- challenge-window and distinct-evidence rules;
- adversarial validator disagreement, where the validator must reject a changed leader result.

## Reproduce live Studionet proofs

```bash
gltest tests/integration/test_sightline_studionet.py -v -s --network studionet
gltest tests/integration/test_sightline_catalog_studionet.py -v -s --network studionet
```

The first suite exercises the deeper lifecycle mechanisms:
- rubric-scored raw image;
- live HTTPS screenshot judgment;
- challengeable visual claim;
- native-GEN milestone escrow through create -> submit -> resolve -> challenge -> re-resolve -> refund.

The second suite deploys and exercises the remaining visual primitives with deterministic PNG fixtures generated during the test.

## What is consensus-backed

Sightline never treats an LLM call as trusted state by itself. Each semantic output is produced inside a nondeterministic block and independently re-evaluated by the validator function. The accepted result is then normalized through deterministic state rules such as confidence floors, score floors, blocker precedence, 2-of-3 quorum, one-shot challenge limits, and settlement locks.

## Evidence identity

Caller-supplied raw images are committed by SHA-256 in contract state. Live webpage screenshots are rendered independently by validators, so their pixel bytes are not required to match; the leader snapshot digest is recorded for auditability while validators agree on the bounded semantic judgment.
