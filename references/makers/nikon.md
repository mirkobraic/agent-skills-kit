# Nikon MakerNote

> Part of [Manufacturer MakerNote Dictionaries](README.md)

Nikon MakerNote stores detailed lens data, autofocus information, shooting
parameters, vibration reduction status, and encrypted color balance data.
Nikon uses a self-contained TIFF format (Type 3) with its own byte order
marker, making it more resilient to EXIF rewrites than Canon's headerless
format.

**ImageIO constant:** `kCGImagePropertyMakerNikonDictionary` (iOS 4.0+)

---

## Three Format Types

Nikon has used three different MakerNote formats across its camera history.
ExifTool and Exiv2 automatically detect which format is present.

### Type 1 (Early Coolpix)

- **Cameras:** Coolpix 700, 800, 900, 950, 995 (original firmware only)
- **Header:** None
- **Structure:** Simple IFD, big-endian byte order
- **Offsets:** Absolute (from main TIFF header)
- **Detection:** No signature; identified by camera model

### Type 2 (Later Coolpix)

- **Cameras:** Coolpix 880, 990, 995 (later firmware), 2500, 4300, 4500,
  5000, 5400, 5700, 8700
- **Header:** `"Nikon\0"` (6 bytes) + `0x01 0x00` (version 1.0)
- **Structure:** IFD directly following header
- **Offsets:** Absolute (from main TIFF header)
- **Byte order:** Same as main TIFF

```
Nikon Type 2 MakerNote:
  Offset 0:   "Nikon\0"       (6 bytes, signature)
  Offset 6:   0x01 0x00       (2 bytes, version)
  Offset 8:   [IFD entries using main TIFF byte order and offsets]
```

### Type 3 (DSLRs and Mirrorless) -- Current Standard

- **Cameras:** All D-series DSLRs (D40 through D6), all Z-series mirrorless
  (Z5, Z6, Z6III, Z7, Z7II, Z8, Z9, Zf, Zfc), newer Coolpix (P-series)
- **Header:** `"Nikon\0"` (6 bytes) + `0x02 0x10 0x00` (version 2.10)
- **Structure:** **Self-contained TIFF** with its own byte order marker
  and TIFF magic number
- **Offsets:** Relative to the internal TIFF header (resilient)

```
Nikon Type 3 MakerNote layout:
  Offset 0:   "Nikon\0"       (6 bytes, hex: 4E 69 6B 6F 6E 00)
  Offset 6:   0x02 0x10 0x00  (3 bytes, version 2.10)
  Offset 9:   [padding]
  --- self-contained TIFF starts here (base offset = 10) ---
  Offset 10:  "MM" or "II"    (byte order -- INDEPENDENT of main TIFF)
  Offset 12:  0x00 0x2A       (TIFF magic number 42)
  Offset 14:  [4-byte offset to IFD0, relative to offset 10]
  Offset 18+: [IFD entries...]
```

**Byte order varies by model:**
- **Big-endian (MM):** D40, D40x, D60, D80, D90, D100, D200, D700,
  D1x, D2x, D3, D3s
- **Little-endian (II):** D300, D300s, D3100, D5100, D5200, D7000,
  D7100, D7200, D500, D750, D810, D850, D5, D6, Z5, Z6, Z6III, Z7,
  Z7II, Z8, Z9, Zf, Zfc

The self-contained TIFF structure means the MakerNote has its own byte
order independent of the main EXIF. This is a key difference from Canon
(which inherits the main TIFF byte order).

---

## Top-Level Tag Reference (Type 3)

### Identification and Version

| Tag ID | Name | Type | Description |
|--------|------|------|-------------|
| 0x0001 (1) | MakerNoteVersion | undef[4] | Version string (e.g., `"0210"`, `"0230"`) |
| 0x001d (29) | SerialNumber | string | Camera serial number string |
| 0x00a0 (160) | SerialNumber2 | string | Alternative serial number location |

### Shooting Parameters

| Tag ID | Name | Type | Description |
|--------|------|------|-------------|
| 0x0002 (2) | ISO | int16u[2] | ISO info: [ISO setting, Auto ISO value] |
| 0x0003 (3) | ColorMode | string | `"COLOR"`, `"B&W"` |
| 0x0004 (4) | Quality | string | `"FINE"`, `"NORMAL"`, `"BASIC"`, `"RAW"`, `"RAW+FINE"` |
| 0x0005 (5) | WhiteBalance | string | `"AUTO"`, `"SUNNY"`, `"CLOUDY"`, `"SHADE"`, `"FLASH"`, `"FLUORESCENT"`, `"INCANDESCENT"`, `"MANUAL"` |
| 0x0006 (6) | Sharpening | string | `"AUTO"`, `"NORMAL"`, `"LOW"`, `"MED LOW"`, `"HIGH"`, `"MED HIGH"`, `"NONE"` |
| 0x0007 (7) | FocusMode | string | `"AF-S"` (single servo), `"AF-C"` (continuous servo), `"AF-A"` (auto), `"MF"` (manual) |
| 0x0008 (8) | FlashSetting | string | `"NORMAL"`, `"SLOW"`, `"REAR"`, `"RED-EYE"` |
| 0x0009 (9) | FlashType | string | `"Built-In"`, `""` (none), external flash model |
| 0x000b (11) | WhiteBalanceFineTune | int16s[2] | Fine-tune [Amber-Blue, Green-Magenta] |
| 0x000c (12) | WB_RBLevels | rational64u[4] | White balance R, B level data |
| 0x000d (13) | ProgramShift | undef[4] | Program shift value (APEX) |
| 0x000e (14) | ExposureDifference | undef[4] | Metered vs actual exposure difference |
| 0x000f (15) | ISOSelection | string | ISO selection mode |
| 0x0012 (18) | FlashExposureComp | undef[4] | Flash exposure compensation (APEX) |
| 0x0013 (19) | ISOSetting | int16u[2] | Manual ISO setting values |
| 0x0017 (23) | ExternalFlashExposureComp | undef[4] | External flash compensation |
| 0x0018 (24) | FlashExposureBracketValue | undef[4] | Flash bracket value |
| 0x0019 (25) | ExposureBracketValue | rational64s | AE bracket compensation |
| 0x001c (28) | ExposureTuning | undef[3] | Exposure tuning adjustment |

### Color and Processing

| Tag ID | Name | Type | Description |
|--------|------|------|-------------|
| 0x001a (26) | ImageProcessing | string | Image processing applied |
| 0x001e (30) | ColorSpace | int16u | `1` = sRGB, `2` = Adobe RGB |
| 0x0022 (34) | ActiveDLighting | int16u | See Active D-Lighting table below |
| 0x0023 (35) | PictureControlData | undef | Picture Control sub-structure (see section below) |
| 0x002a (42) | VignetteControl | int16u | `0` = Off, `1` = Low, `3` = Normal, `5` = High |
| 0x002b (43) | DistortInfo | undef | Auto distortion control info |
| 0x002c (44) | HDRInfo | undef | HDR shooting data sub-structure |
| 0x004f (79) | ColorTemperatureAuto | int16u | Auto WB color temperature (Kelvin) |
| 0x008d (141) | ColorHue | string | Color hue setting |
| 0x0092 (146) | HueAdjustment | int16s | Hue adjustment value |
| 0x0094 (148) | SaturationAdj | int16s | Saturation adjustment |
| 0x0095 (149) | NoiseReduction | string | Noise reduction setting |
| 0x0097 (151) | ColorBalance | undef | **Encrypted** on version 200+ (see Encryption section) |

### Image Information

| Tag ID | Name | Type | Description |
|--------|------|------|-------------|
| 0x0011 (17) | NikonPreview | IFD | Pointer to preview/thumbnail IFD |
| 0x0016 (22) | ImageBoundary | int16u[4] | Active image area: [X, Y, Width, Height] |
| 0x001b (27) | CropHiSpeed | int16u[7] | DX crop info: [mode, w, h, x, y, cropW, cropH] |
| 0x0020 (32) | ImageAuthentication | int8u | `0` = Off, `1` = On |
| 0x0035 (53) | NikonCropInfo | undef | DX crop info (alternate) |
| 0x003d (61) | BlackLevel | int16u[4] | Black level values per channel [R, G1, G2, B] |
| 0x0093 (147) | NEFCompression | int16u | NEF compression type (see table below) |
| 0x009a (154) | SensorPixelSize | rational64u[2] | Physical pixel size in microns [X, Y] |
| 0x00a2 (162) | ImageDataSize | int32u | Compressed image data size in bytes |

### NEFCompression Values

| Value | Compression |
|-------|-------------|
| 1 | Lossy (type 1) |
| 2 | Uncompressed (12-bit) |
| 3 | Lossless (12-bit) |
| 4 | Lossy (type 2) |
| 5 | Striped packed 12-bit |
| 6 | Uncompressed (14-bit) |
| 7 | Lossless (14-bit) |
| 8 | Lossy (14-bit) |
| 10 | Packed 12-bit |
| 13 | Packed 14-bit |
| 14 | High Efficiency |
| 15 | High Efficiency Star |

### Face Detection and AF

| Tag ID | Name | Type | Description |
|--------|------|------|-------------|
| 0x0021 (33) | FaceDetect | undef | Face detection data |
| 0x0088 (136) | AFInfo | undef | AF point and focus info (older format) |
| 0x00b0 (176) | AFInfo2 | undef | Detailed AF info (see section below) |
| 0x00b6 (182) | AFTune | undef | AF fine-tune adjustment data |

### Time and Location

| Tag ID | Name | Type | Description |
|--------|------|------|-------------|
| 0x0024 (36) | WorldTime | undef | Time zone offset and DST info |
| 0x0025 (37) | ISOInfo | undef | Detailed ISO information |
| 0x0039 (57) | LocationInfo | undef | GPS/location data from camera (built-in GPS) |

### Lens

| Tag ID | Name | Type | Description |
|--------|------|------|-------------|
| 0x0083 (131) | LensType | int8u | Lens type bitfield (see section below) |
| 0x0084 (132) | Lens | rational64u[4] | [MinFL, MaxFL, MaxApertureAtMinFL, MaxApertureAtMaxFL] |
| 0x008b (139) | LensFStops | undef[4] | Lens f-stop range (encoded) |
| 0x0098 (152) | LensData | undef | Detailed lens data -- **encrypted** on version 0201+ |

### Flash

| Tag ID | Name | Type | Description |
|--------|------|------|-------------|
| 0x0087 (135) | FlashMode | int8u | `0` = Did not fire, `1` = Fired (manual), `3` = Not ready, `7` = Fired (external), `8` = Fired (Commander), `9` = Fired (TTL) |
| 0x00a8 (168) | FlashInfo | undef | Flash info sub-structure |
| 0x00b7 (183) | NikonFlashInfo | undef | Flash info (newer format) |

### Image Optimization

| Tag ID | Name | Type | Description |
|--------|------|------|-------------|
| 0x00a9 (169) | ImageOptimization | string | Image optimization setting |
| 0x00aa (170) | Saturation | string | Saturation setting string |
| 0x00ab (171) | VariProgram | string | Variable program mode name |
| 0x00ac (172) | ImageStabilization | string | VR/IS mode string |
| 0x00ad (173) | AFResponse | string | AF response description |

### Shutter Count

| Tag ID | Name | Type | Description |
|--------|------|------|-------------|
| 0x00a5 (165) | ImageCount | int32u | Image count since last reset (user-resettable on some models) |
| 0x00a7 (167) | **ShutterCount** | int32u | **Total shutter actuations** since manufacture |
| 0x00bb (187) | MechanicalShutterCount | int32u | Mechanical shutter only (available on some mirrorless bodies, e.g., Z8, Z9) |

### Multi-Exposure

| Tag ID | Name | Type | Description |
|--------|------|------|-------------|
| 0x00b8 (184) | MultiExposure | undef | Multiple exposure data |
| 0x00b9 (185) | HDRInfo2 | undef | HDR info (newer models) |

### Miscellaneous

| Tag ID | Name | Type | Description |
|--------|------|------|-------------|
| 0x008c (140) | ContrastCurve | undef | Contrast/tone curve data |
| 0x008e (142) | SceneMode | string | Scene mode name |
| 0x0091 (145) | ShotInfo | undef | Shot info sub-structure (model-dependent) |
| 0x009c (156) | SceneAssist | string | Scene assist mode |
| 0x009e (158) | RetouchHistory | int16u[10] | Retouch history flags (up to 10 retouching operations) |
| 0x0099 (153) | RawImageCenter | int16u[2] | Raw image center coordinates |
| 0x00b1 (177) | FileInfo | undef | File info sub-structure |

---

## Encryption

Nikon encrypts certain metadata fields to prevent easy extraction by
third-party software. The encryption has been **fully reverse-engineered**
and is handled automatically by ExifTool and Exiv2.

### Encrypted Fields

| Field | Tag | Encrypted Since | Purpose |
|-------|-----|----------------|---------|
| ColorBalance | 0x0097 | Version 200+ (D2H and later) | White balance calibration data; R/B channel coefficients |
| LensData | 0x0098 | LensDataVersion 0201+ | Detailed lens identification, focus distance, focal length at capture |

### Decryption Algorithm

The decryption uses an **XOR-based stream cipher** with two keys derived
from other MakerNote tags:

1. **Key 1:** Derived from the **SerialNumber** (tag 0x001d) -- last 4
   digits converted to a 4-byte value
2. **Key 2:** Derived from the **ShutterCount** (tag 0x00a7) -- lower
   4 bytes

These two keys are combined with a **hardcoded 256-byte lookup table**
(the "xlat" table) to generate a key stream. The encrypted bytes are
XORed with this key stream to produce the decrypted data.

```
Decryption pseudocode:
  serial_key  = last_4_digits_of(SerialNumber)
  shutter_key = lower_4_bytes_of(ShutterCount)
  ci = xlat[0][ serial_key ] XOR shutter_key
  cj = xlat[1][ serial_key ]
  for each encrypted byte:
      ci = (ci + cj) mod 256
      decrypted_byte = encrypted_byte XOR xlat[0][ci]
```

**Implications:**
- If SerialNumber or ShutterCount is missing or corrupted, the encrypted
  data **cannot be decrypted**
- ImageIO likely does not decrypt these fields (not confirmed). For full
  Nikon metadata extraction, ExifTool is required.
- The encryption was first broken in April 2005 by the dcraw community
  within days of the D2X shipping with encrypted white balance data

### History of Nikon Encryption

Nikon introduced ColorBalance encryption with the **D2H** (2003) to
prevent third-party RAW converters from reading white balance coefficients.
This was reverse-engineered almost immediately. Nikon then added LensData
encryption with **LensDataVersion 0201**. Both encryptions use the same
basic algorithm with different starting parameters.

---

## Lens Data (Tag 0x0098)

The LensData tag contains detailed lens information in a sub-structure
whose format varies by LensDataVersion:

| Version | Cameras | Encrypted | Key Fields |
|---------|---------|-----------|------------|
| 0100 | D100, D1x | No | LensIDNumber, FocalLength, FocusDistance, MaxAperture |
| 0101 | D70, D70s | No | Same as 0100 + MinAperture |
| 0201 | D200, D2H, D2Hs | **Yes** | LensIDNumber, FocalLength, FocusDistance, MaxAperture, EffectiveMaxAperture |
| 0204 | D300, D700, D3 | **Yes** | Same as 0201 + additional fields |
| 0400 | D7000, D5100 | **Yes** | Extended lens data |
| 0800 | Z6, Z7, D500, D850 | **Yes** | Extended for Z-mount + adapted lenses |
| 0801 | Z8, Z9 | **Yes** | Latest format |

### LensType Bitfield (Tag 0x0083)

| Bit | Meaning |
|-----|---------|
| 0 | MF (manual focus lens) |
| 1 | D-type lens (has distance encoder) |
| 2 | G-type lens (no aperture ring) |
| 3 | VR lens (vibration reduction) |
| 4 | 1 Nikkor lens (CX mount) |
| 5 | FT-1 adapter attached |
| 6 | E-type lens (electronic aperture) |
| 7 | AF-P lens (pulse motor autofocus) |

### Lens Identification

Nikon lens identification is **complex** because:
- The Lens tag (0x0084) provides focal length + aperture range
- The LensType bitfield (0x0083) identifies lens characteristics
- The LensData sub-structure (0x0098, often encrypted) contains a
  **LensIDNumber** that maps to a specific lens via ExifTool's lookup table
- Multiple lenses can have the same focal length + aperture range, so the
  LensIDNumber is needed for unique identification
- Adapted lenses (F-mount on Z bodies via FTZ adapter) use different
  identification paths

---

## Vibration Reduction (VR) Info (Tag 0x001f)

The VRInfo tag contains a sub-structure with VR/IS settings:

| Offset | Name | Values |
|--------|------|--------|
| 0-3 | VRInfoVersion | Version bytes (e.g., `0100`, `0200`, `0300`) |
| 4 | VibrationReduction | `1` = On, `2` = Off |
| 6 | VRMode | `0` = Normal, `1` = Active (Sport), `2` = Sport |

VR modes control the level of stabilization:
- **Normal:** Optimized for general shooting; allows deliberate panning
- **Active/Sport:** Maximum stabilization; compensates for all motion
  including deliberate panning (useful in vehicles, boats)

---

## AF Info (Tag 0x00b0)

The AFInfo2 structure provides detailed autofocus data. The structure
varies by camera generation and AF system.

### Common Fields

| Field | Description |
|-------|-------------|
| AFAreaMode | AF area selection mode (see table below) |
| ContrastDetectAF | `0` = Off, `1` = On (Live View / Mirrorless) |
| PhaseDetectAF | `0` = Off, `1` = On (DSLR viewfinder / On-sensor PDAF) |
| PrimaryAFPoint | Index of the primary AF point used for focus |
| AFPointsUsed | Bitmask of AF points that contributed to focus |
| AFImageWidth | Image width for AF coordinate mapping |
| AFImageHeight | Image height for AF coordinate mapping |
| AFAreaXPosition | X position of AF area in image coordinates |
| AFAreaYPosition | Y position of AF area in image coordinates |
| AFAreaWidth | Width of AF area |
| AFAreaHeight | Height of AF area |

### AFAreaMode Values

| Value | Mode | Description |
|-------|------|-------------|
| 0 | Single Point | Single selectable AF point |
| 1 | Dynamic Area | Primary point + surrounding helper points |
| 2 | Dynamic Area (closest) | Dynamic area with closest subject priority |
| 3 | Group Dynamic | Group of AF points acts as one |
| 4 | Single Point (dynamic) | Single point with dynamic backup |
| 6 | Pinpoint | Smallest selectable AF area |
| 7 | Dynamic 3D | 3D tracking with subject recognition |
| 8 | Dynamic Auto | Auto-area dynamic selection |
| 9 | Wide-area AF (S) | Small wide-area zone |
| 10 | Wide-area AF (L) | Large wide-area zone |
| 11 | Wide-area AF (S, new) | Small zone (newer models) |
| 12 | Wide-area AF (L, new) | Large zone (newer models) |
| 14 | Wide-area AF (C1) | Custom zone size 1 |
| 15 | Wide-area AF (C2) | Custom zone size 2 |
| 16 | Auto-area AF | Camera selects AF area automatically; includes face/eye detection on Z-series |

### AF System by Camera Generation

| System | Cameras | AF Points | Detection |
|--------|---------|-----------|-----------|
| Multi-CAM 4800 | D300, D300s, D700 | 51 | Phase detect |
| Multi-CAM 3500FX | D750, D610, D810 | 51 | Phase detect |
| Multi-CAM 20K | D5, D500, D6 | 153 | Phase detect |
| Hybrid (on-sensor) | Z5, Z6, Z7 | 273/493 | Phase + contrast (on-sensor PDAF) |
| EXPEED 7 | Z8, Z9, Zf | 493 | Phase + contrast (3D tracking, subject detection) |

---

## Shutter Count

Nikon provides a **straightforward shutter actuation counter**, unlike
Canon which requires model-specific extraction:

| Tag | Value | Notes |
|-----|-------|-------|
| 0x00a7 (ShutterCount) | Total actuations since manufacture | Electronic + mechanical |
| 0x00bb (MechanicalShutterCount) | Mechanical shutter only | Z8, Z9, and select mirrorless |
| 0x00a5 (ImageCount) | Count since last reset | User-resettable on some models |

The ShutterCount (0x00a7) is the definitive actuation counter. It is widely
used to assess camera usage and remaining shutter life on the secondhand
market. Nikon DSLRs are typically rated for 150,000-400,000 actuations
depending on the model tier.

**Note:** ShutterCount is also one of the two keys used for Nikon's
encryption algorithm. If the ShutterCount tag is corrupted, encrypted
LensData and ColorBalance cannot be decrypted.

---

## Active D-Lighting (Tag 0x0022)

Nikon's Active D-Lighting preserves highlight and shadow detail by
adjusting tone mapping:

| Value | Setting |
|-------|---------|
| 0 | Off |
| 1 | Low |
| 3 | Normal |
| 5 | High |
| 7 | Extra High |
| 8 | Extra High 1 |
| 9 | Extra High 2 |
| 10 | Extra High 3 |
| 11 | Extra High 4 |
| 0xFFFF | Auto |

---

## Picture Control (Tag 0x0023)

The PictureControlData tag contains Nikon's Picture Control settings
(analogous to Canon's Picture Styles):

### Picture Control Presets

| Preset | Description |
|--------|-------------|
| Standard | Balanced processing |
| Neutral | Minimal processing; flat output for post-processing |
| Vivid | Enhanced saturation and contrast |
| Monochrome | Black and white |
| Portrait | Optimized skin tones |
| Landscape | Enhanced blues and greens |
| Flat | Maximum dynamic range; very low contrast |
| Auto | Camera-selected processing |
| Creative Picture Controls | 20 preset styles (Dream, Morning, Pop, etc.) |

### Adjustable Parameters

Each Picture Control preset allows adjustment of:
- **Sharpening** (0-9 or Auto)
- **Mid-range Sharpening** (newer models, 0-9 or Auto)
- **Contrast** (-3 to +3 or Auto)
- **Brightness** (-1 to +1)
- **Saturation** (-3 to +3 or Auto)
- **Hue** (-3 to +3)
- **Clarity** (newer models, -5 to +5)

---

## Known Idiosyncrasies

| Issue | Details |
|-------|---------|
| **Nikon Transfer** (v1.3) | Corrupts SubIFD information when processing NEF images |
| **Nikon Capture** | Writes incorrect size for MakerNote block; can cause data loss if file is subsequently edited by other software |
| **Self-contained TIFF** | Byte order inside MakerNote may differ from main EXIF. Code must read the MakerNote's own byte order marker. |
| **Encryption** | ColorBalance (v200+) and LensData (v0201+) are encrypted using serial number + shutter count as keys |
| **Sony/Nikon confusion** | Sony ARW files from cameras with Nikon-heritage sensors sometimes have fragments that look Nikon-like, but they are Sony MakerNotes |
| **NEF-specific structures** | Some MakerNote sub-structures (ShotInfo, CameraInfo) vary significantly by model; ExifTool uses per-model decode tables |

---

## Reading Nikon MakerNote in Swift

```swift
import ImageIO

func readNikonMakerNote(from url: URL) {
    guard let source = CGImageSourceCreateWithURL(url as CFURL, nil),
          let props = CGImageSourceCopyPropertiesAtIndex(source, 0, nil)
                  as? [String: Any],
          let nikon = props[kCGImagePropertyMakerNikonDictionary as String]
                  as? [String: Any] else { return }

    // Focus mode (tag 7)
    if let focusMode = nikon["7"] as? String {
        print("Focus: \(focusMode)")  // "AF-S", "AF-C", "AF-A", "MF"
    }

    // Quality (tag 4)
    if let quality = nikon["4"] as? String {
        print("Quality: \(quality)")  // "FINE", "RAW", "RAW+FINE"
    }

    // White balance (tag 5)
    if let wb = nikon["5"] as? String {
        print("WB: \(wb)")  // "AUTO", "SUNNY", "CLOUDY"
    }

    // Serial number (tag 29, 0x001d)
    if let serial = nikon["29"] as? String {
        print("Serial: \(serial)")
    }

    // Shutter count (tag 167, 0x00a7)
    if let shutterCount = nikon["167"] as? Int {
        print("Shutter count: \(shutterCount)")
    }

    // Active D-Lighting (tag 34, 0x0022)
    if let adl = nikon["34"] as? Int {
        let adlNames = [0: "Off", 1: "Low", 3: "Normal",
                        5: "High", 7: "Extra High", 0xFFFF: "Auto"]
        print("Active D-Lighting: \(adlNames[adl] ?? "Unknown")")
    }

    // Color space (tag 30, 0x001e)
    if let cs = nikon["30"] as? Int {
        print("Color space: \(cs == 1 ? "sRGB" : "Adobe RGB")")
    }

    // Lens (tag 132, 0x0084) -- focal/aperture range
    if let lens = nikon["132"] as? [Double], lens.count == 4 {
        let minFL = lens[0], maxFL = lens[1]
        let maxApMin = lens[2], maxApMax = lens[3]
        if minFL == maxFL {
            print("Lens: \(Int(minFL))mm f/\(maxApMin)")
        } else {
            print("Lens: \(Int(minFL))-\(Int(maxFL))mm f/\(maxApMin)-\(maxApMax)")
        }
    }

    // Vignette control (tag 42, 0x002a)
    if let vc = nikon["42"] as? Int {
        let vcNames = [0: "Off", 1: "Low", 3: "Normal", 5: "High"]
        print("Vignette control: \(vcNames[vc] ?? "Unknown")")
    }

    // Image stabilization (tag 172, 0x00ac)
    if let vr = nikon["172"] as? String {
        print("VR: \(vr)")
    }
}
```

> **Note:** ImageIO may not expose encrypted fields (ColorBalance,
> LensData) in decoded form. For those, ExifTool or Exiv2 is required.
> The decryption algorithm needs the SerialNumber and ShutterCount as keys.

---

## Cross-References

- [MakerNote Concept](makernote-concept.md) -- How MakerNote works, offset fragility
- [Canon MakerNote](canon.md) -- Canon-specific tags for comparison
- [ImageIO Property Keys](../imageio/property-keys.md) -- `kCGImagePropertyMakerNikonDictionary`
- [EXIF Tag Reference](../exif/tag-reference.md) -- Standard EXIF tags

### External References

- [ExifTool Nikon Tags](https://exiftool.org/TagNames/Nikon.html) -- Comprehensive tag reference
- [Exiv2 Nikon Tags](https://exiv2.org/tags-nikon.html) -- Tag documentation (3 formats)
- [Nikon NEF Format](http://lclevy.free.fr/nef/) -- Laurent Clevy's reverse-engineered NEF specification including encryption details
- [ExifTool Nikon.pm source](https://github.com/exiftool/exiftool/blob/master/lib/Image/ExifTool/Nikon.pm) -- Definitive decode tables (~8,000 lines)
- [ExifTool Idiosyncrasies](https://exiftool.org/idiosyncracies.html) -- Nikon-specific bugs and edge cases
