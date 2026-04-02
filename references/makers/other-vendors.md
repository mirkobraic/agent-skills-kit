# Other Vendor MakerNotes

> Part of [Manufacturer MakerNote Dictionaries](README.md)

This file covers Fujifilm, Olympus (OM System), Minolta/Sony, and Pentax
MakerNote data as exposed by Apple's ImageIO framework.

---

## Fujifilm

**ImageIO constant:** `kCGImagePropertyMakerFujiDictionary` (iOS 4.0+)

### Format

- **Header:** `"FUJIFILM"` (8 bytes) + 4-byte offset pointer to IFD
- **Byte order:** Always **little-endian**, regardless of main TIFF byte order
- **Offsets:** Relative to the start of the MakerNote (`"F"` of `"FUJIFILM"`)
- **Structure:** IFD with relative offsets

Fujifilm's combination of fixed little-endian byte order and relative
offsets makes it one of the **most robust** MakerNote formats for
metadata preservation.

### Key Tags

| Tag ID | Name | Type | Description |
|--------|------|------|-------------|
| 0x0000 | Version | undef[4] | MakerNote version string |
| 0x0010 | InternalSerialNumber | string | Internal serial number |
| 0x1000 | Quality | string | `"NORMAL"`, `"FINE"`, `"SUPER FINE"` |
| 0x1001 | Sharpness | int16u | `1`=Soft, `3`=Normal, `4`=Hard, `0x8000`=Film Simulation |
| 0x1002 | WhiteBalance | int16u | `0`=Auto, `256`=Daylight, `512`=Cloudy, `768`=DaylightFluorescent, `1024`=Incandescent, `1280`=Flash, `3840`=Custom |
| 0x1003 | Saturation | int16u | `0`=Normal, `256`=High, `512`=Low, `768`=None (B&W), `0x8000`=Film Simulation |
| 0x1004 | Contrast | int16u | `0`=Normal, `256`=High, `768`=Low |
| 0x1005 | ColorTemperature | int16u | Kelvin (manual WB) |
| 0x100a | WhiteBalanceFineTune | int16s[2] | [Red shift, Blue shift] |
| 0x1010 | FujiFlashMode | int16u | `0`=Auto, `1`=On, `2`=Off, `3`=Red-eye, `4`=External |
| 0x1021 | FocusMode | int16u | `0`=Auto, `1`=Manual |
| 0x1031 | PictureMode | int16u | `0`=Auto, `256`=Aperture priority, `512`=Shutter priority, `768`=Manual |
| 0x1040 | ShadowTone | int32s | `-2`=Hard through `2`=Soft |
| 0x1041 | HighlightTone | int32s | `-2`=Hard through `2`=Soft |
| 0x1050 | ShutterType | int16u | `0`=Mechanical, `1`=Electronic, `2`=Electronic (long), `3`=Electronic (front curtain) |

### Film Simulation (Tag 0x1401)

Fujifilm's **signature feature**. The most-sought metadata value for Fujifilm shooters.

| Value | Film Simulation | Characteristics |
|-------|-----------------|----------------|
| 0x0000 (0) | Provia / Standard | Balanced color; default for most bodies |
| 0x0100 (256) | Studio Portrait | Optimized skin tones |
| 0x0110 (272) | Studio Portrait Enhanced Saturation | Enhanced saturation for portraits |
| 0x0120 (288) | Astia / Soft | Soft, smooth skin tones; lower contrast |
| 0x0130 (304) | Studio Portrait Increased Sharpness | Sharper portrait rendering |
| 0x0200 (512) | Velvia / Vivid | High saturation, high contrast; landscape favorite |
| 0x0300 (768) | Pro Neg. Hi (F3) | Higher contrast negative film look |
| 0x0301 (769) | Pro Neg. Standard | Lower contrast negative film look |
| 0x0400 (1024) | Pro Neg. Hi (F4) | Alternative Pro Neg. variant |
| 0x0500 (1280) | Pro Neg. Std | Standard negative film emulation |
| 0x0501 (1281) | Pro Neg. Hi | High contrast negative film emulation |
| 0x0600 (1536) | Classic Chrome | Muted, desaturated tones; documentary look |
| 0x0700 (1792) | Eterna / Cinema | Low saturation, wide dynamic range; cinematic look |
| 0x0800 (2048) | Classic Negative | Rich color with unique tonality; street photography favorite |
| 0x0900 (2304) | Eterna Bleach Bypass | High contrast, desaturated; bleach bypass film processing look |
| 0x0A00 (2560) | Nostalgic Negative | Warm, amber-shifted; nostalgic analog feel |
| 0x0B00 (2816) | REALA ACE | True-to-life color with gentle tonality; inspired by Fujicolor REALA film |

> REALA ACE was introduced with the X100VI (2024) and has since appeared on other X-Trans V bodies.

**Important:** B&W and sepia simulations (ACROS, etc.) are stored in tag 0x1003 (Saturation) with
value 0x8000; the specific B&W filter/toning is determined by the Saturation value.

### Dynamic Range Tags

| Tag ID | Name | Values |
|--------|------|--------|
| 0x1400 | DynamicRange | `1`=Standard (100%), `3`=Wide (200-400%) |
| 0x1402 | DynamicRangeSetting | `0`=Auto, `1`=Manual |
| 0x1403 | DevelopmentDynamicRange | Actual value (100/200/400) |

### Grain Effect and Color Chrome (Newer Bodies)

| Tag ID | Name | Values |
|--------|------|--------|
| 0x104c | GrainEffectRoughness | `0`=Off, `32`=Weak, `64`=Strong |
| 0x104d | ColorChromeEffect | `0`=Off, `32`=Weak, `64`=Strong |
| 0x104e | ColorChromeFxBlue | `0`=Off, `32`=Weak, `64`=Strong |
| 0x104f | GrainEffectSize | `0`=Off, `16`=Small, `32`=Large |
| 0x100F | ClarityControl | Clarity adjustment (-5 to +5) |

### Recipe Reconstruction

To reconstruct a Fujifilm film simulation recipe from MakerNote data,
read: FilmMode (0x1401), ShadowTone (0x1040), HighlightTone (0x1041),
Saturation (0x1003), Sharpness (0x1001), GrainEffectRoughness (0x104c),
GrainEffectSize (0x104f), ColorChromeEffect (0x104d), ColorChromeFxBlue
(0x104e), WhiteBalance (0x1002) + WhiteBalanceFineTune (0x100a),
DynamicRange (0x1400), ClarityControl (0x100F).

---

## Olympus (OM System)

**ImageIO constant:** `kCGImagePropertyMakerOlympusDictionary` (iOS 4.0+)

### Format

- **Header:** `"OLYMP\0"` (6 bytes, older) or `"OLYMPUS\0"` (8 bytes + 2-byte version, newer)
- **Byte order:** Same as main TIFF header
- **Offsets:** Absolute for `"OLYMP\0"` format (**fragile** to EXIF rewrites); relative to MakerNote start + 12 for `"OLYMPUS\0"` format (more resilient)
- **Structure:** **Nested sub-IFDs** — the most complex MakerNote architecture of any vendor

> OM Digital Solutions cameras (OM-1, OM-5) still use the `"OLYMPUS\0"` format.

### Top-Level Tags

| Tag ID | Name | Description |
|--------|------|-------------|
| 0x0000 | MakerNoteVersion | Version string |
| 0x0104 | BodyFirmwareVersion | Body firmware version |
| 0x0200 | SpecialMode | [mode, sequence number, panorama direction] |
| 0x0201 | Quality | `1`=SQ, `2`=HQ, `3`=SHQ, `4`=RAW, `5`=SQ1, `6`=SQ2 |
| 0x0207 | CameraType | Camera type string (e.g., `"E-M1MarkII"`) |
| 0x0209 | CameraID | Camera ID data |
| 0x0404 | SerialNumber | Camera serial number |

### Sub-IFD Structure

Olympus uses **five nested sub-IFDs**:

| Tag ID | Sub-IFD | Purpose |
|--------|---------|---------|
| 0x2010 | Equipment | Body/lens serial, lens model/type, extender, flash model |
| 0x2020 | CameraSettings | Exposure mode, metering, focus, drive, IS, WB |
| 0x2030 | RawDevelopment | RAW engine, exposure bias, WB, sharpness, contrast |
| 0x2040 | ImageProcessing | WB, color matrix, tone curve, noise filter, art filter |
| 0x2050 | FocusInfo | AF point, focus distance, AF area, macro LED |

### Equipment Sub-IFD (0x2010) — Key Tags

| Tag | Name | Description |
|-----|------|-------------|
| 0x0101 | SerialNumber | Body serial number |
| 0x0201 | LensType | Lens type numeric ID (maps to lens name via lookup table) |
| 0x0202 | LensSerialNumber | Lens serial number |
| 0x0203 | LensModel | Lens model string (e.g., `"M.Zuiko Digital ED 12-40mm F2.8 PRO"`) |
| 0x0204 | LensFirmwareVersion | Lens firmware version |
| 0x0207 | MinFocalLength | Shortest focal length (mm) |
| 0x0208 | MaxFocalLength | Longest focal length (mm) |
| 0x0301 | ExtenderType | Teleconverter ID |
| 0x0303 | ExtenderModel | Teleconverter model string |
| 0x1001 | FlashModel | Flash model string (e.g., `"FL-900R"`) |

### CameraSettings Sub-IFD (0x2020) — Key Tags

| Tag | Name | Notable Values |
|-----|------|---------------|
| 0x0200 | ExposureMode | `1`=Manual, `2`=Program, `3`=Aperture priority, `4`=Shutter priority |
| 0x0202 | MeteringMode | `2`=Center weighted, `3`=Spot, `5`=ESP (Evaluative) |
| 0x0301 | FocusMode | `0`=S-AF, `2`=C-AF, `3`=Multi AF, `4`=Face Detect, `10`=MF |
| 0x0500 | WhiteBalance2 | `0`=Auto, `256`=Custom1 |
| 0x0501 | WhiteBalanceTemperature | Color temperature (Kelvin) |
| 0x0600 | ImageStabilization | `0`=Off, `1`=S-IS1, `2`=S-IS2, `3`=S-IS3 |

### Art Filters (ImageProcessing Sub-IFD 0x2040)

In-camera creative effects applied during JPEG processing. Stored in the ArtFilter tag.

| Value | Art Filter | Value | Art Filter |
|-------|-----------|-------|-----------|
| 0 | Off | 20 | Dramatic Tone |
| 1 | Soft Focus | 21 | Punk |
| 2 | Pop Art | 22 | Soft Focus 2 |
| 3 | Pale & Light Color | 23 | Sparkle |
| 4 | Light Tone | 24 | Watercolor |
| 5 | Pin Hole | 25 | Key Line |
| 6 | Grainy Film | 26 | Key Line II |
| 9 | Diorama | 27 | Miniature |
| 10 | Cross Process | 28 | Reflection |
| 12 | Fish Eye | 29 | Fragmented |
| 13 | Drawing | 31 | Partial Color |
| 14 | Gentle Sepia | 32 | Partial Color II |
| 15 | Pale & Light Color II | 33 | Partial Color III |
| 16 | Pop Art II | 35 | Bleach Bypass |
| 17 | Pin Hole II | 36 | Bleach Bypass II |
| 18 | Pin Hole III | 39 | Vintage |
| 19 | Grainy Film II | 40 | Vintage II |
| | | 41 | Vintage III |

---

## Minolta / Sony

**ImageIO constant:** `kCGImagePropertyMakerMinoltaDictionary` (iOS 4.0+)

Sony acquired Minolta's camera division in 2006. ImageIO uses a single
dictionary constant for both manufacturers.

### Complexity Warning

Minolta/Sony MakerNote is notably difficult to work with:
- Tag meanings change between camera models and generations
- Sony has used at least 6 different MakerNote sub-structures
- Some Sony ARW data references byte offsets **outside** the MakerNote block (fragile)
- ExifTool's Sony.pm is ~10,000 lines

### Key Minolta Tags

| Tag ID | Name | Description |
|--------|------|-------------|
| 0x0001 | CameraSettingsOld | Settings (oldest models: D5, D7) |
| 0x0003 | CameraSettings | Settings (newer: D7Hi, A1, A2, Dynax 5D/7D) |
| 0x0018 | ImageStabilization | AntiShake setting |
| 0x0101 | ColorMode | `0`=Natural, `1`=B&W, `2`=Vivid, `5`=Sepia, `12`=Portrait, `13`=Landscape |
| 0x0102 | MinoltaQuality | `0`=RAW, `1`=Super Fine, `2`=Fine, `3`=Standard |

### Sony-Specific Tags (Non-Minolta Format)

Modern Sony cameras (ILCE, NEX, SLT, RX from ~2012 onward) use their own
format. Key decoded tags: SonyModelID, LensType/LensSpec, AFMode, AFAreaMode,
InternalSerialNumber, ExposureMode, SonyISO.

For detailed Sony tag decoding, refer to [ExifTool Sony Tags](https://exiftool.org/TagNames/Sony.html).

---

## Pentax

**ImageIO constant:** `kCGImagePropertyMakerPentaxDictionary` (iOS 4.0+)

### Format

- **Header:** `"AOC\0"` (4 bytes) followed by its own byte order marker (`"MM"` or `"II"`)
- **Structure:** Standard IFD following header
- Also used by Ricoh GR-series cameras (Ricoh acquired Pentax in 2011)

### Key Tags

| Tag ID | Name | Type | Description |
|--------|------|------|-------------|
| 0x0005 | PentaxModelID | int32u | Numeric model identifier |
| 0x0008 | Quality | int16u | `0`=Good, `1`=Better, `2`=Best, `4`=RAW (PEF), `5`=Premium, `8`=RAW (DNG) |
| 0x000d | FocusMode | int16u | `0`=Normal, `1`=Macro, `3`=Manual, `16`=AF-S, `17`=AF-C, `18`=AF-A |
| 0x000e | AFPointSelected | int16u | Selected AF point index |
| 0x000f | AFPointsInFocus | int32u | Bitmask of focused AF points |
| 0x0014 | ISO | int16u | ISO speed |
| 0x0017 | MeteringMode | int16u | `0`=Multi-segment, `1`=Center-weighted, `2`=Spot |
| 0x0019 | WhiteBalance | int16u | `0`=Auto, `1`=Daylight, `2`=Shade, `3`=Fluorescent, `4`=Tungsten, `5`=Manual |
| 0x001d | FocalLength | int32u | Focal length (units of 0.01mm) |
| 0x003f | LensType | int8u[2] | [Series, Model] — see Lens Identification below |
| 0x0047 | Temperature | int8s | Sensor temperature (Celsius) |
| 0x005c | ImageTone | int16u | `0`=Natural, `1`=Bright, `2`=Portrait, `3`=Landscape, `4`=Vibrant, `5`=Monochrome, `7`=Reversal Film, `8`=Bleach Bypass |
| 0x0215 | **ShutterCount** | int32u | Total shutter actuations since manufacture |

### Lens Identification (Tag 0x003f)

A **two-byte system**: the first byte identifies the lens family/mount (Series), the second identifies the specific lens within that family (Model). Together they map to a lens name.

| Series | Mount/Family |
|--------|-------------|
| 1 | K/M 42mm screw-mount |
| 2 | A series (K-mount, manual aperture ring) |
| 3 | FA / F series (K-mount, autofocus) |
| 4–5 | FA / FA* series |
| 6 | DA / DA* series (APS-C digital) |
| 7 | DA Limited |
| 8 | D FA / HD series (full-frame digital) |
| 11–12 | Various DA/DA* |
| 13 | Q-mount lenses |
| 15 | 645-mount lenses |
| 21 | HD D FA* / HD PENTAX-D FA* |
| 22 | HD PENTAX-DA* |

Covers K-mount, 645-mount, and Q-mount lenses including third-party (Sigma, Tamron, Tokina). The full model-to-name lookup is in ExifTool's `%pentaxLensTypes` table.

### Shake Reduction (Tag 0x007f)

Pentax SR (IBIS) data includes stabilization result and mode. On newer bodies,
SR also enables Astro Tracer (GPS-guided star tracking) and Pixel Shift Resolution.

---

## Reading Other Vendor MakerNotes in Swift

```swift
import ImageIO

func readVendorMakerNote(from url: URL) {
    guard let source = CGImageSourceCreateWithURL(url as CFURL, nil),
          let props = CGImageSourceCopyPropertiesAtIndex(source, 0, nil)
                  as? [String: Any] else { return }

    // Fujifilm
    if let fuji = props[kCGImagePropertyMakerFujiDictionary as String]
            as? [String: Any] {
        // Film simulation (tag 0x1401 = 5121 decimal)
        if let filmMode = fuji["5121"] as? Int {
            let filmNames: [Int: String] = [
                0: "Provia/Standard", 512: "Velvia/Vivid",
                1536: "Classic Chrome", 1792: "Eterna",
                2048: "Classic Negative", 2816: "REALA ACE"
            ]
            print("Film simulation: \(filmNames[filmMode] ?? "Unknown (\(filmMode))")")
        }
    }

    // Olympus
    if let olympus = props[kCGImagePropertyMakerOlympusDictionary as String]
            as? [String: Any] {
        if let cameraType = olympus["519"] as? String {
            print("Camera: \(cameraType)")
        }
    }

    // Pentax
    if let pentax = props[kCGImagePropertyMakerPentaxDictionary as String]
            as? [String: Any] {
        if let shutterCount = pentax["533"] as? Int {
            print("Shutter count: \(shutterCount)")
        }
    }

    // Minolta / Sony
    if let minolta = props[kCGImagePropertyMakerMinoltaDictionary as String]
            as? [String: Any] {
        if let quality = minolta["258"] as? Int {
            print("Quality: \(quality)")
        }
    }
}
```

---

## Cross-References

- [MakerNote Concept](makernote-concept.md) — How MakerNote works, offset fragility
- [Apple MakerNote](apple.md) — iPhone/iPad metadata
- [Canon MakerNote](canon.md) — Canon-specific tags
- [Nikon MakerNote](nikon.md) — Nikon-specific tags
- [ImageIO Property Keys](../imageio/property-keys.md) — All dictionary constants

### External References

- **Fujifilm:** [ExifTool FujiFilm Tags](https://exiftool.org/TagNames/FujiFilm.html)
- **Olympus:** [ExifTool Olympus Tags](https://exiftool.org/TagNames/Olympus.html)
- **Minolta:** [ExifTool Minolta Tags](https://exiftool.org/TagNames/Minolta.html)
- **Sony:** [ExifTool Sony Tags](https://exiftool.org/TagNames/Sony.html)
- **Pentax:** [ExifTool Pentax Tags](https://exiftool.org/TagNames/Pentax.html)
