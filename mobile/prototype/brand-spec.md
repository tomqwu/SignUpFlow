# SignUpFlow · Brand Spec

> Direction: **C — Block-Mono** (Things/Linear-aligned, confident-bold)
> Picked: 2026-05-07
> Source of truth for both this HTML prototype and the future Flutter app.

---

## 🎯 Core Assets

### Wordmark

```
SIGNUP/FLOW
```

- **Form**: All-caps, Inter 700, letter-spacing −0.025em.
- **Slash**: Teal `#0F766E`, Inter 500 weight (intentionally lighter than the letters).
- **Color**: Letters in ink `#18181B` on light surfaces, in cream `#FAFAF9` on dark surfaces. Slash always teal.
- **Minimum size**: 14px high (for status bar / header use).
- **Variants**: stacked (rare), one-line (default).
- **Forbidden**: dropping the slash, italicizing, lowercase, gradient fills, drop-shadow, more than two colors.

### App Icon

- **Form**: Solid teal `#0F766E` rounded square at iOS 22.4% corner-radius.
- **Mark**: White `S` letterform centered, Inter 700, letter-spacing −0.06em.
  - 1024px master: font-size 720px.
  - 128px: font-size 88px.
  - 64px: font-size 44px.
- **No logo lock-up inside the icon** — just the mark.
- **Forbidden**: gradient backgrounds, depth/inner-shadow effects, ornamental swooshes, anything multicolor.

---

## 🎨 Palette

```
Primary  · #0F766E  Teal-700        — accent, brand mark, primary CTAs
Ink      · #18181B  Near-black      — body text, headers, mark on light bg
Cream    · #FAFAF9  Off-white       — page background, cards on dark
Surface  · #FFFFFF  Pure white      — cards, modals on light bg
Line-1   · #E4E4E7  Hairline border — card borders, dividers
Line-2   · #F4F4F5  Soft border     — alternating row tints
Ink-2    · #52525B  Dim text        — secondary copy, captions
Ink-3    · #A1A1AA  Tertiary        — placeholders, hint text
Accent-soft · #CCFBF1  Teal-100     — time chip backgrounds, selection state
Accent-ink  · #134E4A  Teal-900     — text on accent-soft backgrounds
Success     · #15803D  Green-700    — confirmed states, additions in diffs
Warning     · #B45309  Amber-700    — pending, conflicts
Danger      · #B91C1C  Red-700      — declined, removed in diffs, destructive
Dark-bg     · #18181B                — dark mode page bg (system pref)
Dark-surface · #27272A               — dark mode cards
```

**Forbidden**: purple gradients, multicolor icons, pastel-pink anything, neon, more than one accent color in a single screen.

---

## ✏️ Typography

### Stack

```css
--font-display: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
--font-body:    'Inter', -apple-system, system-ui, sans-serif;
--font-mono:    'JetBrains Mono', 'SF Mono', ui-monospace, monospace;
```

In Flutter: Inter from `google_fonts`, JetBrains Mono from same. Map to platform `SF Pro` / `Roboto` only as fallback if Inter fails to load.

### Roles

| Role | Font | Weight | Size | Tracking | Usage |
| ---- | ---- | ------ | ---- | -------- | ----- |
| **Display** | Inter | 700 | 22–32 | −0.025em | Page titles, often UPPERCASE |
| **Subhead** | Inter | 600 | 17 | −0.015em | Card titles, list-item headlines |
| **Body**    | Inter | 500 | 15 | 0       | Default reading copy |
| **Body-sm** | Inter | 400 | 13 | 0       | Secondary copy, descriptions |
| **Caption** | Inter | 500 | 11 | 0.01em  | Timestamps, metadata under names |
| **Mono-label** | JetBrains Mono | 500 | 11 | 0.08em UPPERCASE | Section labels, status text |
| **Mono-data**  | JetBrains Mono | 500 | 13 | 0.04em UPPERCASE | Numbers, IDs, dates in metadata |

### Capitalization rules

- **UPPERCASE Inter 700** for: page titles, primary action button labels, KPI row labels.
- **UPPERCASE JetBrains Mono** for: section labels, status indicators ("● CONFIRMED"), data tags ("SOLVE_MS 274"), date labels above lists ("SUN 25 MAY").
- **Mixed case Inter** for: body text, names, event titles inside cards (so they read naturally).

This mixed-case-inside / UPPERCASE-as-chrome split is the brand signature. Avoid sentence-case headers — they read as soft, off-brand.

---

## 🧩 Components

### Time chip (calendar-app signature)

```
[ 10:00–11:30 ]
```

- Background: `#CCFBF1` (accent-soft), text: `#134E4A` (accent-ink), JetBrains Mono 500, 11px, padding 2/8, border-radius 6.
- Used inline next to event titles in lists.

### Status indicator

```
● CONFIRMED    (success green, mono uppercase)
● PENDING      (warning amber)
● DECLINED     (danger red)
```

- Always text + dot, never just a dot. Color carries semantics, mono caps carry status name.

### Primary CTA

- Solid `--ink-1` background (NOT teal — teal is accent, not button), white Inter 700 caps text, 14px, padding 14/20, border-radius 999.
- Variant: solid teal CTA only for "publish" / "run solver" / other go-actions where commitment is the point.

### Secondary CTA

- Background `#FFFFFF`, border `1px solid #E4E4E7`, text `--ink-1` Inter 600 caps. Same shape as primary.

### Destructive CTA

- White bg, red text `#B91C1C`, red border. Same shape.

### Avatar (no profile photos in MVP — initials only)

- 36px circle, background = deterministic teal-tone variant from name hash (e.g., teal-700 / teal-600 / teal-800 / amber-700 — kept brand-consistent), white initials Inter 700 13px.

### Card

- White surface, 1px line, 14px radius, padding 14–18px. No shadow at rest; hover/press uses subtle inset.

### List row

- 64–72px tall, hairline divider between rows (last row no divider). Tap target full-width.

---

## 🪶 Signature details (the "120% one detail" per huashu-design rule)

The thing that should be done with extra care — what makes this app feel like Block-Mono and not generic iOS:

1. **All-caps page titles** with tight tracking, set in Inter 700. Sets the tone every screen.
2. **JetBrains Mono for any number, ID, status, or date label** above a list. Keeps "data" feel without going full developer-tool.
3. **Solid black primary CTAs** — not teal, not gradient, not bordered. Confidence by reduction.

Pick one of these to do at 120% on every screen; let the rest be 80%.

---

## 🚫 Forbidden zone

- Purple ANYWHERE (use teal or warning amber).
- Bordered/outlined primary CTAs.
- Soft drop-shadows on cards (Block-Mono uses hairline borders, not shadows).
- Multicolor icons (single-tone always — current ink, accent teal, or status color).
- Decorative emoji as content icons. Status uses dots + text. Tab bar uses SF Symbols glyphs (in Flutter; placeholder emoji acceptable in HTML prototype only).
- Italic body text for emphasis (use weight or all-caps instead).
- Sentence-case page titles.

---

## 🌡 Mood keywords

> confident · structural · matter-of-fact · mono-typographic · spacious-but-deliberate

NOT: warm · friendly · playful · approachable.

If a stakeholder asks "can we make it warmer" — reject and offer a different brand direction (B Soft-Overlap is the warm one). Block-Mono earns trust by being un-warm.
