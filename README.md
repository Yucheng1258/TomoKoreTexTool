# TomoKoreTexTool

[中文版本](README_CN.md)

A texture conversion tool for **Tomodachi Life: Living the Dream** 
Converts between game texture formats (`.canvas`, `.ugctex`, `_Thumb.ugctex`) and PNG

This project improves upon the original [TomoKoreFacepaintTool](https://github.com/Timiimiimii/TomoKoreFacepaintTool) by Timimimi

## Improvements over the original

| Area | Change |
|---|---|
| **Image types** | Now supports UgcFacePaint, UgcFood, and UgcGoods (originally only face paint) |
| **File numbers** | Choose slot 000–999 instead of being locked to a single slot |
| **Batch output** | One-click generate all three formats (Canvas + UgcTex + Thumb) from a single PNG |
| **ZS compression** | Outputs `.zs` files directly for Ryujinx emulator use; intermediate raw files are automatically cleaned up |
| **Save location** | Flexible export: default path, custom path, or keep in place. PNG export has the same options. |
| **Persistent default path** | Modifying the default save path persists across restarts via a local config file |
| **Auto path cleaning** | Pasted file paths with surrounding quotes are automatically stripped |
| **Square image auto-skip** | Square images are resized without prompting; only non-square images ask for resize method |
| **Dynamic DDS header** | Replaces the external `DDSHeader.ugctex` binary file with a `make_dds_header()` function that adapts to any resolution and format |
| **Flexible UgcTex** | Supports non-512×512 UgcTex files (e.g., 384×512 Food textures) via block-grid parsing |
| **Gamma fix** | Removed incorrect gamma correction in the game-to-PNG direction that caused washed-out output |
| **Bilingual UI** | All interface text in Chinese and English |
| **Bug fixes** | Cancel no longer crashes; batch-mode resize cancel handled correctly; original files cleaned up after copy |

## Formats

| Format | Resolution | Pixel format | Alpha support |
|---|---|---|---|
| `.canvas` | 256×256 | RGBA8 (uncompressed) | Full 8-bit |
| `.ugctex` | 512×512* | DXT1 | 1-bit only |
| `_Thumb.ugctex` | 256×256 | DXT5 | Full 8-bit |

\* Some Food textures use 384×512 — the tool handles these automatically.

## Requirements

```bash
pip install pillow pyswizzle zstandard
```

## Usage

Run the script:

```bash
python TomoKoreTexTool.py
```

### Main menu

```
1. Canvas/UgcTex/Thumb → PNG
2. PNG → Canvas/UgcTex/Thumb
3. Miitopia PNG → Canvas/UgcTex/Thumb
4. Exit
```

### Option 1: Game format → PNG

1. Enter the file path (supports `.canvas`, `.ugctex`, `_Thumb.ugctex`, and `.zs` compressed versions)
2. Choose where to save the PNG

### Option 2: PNG → Game format

1. Enter the PNG file path
2. Select image type: UgcFacePaint, UgcFood, or UgcGoods
3. Select output format(s):
   - **Canvas+UgcTex+Thumb** — generate all three at once
   - **Canvas** — `.canvas` only (256×256, RGBA8)
   - **UgcTex** — `.ugctex` only (512×512, DXT1)
   - **Thumb** — `_Thumb.ugctex` only (256×256, DXT5)
4. Enter file number (0–999)
5. Choose save location

### Option 3: Miitopia PNG → Game format

Same as Option 2, but applies gamma correction for Miitopia-origin images.

### Resize behaviour

If the PNG doesn't match the target resolution, a prompt appears:

- **Square images** (1:1 aspect ratio) — automatically stretched without asking
- **Non-square images** — you choose: stretch, keep aspect ratio, or cancel

### Save file location

The main save path for the game is generally:

```
%APPDATA%\..\..\user\save\0000000000000001\0\Ugc
```
The backup save path for the game is generally:

```
%APPDATA%\..\..\user\save\0000000000000001\1\Ugc
```
Export the generated files to these paths and replace the existing ones for changes to take effect in-game.

Note: Please back up the original game files before making any changes.




## License

This project follows the original author's license. See the [original repository](https://github.com/Timiimiimii/TomoKoreFacepaintTool) for details.

## Credits

- **Timimimi** — original author
- **RealDarkCraft** — file format reverse engineering
- **Aclios** — [pyswizzle](https://github.com/Aclios/pyswizzle) library
- **Pillow** — Python imaging library
