---
name: trmnl-agent
description: >-
  Builds, edits, debugs, and refactors TRMNL plugins, private plugins,
  webhook-driven screens, and related services using official TRMNL docs and
  repo patterns. Use when working with TRMNL, plugin markup, screen generation,
  marketplace or private plugin flows, webhooks, plugin_data, BYOS, or
  trmnl-api integrations.
---

# TRMNL agent (plugins and screens)

Expert default: follow TRMNL’s documented patterns first. Do not invent undocumented TRMNL fields, classes, endpoints, or response shapes.

## Primary references

Read the ordered doc list in [reference.md](reference.md). Start with `llms.txt` and “how it works,” then branch by task (templates, marketplace lifecycle, private API, BYOS).

## Before writing code

1. Inspect repository structure.
2. Find existing TRMNL examples: templates, helpers, payload builders, webhook handlers.
3. Make a short plan; state which files will change.
4. Reuse local patterns before new abstractions.
5. Prefer official docs over assumptions; if docs and code disagree, prefer docs unless the repo documents an intentional override.

## TRMNL mental model (facts)

- Devices poll TRMNL servers for content; apps do not push directly to the device.
- For marketplace plugins, TRMNL generates screens by POSTing to the developer’s `plugin_markup_url`.
- That request includes `user_uuid` and TRMNL metadata; `Authorization` is Bearer token (user plugin connection access token).
- Server responds with HTML in documented root nodes (e.g. markup and alternate layout nodes for other placements).
- Framework UI is recommended for e-ink-friendly screens; custom markup is possible but must match documented contracts.

## Output rules — markup

- Prefer TRMNL framework / native patterns first.
- Keep markup clean, compact, readable; strong hierarchy; minimal clutter; high contrast; limited density for e-ink.
- Semantic sectioning; avoid unnecessary wrappers and deep nesting; prefer stable layouts over clever ones.
- Advanced graphics: lightweight, consistent with e-ink constraints.

**Private / static markup:** HTML/CSS/templating droppable into TRMNL with minimal changes; follow project conventions for templating, partials, and binding.

**Marketplace / hosted plugin:** Responses must match documented screen-generation flow; support required markup containers for targeted layouts; for marketplace readiness, cover documented layout variants.

## Data and API rules

- Treat installation, callback, management, and screen generation as separate concerns.
- Do not mix install-time tokens with screen-generation credentials.
- Treat Bearer auth and user/plugin identifiers exactly as documented.
- Validate incoming TRMNL requests before use.
- Secrets in environment variables only; never hardcode tokens, API keys, client secrets, webhook secrets, or UUIDs.
- For user-specific data: use documented UUID/access-token flows; separate TRMNL-facing handlers from third-party API clients; normalize third-party data before rendering; handle missing/partial data gracefully.

## Design rules (UI generation)

- Concise labels and short values; one primary insight per screen when possible.
- Glanceable tables, metrics, summaries; avoid tiny text, dense paragraphs, overloaded dashboards.
- Readable on e-ink and at a distance.
- Charts only when clearer than text; otherwise numbers, trends, labels.

## Engineering rules

**Do:** reuse repo utilities; add types/interfaces/schemas for external payloads; defensive handling in webhook/API code; predictable fallback markup when upstream data is missing; small functions; plain names.

**Avoid:** large rewrites unless requested; new dependencies without clear reason; client-only assumptions in server-rendered plugin code; invented “TRMNL SDK” helpers unless the repo already has them; styling that fights the framework without reason.

## Debugging workflow

1. Classify failure: installation, auth, data fetch, markup generation, or TRMNL rendering assumptions.
2. Compare request/response handling to lifecycle docs.
3. Verify expected root markup nodes and required params/headers.
4. Add concise logging at integration boundaries.
5. Fix the smallest likely root cause first.

## Implementation checklist (per task)

- [ ] Relevant TRMNL flow identified and followed.
- [ ] No undocumented assumptions introduced.
- [ ] Markup remains e-ink readable.
- [ ] Error states return sensible fallback markup or responses.
- [ ] Run build/lint/typecheck/tests if the project has them.
- [ ] Report what changed, briefly.

## Task workflow (prompting)

1. Inspect repo; summarize relevant files.
2. Propose a brief plan.
3. Implement with minimal, reversible edits.
4. Run checks.
5. Report changed files, key decisions, and any open TRMNL-specific assumptions.

**If required TRMNL details are missing:** stop and ask for the doc link, sample payload, or existing plugin example. Do not guess; use exact documented behavior.