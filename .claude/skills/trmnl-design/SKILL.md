---
name: trmnl-design
description: >-
  Designs visually polished, TRMNL-friendly plugin screens with minimal layout
  bugs: e-ink readability, correct TRMNL structure, stable layouts, hierarchy,
  and maintainable markup. Use when editing or authoring TRMNL plugin markup,
  Liquid/HTML templates, private plugin screens, marketplace screen layouts,
  charts on TRMNL, or CSS/JS that affects TRMNL display output.
---

# TRMNL design

Specialist guidance for TRMNL plugin screens that look good and fail gracefully on e-ink.

## Priority order

1. Readability on e-ink.
2. Correct TRMNL-compatible structure.
3. Stable rendering across layouts.
4. Clean visual hierarchy.
5. Minimal, maintainable code.

## Source of truth

Use TRMNL documentation and native patterns first. Exact links: [reference.md](reference.md).

If official docs and local code disagree, prefer official docs unless the repo explicitly documents a local exception.

## Core design principles

Every screen must be:

- Instantly scannable.
- Balanced, not crowded.
- High contrast.
- Calm and structured.
- Useful from a distance.
- Safe for e-ink rendering.

Design for a **7.5" e-ink** mindset: fewer elements, larger groupings, short labels, obvious hierarchy, no decorative clutter.

## Visual style

**Prefer:** one dominant focal point; 2–4 content zones max; consistent spacing rhythm; strong alignment; short text blocks; simple dividers; monochrome-friendly contrast; understated styling.

**Avoid:** dense dashboards; tiny helper text; overly clever layouts; excessive borders; too many icons; unnecessary inversion; low-contrast gray-on-gray; long paragraphs; decorative noise; fragile pixel hacks.

## Typography

Use type for hierarchy, not decoration.

**Always:** make the primary value or title obvious first; short line lengths; labels shorter than values when possible; consistent heading/body patterns; trim copy aggressively.

**Avoid:** more than three apparent text sizes on one screen; all-caps for long blocks; multiple competing bold areas; wrapping-prone labels when a shorter word works.

## Layout

**Compose in this order:** start with the single most important insight; add only supporting context; group related items; use whitespace as structure; keep left/right and top/bottom balance intentional; prefer predictable vertical stacking over deep nesting.

**Default vertical rhythm:** top — title or context; middle — primary metric, summary, list, or chart; bottom — secondary metadata or timestamp.

**If it feels busy:** remove elements before resizing; shorten text before adding containers; split an overloaded screen into multiple layouts when the product supports it.

## TRMNL-specific markup

- Prefer TRMNL framework and documented conventions first.
- Do not invent undocumented wrappers, fields, or rendering guarantees.
- Keep DOM depth shallow.
- For private plugins: use shared markup for repeated CSS/JS/resources; reuse partials instead of duplicating blocks.
- When adapting native plugin markup: use official examples and demo output as baseline; convert ERB-style references to Liquid in custom templates; infer real data shape from demos before redesigning.

## Charts and graphics

TRMNL may allow inline styling and libraries (e.g. Highcharts/Chartkick) where documented, but output must stay e-ink-friendly.

**Use a chart only when it is clearly better than:** a single metric, a delta, a compact list, or a small table.

**For charts:** drop unnecessary legends when labels can be direct; remove chart junk; avoid heavy gridlines and tiny axis labels; favor simple line/bar layouts; short titles; grayscale legibility; do not add a chart just because the data is numeric.

If a chart looks technical but ugly, simplify or replace it.

## Reliability

**Always handle:** empty states; missing values; long strings; zero-length lists; API failure; stale timestamps; fallback markup that still looks intentional.

**Never assume:** data exists; text is short; arrays have items; image URLs load; third-party scripts succeed; a plugin has only one layout forever.

## Error-prevention checklist

Before finishing a TRMNL screen task, verify:

1. No undocumented TRMNL behavior was assumed.
2. Markup has a valid root structure for the intended TRMNL flow.
3. Long text cannot destroy the layout (truncation, clamp, or transform).
4. Empty data has a graceful state.
5. Important numbers and labels stay readable.
6. Styling fits monochrome e-ink constraints.
7. Repeated code is extracted when shared markup/templates exist.
8. The design still works if one section is missing.
9. Any JS/chart dependency is necessary, not decorative.
10. The screen is understandable at a glance in under ~3 seconds.

## Task workflow (interaction style)

1. Inspect existing repo files and patterns first.
2. State the intended information hierarchy in 1–3 bullets.
3. Propose a compact layout before coding.
4. Implement the smallest clean solution.
5. Check visual and data edge cases.
6. Summarize why the result is both attractive and stable.

## Preferred character

**Should feel:** editorial, minimal, calm, deliberate, crisp, glanceable.

**Should not feel:** web-app-like, cramped, gimmicky, over-styled, experimental at the expense of clarity.

## When data is weak

Simplify the design; promote the most trustworthy metric; reduce modules; show a tasteful fallback; never fill space with fake complexity.

## Refactoring rule (“make it prettier”)

1. Improve hierarchy first.  
2. Spacing second.  
3. Grouping third.  
4. Styling last.  

Do not start by adding more visual elements.

## Final constraint

The best TRMNL plugin screen is not the one with the most features. It is the one that communicates the right information, clearly and reliably, on an e-ink display.

## Relationship to other skills

If the task is full plugin lifecycle, webhooks, `plugin_data`, BYOS, or API integration, combine this skill with the project’s TRMNL implementation skill. This skill focuses on **visual and structural quality** of screens and markup.