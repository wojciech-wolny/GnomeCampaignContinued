#!/usr/bin/env python3
"""Checks the measurer and the .xmp writer against synthetic photos and a fake catalog."""

from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))

import presetlib

CRS = "{http://ns.adobe.com/camera-raw-settings/1.0/}"
RDF = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        check_styles()
        check_warm_fade(root / "warm")
        check_teal_orange(root / "teal")
        check_exposure_consistency(root / "keys")
        check_style_compensation(root / "comp")
        check_lrcat(root / "catalog")
        check_overrides(root / "override-stats.json")
        check_cli(root / "cli")
        check_empty(root / "empty")
    print("self-test ok")
    return 0


def check_styles() -> None:
    styles = presetlib.load_styles()
    for style_id, recipe in styles.items():
        for key in recipe.get("sliders", {}):
            presetlib.check_override_key(key)
        assert style_id == presetlib.resolve_style(style_id)
    assert presetlib.resolve_style("teal") == "teal-orange"
    assert presetlib.resolve_style("BW") == "black-and-white"
    try:
        presetlib.resolve_style("nope")
    except presetlib.PresetError:
        pass
    else:
        raise AssertionError("unknown style should fail")


def check_warm_fade(folder: Path) -> None:
    folder.mkdir()
    for index in range(4):
        make_warm_fade(folder / f"warm-{index}.png", shift=index)
    stats = presetlib.analyze_catalog(folder)
    assert stats["source"] == "folder"
    assert stats["sampled"] == 4
    assert any("warm" in note.lower() or "lifted" in note.lower() for note in stats["observations"])
    preset = presetlib.build_preset(stats, "match")
    sliders = preset["sliders"]
    assert sliders["Blacks2012"] >= 10
    assert sliders["Contrast2012"] < 0
    assert sliders["IncrementalTemperature"] >= 3
    assert "Temperature" not in sliders
    assert preset.get("curve") is None
    xmp = folder / "warm.xmp"
    presetlib.write_outputs(preset, xmp, xmp.with_suffix(".notes.md"))
    description = read_xmp(xmp)
    assert description.attrib[f"{CRS}SupportsAmount2"] == "True"
    assert f"{CRS}ProcessVersion" not in description.attrib
    assert len(description.attrib[f"{CRS}UUID"]) == 32
    assert description.find(f"{CRS}Look") is None
    notes = xmp.with_suffix(".notes.md").read_text(encoding="utf-8")
    assert "starting point" in notes.lower()
    assert "Importuj ustawienia predefiniowane" in notes


def check_teal_orange(folder: Path) -> None:
    folder.mkdir()
    for index in range(3):
        make_teal_orange(folder / f"split-{index}.png")
    stats = presetlib.analyze_catalog(folder)
    joined = " ".join(stats["observations"]).lower()
    assert "cyan" in joined or "blue" in joined
    assert "orange" in joined
    preset = presetlib.build_preset(stats, "match")
    sliders = preset["sliders"]
    assert 160 <= sliders["ColorGradeShadowHue"] <= 210
    assert 20 <= sliders["ColorGradeHighlightHue"] <= 55
    assert sliders["ColorGradeShadowSat"] >= 6
    assert sliders["SplitToningShadowHue"] == sliders["ColorGradeShadowHue"]
    assert "Temperature" not in sliders


def check_exposure_consistency(folder: Path) -> None:
    bright = folder / "bright"
    mixed = folder / "mixed"
    bright.mkdir(parents=True)
    mixed.mkdir()
    for index in range(3):
        solid(bright / f"{index}.png", (200, 200, 200))
    solid(mixed / "dark.png", (40, 40, 40))
    solid(mixed / "bright.png", (200, 200, 200))
    bright_preset = presetlib.build_preset(presetlib.analyze_catalog(bright), "match")
    assert 0.08 < bright_preset["sliders"]["Exposure2012"] < 0.40
    mixed_preset = presetlib.build_preset(presetlib.analyze_catalog(mixed), "match")
    assert "Exposure2012" not in mixed_preset["sliders"]


def check_style_compensation(folder: Path) -> None:
    folder.mkdir()
    solid(folder / "bright.png", (210, 210, 210))
    solid(folder / "also.png", (205, 205, 205))
    stats = presetlib.analyze_catalog(folder)
    airy = presetlib.build_preset(stats, "airy-bright")
    assert 0 < airy["sliders"]["Exposure2012"] < 0.12
    flat = folder / "flat"
    flat.mkdir()
    solid(flat / "gray.png", (140, 140, 140))
    matte = presetlib.build_preset(presetlib.analyze_catalog(flat), "matte-fade")
    assert -12 < matte["sliders"]["Contrast2012"] < 0
    vintage = presetlib.build_preset(stats, "vintage")
    assert vintage["curve"][0][1] >= 8
    assert 0 < vintage["sliders"]["GrainAmount"] <= 20
    teal = presetlib.build_preset(stats, "teal-orange")
    assert teal["sliders"]["ColorGradeShadowHue"] == 190
    assert teal["sliders"]["SplitToningHighlightHue"] == teal["sliders"]["ColorGradeHighlightHue"]
    mono = presetlib.build_preset(stats, "bw")
    assert mono["sliders"]["ConvertToGrayscale"] is True
    assert "Saturation" not in mono["sliders"]


def check_lrcat(folder: Path) -> None:
    folder.mkdir()
    catalog = folder / "Test.lrcat"
    con = sqlite3.connect(catalog)
    con.executescript(
        """
        CREATE TABLE Adobe_imageDevelopSettings (
            id_local INTEGER,
            image INTEGER,
            text TEXT,
            hasDevelopAdjustmentsEx INTEGER
        );
        CREATE TABLE Adobe_images (id_local INTEGER, rootFile INTEGER);
        CREATE TABLE AgLibraryFile (
            id_local INTEGER, folder INTEGER, baseName TEXT, extension TEXT
        );
        CREATE TABLE AgLibraryFolder (
            id_local INTEGER, pathFromRoot TEXT, rootFolder INTEGER
        );
        CREATE TABLE AgLibraryRootFolder (id_local INTEGER, absolutePath TEXT);
        CREATE TABLE AgLibraryCollection (id_local INTEGER, name TEXT);
        CREATE TABLE AgLibraryCollectionImage (collection INTEGER, image INTEGER);
        """
    )
    def xmp(exposure: str, contrast: str, temperature: str | None = None) -> str:
        temp = f' crs:Temperature="{temperature}" crs:Tint="3"' if temperature else ""
        return (
            '<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">'
            f'<rdf:Description xmlns:crs="http://ns.adobe.com/camera-raw-settings/1.0/" '
            f'crs:Exposure2012="{exposure}" crs:Contrast2012="{contrast}"{temp}/></rdf:RDF></x:xmpmeta>'
        )
    rows = [
        (1, 1, xmp("1.00", "20", "5200"), 1),
        (2, 2, xmp("0.20", "20", "5400"), 1),
        (3, 3, xmp("5.00", "80"), 0),
        (4, 4, None, 1),
    ]
    con.executemany("INSERT INTO Adobe_imageDevelopSettings VALUES (?, ?, ?, ?)", rows)
    con.execute("INSERT INTO AgLibraryCollection VALUES (1, 'Keep')")
    con.execute("INSERT INTO AgLibraryCollectionImage VALUES (1, 1)")
    con.commit()
    con.close()

    stats = presetlib.analyze_catalog(catalog)
    assert stats["source"] == "lrcat-develop"
    assert stats["edited_count"] == 2
    assert "Temperature" in stats["median_sliders"]
    preset = presetlib.build_preset(stats, "match")
    assert abs(preset["sliders"]["Exposure2012"] - 0.45) < 0.02
    assert preset["sliders"]["Contrast2012"] == 15
    assert preset["sliders"]["Temperature"] == 5300
    assert any("As Shot" in note for note in preset["warnings"])

    kept = presetlib.analyze_catalog(catalog, collection="Keep")
    kept_preset = presetlib.build_preset(kept, "match")
    # +1.00 EV softened by 0.75 is +0.75, then the starting-point cap holds it at +0.60.
    assert abs(kept_preset["sliders"]["Exposure2012"] - 0.60) < 0.02
    assert "Held at" in kept_preset["reasons"]["Exposure2012"]

    wide = folder / "Wide.lrcat"
    con = sqlite3.connect(wide)
    con.execute("CREATE TABLE Adobe_imageDevelopSettings (id_local INTEGER, image INTEGER, text TEXT)")
    con.execute(
        "INSERT INTO Adobe_imageDevelopSettings VALUES (1, 1, ?)",
        (xmp("0.40", "10", "4800"),),
    )
    con.execute(
        "INSERT INTO Adobe_imageDevelopSettings VALUES (2, 2, ?)",
        (xmp("0.40", "10", "9000"),),
    )
    con.commit()
    con.close()
    wide_stats = presetlib.analyze_catalog(wide)
    assert "Temperature" not in wide_stats["median_sliders"]
    assert any("Kelvin" in note for note in wide_stats["warnings"])

    try:
        presetlib.analyze_catalog(catalog, collection="Missing")
    except presetlib.PresetError as exc:
        assert "Keep" in str(exc)
    else:
        raise AssertionError("missing collection should fail")


def check_overrides(stats_path: Path) -> None:
    stats = {
        "source": "folder",
        "catalog": "none",
        "photo_count": 0,
        "sampled": 0,
        "warnings": [],
        "observations": [],
        "pixel": None,
        "median_sliders": None,
    }
    stats_path.write_text(json.dumps(stats), encoding="utf-8")
    held = presetlib.build_preset(stats, "custom", overrides={"Contrast2012": 80})
    assert held["sliders"]["Contrast2012"] == 25
    strong = presetlib.build_preset(stats, "custom", overrides={"Contrast2012": 80}, allow_strong=True)
    assert strong["sliders"]["Contrast2012"] == 80
    try:
        presetlib.build_preset(stats, "custom")
    except presetlib.PresetError:
        pass
    else:
        raise AssertionError("empty custom preset should fail")
    named = presetlib.build_preset(
        stats,
        "custom",
        overrides={"Clarity2012": 4},
        name='Warm & "fade"',
    )
    xmp = stats_path.with_suffix(".xmp")
    presetlib.write_outputs(named, xmp, None)
    text = xmp.read_text(encoding="utf-8")
    assert "Warm &amp; \"fade\"" in text
    ET.parse(xmp)


def check_cli(folder: Path) -> None:
    folder.mkdir()
    make_warm_fade(folder / "one.png", shift=0)
    stats = folder / "stats.json"
    xmp = folder / "out.xmp"
    scripts = Path(__file__).resolve().parent
    subprocess.run(
        [sys.executable, str(scripts / "analyze_catalog.py"), "--catalog", str(folder), "--out", str(stats)],
        check=True,
    )
    subprocess.run(
        [
            sys.executable,
            str(scripts / "write_preset.py"),
            "--stats",
            str(stats),
            "--style",
            "match",
            "--out",
            str(xmp),
            "--name",
            "CLI start",
        ],
        check=True,
    )
    description = read_xmp(xmp)
    name = description.find(f"{CRS}Name/{RDF}Alt/{RDF}li")
    assert name is not None and name.text == "CLI start"
    assert xmp.with_suffix(".notes.md").is_file()


def check_empty(folder: Path) -> None:
    folder.mkdir()
    try:
        presetlib.analyze_catalog(folder)
    except presetlib.PresetError:
        return
    raise AssertionError("empty folder should fail")


def read_xmp(path: Path) -> ET.Element:
    root = ET.parse(path).getroot()
    for element in root.iter(f"{RDF}Description"):
        return element
    raise AssertionError("missing description")


def make_warm_fade(path: Path, shift: int) -> None:
    width, height = 320, 200
    image = Image.new("RGB", (width, height))
    pixels = image.load()
    for y in range(height):
        for x in range(width):
            base = 90 + int(100 * x / (width - 1)) + shift
            pixels[x, y] = (min(255, base + 26), min(255, base + 2), max(0, base - 24))
    image.save(path)


def make_teal_orange(path: Path) -> None:
    width, height = 320, 200
    image = Image.new("RGB", (width, height))
    pixels = image.load()
    for y in range(height):
        for x in range(width):
            if y < height * 0.42:
                pixels[x, y] = (232, 148, 48)
            elif y > height * 0.58:
                pixels[x, y] = (18, 72, 84)
            else:
                pixels[x, y] = (140, 140, 140)
    image.save(path)


def solid(path: Path, color: tuple[int, int, int]) -> None:
    image = Image.new("RGB", (80, 60), color)
    image.save(path)


if __name__ == "__main__":
    raise SystemExit(main())
