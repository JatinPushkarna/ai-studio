# AI Studio — Project Law

This file governs every Claude Code session in this repo. Read it before proposing anything.

## Source of Truth

- `AI_Studio_PRD.md` and `description_chain.md` are the source of truth for product and technical decisions. Together they define what gets built and why.
- `Builders_Toolkit_Delegation_Plan.md` governs *how* decisions get made between Jatin and Claude — see Delegation Model below.
- **If a proposal contradicts either document, stop and flag it before proceeding.** Amend deliberately (with Jatin's explicit sign-off on which document changes and why) or conform — never silently pick one interpretation and move on. This applies even when the contradiction is between the two source documents themselves, not just between a new proposal and the docs.

## Naming Convention

| User-facing (UI copy only) | Internal / technical (code, commits, PRs, docs) |
|---|---|
| Writer | Script Engine |
| Editor | Post-Processing Engine |
| — | Video Analyzer (no user-facing name) |

Never let "Writer" or "Editor" leak into code identifiers, service names, schema fields, or internal technical docs. Never use "Script Engine" / "Post-Processing Engine" in user-facing UI copy.

## v1 Scope Boundaries

The following are deliberately out of v1 scope (see PRD "Explicitly Out of Scope for v1"). None of these get implemented without an explicit scope-change conversation, justified against the PRD — not assumed, not quietly added because it seemed useful:

- **No live trend search** — topic suggestions use only RAG-retrieved past scripts and general subject relevance.
- **No automated Editor quality eval or retry loop** — visual/audio quality is manually reviewed by the creator; no scored rubric, deliberately (judged too subjective to trust yet).
- **No background music** — no case was made for it during scoping.
- **SFX no-match fallback is explicitly undefined for v1** — do not invent behavior here. If a beat has no appropriately-tagged SFX, that gap should surface as a known gap, not a silently-decided default.

Other out-of-scope items worth remembering: retake/pause removal, live iterative co-writing as a separate mode (folded into chat refinement), Instagram performance feedback loop, standalone resolution/aspect-ratio reformatting (folded into Editor's render config).

## Delegation Model

From `Builders_Toolkit_Delegation_Plan.md` — this shapes *how* Claude should operate here, not just what to build:

- **Architecture decisions** (e.g. LangChain vs. LangGraph split, RAG store choice, MCP scope, workspace/deploy tooling) — **Augmentation, low-agency.** Jatin is learning; Claude proposes and teaches the reasoning, Jatin reviews and accepts as understanding grows. Don't assume silent agreement — surface the reasoning explicitly, every time, even if it feels repetitive.
- **Implementation decisions** (e.g. exact RAG query shape, whether a field is relevance-gated in a specific prompt, schema field structure) — **Augmentation, high-agency.** Jatin actively drives these. Claude assists, but pushback from Jatin is the expected default here, not friction to route around or a sign something went wrong.
- The distinguishing question when in doubt: is this a big, mostly-one-time structural call Jatin doesn't yet have standing to independently contest (Architecture), or a repeated micro-decision within an already-accepted foundation where Jatin is actively co-shaping the outcome (Implementation)?

## Coaching Stance

Jatin has explicitly asked to be coached like a PM-builder, not hand-held:

- Push back when a request is vague — ask what problem it actually solves before proposing an implementation.
- Demand justification for scope changes against the PRD; don't let scope creep in through a casual aside.
- No hand-waving past a decision, no softening feedback to be agreeable.
- When multiple documents or a document and a proposal disagree, say so plainly and specifically — don't average them into a vague middle position.

## Workflow: Explore → Plan → Code → Commit

- **Explore** — read the relevant PRD/`description_chain.md` sections and existing code before proposing changes. Use read-only search for anything broader than a single known file.
- **Plan** — for anything non-trivial, use plan mode: produce a concrete plan, get explicit review, resolve open questions with Jatin (including AskUserQuestion for genuine judgment calls the docs don't settle) before writing any code.
- **Code** — implement only what the approved plan describes. No feature code without an approved plan beyond genuinely trivial fixes.
- **Commit** — never commit without being explicitly asked, even after a plan is approved and code is written. When asked, follow standard git hygiene: readable messages, no unrelated changes bundled in, review `git status`/`git diff` before staging.

## Repo Structure

```
services/script-engine/            Writer — serverless-shaped (LangChain generation chain + stateful chat refinement)
services/video-analyzer/           intermediate step, no user-facing name — serverless-shaped
services/post-processing-engine/   Editor — long-running compute, LangGraph stateful loop
  └── remotion/                   separate Node/TypeScript Remotion project (Remotion has no Python runtime —
                                    this is the one deliberate polyglot exception; orchestration stays Python)
shared/schemas/                    ai_studio_schemas — canonical Pydantic models (Script, VideoAnalyzerOutput,
                                    Composite, profiles, feedback). One shared source of truth for the schemas
                                    that must converge across generation/Structuring Step paths and flow
                                    Script Engine → Video Analyzer → Editor once, not be re-derived per service.
docs/acceptance_tests/             per-service acceptance tests, given/when/then, each traceable to a PRD section
```

## Tooling Conventions

- **`uv` workspace** — root `pyproject.toml` declares `[tool.uv.workspace] members = ["services/*", "shared/*"]`. `uv sync` from repo root builds one `.venv` covering all three services + `shared/schemas` (installed editable), so schema edits are immediately visible everywhere without a manual reinstall. Each service keeps its own `pyproject.toml` and stays independently deployable — the workspace is a local-dev convenience, not a deploy-time coupling.
- **Workspace-lockfile risk, and its mitigation (both required, not optional):**
  1. **Pin exact dependency versions** in each service's own `pyproject.toml` (e.g. `pydantic==2.10.4`, not `>=2.5`) — a version range left open is exactly what would let a deploy-time resolver silently land on something never tested locally.
  2. **Deploy from a scoped export of the workspace lock** (`uv export --package <service>`), never a fresh independent resolve — what ships must be provably the exact version set tested in the shared local `.venv`, not a re-derived guess.
- Python 3.12 across all services (default — flag if this needs to change, it's a one-line fix in each `pyproject.toml`).

## Acceptance Tests

Live in `docs/acceptance_tests/*.md`, one file per service, given/when/then format, each traceable to a specific PRD (or `description_chain.md`) section. Drafted for Jatin to review and challenge — not committed as final until he has done so. When PRD/spec behavior changes, the corresponding acceptance test must be updated in the same change, not left stale.
