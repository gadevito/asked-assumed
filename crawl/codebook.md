# Codebook v0.3.2 — "Asked or Assumed?"

Normative version for the registered report (Stage 1). Where this file and the paper differ, this file is updated to match the paper; v0.3.2 aligns D1, D5, and the coding protocol with the paper's Sections 4–8.

Principle: every hand-coded dimension is grounded in an established, citable RE construct. Where the original construct does not cover SDD decisions, we state our operationalization explicitly. The table separates what is adopted from what is ours.

| Dimension | Adopted from the source (verified against the original text) | Our operationalization |
|---|---|---|
| D2 Mood | Zave & Jackson 1997, §2: indicative statements describe the environment "as it is in the absence of the machine or regardless of the actions of the machine"; optative statements describe it "as we would like it to be"; NAT constraints are imposed "by nature and previously installed systems". | (a) OPTATIVE extended to design decisions about machine internals, which Zave & Jackson leave out ("describing the environment in the optative mood makes it unnecessary to describe the machine"); cf. descriptive vs prescriptive statements in van Lamsweerde 2009. (b) Explicit list of indicative cues for existing machines in the environment. |
| D3 Locus | Gunter, Gunter, Jackson & Zave 2000: phenomena e = eh ∪ ev, s = sv ∪ sh; W and R use eh, ev, sv; P and M use sh, sv, ev; S is restricted to ev and sv. | Three codes derived from which phenomena a decision refers to (precedence MACHINE > ENV > INTERFACE, see D3). |
| D4 Concern | Glinz 2007, Table 3 classification questions (applied in order); constraint kinds physical, legal, cultural, environmental, design & implementation, interface (Fig. 2); project and process requirements distinguished at the root level (§4.2). | Glinz's open list of "-ilities" replaced by the ISO/IEC 25010:2023 characteristics as sub-codes. |
| R1–R5 | — | Boundary rules written by us from pilot disagreements, each justified by the sources above. |

Unit of analysis: one **recorded decision** = one item as the template records it: one Q→A line, one list item, one assumptions-log row, one inline marker or tag, one discussion-log option question. Items are neither split nor merged. Items in different sections are counted as recorded (a documentary counting rule, not a deduplication), so an assumption confirmed by a later clarification can be counted under both (pilot: about 11 such pairs in 10 of the 118 Spec Kit specifications with at least one asked or assumed decision, lexical match). BMAD inline tags are counted only when no assumptions index exists.

## D1 — Provenance (derived automatically from the artifact section; not hand-coded)

| Code | Definition | Spec Kit | GSD | BMAD |
|---|---|---|---|---|
| ASKED | Agent asked; human's answer recorded | `## Clarifications` Q→A | `CONTEXT.md` `## Implementation Decisions` (settled in the discussion) | — |
| DELEGATED | Human handed the choice back to the agent | — | `CONTEXT.md` `### Claude's Discretion` | — |
| ASSUMED | Agent chose without asking | `## Assumptions` | `RESEARCH.md` `## Assumptions Log` (`[ASSUMED]`) | `[ASSUMPTION: …]`, `## 9. Assumptions Index`, SPEC `## Assumptions`, `.memlog.md` `(assumption)` |
| OPEN | Recorded as unresolved (described; enters no hypothesis) | residual `[NEEDS CLARIFICATION: …]` | `RESEARCH.md` `## Open Questions` | `## 8. Open Questions`, SPEC `## Open Questions`, `.memlog.md` `(question)` |
| SETTLED | Decision without recorded author (not analysed) | — | — | `.memlog.md` `(decision)` |

GSD **auto-settled** units (header of CONTEXT.md or DISCUSSION-LOG.md declares an automatic mode, or every discussion-log answer is the agent's; see `gsd_attribution.py`): their Implementation Decisions and Discretion items are neither ASKED nor DELEGATED and are reported separately (pilot: 14 units, 188 + 36 records, all checked by hand).

GSD `## Deferred Ideas` postpone scope and are not open decisions; they are not analysed (the frozen pilot extraction labelled them OPEN, which no analysis uses).

GSD discussion logs (`DISCUSSION-LOG.md`) feed RQ3 only. There, an answer is the developer's unless the log declares auto mode, carries `[auto]`, or the answer says the agent chose it ("Auto-selected …"); "you decide" answers are hand-backs (see `rq3_pools.py` and the annotation guide of the extractor check).

Section semantics are taken verbatim from each tool's template (sources in `tool-survey.md`).

## D2 — Mood (after Zave & Jackson 1997, *Four Dark Corners of RE*, TOSEM; extended, see table)

- **INDICATIVE** — states how the world is, independent of the machine (domain knowledge / assumption *W*). E.g. "Users have a stable internet connection."
- **OPTATIVE** — states what the system should be or do (requirement *R* or specification *S*), or a choice about the system. E.g. "Sessions expire after 30 minutes."

Test: would the statement remain true if the system were never built? → INDICATIVE.
INDICATIVE also covers properties of machines already in the environment (Zave & Jackson: NAT constraints imposed "by nature and previously installed systems"): behaviour or availability of external services, APIs, models, third-party libraries and tools; facts about existing code, data, infrastructure or capacity; expectations about users, markets or competitors — even when phrased with "will" or "should".
Rationale: an SDD "assumption" may be domain knowledge (legitimate *W*) or a silent requirement decision (*R*). Only OPTATIVE assumptions count as agent-made requirements decisions in RQ2.

## D3 — Locus (Gunter, Gunter, Jackson & Zave 2000, *A Reference Model for Requirements and Specifications*, IEEE Software — WRSPM)

Only for OPTATIVE decisions. PROJECT-PROCESS decisions (D4) take locus NA.
Decide by the phenomena the decision refers to, with precedence MACHINE > ENV > INTERFACE:
- **MACHINE** — refers to any phenomenon hidden inside the machine (sh): internal architecture, libraries, data structures, algorithms, internal configuration. Only P and M can mention sh → program/design (solution space).
- **ENV** — otherwise, refers to any environment phenomenon hidden from the machine (eh), e.g. goals, business rules about domain entities, outcomes in the world. Only W and R can mention eh → requirement *R*. (Consistent with R4.)
- **INTERFACE** — otherwise, refers only to shared phenomena (ev, sv): inputs, outputs, UI behaviour, API contracts, signals to other programs or devices. These are exactly the terms S may use → specification *S*.

Test: can an observer outside the machine check the decision without seeing the code? No → MACHINE.

## D4 — Concern (Glinz 2007, *On Non-Functional Requirements*, RE'07 — concern-based taxonomy)

Only for OPTATIVE decisions. Apply Glinz's classification questions in order:
1. Stated to specify system behaviour, data, input, or reaction to stimuli? → **FUNCTIONAL**
2. Stated because of timing, processing/reaction speed, data volume, or throughput? → **PERFORMANCE**
3. Stated to specify a specific quality the system or a component shall have? → **SPECIFIC-QUALITY** (sub-code with ISO/IEC 25010:2023 characteristic: functional suitability, performance efficiency, compatibility, interaction capability, reliability, security, maintainability, flexibility, safety)
4. Any other restriction on what the system does or how, or a prescribed solution element? → **CONSTRAINT** (sub-code per Glinz: physical, legal, cultural, environmental, design & implementation, interface)
5. About the project or development process rather than the system (testing strategy, CI, phasing, conventions) → **PROJECT/PROCESS** (Glinz's project/process requirements; outside system requirements)


## Boundary rules (added in v0.3 after pilot round 2; each derives from the adopted frameworks)

- **R1 MACHINE ⇒ solution space.** An OPTATIVE decision with locus MACHINE refers only to phenomena hidden in the machine; by WRSPM it is not a requirement on the environment, and by Glinz's definition it restricts the solution space. Code concern = CONSTRAINT (design & implementation) unless it is PROJECT-PROCESS. FUNCTIONAL, PERFORMANCE and SPECIFIC-QUALITY require locus ENV or INTERFACE.
- **R2 Stated rationale decides the concern.** Glinz classifies by the concern a requirement was *stated because of*. When the text gives an explicit reason ("for zero overhead", "to protect the hardware", "looks premium"), use it for D4 (subject to R1).
- **R3 External parties include software and files.** INTERFACE covers phenomena shared with users *and* with other programs, processes, devices or user-edited files (signals sent to a child process, a file format users author, motor commands). Use MACHINE only when nothing outside the machine can observe the decision.
- **R4 Business rules are ENV.** A rule about domain entities (candidates, invoices, orders) is ENV even if its effect is later displayed; code INTERFACE only when the decision is about the display or interaction itself.
- **R5 Delegated topic labels.** A DELEGATED item that names a topic without a value is coded by the concern of the topic (e.g., visual look → SPECIFIC-QUALITY, interaction capability).

## D5 — Choice behaviour (GSD discussion logs, RQ3; derived automatically; normative reading rules in the Guide sheet of `annotation/rq3_extractor_check_v4.xlsx`)

- **REC-ACCEPTED** selected option = option marked recommended
- **ALT-OPTION** another listed option selected
- **FREE** answer outside listed options
- **N/A** no option table, or no option marked recommended

## Derived analysis variables (no extra coding)

- *Solution-space decision* = OPTATIVE ∧ (MACHINE ∨ CONSTRAINT:design&implementation)
- *High-stakes decision* = SPECIFIC-QUALITY:{security, safety} ∨ CONSTRAINT:legal

## Coding protocol (as pre-registered; paper Sections 7–8)
1. Calibration (pilot, done): two rounds of 50 decisions coded by both annotators blind to framework and provenance; boundary rules R1–R5.
2. The model (frozen prompt and weights) codes all decisions; model labels enter only the corrected RQ2 estimates.
3. Both annotators independently code (a) the H2 sample: 150 delegated and 150 answered GSD decisions, at most two per repository; (b) the RQ2 sample: a simple random subset of 66 decisions within each framework × provenance stratum. Disagreements are adjudicated jointly with a written rationale.
4. Cohen's κ per dimension must reach 0.70. If not, the guidelines are revised once, a new sample of the same size is coded, and both rounds are reported; H2 uses the final adjudicated labels and is reported as inconclusive if κ stays below 0.70.
5. Model–human agreement (κ, and Gwet's AC1 where prevalence is extreme) is reported; it gates no test. Model labels are never used without the prediction-powered correction.

## References
- A. van Lamsweerde. Requirements Engineering: From System Goals to UML Models to Software Specifications. Wiley, 2009 (descriptive vs prescriptive statements).
- J. Eckhardt, A. Vogelsang, D. Méndez Fernández. Are "non-functional" requirements really non-functional? ICSE 2016 (critique relevant to D4).
- P. Zave, M. Jackson. Four Dark Corners of Requirements Engineering. ACM TOSEM 6(1), 1997. (Scopus: 544 citations)
- C. A. Gunter, E. L. Gunter, M. Jackson, P. Zave. A Reference Model for Requirements and Specifications. IEEE Software 17(3), 2000. (191)
- M. Glinz. On Non-Functional Requirements. RE 2007. (574)
- ISO/IEC 25010:2023 Product quality model.
- ISO/IEC/IEEE 29148:2018 — "implementation free" characteristic; used by EPIC (Claudino et al., 2026) for "Scope Discipline".
