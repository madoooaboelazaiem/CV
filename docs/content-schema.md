# content.json schema

All site copy. Rendered at runtime by the template; editable later via `#edit`.
Any top-level section key can be removed to hide that section (`ai`, `skills`, `work`, `systems`, `experience`, `learning`, `achievements`, `contact`). `about`, `person`, `hero` are expected.
Inline `*text*` inside `hero.sub`, `about.paragraphs`, ledes, project `description` and experience `summary` renders as serif italic emphasis. Use it at most once per block.

Headings are always a 2-item array `[plain, emphasised]`, e.g. `["Things I've", "built."]` → bold sans + serif italic. Keep the emphasised part to one or two words.

## meta
| field | notes |
|---|---|
| title | `<title>`; "Name — Role" |
| description | meta description, one sentence |
| lang | html lang, default `en` |

## person
`name`, `firstName`, `watermark` (huge faint word behind the hero, usually surname in caps), `monogram` (2 letters), `brandSuffix` (italic word next to monogram), `email`, `location`, `resumeFilename`, `links: [{label, url}]` — use the real link targets from `links.json`.
Phone numbers: leave out unless the person explicitly wants one public.

## nav
Map of section id → label. Only sections with a label appear in the nav. `learning` normally has no nav entry (it highlights "Experience").

## hero
| field | notes |
|---|---|
| eyebrow | small caps line above title (name) |
| titleLines | 2 lines, last gets a muted period. Job title, not a tool. |
| role | serif italic line under the title, e.g. "Full-stack, backend-first." |
| rotPrefix, rotWords | "Building" + rotating words (5–8, short, concrete) |
| sub | 1–2 sentences: years, domains, strengths |
| currentLabel, current | floating tag on the portrait ("Currently" / "Role, Company") |
| hint, hintTouch | reveal hint for mouse and touch |
| ctaWork, ctaTalk, ctaResume | button labels |
| avatarFace | `{x, y, r}` in avatar image UV (0–1): head centre and radius used by the look-at warp. Defaults `0.5, 0.22, 0.3`; tune if the head isn't centred near the top. |
| bigWord | sketch theme: the giant word behind the character (default "Portfolio"); auto-fits the viewport |
| greeting | sketch theme: handwritten prefix before the name ("Hi, I'm") |
| labels | sketch theme: up to 4 taped labels around the hero (2 and 4 render red) |
| sketchHint, sketchHintTouch | sketch theme: handwritten hint ("hover me to see the sketch" / "tap me to redraw") |
| underLabel, underLanes, underCode | optional: label, 3 lane names and code lines shown in the revealed layer. Defaults fit payments/backend engineers; change them for other domains (e.g. a designer: "figma.frames", "tokens.sync"). |

## marquee
Array of 10–14 short terms. Alternating items render serif italic.

## about
`heading`, `paragraphs` (3–4; first one is the lede and renders larger), `resumeLabel`,
`idCard: {heading, location, nameLines[2], role, meta:[[k,v]…3], balanceLabel, balance:[[label, weight]…], code:[2 short lines]}` — `balance` draws a split bar (e.g. Backend 70 / Frontend 30). Weights are relative; tell the person they are editable.
`facts: [[label, value]…]` 5–8 rows, `quote` (optional; if you write it, say so).

## ai (optional)
`heading`, `lede`, `pillars: [{title, detail, tag}]`. The orchestration and polling-vs-workflow animations are built in; only include this section for people who actually build with AI.

## skills
`heading`, `lede`, `categories: [[id, label]…]` (first must be `["all","All"]`), `items: [{sym, name, cat, used[], note?}]`.
- `sym`: 2 characters, unique, element-style (`Ts`, `K8`).
- Order matters: tiles shade from darkest (first) to lightest; put the person's core first.
- `used`: where it was used, from CV job tags. Use "Core competencies" when it's only in a skills list.
- `note`: one factual sentence; otherwise "Used at …" is generated.

## work
`heading`, `lede`, `projects[]`, `sideLabel`, `side: [{title, detail, url}]`.
Project: `title`, `rail` (short label), `org`, `period`, `category`, `visual`, `description`, `points[]` (2–4), `tags[]`, `notes: [[label, text]…]` (case notes), `link?: {label, url}`.
`visual` keys with built-in animated mockups: `pay` (payment lanes + breaker), `syl` (team + scheduling), `orch` (orchestrator→workers), `flow` (durable workflow steps), `skills` (Claude skill files), `surv` (trading candles + flag), `cv` (pose tracking). Any other value renders a generic tag/points mock — fine for most projects. To add a bespoke visual, add a function to `VIS` in the template (see motion.md).

## systems (optional)
`heading`, `lede`, `items: [{name, context, nodes:[{title, summary, why, tradeoff?, stack}]}]`. 4–6 nodes per system, in data-flow order. `why`/`tradeoff` are explanation you write from the CV facts — flag them as written by you.

## experience
`heading`, `items: [{year, label, kind, role, org, place, period, summary, points[], tags[]}]` newest first. `kind`: Work / Founding team / Research / Education.

## learning (optional)
`heading`, `lede`, `items: [{title, detail, when}]`. Show expiry honestly ("2023 – 2026").

## achievements
`heading`, `hint`, `items[]`: either `{big:"Day 1", title, detail, org}` or `{prefix?, value:number, suffix?, title, detail, org}` (count-up animation). 6–8 items, numbers only from the CV or the person.

## contact
`heading: [line1, line2]`, `emailCta`, `resumeLabel`.

## footer
`left`, `right`.
