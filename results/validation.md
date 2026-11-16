# Final validation (codebook v0.3)

Sample: 397 decisions, stratified by framework × provenance (66 per stratum plus the one decision the LLM failed to code), English only, pilot decisions excluded, at most two decisions per repository per stratum. Blind coding by two annotators (A, B) working independently.

LLM: Qwen3.8-27B, open weights, temperature 0, frozen prompt (codebook v0.3), effort xhigh with one retry at medium.

Cells: Cohen's kappa [95% CI, cluster bootstrap over repositories] (percentage agreement).

Annotator A: 6.5 h over 6 sessions.
Annotator B: 6.0 h over 6 sessions.

## Overall

| Dimension | A–B (n=397) | A–LLM (n=396) | B–LLM (n=396) | Consensus–LLM (n=320) |
| --- | --- | --- | --- | --- |
| mood | 0.87 [0.81, 0.93] (96%) | 0.71 [0.60, 0.81] (92%) | 0.72 [0.62, 0.81] (92%) | 0.76 [0.66, 0.86] (92%) |
| locus | 0.79 [0.74, 0.84] (86%) | 0.65 [0.59, 0.71] (76%) | 0.67 [0.62, 0.72] (77%) | 0.75 [0.69, 0.81] (83%) |
| concern | 0.82 [0.77, 0.86] (86%) | 0.64 [0.58, 0.70] (72%) | 0.65 [0.59, 0.70] (72%) | 0.72 [0.66, 0.78] (78%) |
| subcode | 0.76 [0.70, 0.81] (89%) | 0.55 [0.48, 0.62] (77%) | 0.56 [0.49, 0.63] (78%) | 0.63 [0.54, 0.72] (83%) |

## Per stratum (kappa)

| Stratum | n | A–B mood | A–B locus | A–B concern | Cons–LLM mood | Cons–LLM locus | Cons–LLM concern |
| --- | --- | --- | --- | --- | --- | --- | --- |
| speckit/ASKED | 66 | 1.00 | 0.79 | 0.76 | 1.00 | 0.76 | 0.75 |
| speckit/ASSUMED | 66 | 0.79 | 0.61 | 0.69 | 0.65 | 0.62 | 0.56 |
| gsd/ASKED | 66 | -0.02 | 0.79 | 0.74 | n/a (one category) | 0.69 | 0.60 |
| gsd/DELEGATED | 66 | n/a (one category) | 0.87 | 0.85 | n/a (one category) | 0.97 | 0.82 |
| gsd/ASSUMED | 66 | 0.89 | 0.85 | 0.87 | 0.55 | 0.54 | 0.55 |
| bmad/ASSUMED | 67 | 0.75 | 0.70 | 0.82 | 0.67 | 0.73 | 0.72 |

## Disagreement patterns (A vs B)

- **mood**: INDICATIVE vs OPTATIVE (16)
- **locus**: ENV vs INTERFACE (16), INTERFACE vs NA (14), INTERFACE vs MACHINE (11), MACHINE vs NA (8), ENV vs NA (6), ENV vs MACHINE (1)
- **concern**: FUNCTIONAL vs SPECIFIC-QUALITY (13), CONSTRAINT vs FUNCTIONAL (10), CONSTRAINT vs NA (9), FUNCTIONAL vs PROJECT-PROCESS (8), FUNCTIONAL vs NA (5), CONSTRAINT vs PROJECT-PROCESS (4)

## LLM errors against consensus

- **mood** (human → LLM): INDICATIVE → OPTATIVE (21), OPTATIVE → INDICATIVE (3)
- **locus** (human → LLM): INTERFACE → MACHINE (19), NA → MACHINE (16), ENV → INTERFACE (6), NA → INTERFACE (4), ENV → NA (3), ENV → MACHINE (2)
- **concern** (human → LLM): FUNCTIONAL → CONSTRAINT (20), NA → CONSTRAINT (14), SPECIFIC-QUALITY → FUNCTIONAL (10), NA → PROJECT-PROCESS (4), NA → FUNCTIONAL (3), FUNCTIONAL → SPECIFIC-QUALITY (3)
