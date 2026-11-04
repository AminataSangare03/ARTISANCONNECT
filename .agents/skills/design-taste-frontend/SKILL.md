---
name: design-taste-frontend
description: Taste framework and art direction for frontend interfaces across all tech stacks. Enforces editorial composition, strict anti-slop rules, intentional typography ratios, zero-shadow surface layering, and high-craft aesthetic execution.
---

# Design Taste for Frontend Engineering

A rigorous, evidence-based taste engine for crafting high-grade web interfaces. It prevents coding agents from producing formulaic, generic output and forces intentional art direction across any technology stack (Vanilla HTML/CSS, Tailwind CSS, Bootstrap, React, Vue, Svelte, Blade).

## 1. Core Taste Invariants & Negative Constraints

The following rules apply unconditionally to all generated interfaces:

| Banned Pattern | What to Do Instead |
|---|---|
| **Zero Emojis** in UI code, buttons, headings, tables, labels, or documentation. | Authentic monochrome or themed vector icons (SVG), or clear typography. |
| **No Gradients as Backgrounds or Text Masks** | Crisp flat colors, intentional solid surfaces, or authentic editorial photography. |
| **No Shadows on Rest States** | Separate surfaces with subtle background tone shifts (`#f8fafc` vs `#ffffff`). Reserve elevation shadows strictly for elements that truly float (modals, dropdowns, sticky headers). |
| **No Rows of Identical Feature Cards** | Break the grid: use alternating compositions, structured data lists, side-by-side split panels, or timeline steps. |
| **No Artificial Accent Words** (italicizing or recoloring one word in a headline). | Rely on strong copywriting and clean typography for emphasis. |
| **No Floating Glassmorphism** (backdrop-blur floating pills with translucent white borders). | Use clean, anchored navigation bars with deliberate structural hierarchy. |
| **No Assistant Palettes** (terracotta on beige ground, bright saturated purple on white). | Formulate a custom palette tailored specifically to the project's identity: one primary ground, one sharp ink, and one disciplined accent. |

## 2. Typographic Discipline

- **Scale Ratio**: The largest headline must be at least 3.5x to 4.5x the size of the body text. Modest headline-to-body ratios feel timid and amateur.
- **Display Typography**:
  - Tightly tracked: `letter-spacing: -0.025em` to `-0.04em`.
  - Compressed leading: `line-height: 0.95` to `1.15`.
- **Body Typography**:
  - Sized at 15px to 17px with comfortable leading (`line-height: 1.55` to `1.65`).
  - Strict measure: `max-width: 65ch` (45 to 75 characters per line).
- **Text Color Hierarchy**:
  - Headings & Primary Text: Deep, authoritative ink (e.g. `#0f172a`, `#111827`, `#090d16`). Never use low-contrast grey for primary headlines.
  - Secondary Text: High-contrast slate/neutral (e.g. `#475569`, `#64748b`). Minimum contrast ratio 4.5:1.
  - Muted Metadata: Minimum contrast ratio 3.5:1 with clear labels.

## 3. Spatial Composition & Layout Rhythm

- **Unified Grid**: Align all content blocks to a consistent column grid (4-column mobile, 8-column tablet, 12-column desktop).
- **Vertical Rhythm**:
  - Inside components: Tight spacing (8px, 12px, 16px, 24px).
  - Between major sections: Substantial negative space (80px to 140px on desktop) to let content breathe and establish distinct visual chapters.
- **Asymmetry & Focal Points**: Avoid centering everything. Left-aligned content blocks anchored by a strong structural element create natural scanning flow for the eye.

## 4. Components & Interactive Polish

- **Buttons & CTAs**:
  - Flat solid fill for primary action; clean ghost/outline for secondary.
  - Generous horizontal padding (`px-4 py-2.5` or `0.75rem 1.5rem`).
  - Sharp or disciplined radius (4px, 6px, 8px, or full pill) applied consistently across the application. Avoid mixing random border radii.
- **Form Controls**:
  - Clear label positioned directly above the input.
  - High-visibility focus indicators (`outline: 2px solid var(--accent); outline-offset: 2px;` or subtle ring glow).
  - Inline validation messages with clear iconography and descriptive remedy.
- **Tables & Data Grids**:
  - Monospace or tabular figures for numeric data (`font-variant-numeric: tabular-nums`).
  - Right-align numeric columns; left-align textual data.
  - Subtle hairline borders (`1px solid #e2e8f0`) and subtle zebra striping or hover row highlights.

## 5. Pre-Commit Taste Audit

Before declaring any front-end task complete:
1. Are there any emojis present? Remove every single one.
2. Are there repetitive card grids? Convert at least one into an asymmetrical or editorial layout.
3. Is typography sharply scaled with clear hierarchy?
4. Are interactive elements responsive with instant hover and focus feedback?
5. Does the page scale down cleanly to mobile (375px width) without horizontal overflow or clipped text?
