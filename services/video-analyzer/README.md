# Video Analyzer

Serverless-shaped. Intermediate step between Script Engine and Post-Processing Engine - transcribes uploaded footage and semantically matches it to script beats (minor-drift tolerant only; reordering/omission/ad-libbing out of scope for v1, surfaced as unmatched rather than resolved). No user-facing name - backend only. See `../../AI_Studio_PRD.md` "Video Analyzer (Prerequisite for Editor)" section.

No feature code yet - foundation scaffold only, Week 5 Day 1.

## Local dev

From repo root: `uv sync`, then `uv run --package video-analyzer <command>`.
