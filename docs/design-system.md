# Design system

Editorial magazine × engineering. Calm, typographic, one loud moment (the hero reveal).

## Tokens (CSS custom properties on :root; dark theme redefines all)
| token | light | dark | use |
|---|---|---|---|
| --bg | #F3EEE4 | #13162A | page |
| --paper | #FBF8F1 | #1A1E36 | cards |
| --wash | #E9E2D4 | #20253F | soft fills, arch |
| --line | #DCD3C2 | #2D3250 | hairlines |
| --ink | #1F2440 | #EFE8DA | text, dark tiles, dots |
| --ink2 / --muted | #474A61 / #7D776C | … | secondary text |
| --on-ink | #F6F1E6 | #13162A | text on ink |
| --t1…--t6 (+f) | navy → taupe → transparent | inverted | periodic-table tile shades |
| --hx | #D4CAA4 | #FFFFFF | hero text colour used with `mix-blend-mode:difference` so it reads navy on cream and brass on the revealed navy layer |

Changing the palette: keep `--hx = bg − ink` per channel in light mode (difference blend maths), otherwise hero text won't land on the ink colour.

## Type
- Display: Inter Tight 800, tight tracking (−0.045em), line-height ~0.9.
- Editorial accent: Instrument Serif italic — only the second item of every heading array, the hero role line, the quote, the email.
- Body: Inter 400/500, 16px, measure under ~60ch.
- Google Fonts with full system fallbacks; the site still works if fonts are blocked.

## Layout
- Max width 1320px, side padding clamp(20px, 4vw, 56px).
- Asymmetric two-column sections; mobile recomposes (portrait above title, rails become chips, pinned cards become swipe).
- Small numbered kickers are generated in section order — they are a sequence, so numbering is legitimate.
- Radius: 6/12/20 by hierarchy, pills only for chips and buttons.

## Rules that keep it from looking generated
- Don't put a tool or language in the hero title.
- No gradients as decoration, no glass, no neon. Shadows only on lifted objects (cards, ID card).
- One accent colour family (navy/brass). Green and amber only as status.
- Copy: plain verbs, sentence case, specific nouns. No "passionate", "innovative", "cutting-edge".
- Every visual on a project card must depict that project (lanes for payments, calendar for scheduling…).
