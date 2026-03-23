# Other Vendor MakerNotes

> Part of [Manufacturer MakerNote Dictionaries](README.md)

This file covers Fujifilm, Olympus (OM System), Minolta/Sony, and Pentax
MakerNote data as exposed by Apple's ImageIO framework. These vendors have
unique features -- Fujifilm's Film Simulation system, Olympus's nested
sub-IFD architecture, Sony's complex model-dependent formats, and Pentax's
Shake Reduction diagnostics.

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
metadata preservation. The MakerNote survives repositioning during EXIF
rewrites as long as the MakerNote bytes themselves are not modified.

```
Fujifilm MakerNote:
  Offset 0:   "FUJIFILM"     (8 bytes, hex: 46 55 4A 49 46 49 4C 4D)
  Offset 8:   [4-byte offset to IFD0, relative to offset 0]
  Offset 12+: [IFD entries in little-endian...]
```

### Key Tags

| Tag ID | Name | Type | Description |
|--------|------|------|-------------|
| 0x0000 (0) | Version | undef[4] | MakerNote version string |
| 0x0010 (16) | InternalSerialNumber | string | Internal serial number |
| 0x1000 (4096) | Quality | string | Quality setting (`"NORMAL"`, `"FINE"`, `"SUPER FINE"`) |
| 0x1001 (4097) | Sharpness | int16u | `1` = Soft, `2` = Soft2, `3` = Normal, `4` = Hard, `5` = Hard2, `0x82` = Medium Soft, `0x84` = Medium Hard, `0x8000` = Film Simulation, `0xFFFF` = N/A |
| 0x1002 (4098) | WhiteBalance | int16u | `0` = Auto, `256` = Daylight, `512` = Cloudy, `768` = DaylightFluorescent, `769` = DayWhiteFluorescent, `770` = WhiteFluorescent, `771` = WarmWhiteFluorescent, `1024` = Incandescent, `1280` = Flash, `3840` = Custom, `3841` = Custom2, `3842` = Custom3 |
| 0x1003 (4099) | Saturation | int16u | `0` = Normal, `256` = High, `512` = Low, `768` = None (B&W), `769` = B&W Red Filter, `770` = B&W Yellow Filter, `771` = B&W Green Filter, `784` = B&W Sepia, `1024` = Medium High, `1280` = Medium Low, `0x8000` = Film Simulation |
| 0x1004 (4100) | Contrast | int16u | `0` = Normal, `256` = High, `768` = Low |
| 0x1005 (4101) | ColorTemperature | int16u | Color temperature (Kelvin) when using manual WB |
| 0x100a (4106) | WhiteBalanceFineTune | int16s[2] | WB fine-tune [Red shift, Blue shift] |
| 0x100b (4107) | NoiseReduction | int16u | `0x0000` = Normal |
| 0x100e (4110) | HighISONoiseReduction | int16u | `0` = Normal, `256` = Strong, `512` = Weak |
| 0x1010 (4112) | FujiFlashMode | int16u | `0` = Auto, `1` = On, `2` = Off, `3` = Red-eye reduction, `4` = External |
| 0x1011 (4113) | FlashExposureComp | rational64s | Flash exposure compensation |
| 0x1020 (4128) | Macro | int16u | `0` = Off, `1` = On |
| 0x1021 (4129) | FocusMode | int16u | `0` = Auto, `1` = Manual, `65535` = Movie |
| 0x1022 (4130) | AFMode | int16u | AF area mode |
| 0x1023 (4131) | FocusPixel | int16u[2] | Focus pixel coordinates [X, Y] |
| 0x1030 (4144) | SlowSync | int16u | `0` = Off, `1` = On |
| 0x1031 (4145) | PictureMode | int16u | `0` = Auto, `1` = Portrait, `2` = Landscape, `4` = Sports, `5` = Night, `6` = Program AE, `256` = Aperture priority, `512` = Shutter priority, `768` = Manual |
| 0x1032 (4146) | ExposureCount | int16u | Number of exposures used (multi-frame) |
| 0x1033 (4147) | EXRAuto | int16u | EXR Auto mode setting |
| 0x1034 (4148) | EXRMode | int16u | EXR mode: SN (signal-to-noise priority), DR (dynamic range), HR (high resolution) |

### Tone and Highlight Control

| Tag ID | Name | Type | Description |
|--------|------|------|-------------|
| 0x1040 (4160) | ShadowTone | int32s | `-2` = Hard, `-1` = Medium Hard, `0` = Normal, `1` = Medium Soft, `2` = Soft |
| 0x1041 (4161) | HighlightTone | int32s | `-2` = Hard, `-1` = Medium Hard, `0` = Normal, `1` = Medium Soft, `2` = Soft |
| 0x1044 (4164) | DigitalZoom | int32u | Digital zoom factor |
| 0x1050 (4176) | ShutterType | int16u | `0` = Mechanical, `1` = Electronic, `2` = Electronic (long shutter), `3` = Electronic (front curtain) |

### Film Simulation (Tag 0x1401)

Fujifilm's **signature feature**. The FilmMode tag encodes which film
simulation was applied during JPEG/HEIF processing. This is one of the
most-sought metadata values for Fujifilm shooters.

**Important:** Color film simulations are stored in tag 0x1401 (FilmMode).
Black-and-white and sepia simulations (like ACROS) are stored in tag
0x1003 (Saturation) with value 0x8000 (Film Simulation) -- the specific
B&W filter/toning is determined by the Saturation value.

| Value | Film Simulation | Characteristics |
|-------|-----------------|----------------|
| 0x0000 (0) | Provia / Standard (F0) | Balanced color; default for most bodies |
| 0x0100 (256) | Studio Portrait (F1) | Optimized skin tones |
| 0x0110 (272) | Studio Portrait Enhanced Saturation (F1a) | Enhanced saturation for portraits |
| 0x0120 (288) | Astia / Soft (F1b) | Soft, smooth skin tones; lower contrast |
| 0x0130 (304) | Studio Portrait Increased Sharpness (F1c) | Sharper portrait rendering |
| 0x0200 (512) | Velvia / Vivid (F2) | High saturation, high contrast; landscape favorite |
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

> REALA ACE was introduced with the X100VI (2024) and has since appeared
> on other X-Trans V bodies. It is Fujifilm's newest film simulation.

### Dynamic Range Tags

| Tag ID | Name | Type | Values |
|--------|------|------|--------|
| 0x1400 (5120) | DynamicRange | int16u | `1` = Standard (100%), `3` = Wide (200-400%) |
| 0x1402 (5122) | DynamicRangeSetting | int16u | `0` = Auto, `1` = Manual |
| 0x1403 (5123) | DevelopmentDynamicRange | int16u | Actual DR value (100 = DR100, 200 = DR200, 400 = DR400) |

### Lens Tags

| Tag ID | Name | Type | Description |
|--------|------|------|-------------|
| 0x1404 (5124) | MinFocalLength | rational64u | Lens minimum focal length (mm) |
| 0x1405 (5125) | MaxFocalLength | rational64u | Lens maximum focal length (mm) |
| 0x1406 (5126) | MaxApertureAtMinFocal | rational64u | Maximum aperture at shortest focal length |
| 0x1407 (5127) | MaxApertureAtMaxFocal | rational64u | Maximum aperture at longest focal length |

### Grain Effect and Color Chrome (Newer Bodies)

| Tag ID | Name | Type | Values |
|--------|------|------|--------|
| 0x104c (4172) | GrainEffectRoughness | int32s | `0` = Off, `32` = Weak, `64` = Strong |
| 0x104d (4173) | ColorChromeEffect | int32s | `0` = Off, `32` = Weak, `64` = Strong |
| 0x104e (4174) | ColorChromeFxBlue | int32s | `0` = Off, `32` = Weak, `64` = Strong |
| 0x104f (4175) | GrainEffectSize | int32s | `0` = Off, `16` = Small, `32` = Large |
| 0x1050 (4176) | ClarityControl | int32s | Clarity adjustment value (-5 to +5 range) |

### Fujifilm Recipe Reconstruction

To fully reconstruct a Fujifilm film simulation recipe from MakerNote
data, read these tags together:

1. **FilmMode** (0x1401) -- base film simulation
2. **ShadowTone** (0x1040) -- shadow rendering
3. **HighlightTone** (0x1041) -- highlight rendering
4. **Saturation** (0x1003) -- color saturation / B&W mode
5. **Sharpness** (0x1001) -- sharpening level
6. **GrainEffectRoughness** (0x104c) -- film grain roughness
7. **GrainEffectSize** (0x104f) -- film grain size
8. **ColorChromeEffect** (0x104d) -- color chrome intensity
9. **ColorChromeFxBlue** (0x104e) -- color chrome blue intensity
10. **WhiteBalance** (0x1002) + **WhiteBalanceFineTune** (0x100a) -- WB
11. **DynamicRange** (0x1400) -- DR mode
12. **ClarityControl** (0x1050) -- clarity

This is the foundation for Fujifilm recipe-sharing communities (e.g.,
FujiXWeekly) that share complete camera settings as "film simulation
recipes."

---

## Olympus (OM System)

**ImageIO constant:** `kCGImagePropertyMakerOlympusDictionary` (iOS 4.0+)

### Format

- **Header:** `"OLYMP\0"` (6 bytes, older) or `"OLYMPUS\0"` (8 bytes +
  2-byte version, newer cameras including OM System OM-1, OM-5)
- **Byte order:** Same as main TIFF header
- **Offsets:** Absolute for `"OLYMP\0"` format (from TIFF header);
  relative to MakerNote start + 12 for `"OLYMPUS\0"` format
- **Structure:** **Nested sub-IFDs** -- the most complex MakerNote
  architecture of any vendor

The `"OLYMP\0"` format (offset base = main TIFF header) is **fragile** to
EXIF rewrites. The `"OLYMPUS\0"` format (offset base = MakerNote start)
is more resilient.

```
Olympus MakerNote (newer format):
  Offset 0:   "OLYMPUS\0"    (8 bytes, hex: 4F 4C 59 4D 50 55 53 00)
  Offset 8:   0x02 0x00      (version)
  Offset 10:  [IFD entry count]
  Offset 12+: [IFD entries...]
       Tag 0x2010 -> Equipment sub-IFD
       Tag 0x2020 -> CameraSettings sub-IFD
       Tag 0x2030 -> RawDevelopment sub-IFD
       Tag 0x2040 -> ImageProcessing sub-IFD
       Tag 0x2050 -> FocusInfo sub-IFD
```

> **OM System note:** Following the Olympus camera division rebranding
> to OM Digital Solutions, newer cameras (OM-1, OM-5) still use the
> `"OLYMPUS\0"` MakerNote format. ExifTool handles these under the
> Olympus tag tables.

### Top-Level Tags

| Tag ID | Name | Description |
|--------|------|-------------|
| 0x0000 (0) | MakerNoteVersion | Version string |
| 0x0001 (1) | MinoltaCameraSettingsOld | Legacy settings (shared Minolta heritage) |
| 0x0003 (3) | MinoltaCameraSettings | Legacy settings (Minolta heritage) |
| 0x0040 (64) | CompressedImageSize | Compressed image data size |
| 0x0100 (256) | ThumbnailImage | Embedded thumbnail image data |
| 0x0104 (260) | BodyFirmwareVersion | Body firmware version string |
| 0x0200 (512) | SpecialMode | Array: [mode, sequence number, panorama direction] |
| 0x0201 (513) | Quality | `1` = SQ, `2` = HQ, `3` = SHQ, `4` = RAW, `5` = SQ1, `6` = SQ2, `33` = Uncompressed |
| 0x0202 (514) | Macro | `0` = Off, `1` = On, `2` = Super Macro |
| 0x0203 (515) | BWMode | `0` = Off, `1` = On |
| 0x0204 (516) | DigitalZoom | Rational digital zoom factor |
| 0x0205 (517) | FocalPlaneDiagonal | Focal plane diagonal (mm) |
| 0x0206 (518) | LensDistortionParams | Lens distortion correction parameters |
| 0x0207 (519) | CameraType | Camera type string (e.g., `"E-M1MarkII"`, `"E-M5MarkIII"`) |
| 0x0208 (520) | TextInfo | Text info string |
| 0x0209 (521) | CameraID | Camera ID data |
| 0x0300 (768) | PreCaptureFrames | Pre-capture frames count |
| 0x0404 (1028) | SerialNumber | Camera serial number string |

### Sub-IFD Structure

Olympus is unique in using **five nested sub-IFDs**, each containing
specialized metadata categories:

| Tag ID | Sub-IFD Name | Tag Count | Purpose |
|--------|-------------|-----------|---------|
| 0x2010 | Equipment | ~30 tags | Body serial, lens serial, lens model, lens type, extender, flash model |
| 0x2020 | CameraSettings | ~40 tags | Exposure mode, metering, focus mode, drive mode, IS, scene mode, WB |
| 0x2030 | RawDevelopment | ~15 tags | RAW development engine, exposure bias, WB, sharpness, contrast, saturation |
| 0x2040 | ImageProcessing | ~40 tags | WB, color matrix, sharpness, contrast, saturation, tone curve, noise filter, art filter |
| 0x2050 | FocusInfo | ~15 tags | AF point, focus distance, AF area, external flash, macro LED |

### Equipment Sub-IFD (0x2010)

| Tag | Name | Description |
|-----|------|-------------|
| 0x0000 | EquipmentVersion | Version string |
| 0x0100 | CameraType2 | Camera type string |
| 0x0101 | SerialNumber | Body serial number |
| 0x0102 | InternalSerialNumber | Internal serial |
| 0x0103 | FocalPlaneDiagonal | Focal plane diagonal (mm) |
| 0x0104 | BodyFirmwareVersion2 | Body firmware version |
| 0x0201 | LensType | Lens type numeric ID (maps to lens name via lookup table) |
| 0x0202 | LensSerialNumber | Lens serial number |
| 0x0203 | LensModel | Lens model string (e.g., `"M.Zuiko Digital ED 12-40mm F2.8 PRO"`) |
| 0x0204 | LensFirmwareVersion | Lens firmware version |
| 0x0205 | MaxApertureAtMinFocal | Maximum aperture at shortest focal length |
| 0x0206 | MaxApertureAtMaxFocal | Maximum aperture at longest focal length |
| 0x0207 | MinFocalLength | Shortest focal length (mm) |
| 0x0208 | MaxFocalLength | Longest focal length (mm) |
| 0x020a | MaxApertureAtCurrentFocal | Max aperture at the focal length used for this shot |
| 0x020b | LensProperties | Lens properties bitfield |
| 0x0301 | ExtenderType | Teleconverter ID |
| 0x0302 | ExtenderSerialNumber | Teleconverter serial number |
| 0x0303 | ExtenderModel | Teleconverter model string |
| 0x1000 | FlashType | Flash type ID |
| 0x1001 | FlashModel | Flash model string (e.g., `"FL-900R"`) |

### CameraSettings Sub-IFD (0x2020) -- Selected Tags

| Tag | Name | Notable Values |
|-----|------|---------------|
| 0x0100 | PreviewImageValid | `0` = No, `1` = Yes |
| 0x0200 | ExposureMode | `1` = Manual, `2` = Program, `3` = Aperture priority, `4` = Shutter priority, `5` = Program shift |
| 0x0201 | AELock | `0` = Off, `1` = On |
| 0x0202 | MeteringMode | `2` = Center weighted, `3` = Spot, `5` = ESP (Evaluative), `261` = Pattern+AF, `515` = Spot+Highlight, `1027` = Spot+Shadow |
| 0x0300 | MacroMode | `0` = Off, `1` = On, `2` = Super macro |
| 0x0301 | FocusMode | `0` = Single AF (S-AF), `1` = Sequential shooting AF, `2` = Continuous AF (C-AF), `3` = Multi AF, `4` = Face Detect, `10` = MF |
| 0x0302 | FocusProcess | `0` = AF not used, `1` = AF used |
| 0x0303 | AFSearch | `0` = Not ready, `1` = Ready |
| 0x0304 | AFAreas | int32u[] -- AF area coordinates |
| 0x0305 | AFPointSelected | rational64s[5] -- Selected AF point info |
| 0x0306 | AFFineTune | `0` = Off, `1` = On |
| 0x0500 | WhiteBalance2 | `0` = Auto, `16` = 7500K, `17` = 6000K, `18` = 5300K, `20` = 3000K, `23` = 3600K, `256` = Custom1, etc. |
| 0x0501 | WhiteBalanceTemperature | Color temperature (Kelvin) |
| 0x0600 | ImageStabilization | `0` = Off, `1` = On (Mode 1 / S-IS1), `2` = On (Mode 2 / S-IS2), `3` = On (Mode 3 / S-IS3) |

### Art Filters (in ImageProcessing Sub-IFD 0x2040)

Olympus Art Filters are in-camera creative effects applied during
JPEG processing. The ArtFilter tag encodes the filter type:

| Value | Art Filter |
|-------|-----------|
| 0 | Off |
| 1 | Soft Focus |
| 2 | Pop Art |
| 3 | Pale & Light Color |
| 4 | Light Tone |
| 5 | Pin Hole |
| 6 | Grainy Film |
| 9 | Diorama |
| 10 | Cross Process |
| 12 | Fish Eye |
| 13 | Drawing |
| 14 | Gentle Sepia |
| 15 | Pale & Light Color II |
| 16 | Pop Art II |
| 17 | Pin Hole II |
| 18 | Pin Hole III |
| 19 | Grainy Film II |
| 20 | Dramatic Tone |
| 21 | Punk |
| 22 | Soft Focus 2 |
| 23 | Sparkle |
| 24 | Watercolor |
| 25 | Key Line |
| 26 | Key Line II |
| 27 | Miniature |
| 28 | Reflection |
| 29 | Fragmented |
| 31 | Partial Color |
| 32 | Partial Color II |
| 33 | Partial Color III |
| 35 | Bleach Bypass |
| 36 | Bleach Bypass II |
| 39 | Vintage |
| 40 | Vintage II |
| 41 | Vintage III |

### Common Use Cases

- **Lens/body serial tracking:** Equipment sub-IFD (0x2010) contains both
  body and lens serial numbers, plus extender/teleconverter info
- **Focus analysis:** FocusInfo sub-IFD (0x2050) provides AF point data
  and focus distance
- **Art filter identification:** Determine which creative filter was
  applied in-camera (critical for art filter workflows)
- **Image stabilization status:** CameraSettings (0x2020) contains IS mode
  (useful for verifying IBIS was active on handheld shots)
- **Complete lens identification:** Equipment sub-IFD provides lens model
  name, serial, firmware, and focal length/aperture at capture

---

## Minolta / Sony

**ImageIO constant:** `kCGImagePropertyMakerMinoltaDictionary` (iOS 4.0+)

### Heritage

Sony acquired Minolta's camera division in 2006. Early Sony Alpha cameras
(A100, A200, A300, A350, A700) used Minolta's MakerNote format directly.
ImageIO uses a **single dictionary constant** (`kCGImagePropertyMakerMinoltaDictionary`)
for both manufacturers.

In ExifTool, the tag groups are distinguished:
- **`Minolta`** -- Tags from actual Minolta cameras (DiMAGE, Dynax, etc.)
- **`Sony1MltCsOld` / `Sony1MltCsNew`** -- Minolta-format CameraSettings
  in Sony images
- **`Sony1`** -- Sony-specific tags (not Minolta-inherited)

### Format

- **Minolta:** IFD structure with no standard header. Detection based on
  Make = "Minolta" or "Konica Minolta"
- **Sony (early Alpha):** Same Minolta IFD format. Detection based on
  Make = "Sony" but using Minolta tag tables
- **Sony (modern):** Multiple proprietary formats that vary by model
  generation. Some data points to locations **outside** the MakerNote
  block (fragile). Sony.pm in ExifTool is ~10,000 lines.

### Complexity Warning

Minolta/Sony MakerNote is notably difficult to work with because:
- Tag meanings change between camera models and generations
- Data storage locations and formats vary by model
- Sony has used at least 6 different MakerNote sub-structures across
  its camera lineup
- Some Sony ARW MakerNote data references byte offsets **outside** the
  MakerNote block, meaning MakerNote data can be partially lost when
  images are rewritten by third-party software (including Adobe DNG
  Converter)

### Key Minolta Tags

| Tag ID | Name | Type | Description |
|--------|------|------|-------------|
| 0x0001 (1) | CameraSettingsOld | undef | Camera settings (oldest models: D5, D7, S304, S404) |
| 0x0003 (3) | CameraSettings | undef | Camera settings (newer: D7Hi, A1, A2, A200, Dynax 5D/7D) |
| 0x0004 (4) | CameraSettings7D | undef | Camera settings (Dynax/Maxxum 7D and 5D) |
| 0x0018 (24) | ImageStabilization | int32u | Image stabilization (AntiShake) setting |
| 0x0040 (64) | CompressedImageSize | int32u | Compressed image data size |
| 0x0081 (129) | Thumbnail | undef | Embedded JPEG thumbnail (640x480) |
| 0x0088 (136) | ThumbnailOffset | int32u | Offset to thumbnail data |
| 0x0089 (137) | ThumbnailLength | int32u | Thumbnail data size |
| 0x0100 (256) | SceneMode | int32u | Scene mode value |
| 0x0101 (257) | ColorMode | int32u | `0` = Natural, `1` = B&W, `2` = Vivid, `3` = Solarization, `4` = Adobe RGB, `5` = Sepia, `9` = Natural+, `12` = Portrait, `13` = Landscape |
| 0x0102 (258) | MinoltaQuality | int32u | `0` = RAW, `1` = Super Fine, `2` = Fine, `3` = Standard, `4` = Economy, `5` = Extra Fine |
| 0x0103 (259) | MinoltaImageSize | int32u | `0` = Full, `1` = 1600x1200, `2` = 1280x960, `3` = 640x480, `5` = 2560x1920 |

### CameraSettings Array (Tag 0x0003) -- Minolta Format

Minolta uses an indexed array similar to Canon's CameraSettings:

| Offset | Name | Description |
|--------|------|-------------|
| 1 | ExposureMode | `0` = Program, `1` = Aperture priority, `2` = Shutter priority, `3` = Manual |
| 2 | FlashMode | `0` = Fill flash, `1` = Red-eye reduction, `2` = Rear sync, `3` = Wireless, `4` = Off |
| 3 | WhiteBalance | `0` = Auto, `1` = Daylight, `2` = Cloudy, `3` = Tungsten, `4` = Flash, `5` = Fluorescent, `6` = Shade, `7` = Manual |
| 4 | MinoltaImageSize2 | Image size code |
| 5 | MinoltaQuality2 | Quality code |
| 6 | DriveMode | `0` = Single, `1` = Continuous, `2` = Self-timer, `4` = Bracketing, `5` = Interval, `6` = UHS continuous, `7` = HS continuous |
| 7 | MeteringMode | `0` = Multi-segment, `1` = Center weighted, `2` = Spot |
| 8 | ISO | ISO speed value |
| 9 | ShutterSpeed | Shutter speed (APEX encoding) |
| 10 | ApertureValue | Aperture (APEX encoding) |
| 11 | MacroMode | `0` = Off, `1` = On |
| 12 | DigitalZoom | `0` = Off, `1` = Electronic magnification, `2` = 2x |
| 13 | ExposureCompensation | Exposure compensation value |
| 14 | BracketStep | `0` = 1/3 EV, `1` = 2/3 EV, `2` = 1 EV |
| 18 | FocalLength | Focal length (mm) |
| 19 | FocusDistance | Focus distance (mm) |
| 20 | FlashFired | `0` = No, `1` = Yes |
| 24 | FocusMode | `0` = AF, `1` = MF |
| 33 | Sharpness | `0` = Hard, `1` = Normal, `2` = Soft |
| 34 | Contrast | `0` = Hard, `1` = Normal, `2` = Soft |
| 35 | Saturation | `0` = High, `1` = Normal, `2` = Low |

### Sony-Specific Tags (Non-Minolta Format)

Sony cameras that use their own MakerNote format (ILCE, NEX, SLT, RX
series from approximately 2012 onward) store data in structures that vary
significantly by model generation. Key tags decoded by ExifTool:

| Tag | Name | Description |
|-----|------|-------------|
| SonyModelID | int16u | Numeric camera model identifier |
| LensType / LensSpec | varies | Lens identification (A-mount and E-mount have different numbering systems) |
| LensType2 | int16u | E-mount lens identifier (always 0 for adapted A-mount lenses) |
| AFMode | int8u | Autofocus mode |
| AFAreaMode | int8u | AF area selection mode |
| InternalSerialNumber | string | Body serial number |
| Quality / ImageQuality | varies | Quality setting |
| ExposureMode | int8u | Shooting mode |
| SonyISO | int16u | Sony-specific ISO value |
| WhiteBalanceFineTune | int16s | WB fine-tuning value |

### Sony MakerNote Sub-Structures

Sony organizes detailed data into model-dependent sub-structures:

| Tag | Name | Present In | Contents |
|-----|------|-----------|----------|
| 0x0010 | CameraInfo | ILCE, SLT | AF info, exposure data (model-specific format) |
| 0x0020 | FocusInfo / MoreInfo | Many models | Focus data or additional camera info |
| 0x0114 | CameraSettings | A-mount models | Exposure, WB, AF settings |
| 0x0116 | ExtraInfo | Various | Model-dependent extra data |
| 0x9050 | SonyModelInfo | Most models | Camera identification |

### Common Use Cases

- **Lens identification:** Critical for Sony A-mount adapted lenses on
  E-mount bodies (the lens doesn't communicate electronically with all
  adapters, so MakerNote LensType may be the only lens identifier)
- **Image stabilization status:** SteadyShot / IBIS info
- **Legacy camera support:** Minolta DiMAGE, Konica Minolta Dynax, early
  Sony Alpha (A100-A700)
- **Body/lens serial numbers:** For warranty and theft tracking

---

## Pentax

**ImageIO constant:** `kCGImagePropertyMakerPentaxDictionary` (iOS 4.0+)

### Format

- **Header:** `"AOC\0"` (4 bytes, hex: `41 4F 43 00`) followed by its
  own byte order marker (`"MM"` or `"II"`) which may differ from the
  main TIFF byte order
- **Structure:** Standard IFD following the header and byte order bytes
- **Offsets:** Absolute from main TIFF header (older models) or relative
  to MakerNote start (newer models)

Pentax is also used by some **Ricoh** cameras (after Ricoh acquired
Pentax in 2011). The `"AOC\0"` header is used by both Pentax and Ricoh
GR-series cameras.

```
Pentax MakerNote:
  Offset 0:   "AOC\0"        (4 bytes, hex: 41 4F 43 00)
  Offset 4:   "MM" or "II"   (byte order -- may differ from main TIFF)
  Offset 6:   [IFD entries...]
```

### Key Tags

| Tag ID | Name | Type | Description |
|--------|------|------|-------------|
| 0x0000 (0) | PentaxVersion | int8u[4] | MakerNote version |
| 0x0001 (1) | PentaxModelType | int16u | `0` = Film, `1` = Digital |
| 0x0002 (2) | PreviewImageSize | int16u[2] | Preview dimensions [Width, Height] |
| 0x0003 (3) | PreviewImageLength | int32u | Preview image data size |
| 0x0004 (4) | PreviewImageStart | int32u | Offset to preview image data |
| 0x0005 (5) | PentaxModelID | int32u | Numeric model identifier (maps to camera name) |
| 0x0006 (6) | Date | int32u | Date (encoded) |
| 0x0007 (7) | Time | int32u | Time (encoded) |
| 0x0008 (8) | Quality | int16u | `0` = Good, `1` = Better, `2` = Best, `3` = TIFF, `4` = RAW (PEF), `5` = Premium, `7` = RAW (PEF, alt), `8` = RAW (DNG), `65535` = N/A |
| 0x0009 (9) | PentaxImageSize | int32u | Image dimensions (encoded) |
| 0x000b (11) | PictureMode | int16u[] | Picture mode values |
| 0x000c (12) | FlashMode | int16u[2] | Flash mode settings |
| 0x000d (13) | FocusMode | int16u | `0` = Normal, `1` = Macro, `2` = Infinity, `3` = Manual, `4` = Super Macro, `5` = Pan Focus, `16` = AF-S (single), `17` = AF-C (continuous), `18` = AF-A (auto), `32` = Contrast-detect, `33` = Tracking Contrast-detect |
| 0x000e (14) | AFPointSelected | int16u | Selected AF point index |
| 0x000f (15) | AFPointsInFocus | int32u | Bitmask of AF points that achieved focus |
| 0x0010 (16) | FocusPosition | int16u | Lens focus position (hardware level) |
| 0x0012 (18) | ExposureTime | int32u | Exposure time (encoded) |
| 0x0013 (19) | FNumber | int16u | F-number (encoded) |
| 0x0014 (20) | ISO | int16u | ISO speed |
| 0x0016 (22) | ExposureCompensation | int16u | Exposure compensation value |
| 0x0017 (23) | MeteringMode | int16u | `0` = Multi-segment, `1` = Center-weighted, `2` = Spot |
| 0x0018 (24) | AutoBracketing | int16u[2] | AEB settings |
| 0x0019 (25) | WhiteBalance | int16u | `0` = Auto, `1` = Daylight, `2` = Shade, `3` = Fluorescent, `4` = Tungsten, `5` = Manual, `6` = DaylightFluorescent, `7` = DayWhiteFluorescent, `8` = WhiteFluorescent, `65534` = Multi Auto, `65535` = Unknown |
| 0x001a (26) | WhiteBalanceMode | int16u | WB mode details |
| 0x001d (29) | FocalLength | int32u | Focal length (units of 0.01mm) |
| 0x001f (31) | Saturation | int16u | Saturation setting |
| 0x0020 (32) | Contrast | int16u | Contrast setting |
| 0x0021 (33) | Sharpness | int16u | Sharpness setting |
| 0x0029 (41) | FrameNumber | int32u | Frame number |

### World Time Tags

| Tag ID | Name | Type | Description |
|--------|------|------|-------------|
| 0x0022 (34) | WorldTimeLocation | int16u | `0` = Hometown, `1` = Destination |
| 0x0023 (35) | HometownCity | int16u | City code (hometown setting) |
| 0x0024 (36) | DestinationCity | int16u | City code (destination setting) |
| 0x0025 (37) | HometownDST | int16u | DST flag (hometown) |
| 0x0026 (38) | DestinationDST | int16u | DST flag (destination) |

### Lens and Advanced

| Tag ID | Name | Type | Description |
|--------|------|------|-------------|
| 0x003f (63) | LensType | int8u[2] | Lens type: [Series, Model]. See Lens Identification below. |
| 0x0047 (71) | Temperature | int8s | Sensor temperature (Celsius) |
| 0x0049 (73) | NoiseReduction | int16u | `0` = Off, `1` = On |
| 0x004d (77) | FlashExposureComp | int32s | Flash exposure compensation |

### Image Tone and Creative

| Tag ID | Name | Type | Description |
|--------|------|------|-------------|
| 0x005c (92) | ImageTone | int16u | Image tone preset (see table below) |
| 0x005d (93) | ColorTemperature | int16u | WB color temperature (Kelvin) |
| 0x0073 (115) | MonochromeFilterEffect | int16u | B&W filter: `1` = Green, `2` = Yellow, `3` = Orange, `4` = Red, `5` = Magenta, `6` = Blue, `7` = Cyan, `8` = Infrared |
| 0x0074 (116) | MonochromeToning | int16u | B&W toning color |
| 0x007b (123) | CrossProcess | int8u | `0` = Off, `1` = Random, `2` = Preset1, `3` = Preset2, `4` = Preset3, `33` = Favorite1, `34` = Favorite2, `35` = Favorite3 |

### ImageTone Values (Tag 0x005c)

| Value | Image Tone |
|-------|-----------|
| 0 | Natural |
| 1 | Bright |
| 2 | Portrait |
| 3 | Landscape |
| 4 | Vibrant |
| 5 | Monochrome |
| 6 | Muted |
| 7 | Reversal Film |
| 8 | Bleach Bypass |
| 9 | Radiant |
| 256 | Auto |
| 512 | Custom1 |
| 513 | Custom2 |
| 514 | Custom3 |

### HDR and Dynamic Range

| Tag ID | Name | Type | Description |
|--------|------|------|-------------|
| 0x0069 (105) | DynamicRangeExpansion | int8u[4] | HDR / Dynamic Range Expansion settings |
| 0x0071 (113) | HighISONoiseReduction | int8u | `0` = Off, `1` = Weakest, `2` = Weak, `3` = Strong, `4` = Custom |
| 0x0079 (121) | ShadowCorrection | int8u[2] | Shadow correction settings |
| 0x007a (122) | ISOAutoParameters | int8u[2] | ISO Auto min/max settings |

### Face Detection and AF Adjustment

| Tag ID | Name | Type | Description |
|--------|------|------|-------------|
| 0x0072 (114) | AFAdjustment | int16s | AF fine-tune adjustment value |
| 0x0076 (118) | FaceDetect | int8u[4] | Face detection results |
| 0x0077 (119) | FaceDetectFrameSize | int16u[2] | Face detection frame [Width, Height] |
| 0x007d (125) | LensCorr | int8u[4] | Lens correction parameters |

### Shake Reduction (Tag 0x007f)

Pentax's **Shake Reduction (SR)** is their in-body image stabilization
system (IBIS). On newer bodies, SR also enables sensor-shift features
like Astro Tracer (GPS-guided star tracking) and Pixel Shift Resolution.

The SR binary sub-structure contains:

| Field | Name | Values |
|-------|------|--------|
| SRResult | Stabilization result | `0` = Not stabilized, `1` = Stabilized, `2` = Not ready |
| ShakeReduction | SR enabled | `0` = Off, `1` = On |

### Shutter Count and Calibration

| Tag ID | Name | Type | Description |
|--------|------|------|-------------|
| 0x0200 (512) | BlackPoint | int16u[4] | Black level per channel [R, G1, G2, B] |
| 0x0201 (513) | WhitePoint | int16u[4] | White point per channel [R, G1, G2, B] |
| 0x0215 (533) | **ShutterCount** | int32u | **Total shutter actuations** since manufacture |

### Lens Identification

Pentax lens identification uses a **two-byte system** in tag 0x003f:
- **First byte (Series):** Identifies the lens family/mount
- **Second byte (Model):** Identifies the specific lens within that family

| Series | Mount/Family |
|--------|-------------|
| 1 | K/M 42mm screw-mount |
| 2 | A series (K-mount, manual aperture ring) |
| 3 | FA / F series (K-mount, autofocus) |
| 4-5 | FA / FA* series |
| 6 | DA / DA* series (APS-C digital) |
| 7 | DA Limited |
| 8 | D FA / HD series (full-frame digital) |
| 11-12 | Various DA/DA* |
| 13 | Q-mount lenses |
| 15 | 645-mount lenses |
| 21 | HD D FA* / HD PENTAX-D FA* |
| 22 | HD PENTAX-DA* |

The combination maps to a specific lens name via ExifTool's lookup table
(`%pentaxLensTypes`). This covers K-mount, 645-mount, and Q-mount lenses,
including third-party lenses from Sigma, Tamron, and Tokina.

### Common Use Cases

- **Shutter count:** Tag 0x0215 provides total actuations (useful for
  secondhand market valuation)
- **Shake Reduction status:** Verify IBIS was active and working
- **Sensor temperature:** Tag 0x0047 for thermal monitoring (useful for
  astrophotography)
- **Image tone analysis:** Determine which Picture Mode was applied
- **Lens identification:** Two-byte LensType system for K-mount lenses
  (including adapted lenses)
- **Astro Tracer verification:** SR data can indicate Astro Tracer mode

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
                2048: "Classic Negative", 2304: "Bleach Bypass",
                2560: "Nostalgic Negative", 2816: "REALA ACE"
            ]
            print("Film simulation: \(filmNames[filmMode] ?? "Unknown (\(filmMode))")")
        }
        // Focus mode (tag 0x1021 = 4129 decimal)
        if let focusMode = fuji["4129"] as? Int {
            print("Focus: \(focusMode == 0 ? "Auto" : "Manual")")
        }
        // Shadow/Highlight tone
        if let shadow = fuji["4160"] as? Int {  // 0x1040
            print("Shadow tone: \(shadow)")
        }
        if let highlight = fuji["4161"] as? Int {  // 0x1041
            print("Highlight tone: \(highlight)")
        }
    }

    // Olympus
    if let olympus = props[kCGImagePropertyMakerOlympusDictionary as String]
            as? [String: Any] {
        // Camera type (tag 0x0207 = 519 decimal)
        if let cameraType = olympus["519"] as? String {
            print("Camera: \(cameraType)")
        }
        // Quality (tag 0x0201 = 513 decimal)
        if let quality = olympus["513"] as? Int {
            let qualNames = [1: "SQ", 2: "HQ", 3: "SHQ", 4: "RAW"]
            print("Quality: \(qualNames[quality] ?? "Unknown")")
        }
    }

    // Pentax
    if let pentax = props[kCGImagePropertyMakerPentaxDictionary as String]
            as? [String: Any] {
        // Quality (tag 8)
        if let quality = pentax["8"] as? Int {
            let qualNames = [0: "Good", 1: "Better", 2: "Best",
                             4: "RAW (PEF)", 5: "Premium", 8: "RAW (DNG)"]
            print("Quality: \(qualNames[quality] ?? "Unknown")")
        }
        // Shutter count (tag 533, 0x0215)
        if let shutterCount = pentax["533"] as? Int {
            print("Shutter count: \(shutterCount)")
        }
        // Image tone (tag 92, 0x005c)
        if let imageTone = pentax["92"] as? Int {
            let toneNames = [0: "Natural", 1: "Bright", 2: "Portrait",
                             3: "Landscape", 4: "Vibrant", 5: "Monochrome",
                             7: "Reversal Film", 8: "Bleach Bypass"]
            print("Image tone: \(toneNames[imageTone] ?? "Unknown")")
        }
        // Temperature (tag 71, 0x0047)
        if let temp = pentax["71"] as? Int {
            print("Sensor temp: \(temp) C")
        }
    }

    // Minolta / Sony
    if let minolta = props[kCGImagePropertyMakerMinoltaDictionary as String]
            as? [String: Any] {
        // Quality (tag 0x0102 = 258 decimal)
        if let quality = minolta["258"] as? Int {
            let qualNames = [0: "RAW", 1: "Super Fine", 2: "Fine",
                             3: "Standard", 4: "Economy"]
            print("Quality: \(qualNames[quality] ?? "Unknown")")
        }
        // Color mode (tag 0x0101 = 257 decimal)
        if let colorMode = minolta["257"] as? Int {
            let modeNames = [0: "Natural", 1: "B&W", 2: "Vivid",
                             5: "Sepia", 12: "Portrait", 13: "Landscape"]
            print("Color mode: \(modeNames[colorMode] ?? "Unknown")")
        }
    }
}
```

---

## Cross-References

- [MakerNote Concept](makernote-concept.md) -- How MakerNote works, offset fragility
- [Apple MakerNote](apple.md) -- iPhone/iPad metadata
- [Canon MakerNote](canon.md) -- Canon-specific tags
- [Nikon MakerNote](nikon.md) -- Nikon-specific tags
- [ImageIO Property Keys](../imageio/property-keys.md) -- All dictionary constants

### External References -- Fujifilm

- [ExifTool FujiFilm Tags](https://exiftool.org/TagNames/FujiFilm.html) -- Comprehensive tag reference
- [Exiv2 Fujifilm Tags](https://exiv2.org/tags-fujifilm.html) -- Tag documentation
- [ExifTool FujiFilm.pm source](https://github.com/exiftool/exiftool/blob/master/lib/Image/ExifTool/FujiFilm.pm) -- Decode tables

### External References -- Olympus

- [ExifTool Olympus Tags](https://exiftool.org/TagNames/Olympus.html) -- Comprehensive tag reference (includes sub-IFDs)
- [Exiv2 Olympus Tags](https://exiv2.org/tags-olympus.html) -- Tag documentation
- [ExifTool Olympus.pm source](https://github.com/exiftool/exiftool/blob/master/lib/Image/ExifTool/Olympus.pm) -- Sub-IFD decode tables

### External References -- Minolta / Sony

- [ExifTool Minolta Tags](https://exiftool.org/TagNames/Minolta.html) -- Minolta tag reference
- [ExifTool Sony Tags](https://exiftool.org/TagNames/Sony.html) -- Sony tag reference
- [Exiv2 Minolta Tags](https://exiv2.org/tags-minolta.html) -- Minolta tag documentation
- [Exiv2 Sony Tags](https://exiv2.org/tags-sony.html) -- Sony tag documentation
- [ExifTool Sony.pm source](https://github.com/exiftool/exiftool/blob/master/lib/Image/ExifTool/Sony.pm) -- Sony decode tables (~10,000 lines)
- [Sony-Specific Metadata DeepWiki](https://deepwiki.com/exiftool/exiftool/9.2-sony-specific-metadata) -- Architecture overview

### External References -- Pentax

- [ExifTool Pentax Tags](https://exiftool.org/TagNames/Pentax.html) -- Comprehensive tag reference
- [Exiv2 Pentax Tags](https://exiv2.org/tags-pentax.html) -- Tag documentation
- [Pentax MakerNote Specification](https://www.ozhiker.com/electronics/pjmt/jpeg_info/pentax_mn.html) -- Early reverse-engineered spec
- [ExifTool Pentax.pm source](https://github.com/exiftool/exiftool/blob/master/lib/Image/ExifTool/Pentax.pm) -- Lens lookup tables
