# ICC Color Profiles

ICC color profile reference for iOS/macOS image metadata workflows. Covers the
ICC specification, common profiles, per-format embedding, Apple ImageIO
integration, and practical pitfalls.

---

## Overview

An **ICC profile** is a standardized binary file (ICC.1:2022, v4.4) that
describes how a device or color space reproduces color. The profile maps between
device-native color values and a device-independent **Profile Connection Space
(PCS)**, enabling accurate color conversion between any two profiled devices.

On iOS, ICC profiles are the mechanism behind `kCGImagePropertyProfileName`,
`CGColorSpace`, and the automatic color management that ColorSync performs when
you draw a Display P3 image into an sRGB context.

### ImageIO Surface

ICC profile data is not accessed through a sub-dictionary like EXIF or GPS.
Instead, it surfaces through top-level image properties and CoreGraphics APIs:

| Access Method | iOS | Description |
|---------------|-----|-------------|
| `kCGImagePropertyProfileName` | 4.0+ | ICC profile name string (e.g. `"Display P3"`) |
| `kCGImagePropertyColorModel` | 4.0+ | Color model: `"RGB"`, `"CMYK"`, `"Gray"`, `"Lab"` |
| `kCGImagePropertyNamedColorSpace` | 11.0+ | Numeric enum for well-known Apple color spaces |
| `CGImage.colorSpace` | 2.0+ | `CGColorSpace` object with full profile data |
| `CGColorSpace.copyICCData()` | 10.0+ | Raw ICC profile binary bytes |
| `CGColorSpace(iccData:)` | 10.0+ | Create color space from ICC profile bytes |
| `kCGImageDestinationOptimizeColorForSharing` | 9.3+ | Convert to sRGB on write |

### Format Support

| Format | ICC Embedding | Mechanism |
|--------|---------------|-----------|
| JPEG | Yes | APP2 marker (`ICC_PROFILE`), chunked for large profiles |
| PNG | Yes | `iCCP` chunk (zlib compressed); `cICP` chunk for CICP (PNG 3rd edition) |
| TIFF | Yes | Tag 34675 |
| HEIF/HEIC | Yes | `colr` box (nclx CICP or embedded ICC) |
| DNG | Yes | Tag 34675 + DNG-specific tags 50833/50834 |
| WebP | Yes | `ICCP` chunk |
| AVIF | Yes | `colr` box (same as HEIF) |
| JPEG XL | Yes | Codestream header (compressed ICC or CICP enum) |
| GIF | No | No mechanism |

---

## File Index

| File | Description |
|------|-------------|
| [profile-basics.md](profile-basics.md) | ICC specification fundamentals: what a profile encodes, binary structure (128-byte header, tag table, tag data), profile classes (Input, Display, Output, DeviceLink, ColorSpace, Abstract, NamedColor), color spaces, key tags (TRC, XYZ, A2B/B2A, desc, wtpt), rendering intents (Perceptual, Relative Colorimetric, Saturation, Absolute Colorimetric), ICC v2 vs v4 differences, iccMAX (v5) overview |
| [common-profiles.md](common-profiles.md) | Reference for widely-used profiles: sRGB IEC61966-2.1, Display P3, Adobe RGB (1998), ProPhoto RGB (ROMM RGB), Rec. 709, Rec. 2020, DCI-P3, generic system profiles. Primaries, white points, transfer functions, gamut comparisons, CGColorSpace constants, and when to use each |
| [embedding.md](embedding.md) | Per-format ICC embedding mechanisms: JPEG APP2 chunking, PNG iCCP compression and cICP (CICP) chunk, TIFF tag 34675, HEIF colr box (nclx/rICC), DNG ICC tags, WebP ICCP chunk, JPEG XL codestream, PDF ICCBased, GIF (none). Profile size considerations, stripping trade-offs, CICP as compact alternative |
| [imageio-integration.md](imageio-integration.md) | Reading ICC profiles via ImageIO properties and CGColorSpace. Writing profiles via CGImageDestination. kCGImageDestinationOptimizeColorForSharing. All CGColorSpace named constants (sRGB, Display P3, Rec. 709/2020, HDR variants, grayscale, CMYK, Lab). EXIF ColorSpace interaction. Profile preservation through read/write cycles. DNG-specific ICC keys. Color management pipeline. Swift code examples |
| [pitfalls.md](pitfalls.md) | 10 common pitfalls: assuming sRGB for P3 images, silent sRGB conversion via OptimizeColorForSharing, ICC v2/v4 compatibility, missing profile defaults, CMYK limitations on iOS, UIImage profile stripping, HDR gain map loss, large JPEG profile chunking, generic/device profiles, EXIF ColorSpace tag mismatch |

---

## Key Concepts

- **Profile Connection Space (PCS):** CIEXYZ or CIELAB D50 -- the
  device-independent space that bridges any two profiles.
- **Display P3:** Apple's default capture and display gamut on iPhone 7+.
  ~25% larger than sRGB in reds, oranges, and greens.
- **Wide Color:** Apple's term for Display P3 content. Check
  `CGColorSpace.isWideGamutRGB` (iOS 12+).
- **Rendering Intent:** How out-of-gamut colors are handled during
  conversion. Apple defaults to Relative Colorimetric.
- **CICP / nclx:** Compact color signaling in HEIF/AVIF/PNG (no full profile
  needed for well-known spaces). Uses ITU-T H.273 code points for primaries,
  transfer characteristics, and matrix coefficients.
- **iccMAX (v5):** Next-generation ICC specification (ICC.2 / ISO 20677)
  supporting spectral PCS, color appearance, and programmable transforms.
  Not yet supported by Apple frameworks.

---

## Cross-References

| Related Section | Relevance |
|-----------------|-----------|
| [`imageio/property-keys.md`](../imageio/property-keys.md) | `kCGImagePropertyProfileName`, `kCGImagePropertyColorModel`, `kCGImagePropertyNamedColorSpace` |
| [`imageio/supported-formats.md`](../imageio/supported-formats.md) | ICC support column in format metadata matrix |
| [`imageio/cgimagedestination.md`](../imageio/cgimagedestination.md) | `kCGImageDestinationOptimizeColorForSharing` option |
| [`imageio/pitfalls.md`](../imageio/pitfalls.md) | UIImage metadata loss (including ICC profile) |
| [`imageio/auxiliary-data.md`](../imageio/auxiliary-data.md) | HDR gain maps and their interaction with color spaces |
| [`exif/tag-reference.md`](../exif/tag-reference.md) | EXIF `ColorSpace` tag (40961) -- sRGB vs Uncalibrated |
