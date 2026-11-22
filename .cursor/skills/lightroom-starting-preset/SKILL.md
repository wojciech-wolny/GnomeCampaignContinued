---
name: lightroom-starting-preset
description: >-
  Analyzes photos in a folder or a Lightroom Classic catalog (.lrcat) and
  writes a conservative .xmp preset in a given style, for import into
  Lightroom (LR) as a starting point. Use when the user asks for a Lightroom
  or Lightroom Classic preset, an XMP develop starting point, or a look
  matched to a photo catalog or reference images.
---

# Lightroom starting-point preset

Build a Lightroom develop preset the user can import and then push around. The file is a start, not a finished grade. Do not modify the Lightroom catalog. Do not invent a folder or a style.

## What you need from the user

1. A catalog: a folder of JPEG, PNG, TIFF or WebP files, or a Lightroom Classic `.lrcat` file.
2. A style: one of the built-in ids, or a short description of the look.

If either is missing, ask. If they say "like these photos" or do not name a look, the style is `match`.

Built-in ids: `match`, `filmic`, `matte-fade`, `airy-bright`, `moody`, `teal-orange`, `warm-portrait`, `cool-editorial`, `black-and-white`, `vintage`. Aliases such as `bw`, `teal` and `matte` are accepted. Run `python3 scripts/write_preset.py --list-styles` for the one-line summaries.

A free-text look ("a bit warmer, lifted blacks, less green") is `--style custom` plus `--set` flags. Translate words with `references/sliders.md`. Stay inside the ranges in that file.

## Steps

Work from the directory that contains this `SKILL.md`. Call that path `SKILL_DIR`.

1. Install Pillow if `import PIL` fails: `python3 -m pip install pillow`. Reading a `.lrcat` does not need Pillow unless you fall back to image files.
2. Measure:

```bash
python3 "$SKILL_DIR/scripts/analyze_catalog.py" \
  --catalog "PATH" \
  --out "/tmp/lr-stats.json"
```

Add `--collection "Name"` only when they named a Lightroom collection. The default sample is 80 photos, spread across the set. The catalog opens read-only.

3. Read the JSON. Relay every `warnings` entry. The `observations` are hints, not slider values.
4. Look at the files in `review_paths` (the Read tool can open JPEG, PNG and WebP). Do this before writing the preset when those files open. Confirm the direction (warm or cool, faded or deep, split color or not). If a picture disagrees with the numbers, add a `--set` for that slider. Do not treat the color of the subject (sky, grass, skin, a red wall) as a grade. Color grading is only for a cast that shows up in shadows versus highlights across the set.
5. Write the preset outside the campaign folders (`MG`, `gracze`, `druk`). Do not commit the `.xmp` or the notes unless the user asks.

```bash
python3 "$SKILL_DIR/scripts/write_preset.py" \
  --stats "/tmp/lr-stats.json" \
  --style "STYLE" \
  --name "Short name (start)" \
  --out "DESTINATION.xmp"
```

Useful flags:

- `--strength 0.6` softens the result. Built-in recipes are already mild, so the default strength for them is `1`. Match mode defaults to `0.65` (pixels) or `0.75` (develop settings already in a catalog).
- `--set Contrast2012=-12` sets that slider after strength. Repeat the flag. It is clamped.
- `--no-white-balance` when they want tone and color only.
- `--allow-strong` only when they explicitly want sliders past the starting-point caps.
- `--group "Starting Points"` is the default group name inside the file.

6. Open the `.notes.md` next to the preset. Tell the user, in their language:
   - the `.xmp` path and the group name
   - the sliders that were written, and that everything else in Lightroom is left alone
   - that Amount 100% is this starting point; they should lower Amount if it is heavy, then move Exposure and White Balance
   - the import clicks from `references/import.md` (include the Polish menu names if they are working in Polish)
   - any warning about Kelvin replacing As Shot, a thin sample, or pixel matching being a guess

## How the two sources differ

- A folder, or a catalog with no develop settings: the script reads the rendered pictures. It can see fade, contrast, a warm or cool cast, and a shadow/highlight split. It cannot see the raw file's as-shot white balance, profile or process version. Those stay out of the preset. `IncrementalTemperature` moves JPEG/TIFF white balance only.
- A `.lrcat` that already has develop settings: the script takes the median of those sliders and softens it. That is the better match, because it is the user's actual edits. Absolute Kelvin is copied only when the photos agree; otherwise it is left out. Point curves and masks are not copied.

Imported presets change only the sliders stored in the file. Say that plainly so the user is not afraid it will reset sharpening or the camera profile.

## Do not

- Do not hand-write the XMP. The writer sets the Amount flag, the group, the UUID and the split-toning mirror of the color grade.
- Do not put `ProcessVersion`, a camera profile, or a Look in the preset.
- Do not edit, vacuum or write the `.lrcat`.
- Do not turn one odd frame into a strong slider. Fewer than 8 photos is a weak sample; say so.
- Do not claim the preset reproduces the catalog. Call it a starting point.
