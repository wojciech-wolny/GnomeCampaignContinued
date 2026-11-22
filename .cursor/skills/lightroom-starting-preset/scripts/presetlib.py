"""Measure a photo folder or a Lightroom catalog and write a starting-point .xmp preset."""

from __future__ import annotations

import json
import math
import re
import sqlite3
import statistics
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.sax.saxutils import escape

SKILL_ROOT = Path(__file__).resolve().parents[1]
STYLES_PATH = SKILL_ROOT / "assets" / "styles.json"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp", ".bmp"}
REVIEW_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

CRS_NS = "http://ns.adobe.com/camera-raw-settings/1.0/"
RDF_NS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"

HUE_WHEELS = {
    "ColorGradeShadowHue",
    "ColorGradeHighlightHue",
    "ColorGradeMidtoneHue",
    "ColorGradeGlobalHue",
    "SplitToningShadowHue",
    "SplitToningHighlightHue",
}
GRADE_MIRRORS = (
    ("ColorGradeShadowHue", "SplitToningShadowHue"),
    ("ColorGradeShadowSat", "SplitToningShadowSaturation"),
    ("ColorGradeHighlightHue", "SplitToningHighlightHue"),
    ("ColorGradeHighlightSat", "SplitToningHighlightSaturation"),
)
UNSCALED = HUE_WHEELS | {
    "ConvertToGrayscale",
    "Temperature",
    "ColorGradeBlending",
    "SplitToningBalance",
    "PostCropVignetteStyle",
    "PostCropVignetteMidpoint",
    "PostCropVignetteFeather",
    "PostCropVignetteRoundness",
    "GrainSize",
    "GrainFrequency",
    "ParametricShadowSplit",
    "ParametricMidtoneSplit",
    "ParametricHighlightSplit",
}
WB_KEYS = ("Temperature", "Tint", "IncrementalTemperature", "IncrementalTint")
COMPANION_KEYS = {
    "GrainSize": "GrainAmount",
    "GrainFrequency": "GrainAmount",
    "PostCropVignetteMidpoint": "PostCropVignetteAmount",
    "PostCropVignetteFeather": "PostCropVignetteAmount",
    "PostCropVignetteRoundness": "PostCropVignetteAmount",
    "PostCropVignetteStyle": "PostCropVignetteAmount",
    "PostCropVignetteHighlightContrast": "PostCropVignetteAmount",
    "ColorGradeBlending": "ColorGradeShadowSat",
    "SplitToningBalance": "SplitToningShadowSaturation",
}

# Caps that keep a generated preset useful as a starting point.
CLAMPS = {
    "Exposure2012": (-0.60, 0.60),
    "Contrast2012": (-30, 25),
    "Highlights2012": (-40, 25),
    "Shadows2012": (-30, 40),
    "Whites2012": (-30, 25),
    "Blacks2012": (-30, 28),
    "Texture": (-20, 20),
    "Clarity2012": (-25, 25),
    "Dehaze": (-20, 20),
    "Vibrance": (-25, 25),
    "Saturation": (-30, 20),
    "IncrementalTemperature": (-18, 18),
    "IncrementalTint": (-15, 15),
    "Temperature": (2500, 12000),
    "Tint": (-30, 30),
    "ColorGradeShadowSat": (0, 24),
    "ColorGradeHighlightSat": (0, 24),
    "ColorGradeMidtoneSat": (0, 18),
    "ColorGradeGlobalSat": (0, 16),
    "ColorGradeShadowLum": (-15, 15),
    "ColorGradeHighlightLum": (-15, 15),
    "ColorGradeMidtoneLum": (-15, 15),
    "ColorGradeGlobalLum": (-15, 15),
    "ColorGradeBlending": (0, 100),
    "SplitToningShadowSaturation": (0, 24),
    "SplitToningHighlightSaturation": (0, 24),
    "SplitToningBalance": (-50, 50),
    "GrainAmount": (0, 20),
    "GrainSize": (1, 100),
    "GrainFrequency": (1, 100),
    "PostCropVignetteAmount": (-25, 0),
    "PostCropVignetteMidpoint": (0, 100),
    "PostCropVignetteFeather": (0, 100),
    "PostCropVignetteRoundness": (-100, 100),
    "PostCropVignetteStyle": (1, 3),
    "PostCropVignetteHighlightContrast": (0, 50),
    "ParametricShadows": (-30, 30),
    "ParametricDarks": (-30, 30),
    "ParametricLights": (-30, 30),
    "ParametricHighlights": (-30, 30),
}
STRONG_CLAMPS = {
    "Exposure2012": (-2.0, 2.0),
    "Temperature": (2000, 50000),
    "Tint": (-150, 150),
    "IncrementalTemperature": (-100, 100),
    "IncrementalTint": (-100, 100),
    "GrainAmount": (0, 100),
    "PostCropVignetteAmount": (-100, 100),
    "ColorGradeShadowSat": (0, 100),
    "ColorGradeHighlightSat": (0, 100),
    "ColorGradeMidtoneSat": (0, 100),
    "ColorGradeGlobalSat": (0, 100),
    "SplitToningShadowSaturation": (0, 100),
    "SplitToningHighlightSaturation": (0, 100),
}
HSL_PREFIXES = ("HueAdjustment", "SaturationAdjustment", "LuminanceAdjustment")
HUE_NAMES = ("Red", "Orange", "Yellow", "Green", "Aqua", "Blue", "Purple", "Magenta")

DEVELOP_ALLOW = set(CLAMPS) | {"ConvertToGrayscale"}
SLIDER_RE = re.compile(r"crs:([A-Za-z0-9]+)=\"([^\"]*)\"")
NUMBER_RE = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)$")

ALIASES = {
    "match": "match",
    "catalog": "match",
    "as-shot": "match",
    "like-these": "match",
    "matte": "matte-fade",
    "fade": "matte-fade",
    "faded": "matte-fade",
    "matte-fade": "matte-fade",
    "film": "filmic",
    "filmic": "filmic",
    "airy": "airy-bright",
    "bright": "airy-bright",
    "airy-bright": "airy-bright",
    "moody": "moody",
    "teal": "teal-orange",
    "teal-orange": "teal-orange",
    "orange-teal": "teal-orange",
    "portrait": "warm-portrait",
    "warm": "warm-portrait",
    "warm-portrait": "warm-portrait",
    "editorial": "cool-editorial",
    "cool": "cool-editorial",
    "cool-editorial": "cool-editorial",
    "bw": "black-and-white",
    "black-and-white": "black-and-white",
    "mono": "black-and-white",
    "monochrome": "black-and-white",
    "vintage": "vintage",
    "custom": "custom",
}

SLIDER_ORDER = [
    "WhiteBalance",
    "Temperature",
    "Tint",
    "IncrementalTemperature",
    "IncrementalTint",
    "Exposure2012",
    "Contrast2012",
    "Highlights2012",
    "Shadows2012",
    "Whites2012",
    "Blacks2012",
    "Texture",
    "Clarity2012",
    "Dehaze",
    "Vibrance",
    "Saturation",
    "ConvertToGrayscale",
    "ToneCurveName2012",
]


class PresetError(Exception):
    """The catalog or the requested preset could not be built."""


def load_styles() -> dict:
    data = json.loads(STYLES_PATH.read_text(encoding="utf-8"))
    if "match" not in data:
        raise PresetError(f"Style file is missing 'match': {STYLES_PATH}")
    return data


def style_ids() -> list[str]:
    return list(load_styles())


def resolve_style(name: str) -> str:
    key = name.strip().lower().replace("_", "-").replace(" ", "-")
    if key not in ALIASES:
        known = ", ".join(style_ids())
        raise PresetError(f"Unknown style '{name}'. Built-in styles: {known}. Use 'custom' with --set for a described look.")
    return ALIASES[key]


def default_strength(source: str, style_id: str) -> float:
    if style_id == "match" and source == "lrcat-develop":
        return 0.75
    if style_id == "match" or style_id == "custom":
        return 0.65 if style_id == "match" else 1.0
    return 1.0


def analyze_catalog(path: Path, limit: int = 80, collection: str | None = None) -> dict:
    path = path.expanduser().resolve()
    if not path.exists():
        raise PresetError(f"Catalog path does not exist: {path}")
    if path.is_file() and path.suffix.lower() == ".lrcat":
        return analyze_lrcat(path, limit=limit, collection=collection)
    if path.is_dir():
        return analyze_folder(path, limit=limit)
    if path.is_file():
        return analyze_folder(path.parent, limit=limit, only=path)
    raise PresetError(f"Give a folder of photos or a Lightroom .lrcat file, not {path}")


def analyze_folder(folder: Path, limit: int = 80, only: Path | None = None) -> dict:
    if only is not None:
        paths = [only]
    else:
        paths = list_images(folder)
    if not paths:
        raise PresetError(f"No JPEG, PNG, TIFF or WebP photos in {folder}. Raw files alone cannot be measured; export JPEGs or point at a catalog that already has develop settings.")
    chosen = spread(paths, limit)
    per_image = []
    skipped = 0
    for item in chosen:
        try:
            per_image.append(measure_image(item))
        except PresetError:
            skipped += 1
    if not per_image:
        raise PresetError(f"Could not read any photos in {folder}. Install Pillow (`python3 -m pip install pillow`) if the files are real images.")
    pixel = aggregate_pixels(per_image)
    warnings = []
    if len(paths) < 8:
        count = len(paths)
        noun = "photo" if count == 1 else "photos"
        warnings.append(f"Only {count} {noun}. A starting point from fewer than 8 frames is easy to overfit to one scene.")
    if skipped:
        warnings.append(f"Skipped {skipped} unreadable file(s) in the sample.")
    if len(paths) > len(chosen):
        warnings.append(f"Sampled {len(chosen)} of {len(paths)} photos, spread across the file list.")
    return {
        "source": "folder",
        "catalog": str(folder if only is None else only),
        "photo_count": len(paths),
        "sampled": len(per_image),
        "edited_count": None,
        "skipped": skipped,
        "warnings": warnings,
        "observations": observations(pixel),
        "pixel": pixel,
        "median_sliders": None,
        "review_paths": review_paths(per_image),
    }


def analyze_lrcat(path: Path, limit: int = 80, collection: str | None = None) -> dict:
    try:
        uri = path.resolve().as_uri() + "?mode=ro"
        con = sqlite3.connect(uri, uri=True)
    except sqlite3.Error as exc:
        raise PresetError(f"Could not open {path} read-only. If Lightroom has it open, copy the .lrcat and try the copy. ({exc})") from exc
    try:
        rows, warnings = read_develop_rows(con, collection)
        file_paths = list_catalog_files(con, collection)
    finally:
        con.close()
    edited = [row for row in rows if row_is_edited(row["sliders"])]
    if edited:
        kept = spread(edited, max(limit, 1))
        if len(edited) > len(kept):
            warnings.append(f"Sampled {len(kept)} of {len(edited)} edited photos, spread across the catalog.")
        median = median_settings([row["sliders"] for row in kept])
        wb_note = white_balance_warning(median, [row["sliders"] for row in kept])
        if wb_note:
            warnings.append(wb_note)
        review = [str(item) for item in file_paths if item.suffix.lower() in REVIEW_EXTENSIONS][:6]
        if not median:
            warnings.append("Develop settings were present but every slider median was neutral.")
        return {
            "source": "lrcat-develop",
            "catalog": str(path),
            "photo_count": len(rows),
            "sampled": len(kept),
            "edited_count": len(edited),
            "skipped": 0,
            "warnings": warnings,
            "observations": ["Develop settings were read from the catalog. Sliders below are medians of those edits."],
            "pixel": None,
            "median_sliders": median,
            "review_paths": review,
        }
    existing = [item for item in file_paths if item.is_file() and item.suffix.lower() in IMAGE_EXTENSIONS]
    if existing:
        chosen = spread(existing, limit)
        per_image = []
        skipped = 0
        for item in chosen:
            try:
                per_image.append(measure_image(item))
            except PresetError:
                skipped += 1
        if not per_image:
            raise PresetError("The catalog has no develop settings, and the JPEG files it points at could not be read.")
        pixel = aggregate_pixels(per_image)
        warnings.insert(0, "The catalog has no usable develop settings. Measured the image files it points at instead.")
        if skipped:
            warnings.append(f"Skipped {skipped} unreadable file(s).")
        return {
            "source": "lrcat-files",
            "catalog": str(path),
            "photo_count": len(existing),
            "sampled": len(per_image),
            "edited_count": 0,
            "skipped": skipped,
            "warnings": warnings,
            "observations": observations(pixel),
            "pixel": pixel,
            "median_sliders": None,
            "review_paths": review_paths(per_image),
        }
    raise PresetError(
        "This catalog has no develop settings, and the original files are not on this disk. "
        "Export JPEGs of the set you want to match, or point --catalog at that folder."
    )


def list_images(folder: Path) -> list[Path]:
    found = []
    for item in folder.rglob("*"):
        if not item.is_file():
            continue
        if any(part.startswith(".") or part.endswith(".lrdata") for part in item.parts):
            continue
        if item.suffix.lower() in IMAGE_EXTENSIONS:
            found.append(item)
    return sorted(found)


def spread(items, limit: int) -> list:
    if limit < 1:
        raise PresetError("--limit must be at least 1.")
    items = list(items)
    if len(items) <= limit:
        return items
    picked = []
    seen = set()
    last = len(items) - 1
    for step in range(limit):
        index = round(step * last / (limit - 1))
        if index not in seen:
            seen.add(index)
            picked.append(items[index])
    return picked


def measure_image(path: Path) -> dict:
    try:
        from PIL import Image, UnidentifiedImageError
    except ImportError as exc:
        raise PresetError("Pillow is required to read photos. Install it with: python3 -m pip install pillow") from exc
    try:
        with Image.open(path) as image:
            rgb = image.convert("RGB")
            rgb.thumbnail((160, 160))
            pixels = list(rgb.getdata())
    except (UnidentifiedImageError, OSError) as exc:
        raise PresetError(str(exc)) from exc
    if not pixels:
        raise PresetError(f"Empty image: {path}")
    ys = []
    sats = []
    for red, green, blue in pixels:
        ys.append((0.2126 * red + 0.7152 * green + 0.0722 * blue) / 255.0)
        peak = max(red, green, blue)
        sats.append(0.0 if peak == 0 else (peak - min(red, green, blue)) / peak)
    ordered = sorted(ys)
    count = len(ordered)

    def percentile(fraction: float) -> float:
        index = min(count - 1, max(0, int(round(fraction * (count - 1)))))
        return ordered[index]

    p30 = percentile(0.30)
    p40 = percentile(0.40)
    p60 = percentile(0.60)
    p70 = percentile(0.70)
    shadow = region_mean(pixels, ys, lambda y: 0.02 <= y <= p30)
    highlight = region_mean(pixels, ys, lambda y: p70 <= y <= 0.98)
    mid = region_mean(pixels, ys, lambda y: p40 <= y <= p60)
    if mid is None:
        reds = sum(pixel[0] for pixel in pixels) / count / 255.0
        greens = sum(pixel[1] for pixel in pixels) / count / 255.0
        blues = sum(pixel[2] for pixel in pixels) / count / 255.0
        mid = (reds, greens, blues)
    return {
        "path": str(path),
        "y_p05": percentile(0.05),
        "y_p25": percentile(0.25),
        "y_p50": percentile(0.50),
        "y_p75": percentile(0.75),
        "y_p95": percentile(0.95),
        "y_p99": percentile(0.99),
        "mean_sat": sum(sats) / count,
        "black_clip": sum(1 for y in ys if y < 0.02) / count,
        "white_clip": sum(1 for y in ys if y > 0.98) / count,
        "shadow": shadow,
        "highlight": highlight,
        "mid": mid,
    }


def region_mean(pixels, ys, predicate) -> tuple[float, float, float] | None:
    reds = greens = blues = count = 0
    for (red, green, blue), y in zip(pixels, ys):
        if predicate(y):
            reds += red
            greens += green
            blues += blue
            count += 1
    if count == 0:
        return None
    return (reds / count / 255.0, greens / count / 255.0, blues / count / 255.0)


def aggregate_pixels(images: list[dict]) -> dict:
    def med(key: str) -> float:
        return statistics.median(item[key] for item in images)

    shadow_hues = []
    shadow_sats = []
    highlight_hues = []
    highlight_sats = []
    warms = []
    greens = []
    for item in images:
        if item["shadow"] is not None:
            hue, sat = hue_and_sat(item["shadow"])
            if hue is not None:
                shadow_hues.append(hue)
                shadow_sats.append(sat)
        if item["highlight"] is not None:
            hue, sat = hue_and_sat(item["highlight"])
            if hue is not None:
                highlight_hues.append(hue)
                highlight_sats.append(sat)
        warms.append(warmth(item["mid"]))
        greens.append(green_cast(item["mid"]))
    y50 = [item["y_p50"] for item in images]
    pixel = {
        "y_p05": med("y_p05"),
        "y_p25": med("y_p25"),
        "y_p50": med("y_p50"),
        "y_p75": med("y_p75"),
        "y_p95": med("y_p95"),
        "y_p99": med("y_p99"),
        "mean_sat": med("mean_sat"),
        "black_clip": med("black_clip"),
        "white_clip": med("white_clip"),
        "warm": statistics.median(warms),
        "green": statistics.median(greens),
        "y_spread": statistics.pstdev(y50) if len(y50) > 1 else 0.0,
        "shadow_hue": circular_mean(shadow_hues) if shadow_hues else None,
        "shadow_sat": statistics.median(shadow_sats) if shadow_sats else 0.0,
        "shadow_hue_std": circular_std(shadow_hues) if len(shadow_hues) > 1 else 0.0,
        "highlight_hue": circular_mean(highlight_hues) if highlight_hues else None,
        "highlight_sat": statistics.median(highlight_sats) if highlight_sats else 0.0,
        "highlight_hue_std": circular_std(highlight_hues) if len(highlight_hues) > 1 else 0.0,
    }
    pixel["span"] = pixel["y_p95"] - pixel["y_p05"]
    return round_tree(pixel)


def observations(pixel: dict) -> list[str]:
    notes = []
    if pixel["y_p05"] > 0.08:
        notes.append("Blacks look lifted.")
    if pixel["span"] < 0.62:
        notes.append("Contrast looks low.")
    elif pixel["span"] > 0.9:
        notes.append("Contrast looks high.")
    if pixel["warm"] > 0.06:
        notes.append("Midtones run warm.")
    elif pixel["warm"] < -0.06:
        notes.append("Midtones run cool.")
    if pixel["mean_sat"] < 0.2:
        notes.append("Color looks muted.")
    elif pixel["mean_sat"] > 0.45:
        notes.append("Color looks strong.")
    if pixel["y_spread"] <= 0.07 and pixel["y_p50"] < 0.32:
        notes.append("The set is consistently low-key.")
    elif pixel["y_spread"] <= 0.07 and pixel["y_p50"] > 0.62:
        notes.append("The set is consistently high-key.")
    shadow_hue = pixel.get("shadow_hue")
    highlight_hue = pixel.get("highlight_hue")
    if (
        shadow_hue is not None
        and highlight_hue is not None
        and pixel["shadow_sat"] >= 0.08
        and pixel["highlight_sat"] >= 0.08
        and angular_diff(shadow_hue, highlight_hue) >= 28
    ):
        notes.append(
            f"Shadows read {hue_name(shadow_hue)} and highlights read {hue_name(highlight_hue)}."
        )
    if not notes:
        notes.append("No strong shared grade jumped out of the pixels. The preset stays very light.")
    return notes


def review_paths(images: list[dict]) -> list[str]:
    if not images:
        return []
    ranked = sorted(images, key=lambda item: item["y_p50"])
    median_image = ranked[len(ranked) // 2]
    chosen = [ranked[0], median_image, ranked[-1], max(images, key=lambda item: item["mean_sat"])]
    paths = []
    for item in chosen:
        path = Path(item["path"])
        if path.suffix.lower() in REVIEW_EXTENSIONS and item["path"] not in paths:
            paths.append(item["path"])
    return paths[:6]


def hue_and_sat(rgb: tuple[float, float, float]) -> tuple[float | None, float]:
    red, green, blue = rgb
    peak = max(red, green, blue)
    floor = min(red, green, blue)
    delta = peak - floor
    if delta < 1e-6 or peak < 1e-6:
        return None, 0.0
    if peak == red:
        hue = ((green - blue) / delta) % 6
    elif peak == green:
        hue = (blue - red) / delta + 2
    else:
        hue = (red - green) / delta + 4
    return (hue * 60.0) % 360.0, delta / peak


def hue_name(hue: float) -> str:
    hue = hue % 360
    stops = (
        (15, "red"),
        (45, "orange"),
        (70, "yellow"),
        (165, "green"),
        (200, "cyan"),
        (255, "blue"),
        (295, "purple"),
        (345, "magenta"),
        (360, "red"),
    )
    for edge, name in stops:
        if hue < edge:
            return name
    return "red"


def warmth(rgb: tuple[float, float, float]) -> float:
    red, green, blue = rgb
    return (red - blue) / (red + green + blue + 1e-6)


def green_cast(rgb: tuple[float, float, float]) -> float:
    red, green, blue = rgb
    return (green - (red + blue) / 2.0) / (red + green + blue + 1e-6)


def angular_diff(left: float, right: float) -> float:
    return abs((left - right + 180) % 360 - 180)


def circular_mean(hues: list[float]) -> float:
    radians = [math.radians(hue) for hue in hues]
    mean = math.degrees(math.atan2(sum(math.sin(item) for item in radians), sum(math.cos(item) for item in radians)))
    return mean % 360


def circular_std(hues: list[float]) -> float:
    radians = [math.radians(hue) for hue in hues]
    resultant = math.hypot(sum(math.sin(item) for item in radians), sum(math.cos(item) for item in radians)) / len(radians)
    if resultant <= 1e-6:
        return 180.0
    return math.degrees(math.sqrt(max(0.0, -2.0 * math.log(min(resultant, 1.0)))))


def read_develop_rows(con: sqlite3.Connection, collection: str | None) -> tuple[list[dict], list[str]]:
    warnings = []
    table, column = find_xmp_column(con)
    columns = {row[1].lower(): row[1] for row in con.execute(f'PRAGMA table_info("{table}")')}
    image_column = columns.get("image")
    flag_column = columns.get("hasdevelopadjustmentsex") or columns.get("hasdevelopadjustments")
    select = [f'"{column}"']
    if image_column:
        select.append(f'"{image_column}"')
    if flag_column:
        select.append(f'"{flag_column}"')
    query = f'SELECT {", ".join(select)} FROM "{table}"'
    allowed_ids = None
    if collection:
        allowed_ids = collection_ids(con, collection)
        if image_column is None:
            raise PresetError("A collection was requested, but the develop table has no image id column to filter on.")
    rows = []
    for record in con.execute(query):
        text = record[0]
        cursor = 1
        image_id = None
        if image_column:
            image_id = record[cursor]
            cursor += 1
        flag = None
        if flag_column:
            flag = record[cursor]
        if allowed_ids is not None and image_id not in allowed_ids:
            continue
        if flag in (0, "0", False):
            continue
        if not text or "crs:" not in str(text):
            rows.append({"sliders": {}, "image": image_id})
            continue
        rows.append({"sliders": parse_sliders(str(text)), "image": image_id})
    if not rows:
        warnings.append("No develop-setting rows were found in the catalog.")
    return rows, warnings


def find_xmp_column(con: sqlite3.Connection) -> tuple[str, str]:
    tables = [row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    found = []
    for table in tables:
        if '"' in table:
            continue
        info = list(con.execute(f'PRAGMA table_info("{table}")'))
        for _cid, name, _kind, *_rest in info:
            if '"' in name:
                continue
            if name.lower() not in {"text", "xmp", "developsettings", "settings"} and "xmp" not in name.lower():
                continue
            try:
                sample = con.execute(
                    f'SELECT "{name}" FROM "{table}" WHERE "{name}" IS NOT NULL LIMIT 1'
                ).fetchone()
            except sqlite3.Error:
                continue
            if sample and sample[0] and "crs:" in str(sample[0])[:8000]:
                found.append((table, name))
    if not found:
        names = ", ".join(tables[:30]) or "(no tables)"
        raise PresetError(f"No column with Camera Raw settings (crs:) was found. Tables seen: {names}")
    found.sort(key=lambda item: (0 if "develop" in item[0].lower() else 1, item[0]))
    return found[0]


def collection_ids(con: sqlite3.Connection, name: str) -> set:
    tables = {row[0].lower(): row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    collection_table = tables.get("aglibrarycollection")
    member_table = tables.get("aglibrarycollectionimage")
    if not collection_table or not member_table:
        raise PresetError("This catalog has no collection tables, so --collection cannot be applied.")
    collections = con.execute(f'SELECT id_local, name FROM "{collection_table}"').fetchall()
    matches = [row[0] for row in collections if str(row[1]).lower() == name.lower()]
    if not matches:
        sample = ", ".join(sorted(str(row[1]) for row in collections)[:20]) or "(none)"
        raise PresetError(f"No collection named '{name}'. Names in the catalog: {sample}")
    members = con.execute(
        f'SELECT image FROM "{member_table}" WHERE collection = ?',
        (matches[0],),
    ).fetchall()
    return {row[0] for row in members}


def list_catalog_files(con: sqlite3.Connection, collection: str | None) -> list[Path]:
    tables = {row[0].lower(): row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    needed = ("adobe_images", "aglibraryfile", "aglibraryfolder", "aglibraryrootfolder")
    if any(name not in tables for name in needed):
        return []
    query = f'''
        SELECT root.absolutePath, folder.pathFromRoot, file.baseName, file.extension
        FROM "{tables["adobe_images"]}" AS image
        JOIN "{tables["aglibraryfile"]}" AS file ON file.id_local = image.rootFile
        JOIN "{tables["aglibraryfolder"]}" AS folder ON folder.id_local = file.folder
        JOIN "{tables["aglibraryrootfolder"]}" AS root ON root.id_local = folder.rootFolder
    '''
    params: tuple = ()
    if collection and "aglibrarycollectionimage" in tables:
        ids = collection_ids(con, collection)
        if not ids:
            return []
        placeholders = ",".join("?" for _ in ids)
        query += f' WHERE image.id_local IN ({placeholders})'
        params = tuple(ids)
    paths = []
    try:
        records = con.execute(query, params).fetchall()
    except sqlite3.Error:
        return []
    for absolute, relative, base, extension in records:
        if not absolute or not base:
            continue
        suffix = extension or ""
        if suffix and not str(suffix).startswith("."):
            suffix = "." + str(suffix)
        paths.append(Path(str(absolute)) / str(relative or "") / f"{base}{suffix}")
    return paths


def parse_sliders(xmp: str) -> dict:
    parsed = {}
    for key, raw in SLIDER_RE.findall(xmp):
        if not allowed_develop_key(key):
            continue
        if key == "ConvertToGrayscale":
            if raw in {"True", "False"}:
                parsed[key] = raw == "True"
            continue
        if NUMBER_RE.match(raw):
            parsed[key] = float(raw)
    return parsed


def allowed_develop_key(key: str) -> bool:
    if key in DEVELOP_ALLOW:
        return True
    return key.startswith(HSL_PREFIXES) or key.startswith(("ColorGrade", "SplitToning", "Parametric", "PostCropVignette", "Grain"))


def row_is_edited(sliders: dict) -> bool:
    if sliders.get("ConvertToGrayscale") is True:
        return True
    for key, value in sliders.items():
        if key in {"Temperature", "Tint", "ConvertToGrayscale"}:
            continue
        if isinstance(value, (int, float)) and abs(value) >= (0.05 if key == "Exposure2012" else 0.5):
            return True
    return False


def median_settings(rows: list[dict]) -> dict:
    if not rows:
        return {}
    keys = set()
    for row in rows:
        keys.update(row)
    keys.discard("ConvertToGrayscale")
    count = len(rows)
    result = {}
    for key in sorted(keys):
        if key in {"Temperature", "Tint"}:
            values = [row[key] for row in rows if key in row]
            if len(values) < max(1, math.ceil(0.7 * count)):
                continue
            spread_limit = 800 if key == "Temperature" else 20
            if len(values) >= 2 and max(values) - min(values) > spread_limit:
                continue
            result[key] = statistics.median(values)
            continue
        values = [float(row.get(key, 0.0)) for row in rows]
        result[key] = statistics.median(values)
    if sum(1 for row in rows if row.get("ConvertToGrayscale") is True) * 2 > count:
        result["ConvertToGrayscale"] = True
    return result


def white_balance_warning(median: dict, rows: list[dict]) -> str | None:
    temps = [row["Temperature"] for row in rows if "Temperature" in row]
    if len(temps) >= 2 and max(temps) - min(temps) > 800 and "Temperature" not in median:
        return "White balance Kelvin varied across the catalog, so it was left out. Set Temperature yourself."
    if "Temperature" in median:
        return "White balance Kelvin is the median from the catalog and will replace As Shot on raw files."
    return None


def build_preset(
    stats: dict,
    style: str,
    strength: float | None = None,
    overrides: dict | None = None,
    allow_strong: bool = False,
    white_balance: bool = True,
    name: str | None = None,
    group: str = "Starting Points",
) -> dict:
    styles = load_styles()
    style_id = resolve_style(style)
    if style_id == "custom":
        recipe = {"label": "Custom", "summary": "Sliders translated from the requested description.", "sliders": {}, "curve": None, "grayscale": False}
    else:
        recipe = styles[style_id]
    source = stats.get("source") or "folder"
    used_strength = default_strength(source, style_id) if strength is None else float(strength)
    if used_strength <= 0 or used_strength > 1.5:
        raise PresetError("--strength must be greater than 0 and at most 1.5.")
    reasons: dict[str, str] = {}
    warnings = list(stats.get("warnings") or [])
    sliders: dict = {}
    curve = None
    grayscale = False

    if style_id == "match" and stats.get("median_sliders"):
        sliders, reasons = from_measured_sliders(stats["median_sliders"], used_strength)
        warnings.append("Matched the catalog's own develop sliders, then softened them. This is still a starting point.")
    elif style_id == "match":
        pixel = stats.get("pixel")
        if not pixel:
            raise PresetError("Nothing to match: no pixel measurements and no develop settings.")
        sliders, curve, reasons = from_pixels(pixel, used_strength)
        warnings.append("Matched from rendered pixels, not from raw slider data. Subject color was ignored. Expect to move Exposure and White Balance.")
    else:
        sliders = {key: value for key, value in recipe.get("sliders", {}).items()}
        curve = recipe.get("curve")
        grayscale = bool(recipe.get("grayscale"))
        for key in list(sliders):
            if scales_with_strength(key):
                sliders[key] = float(sliders[key]) * used_strength
            reasons[key] = "Part of the chosen style."
        if curve:
            curve = scale_curve(curve, used_strength)
            reasons["ToneCurve"] = "Part of the chosen style."
        pixel = stats.get("pixel")
        if pixel:
            compensate(sliders, pixel, reasons)
        elif style_id != "custom":
            warnings.append("No pixel measurements, so the style was not adjusted for this catalog's brightness or contrast.")

    if grayscale or sliders.get("ConvertToGrayscale") is True:
        sliders["ConvertToGrayscale"] = True
        sliders.pop("Saturation", None)
        reasons["ConvertToGrayscale"] = "Black and white treatment, so global saturation is left out."

    for key, value in (overrides or {}).items():
        check_override_key(key)
        sliders[key] = value
        reasons[key] = "Set explicitly for this request."

    if not white_balance:
        for key in WB_KEYS:
            sliders.pop(key, None)
            reasons.pop(key, None)
        warnings.append("White balance sliders were left out.")

    sliders = mirror_color_grade(sliders)
    sliders, clamp_notes = clamp_sliders(sliders, allow_strong=allow_strong)
    for key, note in clamp_notes.items():
        reasons[key] = f"{reasons[key]} {note}" if key in reasons else note
    sliders = drop_negligible(sliders)
    if curve:
        curve = drop_flat_curve(curve)
    if not sliders and not curve:
        raise PresetError("The preset would be empty. Give a stronger style, more photos, or explicit --set sliders.")

    label = recipe["label"]
    preset_name = name or (f"{label} (start)" if style_id != "match" else "Catalog match (start)")
    description = f"Starting point. {recipe['summary']}"
    return {
        "name": preset_name,
        "group": group,
        "description": description,
        "style": style_id,
        "strength": used_strength,
        "sliders": sliders,
        "curve": curve,
        "reasons": reasons,
        "warnings": warnings,
        "observations": list(stats.get("observations") or []),
        "source": source,
        "catalog": stats.get("catalog"),
        "photo_count": stats.get("photo_count"),
        "sampled": stats.get("sampled"),
    }


def from_measured_sliders(measured: dict, strength: float) -> tuple[dict, dict]:
    sliders = {}
    reasons = {}
    for key, value in measured.items():
        if key == "ConvertToGrayscale":
            sliders[key] = bool(value)
            reasons[key] = "Most edited photos in the sample are black and white."
            continue
        number = float(value)
        if scales_with_strength(key):
            number *= strength
        sliders[key] = number
        reasons[key] = "Median of develop settings stored in the catalog, softened."
    return sliders, reasons


def from_pixels(pixel: dict, strength: float) -> tuple[dict, list | None, dict]:
    sliders = {}
    reasons = {}
    span = float(pixel["span"])
    contrast = (span - 0.78) * 55 * strength
    if abs(contrast) >= 3:
        sliders["Contrast2012"] = contrast
        reasons["Contrast2012"] = "Contrast follows how wide the tonal range of the catalog is, pulled toward a normal frame."

    if float(pixel["y_p05"]) > 0.06:
        blacks = (float(pixel["y_p05"]) - 0.045) * 80 * strength
        sliders["Blacks2012"] = blacks
        reasons["Blacks2012"] = "The dark end of these files sits above black, so blacks are lifted a little."
    elif float(pixel["black_clip"]) > 0.03:
        sliders["Blacks2012"] = -10 * strength
        reasons["Blacks2012"] = "A visible share of pixels is crushed, so blacks go slightly deeper."

    if float(pixel["y_p25"]) > 0.28:
        sliders["Shadows2012"] = (float(pixel["y_p25"]) - 0.22) * 70 * strength
        reasons["Shadows2012"] = "Shadows in the catalog are already open."
    elif float(pixel["y_p25"]) < 0.12:
        sliders["Shadows2012"] = (float(pixel["y_p25"]) - 0.18) * 70 * strength
        reasons["Shadows2012"] = "Shadows in the catalog are heavy."

    if float(pixel["y_p95"]) < 0.88:
        sliders["Highlights2012"] = (float(pixel["y_p95"]) - 0.92) * 100 * strength
        reasons["Highlights2012"] = "Highlights do not reach the top of the scale, so they are rolled off slightly."
    if float(pixel["white_clip"]) > 0.03:
        sliders["Highlights2012"] = sliders.get("Highlights2012", 0) - 8 * strength
        reasons["Highlights2012"] = "Bright pixels are clipping, so highlights are pulled down."

    sat_delta = (float(pixel["mean_sat"]) - 0.32) * 36 * strength
    if abs(sat_delta) >= 3:
        sliders["Vibrance"] = sat_delta * 0.75
        sliders["Saturation"] = sat_delta * 0.35
        reasons["Vibrance"] = "Colorfulness is nudged toward a moderate frame. Most of it is vibrance, not saturation."
        reasons["Saturation"] = reasons["Vibrance"]

    grade = False
    shadow_hue = pixel.get("shadow_hue")
    highlight_hue = pixel.get("highlight_hue")
    if (
        shadow_hue is not None
        and highlight_hue is not None
        and float(pixel["shadow_sat"]) >= 0.08
        and float(pixel["highlight_sat"]) >= 0.08
        and angular_diff(float(shadow_hue), float(highlight_hue)) >= 28
        and float(pixel.get("shadow_hue_std") or 0) <= 40
        and float(pixel.get("highlight_hue_std") or 0) <= 40
    ):
        shadow_sat = float(pixel["shadow_sat"]) * 32 * strength
        highlight_sat = float(pixel["highlight_sat"]) * 32 * strength
        if shadow_sat >= 6 or highlight_sat >= 6:
            sliders["ColorGradeShadowHue"] = float(shadow_hue)
            sliders["ColorGradeShadowSat"] = shadow_sat
            sliders["ColorGradeHighlightHue"] = float(highlight_hue)
            sliders["ColorGradeHighlightSat"] = highlight_sat
            sliders["ColorGradeBlending"] = 50
            reasons["ColorGradeShadowSat"] = "Shadow and highlight hues disagree across the catalog, so a light color grade was added."
            reasons["ColorGradeHighlightSat"] = reasons["ColorGradeShadowSat"]
            grade = True

    warm = float(pixel["warm"])
    green = float(pixel["green"])
    temperature = warm * 70 * strength * (0.45 if grade else 1)
    tint = -green * 55 * strength
    if abs(temperature) >= 3:
        sliders["IncrementalTemperature"] = temperature
        reasons["IncrementalTemperature"] = "A mild warmth or coolness from the midtones. This moves JPEG white balance only, not raw Kelvin."
    if abs(tint) >= 3:
        sliders["IncrementalTint"] = tint
        reasons["IncrementalTint"] = "A mild green or magenta nudge from the midtones, for JPEG and TIFF."

    if float(pixel["y_spread"]) <= 0.07:
        ev = math.log2(max(float(pixel["y_p50"]), 0.05) / 0.46)
        nudged = ev * 0.35 * strength
        if abs(nudged) >= 0.08:
            sliders["Exposure2012"] = max(-0.35, min(0.35, nudged))
            reasons["Exposure2012"] = "The whole set shares one brightness, so exposure gets a small nudge. Mixed scenes do not."

    curve = None
    # The basic sliders already express a lifted black or a rolled highlight.
    # A second copy of that move on the point curve makes the start too heavy.
    lift = 0
    rolloff = 0
    if float(pixel["y_p05"]) > 0.06 and float(sliders.get("Blacks2012", 0)) <= 0:
        lift = int(round(min(28, (float(pixel["y_p05"]) - 0.03) * 70 * strength)))
    if float(pixel["y_p99"]) < 0.94 and float(sliders.get("Highlights2012", 0)) > -5:
        rolloff = int(round(min(24, (0.98 - float(pixel["y_p99"])) * 80 * strength)))
    if lift >= 8 or rolloff >= 8:
        curve = [[0, lift], [255, 255 - rolloff]]
        reasons["ToneCurve"] = "The point curve lifts the black point or eases the white point to match a faded file."
    return sliders, curve, reasons


def compensate(sliders: dict, pixel: dict, reasons: dict) -> None:
    """Pull a style recipe back when the catalog is already there."""
    y50 = float(pixel["y_p50"])
    span = float(pixel["span"])
    sat = float(pixel["mean_sat"])
    if y50 > 0.58 and float(sliders.get("Exposure2012", 0)) > 0:
        sliders["Exposure2012"] = float(sliders["Exposure2012"]) * 0.35
        reasons["Exposure2012"] = "The catalog is already bright, so the exposure lift was reduced."
    if y50 < 0.34 and float(sliders.get("Exposure2012", 0)) < 0:
        sliders["Exposure2012"] = float(sliders["Exposure2012"]) * 0.35
        reasons["Exposure2012"] = "The catalog is already dark, so the exposure cut was reduced."
    if span < 0.62 and float(sliders.get("Contrast2012", 0)) < 0:
        sliders["Contrast2012"] = float(sliders["Contrast2012"]) * 0.45
        reasons["Contrast2012"] = "The catalog is already flat, so the contrast cut was reduced."
    if span > 0.9 and float(sliders.get("Contrast2012", 0)) > 0:
        sliders["Contrast2012"] = float(sliders["Contrast2012"]) * 0.45
        reasons["Contrast2012"] = "The catalog is already contrasty, so the contrast boost was reduced."
    if sat > 0.45 and float(sliders.get("Vibrance", 0)) > 0:
        sliders["Vibrance"] = float(sliders["Vibrance"]) * 0.4
        reasons["Vibrance"] = "The catalog is already colorful, so the vibrance boost was reduced."
    if sat < 0.18 and float(sliders.get("Vibrance", 0)) < 0:
        sliders["Vibrance"] = float(sliders["Vibrance"]) * 0.4
        reasons["Vibrance"] = "The catalog is already muted, so the vibrance cut was reduced."


def scale_curve(curve: list, strength: float) -> list:
    scaled = []
    for point in curve:
        x_value, y_value = int(point[0]), float(point[1])
        y_value = x_value + (y_value - x_value) * strength
        scaled.append([x_value, int(round(y_value))])
    return scaled


def scales_with_strength(key: str) -> bool:
    return key not in UNSCALED


def mirror_color_grade(sliders: dict) -> dict:
    mirrored = dict(sliders)
    for left, right in GRADE_MIRRORS:
        if left in mirrored and right not in mirrored:
            mirrored[right] = mirrored[left]
        elif right in mirrored and left not in mirrored:
            mirrored[left] = mirrored[right]
    sat_keys = ("ColorGradeShadowSat", "ColorGradeHighlightSat", "ColorGradeMidtoneSat", "ColorGradeGlobalSat")
    if any(float(mirrored.get(key, 0)) > 0 for key in sat_keys) and "ColorGradeBlending" not in mirrored:
        mirrored["ColorGradeBlending"] = 50
    return mirrored


def clamp_sliders(sliders: dict, allow_strong: bool) -> tuple[dict, dict]:
    clamped = {}
    notes = {}
    for key, value in sliders.items():
        if key == "ConvertToGrayscale":
            clamped[key] = bool(value)
            continue
        number = float(value)
        low, high = clamp_bounds(key, allow_strong)
        limited = min(high, max(low, number))
        if key in HUE_WHEELS:
            limited = float(int(round(number)) % 360)
        else:
            notice = 0.05 if key == "Exposure2012" else 0.6
            if abs(limited - number) >= notice:
                notes[key] = (
                    f"Held at {format_value(key, limited)} so the preset stays a starting point "
                    f"(asked for {format_value(key, number)})."
                )
        clamped[key] = limited
    return clamped, notes


def clamp_bounds(key: str, allow_strong: bool) -> tuple[float, float]:
    if key in HUE_WHEELS:
        return (0, 359)
    if allow_strong:
        if key in STRONG_CLAMPS:
            return STRONG_CLAMPS[key]
        if key.startswith(HSL_PREFIXES):
            return (-80, 80)
        return (-100, 100)
    if key in CLAMPS:
        return CLAMPS[key]
    if key.startswith(HSL_PREFIXES):
        return (-12, 12)
    return (-20, 20)


def drop_negligible(sliders: dict) -> dict:
    kept = {}
    for key, value in sliders.items():
        if key == "ConvertToGrayscale":
            if value is True:
                kept[key] = True
            continue
        if key in COMPANION_KEYS or key in HUE_WHEELS or key == "ColorGradeBlending":
            kept[key] = value
            continue
        number = float(value)
        if key == "Exposure2012":
            if abs(number) >= 0.05:
                kept[key] = number
            continue
        if abs(number) >= 0.5:
            kept[key] = number
    if "GrainAmount" not in kept:
        kept.pop("GrainSize", None)
        kept.pop("GrainFrequency", None)
    if "PostCropVignetteAmount" not in kept:
        for key in list(kept):
            if key.startswith("PostCropVignette") and key != "PostCropVignetteAmount":
                kept.pop(key, None)
    grade_sats = [key for key in ("ColorGradeShadowSat", "ColorGradeHighlightSat", "ColorGradeMidtoneSat", "ColorGradeGlobalSat") if key in kept]
    if not grade_sats:
        for key in list(kept):
            if key.startswith("ColorGrade") or key.startswith("SplitToning"):
                kept.pop(key, None)
    else:
        if "ColorGradeShadowSat" not in kept:
            kept.pop("ColorGradeShadowHue", None)
            kept.pop("SplitToningShadowHue", None)
            kept.pop("SplitToningShadowSaturation", None)
        if "ColorGradeHighlightSat" not in kept:
            kept.pop("ColorGradeHighlightHue", None)
            kept.pop("SplitToningHighlightHue", None)
            kept.pop("SplitToningHighlightSaturation", None)
    return kept


def drop_flat_curve(curve: list) -> list | None:
    if all(abs(int(point[0]) - int(point[1])) < 2 for point in curve):
        return None
    cleaned = []
    for point in curve:
        x_value = max(0, min(255, int(point[0])))
        y_value = max(0, min(255, int(round(point[1]))))
        cleaned.append([x_value, y_value])
    cleaned = sorted(cleaned, key=lambda point: point[0])
    if cleaned[0][0] != 0:
        cleaned.insert(0, [0, 0])
    if cleaned[-1][0] != 255:
        cleaned.append([255, 255])
    return cleaned


def check_override_key(key: str) -> None:
    if key in CLAMPS or key in HUE_WHEELS or key == "ConvertToGrayscale" or key.startswith(HSL_PREFIXES):
        return
    if key.startswith(("ColorGrade", "SplitToning", "PostCropVignette", "Grain", "Parametric")):
        return
    raise PresetError(f"Unknown slider '{key}'. See references/sliders.md for names Lightroom will honor.")


def write_outputs(preset: dict, xmp_path: Path, notes_path: Path | None) -> None:
    xmp_path.parent.mkdir(parents=True, exist_ok=True)
    xmp_path.write_text(render_xmp(preset), encoding="utf-8")
    if notes_path is not None:
        notes_path.parent.mkdir(parents=True, exist_ok=True)
        notes_path.write_text(render_notes(preset, xmp_path), encoding="utf-8")


def render_xmp(preset: dict) -> str:
    attributes = {
        "PresetType": "Normal",
        "Cluster": "",
        "UUID": uuid.uuid4().hex.upper(),
        "SupportsAmount2": "True",
        "SupportsAmount": "True",
        "SupportsColor": "True",
        "SupportsMonochrome": "True",
        "SupportsHighDynamicRange": "True",
        "SupportsNormalDynamicRange": "True",
        "SupportsSceneReferred": "True",
        "SupportsOutputReferred": "True",
        "RequiresRGBTables": "False",
        "CameraModelRestriction": "",
        "Copyright": "",
        "ContactInfo": "",
        "Version": "15.4",
        "HasSettings": "True",
    }
    sliders = preset["sliders"]
    if any(key in sliders for key in WB_KEYS):
        attributes["WhiteBalance"] = "Custom"
    if preset.get("curve"):
        attributes["ToneCurveName2012"] = "Custom"
    for key in SLIDER_ORDER:
        if key in sliders:
            attributes[key] = format_value(key, sliders[key])
    extras = sorted(key for key in sliders if key not in attributes and key != "ConvertToGrayscale")
    for key in extras:
        attributes[key] = format_value(key, sliders[key])
    if sliders.get("ConvertToGrayscale") is True:
        attributes["ConvertToGrayscale"] = "True"

    attr_text = "\n".join(f'    crs:{key}="{escape(str(value), {'"': "&quot;"})}"' for key, value in attributes.items())
    children = [
        alt_block("Name", preset["name"]),
        alt_block("ShortName", ""),
        alt_block("SortName", ""),
        alt_block("Group", preset["group"]),
        alt_block("Description", preset["description"]),
    ]
    if preset.get("curve"):
        children.append(curve_block("ToneCurvePV2012", preset["curve"]))
        for channel in ("ToneCurvePV2012Red", "ToneCurvePV2012Green", "ToneCurvePV2012Blue"):
            children.append(curve_block(channel, [[0, 0], [255, 255]]))
    inner = "\n".join(children)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="Adobe XMP Core 5.6-c140 79.160451, 2017/05/06-01:08:21">\n'
        ' <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">\n'
        '  <rdf:Description rdf:about=""\n'
        f'    xmlns:crs="{CRS_NS}"\n'
        f"{attr_text}>\n"
        f"{inner}\n"
        "  </rdf:Description>\n"
        " </rdf:RDF>\n"
        "</x:xmpmeta>\n"
    )


def alt_block(tag: str, text: str) -> str:
    return (
        f"   <crs:{tag}>\n"
        "    <rdf:Alt>\n"
        f'     <rdf:li xml:lang="x-default">{escape(text)}</rdf:li>\n'
        "    </rdf:Alt>\n"
        f"   </crs:{tag}>"
    )


def curve_block(tag: str, points: list) -> str:
    items = "\n".join(f"     <rdf:li>{int(point[0])}, {int(point[1])}</rdf:li>" for point in points)
    return f"   <crs:{tag}>\n    <rdf:Seq>\n{items}\n    </rdf:Seq>\n   </crs:{tag}>"


def format_value(key: str, value) -> str:
    if key == "ConvertToGrayscale":
        return "True" if value else "False"
    if isinstance(value, str):
        return value
    number = float(value)
    if key == "Exposure2012":
        return f"{number:.2f}"
    if key in HUE_WHEELS:
        return str(int(round(number)) % 360)
    rounded = int(round(number))
    return str(rounded)


def render_notes(preset: dict, xmp_path: Path) -> str:
    lines = [
        f"# {preset['name']}",
        "",
        preset["description"],
        "",
        "This is a starting point for Lightroom, not a finished grade. Apply it, then use the Amount slider. Move Exposure and White Balance before the smaller sliders.",
        "",
        f"- Style: `{preset['style']}`",
        f"- Strength: {preset['strength']}",
        f"- Source: {preset['source']}",
        f"- Catalog: {preset.get('catalog')}",
        f"- Photos considered: {preset.get('photo_count')}; measured: {preset.get('sampled')}",
        f"- Preset file: `{xmp_path}`",
        "",
        "Only the sliders below are in the file. Lightroom leaves every other slider, the camera profile, crop, masks, sharpening and noise reduction as they are.",
        "",
        "## Sliders",
        "",
        "| Slider | Value | Why |",
        "|---|---:|---|",
    ]
    for key, value in ordered_sliders(preset["sliders"]).items():
        why = preset["reasons"].get(key, "")
        if key.startswith("SplitToning") and not why:
            why = "Same color grade, written under the older split-toning name so more Lightroom versions see it."
        lines.append(f"| `{key}` | {format_value(key, value)} | {why} |")
    if preset.get("curve"):
        pretty = ", ".join(f"{point[0]}→{point[1]}" for point in preset["curve"])
        lines.append(f"| point curve | {pretty} | {preset['reasons'].get('ToneCurve', '')} |")
    if preset.get("observations"):
        lines.extend(["", "## What the photos suggested", ""])
        for note in preset["observations"]:
            lines.append(f"- {note}")
    if preset.get("warnings"):
        lines.extend(["", "## Watch-outs", ""])
        for note in preset["warnings"]:
            lines.append(f"- {note}")
    lines.extend(
        [
            "",
            "## Import",
            "",
            "Lightroom Classic: Develop → Presets → **+** → **Import Presets…** and choose the `.xmp`.",
            "",
            "Po polsku: Wywoływanie → Ustawienia predefiniowane → **+** → **Importuj ustawienia predefiniowane…**",
            "",
            f"The group name inside the file is **{preset['group']}**.",
            "",
            "Or copy the file and restart Lightroom:",
            "",
            "- Windows: `%APPDATA%\\Adobe\\CameraRaw\\Settings`",
            "- macOS: `~/Library/Application Support/Adobe/CameraRaw/Settings`",
            "",
            "After it is applied, Amount at 100% is this starting point. Lower Amount if it is too much.",
            "",
        ]
    )
    return "\n".join(lines)


def ordered_sliders(sliders: dict) -> dict:
    ordered = {}
    for key in SLIDER_ORDER:
        if key in sliders:
            ordered[key] = sliders[key]
    for key in sorted(sliders):
        if key not in ordered:
            ordered[key] = sliders[key]
    return ordered


def parse_override(text: str) -> tuple[str, object]:
    if "=" not in text:
        raise PresetError(f"--set must look like Key=Value, not '{text}'")
    key, raw = text.split("=", 1)
    key = key.strip()
    raw = raw.strip()
    check_override_key(key)
    if raw in {"True", "true"}:
        return key, True
    if raw in {"False", "false"}:
        return key, False
    if not NUMBER_RE.match(raw):
        raise PresetError(f"Slider {key} needs a number, not '{raw}'")
    return key, float(raw)


def read_stats(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PresetError(f"Could not read stats JSON {path}: {exc}") from exc


def round_tree(value):
    if isinstance(value, float):
        return round(value, 4)
    if isinstance(value, dict):
        return {key: round_tree(item) for key, item in value.items()}
    if isinstance(value, list):
        return [round_tree(item) for item in value]
    return value


def xmp_is_well_formed(path: Path) -> ET.Element:
    root = ET.parse(path).getroot()
    description = None
    for element in root.iter():
        if element.tag == f"{{{RDF_NS}}}Description":
            description = element
            break
    if description is None:
        raise PresetError("XMP has no rdf:Description.")
    return description
