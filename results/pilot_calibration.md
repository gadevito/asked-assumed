# Pilot calibration results

Codebook dimensions: D2 mood (Zave & Jackson 1997), D3 locus (WRSPM, Gunter et al. 2000), D4 concern and sub-code (Glinz 2007; ISO/IEC 25010:2023). Cohen's kappa; percentage agreement in brackets.

Humans coded both rounds with codebook v0.2. Round 1 (50 decisions) was completed quickly and is treated as calibration; round 2 used 50 new decisions (no decision or repository in common with round 1). Sampling: stratified by framework × provenance, English only, at most one decision per repository.

## Round 1: human–human agreement (n=50)

| Dimension | A–B as coded (v0.2) | A–B after mechanical v0.3 rules |
| --- | --- | --- |
| mood | 1.00 (100%) | 1.00 (100%) |
| locus | 1.00 (100%) | 0.97 (98%) |
| concern | 0.90 (92%) | 0.92 (94%) |
| subcode | 0.81 (92%) | 0.87 (94%) |

Disagreements: 4 decisions.

| ID | Framework/provenance | Dimension: A vs B |
| --- | --- | --- |
| P20 | gsd/DELEGATED | concern: FUNCTIONAL vs CONSTRAINT; subcode: NONE vs Constraint:design & implementation |
| P24 | gsd/ASSUMED | concern: CONSTRAINT vs PROJECT-PROCESS; subcode: Constraint:design & implementation vs NONE |
| P29 | gsd/ASKED | concern: FUNCTIONAL vs CONSTRAINT; subcode: NONE vs Constraint:design & implementation |
| P44 | bmad/ASSUMED | concern: FUNCTIONAL vs CONSTRAINT; subcode: NONE vs Constraint:interface |

Sub-code agreement when concern agrees: 11/11.

## Round 2: human–human agreement (n=50)

| Dimension | A–B as coded (v0.2) | A–B after mechanical v0.3 rules |
| --- | --- | --- |
| mood | 1.00 (100%) | 1.00 (100%) |
| locus | 0.88 (92%) | 0.91 (94%) |
| concern | 0.78 (84%) | 0.81 (86%) |
| subcode | 0.67 (86%) | 0.71 (86%) |

Disagreements: 12 decisions.

| ID | Framework/provenance | Dimension: A vs B |
| --- | --- | --- |
| P03 | speckit/ASSUMED | concern: CONSTRAINT vs FUNCTIONAL; subcode: Constraint:design & implementation vs NONE |
| P04 | gsd/DELEGATED | locus: ENV vs MACHINE |
| P07 | gsd/ASKED | concern: FUNCTIONAL vs CONSTRAINT; subcode: NONE vs Constraint:design & implementation |
| P09 | bmad/ASSUMED | locus: ENV vs INTERFACE |
| P12 | gsd/ASKED | concern: FUNCTIONAL vs SPECIFIC-QUALITY; subcode: NONE vs ISO25010:safety |
| P14 | bmad/ASSUMED | locus: MACHINE vs INTERFACE |
| P22 | speckit/ASKED | concern: FUNCTIONAL vs CONSTRAINT; subcode: NONE vs Constraint:design & implementation |
| P29 | gsd/ASKED | concern: FUNCTIONAL vs PERFORMANCE |
| P38 | gsd/DELEGATED | concern: CONSTRAINT vs SPECIFIC-QUALITY; subcode: Constraint:design & implementation vs ISO25010:interaction capability |
| P42 | gsd/DELEGATED | concern: CONSTRAINT vs SPECIFIC-QUALITY; subcode: Constraint:design & implementation vs ISO25010:interaction capability |
| P43 | speckit/ASKED | locus: MACHINE vs INTERFACE |
| P44 | speckit/ASSUMED | concern: PERFORMANCE vs CONSTRAINT; subcode: NONE vs Constraint:design & implementation |

Sub-code agreement when concern agrees: 9/9.

## LLM model selection

Round 1 was used to develop the prompt (dev set); round 2 was held out as test set and coded once with the frozen prompt. Human labels are compared after the mechanical v0.3 rules, because the LLM prompt implements v0.3.

| Round | Configuration | Prompt | n | mood | locus | concern | sub-code | failed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | gpt-oss-120b, constrained JSON, effort medium | v0.3 | 50 (consensus 47) | 0.43 / 0.43 / **0.43** | 0.57 / 0.54 / **0.55** | 0.57 / 0.49 / **0.54** | 0.59 / 0.49 / **0.57** | 0 |
| 1 | gpt-oss-120b, free reasoning, effort medium | v0.3 | 50 (consensus 47) | 0.43 / 0.43 / **0.43** | 0.57 / 0.55 / **0.55** | 0.54 / 0.47 / **0.52** | 0.58 / 0.48 / **0.56** | 0 |
| 1 | gpt-oss-120b, free reasoning, effort high | v0.3 + indicative cues | 50 (consensus 47) | 0.58 / 0.58 / **0.57** | 0.57 / 0.54 / **0.54** | 0.59 / 0.51 / **0.57** | 0.64 / 0.53 / **0.62** | 0 |
| 1 | Qwen3.6-35B-A3B, free reasoning, effort high | v0.3 + indicative cues | 50 (consensus 47) | 0.77 / 0.77 / **0.76** | 0.70 / 0.67 / **0.69** | 0.73 / 0.65 / **0.72** | 0.72 / 0.61 / **0.71** | 0 |
| 1 | Qwen3.8-27B, free reasoning, effort xhigh | v0.3 + indicative cues | 50 (consensus 47) | 0.78 / 0.78 / **0.78** | 0.85 / 0.82 / **0.84** | 0.79 / 0.76 / **0.80** | 0.80 / 0.76 / **0.82** | 0 |
| 2 | gpt-oss-120b, constrained JSON, effort medium | v0.3 | 50 (consensus 42) | 0.26 / 0.26 / **0.24** | 0.41 / 0.40 / **0.40** | 0.34 / 0.47 / **0.45** | 0.26 / 0.36 / **0.38** | 0 |
| 2 | Qwen3.8-27B, free reasoning, effort xhigh (selected) | v0.3 + indicative cues | 48 (consensus 40) | 0.83 / 0.83 / **0.82** | 0.72 / 0.75 / **0.77** | 0.63 / 0.78 / **0.79** | 0.62 / 0.79 / **0.84** | 2 |

Cells: kappa vs A / vs B / **vs consensus** (items where A and B agree on all dimensions). Threshold: 0.70.

Failed items on the test set (timeouts in long reasoning) were P30 and P39; the full run retries such items once at effort medium.
