# ICC Profile Basics

An ICC profile is a standardized data file that characterizes how a device (camera,
display, printer) or color space reproduces color. The International Color
Consortium (ICC) specification -- formally **ICC.1:2022 (v4.4)** -- defines the
binary format, required tags, and the Profile Connection Space (PCS) that lets any
two profiles be chained together for device-independent color conversion.

---

## What an ICC Profile Encodes

At its core, a profile provides a mathematical mapping between a device's native
color encoding and a device-independent **Profile Connection Space (PCS)**. The
PCS is either **CIEXYZ** or **CIELAB D50**, giving a common reference that the
Color Management Module (CMM) uses to convert between any two profiled devices.

A profile encodes:

| Data | Purpose |
|------|---------|
| **Color primaries** | CIE XYZ coordinates of R, G, B (or C, M, Y, K) primaries |
| **White point** | Media or illuminant white in XYZ |
| **Tone response curves (TRC)** | Non-linear transfer functions (gamma, sRGB curve, PQ, HLG) |
| **Gamut boundary** | The range of reproducible colors |
| **Rendering intent transforms** | Perceptual, Relative Colorimetric, Saturation, Absolute Colorimetric |
| **Profile metadata** | Description, creator, copyright, creation date, version |

### How a Profile Conversion Works

To convert color values from Device A to Device B:

```
Device A values ──[Profile A]──> PCS (XYZ or Lab D50) ──[Profile B]──> Device B values
```

The CMM (Color Management Module) chains the two profiles through the PCS. On
Apple platforms, the CMM is **ColorSync**, invoked automatically by CoreGraphics
whenever you draw content with a different `CGColorSpace` than the destination
context.

---

## Profile Binary Structure

Every ICC profile is a single binary blob with three sections. All multi-byte
values are encoded as **big-endian**:

```
+---------------------------+
|  Header  (128 bytes)      |
+---------------------------+
|  Tag Table (variable)     |
+---------------------------+
|  Tag Data  (variable)     |
+---------------------------+
```

### 1. Header (128 bytes, fixed)

The header provides identification and selection fields. Key fields:

| Offset | Size | Field | Description |
|--------|------|-------|-------------|
| 0 | 4 | Profile size | Total file size in bytes |
| 4 | 4 | Preferred CMM | Four-char CMM signature (e.g. `'appl'` for Apple ColorSync) |
| 8 | 4 | Version | Major.minor.bugfix (e.g. `0x04400000` = v4.4) |
| 12 | 4 | Profile/Device class | See profile classes below |
| 16 | 4 | Data color space | Four-char signature: `'RGB '`, `'CMYK'`, `'GRAY'`, `'Lab '`, `'XYZ '` |
| 20 | 4 | PCS | Connection space: `'XYZ '` or `'Lab '` |
| 24 | 12 | Date/time | Profile creation date (year, month, day, hour, minute, second) |
| 36 | 4 | File signature | Always `'acsp'` (0x61637370) -- magic number identifying a valid ICC profile |
| 40 | 4 | Primary platform | `'APPL'` (Apple), `'MSFT'` (Microsoft), `'SGI '`, `'SUNW'` |
| 44 | 4 | Profile flags | Bit 0: embedded in file; Bit 1: cannot be used independently |
| 48 | 4 | Device manufacturer | Four-char vendor signature |
| 52 | 4 | Device model | Four-char model signature |
| 56 | 8 | Device attributes | Reflective/transparency, glossy/matte, positive/negative, color/B&W |
| 64 | 4 | Rendering intent | Default: 0=Perceptual, 1=Relative Colorimetric, 2=Saturation, 3=Absolute Colorimetric |
| 68 | 12 | PCS illuminant | Fixed D50 XYZ: (0.9642, 1.0000, 0.8249) |
| 80 | 4 | Profile creator | Four-char signature of creating software |
| 84 | 16 | Profile ID (v4) | MD5 hash of profile for unique identification (zero-filled in v2) |
| 100 | 28 | Reserved | Must be zero |

> **Key detail:** The magic number `'acsp'` at offset 36 is how software
> identifies a blob of bytes as an ICC profile. If the four bytes at offset 36
> are not `0x61637370`, it is not a valid ICC profile.

> **Version encoding:** The version number at offset 8 is encoded as
> major.minor.bugfix in BCD. For example, v4.4.0.0 is `0x04400000`, v2.4.0.0
> is `0x02400000`. The minor version occupies the upper nibble of byte 9.

### 2. Tag Table

Immediately after the header. Starts with a 4-byte count of tags, then each
entry is 12 bytes:

| Size | Field | Description |
|------|-------|-------------|
| 4 | Tag signature | Four-char tag name (e.g. `'desc'`, `'rXYZ'`, `'rTRC'`) |
| 4 | Offset | Byte offset from start of profile to tag data |
| 4 | Size | Byte length of tag data |

Multiple tags may share the same data (same offset) -- a common optimization
when red/green/blue TRC curves are identical (as in sRGB, where all three
channels use the same piece-wise transfer function).

### 3. Tag Data

The actual profile data: curves, matrices, lookup tables, text descriptions.
Each tag's data starts with a 4-byte type signature identifying how to
interpret the bytes:

| Type Signature | Name | Description |
|----------------|------|-------------|
| `'curv'` | Curve | Tone response curve: single gamma value or array of 16-bit entries |
| `'para'` | Parametric Curve | Formula-based curve with parameters (v4+) |
| `'XYZ '` | XYZ Number | CIE XYZ tristimulus values (s15Fixed16 format) |
| `'mluc'` | Multi-Localized Unicode | Unicode text with multiple language/country variants (v4) |
| `'desc'` | Text Description | Platform-specific text (v2; deprecated in v4) |
| `'text'` | Text | Simple ASCII text |
| `'mAB '` | lutAtoB | Multi-dimensional LUT: device to PCS (v4) |
| `'mBA '` | lutBtoA | Multi-dimensional LUT: PCS to device (v4) |
| `'mft1'` | lut8 | 8-bit lookup table (v2) |
| `'mft2'` | lut16 | 16-bit lookup table (v2) |
| `'sf32'` | s15Fixed16Array | Array of signed 15.16 fixed-point numbers |
| `'sig '` | Signature | Four-byte signature value |

---

## Profile Classes

The profile class (byte 12-15 of the header) identifies the type of device or
conversion the profile represents. Seven classes are defined:

| Class | Signature | Description | Typical Use |
|-------|-----------|-------------|-------------|
| **Input** | `'scnr'` | Scanner, camera, or other capture device | Map device RGB/CMYK to PCS |
| **Display** | `'mntr'` | Monitor, projector, or display device | Map PCS to device RGB (and back) |
| **Output** | `'prtr'` | Printer, press, or output device | Map PCS to CMYK/RGB device space |
| **DeviceLink** | `'link'` | Direct device-to-device conversion | Skip PCS; concatenated transform |
| **ColorSpace** | `'spac'` | Abstract color space conversion | Map one PCS encoding to another |
| **Abstract** | `'abst'` | Abstract visual effect transform | Artistic color adjustments in PCS |
| **NamedColor** | `'nmcl'` | Named color palette | Spot colors (Pantone, HKS) |

Most image files embed **Display** class profiles (sRGB, Display P3, Adobe RGB).
Camera-captured images may embed **Input** class profiles. **DeviceLink**
profiles are used in prepress workflows where PCS round-tripping would lose
precision.

---

## Color Spaces

The data color space field (header bytes 16-19) identifies the device-side
color model:

| Signature | Color Space | Components | Notes |
|-----------|-------------|------------|-------|
| `'RGB '` | RGB | 3 | Most common for displays and digital cameras |
| `'CMYK'` | CMYK | 4 | Print workflows |
| `'GRAY'` | Grayscale | 1 | Monochrome images |
| `'Lab '` | CIELAB | 3 | Used as PCS and for device-independent encoding |
| `'XYZ '` | CIEXYZ | 3 | Used as PCS; rare as device space |
| `'HLS '` | HLS | 3 | Hue-Lightness-Saturation |
| `'HSV '` | HSV | 3 | Hue-Saturation-Value |
| `'YCbr'` | YCbCr | 3 | Video encoding |
| `'Luv '` | CIELuv | 3 | Rarely used |
| `'2CLR'`..`'FCLR'` | 2-15 color | 2-15 | Multi-channel (e.g. hexachrome, n-color inkjet) |

ImageIO reports the color space via `kCGImagePropertyColorModel`:

| ImageIO Constant | Value |
|------------------|-------|
| `kCGImagePropertyColorModelRGB` | `"RGB"` |
| `kCGImagePropertyColorModelGray` | `"Gray"` |
| `kCGImagePropertyColorModelCMYK` | `"CMYK"` |
| `kCGImagePropertyColorModelLab` | `"Lab"` |

---

## Key Profile Tags

### Required Tags (all profile classes)

| Tag | Signature | Type | Description |
|-----|-----------|------|-------------|
| **profileDescription** | `'desc'` | `mluc` (v4) / `desc` (v2) | Human-readable profile name |
| **mediaWhitePoint** | `'wtpt'` | `XYZ ` | Media white point in PCS XYZ (always D50 for v4) |
| **copyright** | `'cprt'` | `mluc` / `text` | Copyright string |

### RGB Display Profile Tags (the most common type in images)

| Tag | Signature | Type | Description |
|-----|-----------|------|-------------|
| **redTRC** | `'rTRC'` | `curv` / `para` | Red channel tone response curve |
| **greenTRC** | `'gTRC'` | `curv` / `para` | Green channel tone response curve |
| **blueTRC** | `'bTRC'` | `curv` / `para` | Blue channel tone response curve |
| **redColorant** | `'rXYZ'` | `XYZ ` | Red primary in PCS XYZ |
| **greenColorant** | `'gXYZ'` | `XYZ ` | Green primary in PCS XYZ |
| **blueColorant** | `'bXYZ'` | `XYZ ` | Blue primary in PCS XYZ |
| **chromaticAdaptation** | `'chad'` | `sf32` | 3x3 matrix for adapting to/from D50 (v4 required) |

> **How a simple RGB profile works:** To convert RGB values to PCS XYZ, the CMM
> applies the TRC curves to linearize each channel, then multiplies by the 3x3
> matrix formed from the rXYZ/gXYZ/bXYZ column vectors. The `chad` tag provides
> chromatic adaptation from the actual white point to D50 (the fixed PCS
> illuminant).

### Tone Response Curves: `curv` vs `para`

The TRC tags define the non-linear transfer function for each channel. ICC
defines two curve types:

**`curv` (curve type, v2 and v4):**

| Count | Interpretation |
|-------|---------------|
| 0 entries | Identity curve (linear, gamma 1.0) |
| 1 entry | Single unsigned 8.8 fixed-point gamma value (e.g. `0x0233` = 2.19921875 for Adobe RGB) |
| N entries | Lookup table with N evenly-spaced 16-bit entries (0-65535 maps to 0.0-1.0) |

**`para` (parametric curve type, v4 only):**

Five function types are defined, from a simple power law to the full sRGB
piece-wise curve:

| Type | Parameters | Formula |
|------|-----------|---------|
| 0 | g | `Y = X^g` |
| 1 | g, a, b | `Y = (aX + b)^g` for X >= -b/a; else `Y = 0` |
| 2 | g, a, b, c | `Y = (aX + b)^g + c` for X >= -b/a; else `Y = c` |
| 3 | g, a, b, c, d | `Y = (aX + b)^g` for X >= d; `Y = cX` for X < d |
| 4 | g, a, b, c, d, e, f | `Y = (aX + b)^g + e` for X >= d; `Y = cX + f` for X < d |

Type 3 encodes the sRGB transfer function: `g=2.4, a=1/1.055, b=0.055/1.055,
c=1/12.92, d=0.04045`. Type 0 encodes a pure gamma (Adobe RGB: `g≈2.2`, stored as 2.19999695 in s15Fixed16).

> **Precision advantage of `para`:** A `curv` with a single entry encodes gamma
> as u8Fixed8Number (e.g. 2.19921875 for Adobe RGB, the closest to 2.2
> representable in 8.8 format). A `para` type-0 curve uses s15Fixed16Number,
> allowing gamma 2.19999695 -- much closer to the true 2.2.

### Lookup Table Tags (for complex transforms)

| Tag | Signature | Type | Description |
|-----|-----------|------|-------------|
| **AToB0** | `'A2B0'` | `mAB ` / `mft2` | Device to PCS, perceptual intent |
| **AToB1** | `'A2B1'` | `mAB ` / `mft2` | Device to PCS, relative colorimetric |
| **AToB2** | `'A2B2'` | `mAB ` / `mft2` | Device to PCS, saturation |
| **BToA0** | `'B2A0'` | `mBA ` / `mft2` | PCS to device, perceptual intent |
| **BToA1** | `'B2A1'` | `mBA ` / `mft2` | PCS to device, relative colorimetric |
| **BToA2** | `'B2A2'` | `mBA ` / `mft2` | PCS to device, saturation |
| **gamut** | `'gamt'` | `mAB ` | Gamut boundary check (in/out) |

CLUT (Color Look-Up Table) profiles are used when the simple matrix model is
insufficient -- CMYK profiles always use CLUTs because the CMYK-to-XYZ mapping
is non-linear and device-dependent.

### Other Notable Tags

| Tag | Signature | Description |
|-----|-----------|-------------|
| **technology** | `'tech'` | Device technology (CRT, LCD, inkjet, etc.) |
| **viewingConditions** | `'view'` | Illuminant and surround for intended viewing |
| **luminance** | `'lumi'` | Absolute luminance of the display in cd/m2 |
| **measurement** | `'meas'` | Measurement conditions (observer, illuminant, geometry) |
| **profileSequenceDesc** | `'pseq'` | Sequence of profiles used to create a DeviceLink |
| **colorantTable** | `'clrt'` | Names and PCS values of colorants (for multi-channel profiles) |

---

## Rendering Intents

Every ICC conversion specifies one of four rendering intents, which controls
how out-of-gamut colors are handled:

### 1. Perceptual (0)

Compresses the entire source gamut into the destination gamut, preserving
the visual relationship between all colors. Shadows and highlights may shift
slightly, but no colors clip. Best for photographs with many out-of-gamut
colors.

In v2, the perceptual intent behavior was vendor-dependent and inconsistent
across implementations. V4 standardized the PCS encoding for perceptual
transforms, improving cross-CMM consistency.

### 2. Relative Colorimetric (1)

Maps the source white point to the destination white point, then reproduces
in-gamut colors exactly. Out-of-gamut colors are clipped to the nearest
reproducible color. Best for proofing and when most colors are in-gamut.

**This is the default rendering intent for most ICC workflows and the one
Apple's ColorSync uses when no intent is specified.**

### 3. Saturation (2)

Prioritizes vivid, saturated colors over colorimetric accuracy. Maps
saturated source colors to the most saturated destination colors. Best for
business graphics (charts, logos) where vibrancy matters more than accuracy.

### 4. Absolute Colorimetric (3)

Like Relative Colorimetric, but does NOT remap the white point. Reproduces
colors exactly as measured, including simulating the source media white on
the destination. Used for hard proofing (simulating one printer on another).

| Intent | Gamut Mapping | White Point | Best For |
|--------|---------------|-------------|----------|
| Perceptual | Compress all | Adapted | Photos with many OOG colors |
| Relative Colorimetric | Clip OOG | Adapted | Proofing, in-gamut images |
| Saturation | Maximize vividness | Adapted | Business graphics |
| Absolute Colorimetric | Clip OOG | Preserved | Hard proofing, spot color |

### Rendering Intent in Practice on iOS

CoreGraphics uses Relative Colorimetric as the default when converting between
color spaces (e.g., drawing a Display P3 `CGImage` into an sRGB context). The
rendering intent is not configurable through ImageIO -- it is controlled at the
CoreGraphics level via `CGColorConversionInfo`:

```swift
let info = CGColorConversionInfo(
    src: sourceColorSpace,
    dst: destColorSpace
)
// Default intent: Relative Colorimetric
// For explicit intent control:
let info = CGColorConversionInfo(
    src: sourceColorSpace, srcIntent: .perceptual,
    dst: destColorSpace, dstIntent: .perceptual,
    options: nil
)
```

---

## ICC v2 vs v4

The ICC specification has evolved through several major versions. Most profiles
in the wild are v2.x (especially v2.4) or v4.x. Here are the key differences:

### Version History

| Version | Spec | Year | Status |
|---------|------|------|--------|
| v2.0 | ICC.1:1994 | 1994 | Obsolete |
| v2.1 | ICC.1:1998-04 | 1998 | Obsolete |
| v2.4 | ICC.1:2001-04 | 2001 | Widely used (legacy) |
| v4.0 | ICC.1:2004-10 | 2004 | Current family |
| v4.2 | ICC.1:2004-10 (amd1) | 2006 | Current family |
| v4.3 | ICC.1:2010-12 | 2010 | Current family |
| v4.4 | ICC.1:2022-05 | 2022 | Current (latest v4) |
| v5 (iccMAX) | ICC.2 / ISO 20677 | 2016+ | Next generation (see below) |

### Key Differences

| Aspect | v2 | v4 |
|--------|----|----|
| **Profile ID** | None | MD5 hash of profile data; unique identification |
| **Chromatic adaptation** | Unspecified viewer adaptation state | `chad` tag required; viewer fully adapted to display white |
| **Perceptual intent** | Vendor-dependent; inconsistent across implementations | Standardized PCS encoding for perceptual transforms |
| **Text tags** | `desc` type (platform-specific encodings: Mac, Win, Unicode) | `mluc` type (Unicode, multi-language, multi-country) |
| **D50 adaptation** | Ambiguous: some profiles pre-adapt, some don't | All colorant tags must be D50-adapted; `chad` provides the adaptation matrix |
| **Curve types** | `curv` only (array of 16-bit values or single gamma) | `curv` plus `para` (parametric curve with formula parameters) |
| **Media white point** | Actual media white in XYZ | Must be D50 (0.9642, 1.0000, 0.8249); `chad` carries actual adaptation |
| **Black point** | No standard calculation | Defined calculation method |
| **LUT types** | `mft1` (8-bit) and `mft2` (16-bit) only | `mAB ` and `mBA ` with separate curve, matrix, and CLUT stages |

### Compatibility Considerations

- **v2 profiles are more widely compatible.** Some older software, web
  browsers, and RIPs do not fully support v4. If a v4 profile is encountered
  by a v2-only renderer, the profile may be ignored entirely, causing the
  image to render in the default color space (often sRGB).

- **Apple platforms fully support v4.** CoreGraphics and ColorSync on iOS and
  macOS handle both v2 and v4 profiles correctly.

- **The sRGB profile shipped with most operating systems is v2.** Apple,
  Microsoft, and the ICC itself distribute v2 sRGB profiles for maximum
  compatibility. The ICC also provides a v4 sRGB profile (`sRGB2014.icc`).

- **v4 profiles cannot be losslessly downgraded to v2.** The `chad` tag and
  parametric curves have no exact v2 equivalent.

- **Adobe applications default to v2 profiles** for embedded profiles in images,
  to maximize compatibility with downstream workflows.

- **Almost all modern platforms now support v4.** As of 2025, all major web
  browsers, operating systems, and image processing libraries support ICC v4.
  The primary remaining v4 compatibility issues are with older hardware RIPs
  and legacy prepress systems.

> **Practical advice for iOS developers:** Apple's named color spaces
> (`CGColorSpace.sRGB`, `CGColorSpace.displayP3`, etc.) handle versioning
> internally. You rarely need to worry about v2 vs v4 unless you are parsing
> raw ICC profile bytes or embedding third-party profiles.

---

## iccMAX (v5)

**iccMAX** (ICC.2 / ISO 20677) is the next-generation ICC specification,
designed to go beyond the D50 colorimetric PCS of v2/v4. Profiles show **v5**
in the header to distinguish them from earlier versions.

### Key Capabilities

| Feature | v4 | iccMAX (v5) |
|---------|-------|-------------|
| PCS | CIEXYZ or CIELAB D50 only | Spectral PCS, custom illuminants, custom observers |
| Color appearance | Not supported | Color appearance model attributes in profile |
| Transforms | Matrix + CLUT | Multi-processing calc elements with programmable operations |
| Illuminant | Fixed D50 | Any standard or custom illuminant |
| Device models | Implicit in LUT data | Direct encoding of device models |

### Current Status

- Published by both ICC (ICC.2) and ISO (ISO 20677).
- Open-source reference implementation: **iccDEV** (formerly DemoIccMax),
  providing libraries and tools for creating and applying iccMAX profiles.
- **Not supported by Apple frameworks** as of iOS 18 / macOS 15. CoreGraphics
  and ColorSync only process v2 and v4 profiles. Passing a v5 profile to
  `CGColorSpace(iccData:)` will fail.
- Primary use cases: spectral color measurement, advanced prepress, textile
  and packaging color management.

> **For iOS developers:** iccMAX is not relevant to current mobile workflows.
> It is included here for completeness, as the specification may influence
> future Apple framework updates.

---

## Profile Size

Typical ICC profile sizes:

| Profile Type | Typical Size |
|-------------|-------------|
| Simple matrix RGB (sRGB, Display P3) | 500 bytes - 4 KB |
| Parametric RGB with LUTs | 4 - 50 KB |
| CMYK output profile | 500 KB - 2 MB |
| n-color profile | 1 - 10 MB |

The minimal viable sRGB profile (`sRGBz`) is only 491 bytes. Apple's built-in
sRGB profile is approximately 3 KB. Printer profiles with detailed CLUT data
for multiple rendering intents can reach several megabytes.

Compact ICC profiles (like those from the
[saucecontrol/Compact-ICC-Profiles](https://github.com/saucecontrol/Compact-ICC-Profiles)
project) minimize embedded profile size while maintaining full compliance.

---

## Cross-References

- [Common ICC Profiles](common-profiles.md) -- sRGB, Display P3, Adobe RGB, ProPhoto RGB, Rec. 709, Rec. 2020
- [Embedding ICC Profiles](embedding.md) -- How profiles are stored in JPEG, PNG, TIFF, HEIF, WebP
- [ImageIO Integration](imageio-integration.md) -- Reading/writing ICC profiles with Apple frameworks
- [Pitfalls](pitfalls.md) -- Common color management mistakes on iOS
