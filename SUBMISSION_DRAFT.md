# Sightline — Visual Consensus Primitives (DRAFT — DO NOT SUBMIT YET)

## Summary

Sightline is a catalog of 12 reusable GenLayer Intelligent Contracts that turn receipts, photos, screenshots, charts and visual milestone proofs into bounded consensus-backed on-chain decisions. The suite includes a native-GEN visual milestone escrow and a live webpage screenshot attestor.

## Why it is distinct

The earlier SourceVerifier contribution verifies one textual factual claim against two web sources. Sightline instead uses GenLayer's image-processing surface and builds independent visual mechanisms: before/after change, 2-of-3 visual quorum, UI-state attestation, chart claims, document fields, challengeable visual claims, live screenshot attestation and GEN-backed visual settlement.

## Why GenLayer is central

The decisive inputs are visual and semantic. A deterministic smart contract cannot inspect photos, receipts, charts, or rendered webpage screenshots. Sightline uses GenLayer vision-capable validator execution, then normalizes model output into bounded fields before deterministic state transitions.

## Submission gate

Do not submit until:
- all 24 direct tests pass;
- all 12 contracts pass GenVM lint;
- flagship Studionet deployments and writes are finalized;
- exact contract addresses and transaction hashes are pinned;
- reviewer reproduction steps are complete.
