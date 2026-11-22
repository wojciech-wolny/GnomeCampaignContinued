# Slider cheat sheet

Use this when the user describes a look that is not one of the built-in styles. Pass the result as `--set Key=Value` with `--style custom`, or as extra `--set` flags on top of a built-in style.

`--set` is the final value. It is not multiplied by `--strength`. The writer then clamps it to the starting-point range unless `--allow-strong` is set. Do not pass `--allow-strong` unless the user asked for a heavy preset.

Leave a slider out rather than setting it to 0. A value in the file overwrites that slider in Lightroom. A missing value leaves the photo's current slider alone.

## What to copy, and what to leave out

| Put in the preset | Leave out |
|---|---|
| Tone, presence, vibrance, a mild white-balance nudge | Camera profile, process version, calibration |
| Color grading when shadows and highlights really diverge | Crop, brushes, masks, healing |
| A lifted or rolled point curve when the files are faded | Sharpening and noise reduction |
| Light grain or a light vignette when the style asks | Absolute Kelvin guessed from a JPEG |

JPEG analysis cannot see the raw file's as-shot white balance. The writer may set `IncrementalTemperature` and `IncrementalTint` (the JPEG/TIFF sliders, about −18 to +18 here). It does not invent `Temperature` in Kelvin from pixels. Kelvin is copied only from develop settings already stored in a catalog, and only when those photos agree.

## Starting-point ranges

| Key | Range | Raise it when the user wants |
|---|---|---|
| `Exposure2012` | −0.60 to +0.60 | brighter / darker overall |
| `Contrast2012` | −30 to +25 | punchier / flatter |
| `Highlights2012` | −40 to +25 | darker skies and bright skin; negative recovers highlights |
| `Shadows2012` | −30 to +40 | open shadows (positive) or moodier shadows (negative) |
| `Whites2012` | −30 to +25 | brighter / duller white point |
| `Blacks2012` | −30 to +28 | milky blacks (positive) or deeper blacks (negative) |
| `Texture` | −20 to +20 | smoother (negative) or grittier (positive) |
| `Clarity2012` | −25 to +25 | softer (negative) or crunchier (positive) |
| `Dehaze` | −20 to +20 | washed (negative) or clearer (positive) |
| `Vibrance` | −25 to +25 | more color without hammering skin |
| `Saturation` | −30 to +20 | a global color cut or a small boost |
| `IncrementalTemperature` | −18 to +18 | warmer (positive) or cooler (negative) on JPEG/TIFF |
| `IncrementalTint` | −15 to +15 | magenta (positive) or green (negative) |
| `ColorGradeShadowHue` | 0–359 | shadow color: 0 red, 40 orange, 90 yellow, 150 green, 190 cyan, 230 blue, 280 purple |
| `ColorGradeShadowSat` | 0–24 | stronger shadow tint |
| `ColorGradeHighlightHue` | 0–359 | highlight color, same wheel |
| `ColorGradeHighlightSat` | 0–24 | stronger highlight tint |
| `ColorGradeBlending` | 0–100 | how far the shadow and highlight colors reach; 50 is normal |
| `GrainAmount` | 0–20 | visible grain; keep this low |
| `PostCropVignetteAmount` | −25 to 0 | a dark edge; more negative is stronger |
| `HueAdjustment*` / `SaturationAdjustment*` / `LuminanceAdjustment*` | −12 to +12 | a grade you can see in every photo, not the color of the subject |

Eight hue names: Red, Orange, Yellow, Green, Aqua, Blue, Purple, Magenta. Example: `SaturationAdjustmentAqua=-8`.

`ConvertToGrayscale=True` is the black-and-white treatment. Do not also set `Saturation=-100`.

## Words to sliders

- faded, matte, milky: `Blacks2012` positive, `Contrast2012` negative, sometimes `Dehaze` negative
- crushed, inky: `Blacks2012` negative, `Shadows2012` negative
- bright and soft: `Exposure2012` small positive, `Highlights2012` negative, `Shadows2012` positive, `Clarity2012` negative
- warm: `IncrementalTemperature` positive
- cool: `IncrementalTemperature` negative
- teal shadows and orange highlights: shadow hue near 190, highlight hue near 40, saturation under 20
- punch: `Contrast2012` positive, `Clarity2012` small positive, highlights a bit negative
- pastel: `Saturation` and `Vibrance` negative, blacks a bit positive

If the catalog is already dark, do not add a large negative exposure. If it is already flat, do not add a large negative contrast. The writer does this when pixel stats exist. Do not stack a second copy of the same move by hand.
