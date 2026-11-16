# Asked or Assumed?

Replication package for *Asked or Assumed? How Coding Agents Allocate Requirements Decisions in
Spec-Driven Development* (Registered Report, Stage 1). It contains the instruments, the pilot
analysis scripts, the annotation workbooks, and the pilot results.

## Research questions
- **RQ1** How are recorded requirements decisions allocated between developers and agents? (H1)
- **RQ2** What kinds of requirements decisions are asked, delegated, and assumed? (H2; exploratory estimates)
- **RQ3** How is the developer's choice associated with the order and labelling of the options the agent proposes? (H3, H4)

## Frameworks and artifacts
| Framework | Artifacts analysed |
|---|---|
| GitHub Spec Kit | `specs/*/spec.md` (`## Clarifications`, `## Assumptions`, `[NEEDS CLARIFICATION]`) |
| GSD (get-shit-done) | `.planning/phases/*/NN-CONTEXT.md`, `NN-DISCUSSION-LOG.md`, `NN-RESEARCH.md` |
| BMAD-METHOD | `_bmad-output/**/prd.md`, `SPEC.md`, `.memlog.md` |

## Layout
```
crawl/
  codebook.md          coding scheme v0.3.2 (D1 provenance, D2 mood, D3 locus, D4 concern)
  tool-survey.md       survey of SDD frameworks and their decision artifacts
  crawl.py             GitHub code search -> quality filters -> one artifact unit per repository
  crawl_rq3.py         GSD discussion logs for RQ3
  lang.py              English-language filter
  extract.py           artifacts -> decisions with provenance (D1); RQ3 option-table parser (frozen)
  gsd_attribution.py   GSD units settled by the agent (auto mode), kept apart for H2/RQ2
  rq3.py               RQ3 option blocks -> data/rq3_blocks.jsonl
  rq3_pools.py         RQ3 attribution, exclusions, and the H4 test (shared by all RQ3 scripts)
  rq3_presentation.py  pilot figures for H3, H4, and the agent-answered diagnostic
  power_sim.py         power and type-I error of the H1 and H4 tests, simulated on pilot data
  coding_prompt.py     frozen prompt and JSON schema for model pre-coding (D2-D4)
  llm_code_local.py    model pre-coding with an open-weight model served by vLLM (temperature 0)
  build_pilot.py, build_validation.py, build_adjudication.py, build_rq3_check.py
                       blinded annotation workbooks and keys
  agreement.py, pilot_report.py, validation_report.py, score_rq3_check.py, analysis_prelim.py
                       agreement, reports, extractor scoring, preliminary tables
pilot/                 feasibility pilot scripts
annotation/            annotation workbooks, keys, and adjudications
  pilot_*              two calibration rounds (annotators A and B)
  validation_*         final validation sample and adjudication
  rq3_extractor_check_v4.xlsx, rq3_v4_in/, rq3_check_v4_key.json, rq3_v4_adjudication.json
                       held-out check of the frozen RQ3 extractor (60 questions)
results/               pilot calibration, validation, power simulation, auto-settled GSD units
```

## Data
- `crawl/data/artifacts/{speckit,gsd,bmad}/`: one crawled artifact unit per repository (pilot crawl)
- `crawl/data/candidates_*.jsonl`, `repos.json`: code-search candidates and repository metadata
- `crawl/data/decisions.jsonl`: extracted decisions with provenance (D1)
- `crawl/data/gsdlogs.jsonl`, `rq3_blocks.jsonl`: GSD discussion logs and parsed option blocks (RQ3, frozen extractor)
- `crawl/data/llm_*.jsonl`: model pre-coding outputs (pilot comparisons and full run)
- `pilot/*.json`: feasibility pilot samples

The artifacts are excerpts of public GitHub repositories, redistributed for research purposes only;
they remain under the licenses of their respective repositories and are not covered by this package's licenses.

## Reproduce
Requires Python 3.12 and `pip install -r requirements.txt`.
```bash
cd crawl
export GITHUB_TOKEN=...          # GitHub token for code search
python3 crawl.py
python3 crawl_rq3.py && python3 rq3.py
python3 extract.py
python3 gsd_attribution.py
python3 rq3_presentation.py
SIMS=500 python3 power_sim.py
export VLLM_API_KEY=...          # key of the vLLM endpoint
python3 llm_code_local.py all --url http://localhost:8000 --free --model qwen3.8-27b --effort xhigh --fallback-effort medium
```
Sampling is seeded (`SEED = 20261019`); pilot crawl date 2026-10-19. `build_rq3_check.py` excludes
repositories used in earlier, non-published extractor checks, so regenerating the v4 sheet requires
the repository list in `annotation/rq3_check_v4_key.json`.

## License
Code: MIT (`LICENSE`). Codebook (`crawl/codebook.md`) and annotations (`annotation/`): CC BY 4.0 (`LICENSE-CC-BY-4.0`).
