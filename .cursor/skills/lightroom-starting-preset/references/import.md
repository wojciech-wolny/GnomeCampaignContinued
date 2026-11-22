# Import the preset into Lightroom

The file is a develop preset for Lightroom Classic and the Lightroom desktop app. It is a partial preset: Lightroom changes only the sliders in the file. Profile, crop, masks, sharpening and noise reduction stay as they are.

`SupportsAmount2` is set, so Classic shows an Amount slider after you apply the preset. Amount scales each included slider toward its neutral value. It does not blend with edits you already made. 100% is this starting point. Drop Amount if the look is too strong, then move Exposure and White Balance by hand.

## Lightroom Classic

English:

1. Open the Develop module.
2. In the Presets panel, click **+**.
3. Choose **Import Presets…**
4. Select the `.xmp` file.
5. Apply it from the **Starting Points** group (the group name is inside the file).

Polish UI:

1. Moduł **Wywoływanie**.
2. Panel **Ustawienia predefiniowane**, przycisk **+**.
3. **Importuj ustawienia predefiniowane…**
4. Wskaż plik `.xmp`.
5. Preset jest w grupie **Starting Points**.

You can also copy the file into the Camera Raw settings folder and restart Lightroom:

- Windows: `%APPDATA%\Adobe\CameraRaw\Settings`
- macOS: `~/Library/Application Support/Adobe/CameraRaw/Settings`

## If the preset looks too strong or too weak

The numbers are deliberately small. They are a place to start, not a finished grade.

- Too strong: lower Amount, or ask for the same style with `--strength 0.6`.
- Too weak, and you want the recipe itself turned up: `--strength 1` is already the built-in recipe. Ask for `--allow-strong` only when you want sliders past the starting-point caps.
- White balance on a raw file did not move: pixel matching sets the JPEG temperature slider only. Nudge Temperature (Kelvin) yourself, or match a catalog that already has develop settings.

## If Lightroom will not list the file

- The file must end in `.xmp`.
- Import the file. Do not only drop it on the filmstrip.
- A faded italic name means Lightroom thinks part of the preset does not apply to that file type. The tone sliders still apply.
