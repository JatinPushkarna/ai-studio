# Post-Processing Engine (Editor)

Long-running compute (Render-style) - a LangGraph stateful loop running the six-step pipeline (interpretation -> generation -> sfx_selection -> assembly -> rendering -> finalizing). See `../../AI_Studio_PRD.md` Section 5.

Polyglot service: the orchestration/business logic (pipeline steps, MCP tools, API layer) is Python. `remotion/` is a separate Node/TypeScript Remotion project - Remotion has no Python runtime, so the `generation` step's LLM-written component code (React/JSX) and the actual render both live there. This is the one place the "Python monorepo" framing has a necessary exception.

No feature code yet - foundation scaffold only, Week 5 Day 1.

## Local dev

Python side, from repo root: `uv sync`, then `uv run --package post-processing-engine <command>`.
Remotion side: `cd remotion && npm install`.
