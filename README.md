# AI Studio

From idea to publish-ready content in minutes.

Monorepo for three independently deployable services — Script Engine (Writer), Video Analyzer, Post-Processing Engine (Editor) — connected by plain service-to-service API calls, per `description_chain.md`.

## Source of truth

- `AI_Studio_PRD.md` — product requirements, feature specs, schemas
- `description_chain.md` — technical shape, pipeline flow, MCP scope
- `Builders_Toolkit_Delegation_Plan.md` — how build decisions get made
- `CLAUDE.md` — project law for every Claude Code session in this repo

## Structure

```
services/script-engine/            Writer — serverless-shaped
services/video-analyzer/           intermediate step, no user-facing name — serverless-shaped
services/post-processing-engine/   Editor — long-running compute (+ remotion/ Node project)
shared/schemas/                    ai_studio_schemas — canonical Pydantic models
docs/acceptance_tests/             per-service acceptance tests, given/when/then, traceable to PRD
```

## Local dev

`uv sync` from repo root — one `.venv` covering all three services + the shared schema package (editable, so schema edits are visible everywhere immediately). Each service still has its own `pyproject.toml` and stays independently buildable/deployable — see `CLAUDE.md` for the workspace/deploy conventions.

Post-Processing Engine also has a separate Node/TypeScript Remotion project under `services/post-processing-engine/remotion/` — `cd` there and `npm install` for that side.

## Status

Week 5, Day 1 — foundation only (repo scaffold, project law, draft acceptance tests). No feature code yet.
