# Assets and prompts

## Portrait (top layer)
Needs transparency. Best source order: a high-res photo the person sends (run `build.py --cutout`), else the CV's embedded photo (`extract_cv_assets.py` keeps its soft mask as alpha). Under ~300px wide still works because the halftone hides softness, but ask for a better one.

## ID card photo
Defaults to the portrait composited on `--wash`. Pass `--card` for a different crop.

## 3D avatar (revealed layer)
Any half-body character with a plain background; `--cutout` removes it (rembg `isnet-general-use` handles hair well). Head should sit near the top centre; otherwise tune `hero.avatarFace`.

Prompt (ChatGPT image / similar), with the person's photo as image 1:
```
Use my photo as the PRIMARY IDENTITY REFERENCE. Create a premium 3D animated-film style half-body portrait of me: preserve my exact face, hair, skin tone and proportions. Friendly confident smile, arms crossed, plain light shirt. Centred, looking at the camera, soft studio light, plain neutral grey background, no objects, no text. Portrait 4:5, high resolution.
```

## Real head-turn tracking (optional upgrade)
Generate a short video from the avatar (Google Flow / Veo, Kling, Runway):
```
Same character, same framing, locked camera, plain background. The character slowly turns their head from looking far left to looking far right, eyes leading the movement, then back. No body movement, no lip movement, no camera movement. 4 seconds, smooth.
```
Then follow "Upgrade: real head-turn" in motion.md.

## Optional dark variant
A second image of the avatar in a dark/tech setting can replace the procedural world layer (draw it full-hero in `drawWorld` instead of grid/code/lanes). Keep identical pose and framing.
