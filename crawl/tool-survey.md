# SDD framework survey — how decisions are recorded

Checked against the frameworks' source templates on 2026-10-19 (shallow clones; commit or tag in brackets).
Stars from the GitHub API on the same date.

| Framework | Artifacts in user repositories | Asked (Q&A persisted) | Decided without asking | Unresolved | Included |
|---|---|---|---|---|---|
| GitHub Spec Kit [c6a4c18], 141.9k★ | `specs/<feature>/spec.md`, `plan.md`, `research.md`, `tasks.md` | `## Clarifications` → `### Session YYYY-MM-DD` → `- Q: … → A: …` (`/speckit.clarify`, ≤5 questions) | `## Assumptions` ("reasonable defaults") | inline `[NEEDS CLARIFICATION: …]` (≤3 in specify) | yes |
| GSD / get-shit-done [bdcaab2], 64.3k★ | `.planning/phases/NN-slug/NN-CONTEXT.md`, `NN-DISCUSSION-LOG.md`, `NN-RESEARCH.md` | `DISCUSSION-LOG.md`: option table with `Selected`, `**User's choice:**`; `CONTEXT.md` `## Implementation Decisions` | `### Claude's Discretion` (human said "you decide"); `RESEARCH.md` `## Assumptions Log` (`[ASSUMED]`) | `## Open Questions`, `## Deferred Ideas` | yes |
| BMAD-METHOD [61e01f8 / v6.12.0], 54.3k★ | `_bmad-output/**/prd*.md`, `SPEC.md`, `.memlog.md` | not identifiable: `.memlog.md` `(decision)` lines do not record who decided | `[ASSUMPTION: …]`, `## 9. Assumptions Index`, SPEC `## Assumptions` | `## 8. Open Questions`, SPEC `## Open Questions` | yes (assumed/open only) |
| OpenSpec [c794978], 72.4k★ | `openspec/changes/<change>/proposal.md`, `design.md`, `tasks.md` | asks when ambiguity is material; Q&A not persisted | "record it in the planning artifacts", no dedicated heading | `Open Questions` named in schema only | no: provenance not recorded |
| Kiro (closed source; docs only) | `.kiro/specs/<feature>/requirements.md`, `design.md`, `tasks.md` | questions in chat; Q&A not persisted | no documented heading | no documented heading | no: provenance not recorded |
| cc-sdd [e2a0c67], 3.7k★ | `.kiro/specs/<feature>/…` | Q&A not persisted | instructed not to assume | none | no |
| Agent OS v3 [e892e61], 5.5k★ | `agent-os/specs/<date-slug>/shape.md`, `plan.md` | Q&A not persisted | `## Decisions` (not split by who decided) | none | no |
| spec-workflow-mcp [d38e82e], 4.3k★ | `.spec-workflow/specs/<name>/…` | no clarification step (approvals as JSON) | `### Decision Log` | `## Known Limitations` | no |
| Tessl SDD tile [b8fdff7] | `specs/*.spec.md` | Q&A not persisted | none | none | no |

Inclusion criterion: the framework persists, under distinct headings, at least decisions taken without asking and either the human's answers or unresolved items.

## Key template sources
- Spec Kit: `templates/commands/clarify.md`, `templates/spec-template.md`, `templates/commands/specify.md` — https://github.com/github/spec-kit
- GSD: `get-shit-done/workflows/discuss-phase/templates/context.md`, `…/discussion-log.md`, `agents/gsd-phase-researcher.md` — https://github.com/gsd-build/get-shit-done
- BMAD: `skills/bmad-prd/assets/prd-template.md`, `skills/bmad-prd/SKILL.md` (memlog types `decision|change|override|assumption|event`) — https://github.com/bmad-code-org/BMAD-METHOD
- OpenSpec: `schemas/spec-driven/schema.yaml`, `schemas/spec-driven/templates/design.md` — https://github.com/Fission-AI/OpenSpec
- Kiro: https://kiro.dev/docs/specs/
