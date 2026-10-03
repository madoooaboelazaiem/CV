# Motion and interaction recipes

All motion lives in the single `<script>` at the end of `assets/template.html`. Every effect checks `RM` (prefers-reduced-motion) and either renders its final state or does nothing.

## Hero load sequence
CSS only: `.js` hides hero parts, `.is-loaded` (added after fonts are ready, max 900ms) transitions them in with staggered delays. Title lines rise from an overflow mask.

## Halftone portrait (top layer)
`layout()` samples the portrait (must have alpha) on a grid (4–5.6px step). Dot radius = darkness × alpha. Intro: dots fly from random positions, staggered top→bottom. Pointer repels dots within 20% of the figure width. "Look-at lean": each dot shifts toward the cursor proportionally to `1 − y/height` so the head leans while shoulders stay.

## Scratch-to-reveal ("under the hood")
- **Brush**: procedurally generated once (`makeBrush`): an irregular quadratic-curve blob, spatter around the edge, bristle gaps and speckle holes cut with `destination-out`. Long axis is perpendicular to motion.
- **Strokes**: pointer path is interpolated every `size × 0.14` px and stamped with the brush rotated to the movement angle (+ jitter). First move stamps a cluster. Leaving the hero ends the stroke; re-entering starts a new one. No automatic reveal.
- **Decay**: every stamp lives 2.7s; the last 0.95s it shrinks (smoothstep) to nothing, so stopping makes the reveal physically shrink away.
- **Compositing**: an offscreen mask canvas holds the stamps. The under layer (`#under`, full hero) draws the world then `destination-in` with the mask. The top portrait canvas draws arch + dots then `destination-out` with the same mask region, so the portrait is scratched too. DOM text stays above and switches colour via `mix-blend-mode:difference` (see design-system `--hx`).
- **World layer**: navy fill, faint grid, scrolling code columns (`hero.underCode`), three queue lanes with packets (one amber packet drops out = circuit breaker), a small orchestrator graph, then the avatar with a soft radial highlight.
- Performance: under canvas at ≤1.25 DPR, only drawn while stamps are alive; rAF stops when idle.

## Avatar look-at (WebGL)
`makeWarp` uploads the avatar as a premultiplied texture and renders one quad. The fragment shader samples `uv − offset`, where offset = look × weight; weight is a smooth falloff around `hero.avatarFace` (head) plus a smaller one around the eyes, fading toward the chin. Result: head and eyes drift toward the cursor while shoulders stay — a convincing small head-turn from a single still. Falls back to a static image without WebGL. Tune strength in the shader constants (`vec2(.05,.024)` head, `vec2(.02,.012)` eyes).

### Upgrade: real head-turn (video scrub)
If the person generates a head-turn video (see assets-and-prompts.md), extract ~24–40 frames (`ffmpeg -i turn.mp4 -vf fps=12,scale=640:-1 f%03d.webp`), pack them into a horizontal sprite, and replace `warp.render` with picking `frame = round((look.x+1)/2 × (n−1))`. Keep the warp for vertical look.

## Rotating word
Inline-grid stack; incoming word slides up from below, outgoing slides up and out, every 2.2s.

## Marquee
Two rows, opposite directions, base speed + smoothed scroll velocity. Paused offscreen via IntersectionObserver.

## Split headings
Words wrapped in overflow masks, revealed with 70ms stagger when 40% visible. `aria-label` keeps the original text for screen readers.

## Periodic table
Tiles shaded by order (`--t1`…`--t6`). Entrance: diagonal stagger pop (`--d` = (col+row)×38ms), class removed afterwards so filters can dim tiles. Selection re-animates the big tile.

## Project carousel
Rail of vertical tabs (horizontal chips on mobile), swipe on touch, 3D tilt of the mockup toward the mouse. Mockups use SVG `animateMotion` for packets.

## AI section demos
Orchestrator graph: promise-based timeline (packets via rAF), log lines written in step order, one failed worker check and retry each cycle, only runs while visible. Polling vs workflow: two lanes; polling adds a request dot every 280ms, workflow shows one `waitForEvent` and an event at the end.

## Pinned achievements (desktop ≥900px, >3 cards)
Wrapper height = viewport + track overflow; sticky inner; scroll progress → translateX, progress bar, and each card tilts/drops by its distance from viewport centre.

## Adding a project visual
Add `key: function(){ return '<div class="mock">…</div>' }` to `VIS`. Use `.mock`, `.mock-h`, `.row`, `.pill(--ok|--wait|--ink)`, `.bars`, `.cells`, `.cal`, and SVG with classes `s` (stroke ink), `f` (fill ink), `m` (muted), `w` (warning). Animate with SMIL or CSS; keep it under ~40 elements.

## Reduced-motion pattern
```js
if (RM) { renderFinalState(); return; }
onView(el, function (visible) { running = visible; if (visible) loop(); }, { threshold: .25 });
```

## Sketchbook theme: self-drawing stickers
Assets (made by `build.py --theme sketch`): `sticker` = colour avatar with a white die-cut border; `sketch` = graphite line art with identical size and alignment.
Every `[data-sticker]` element (hero, about bust, achievements mini, contact) gets a canvas; `data-crop="y0,y1"` picks a vertical slice of the character (0–0.5 = bust).
Per sticker, on first view (hero: right after load):
1. **Pencil** 0–1.4s: a mask built by stamping circles along a zig-zag scribble path (rows top→bottom, alternating direction, jittered) reveals the line art, as if shaded in.
2. **Colour** 1.05–2.3s: the colour sticker washes in behind a diagonal edge with jagged teeth; line art stays on top at 26% so it keeps an illustrated look.
3. **Hero only, after drawing**: pointer leaves soft eraser stamps (1.6s life, shrinking) that cut the colour away → the pencil sketch shows through, then heals.
Click/tap any sticker to redraw it. Reduced motion renders the final state.
Big word: `-webkit-text-stroke` outline revealed by `clip-path` left→right, then filled; `fitBig()` scales it to ≤96% of the viewport whatever font loads.
Doodles: inline SVG with `pathLength="1"`; `stroke-dashoffset 1→0` with per-path `--dd` delays draws them after the word.
