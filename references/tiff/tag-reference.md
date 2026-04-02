# TIFF Tag Reference

> Part of [TIFF Reference](README.md)

Complete reference for all TIFF IFD tags exposed by Apple's ImageIO framework
through `kCGImagePropertyTIFFDictionary`. Each tag includes its numeric ID,
TIFF data type, ImageIO key name, description, and typical values.

These tags live in IFD0 (the primary Image File Directory) of the TIFF
structure. They describe the image file itself -- dimensions, encoding, device
info, creator, and timestamps. Camera-specific capture data (exposure, ISO,
focal length) lives in the Exif SubIFD, not here. See
[`../exif/tag-reference.md`](../exif/tag-reference.md) for those tags.

---

## Image Structure Tags

These tags describe the fundamental encoding of the pixel data. They are
required for TIFF files but are also present in JPEG EXIF data (in IFD0 and
IFD1). ImageIO exposes them for TIFF files but typically does not populate them
in the TIFF dictionary for JPEG -- it uses top-level keys like
`kCGImagePropertyPixelWidth` instead.

### ImageWidth

| Field | Value |
|-------|-------|
| Tag ID | 256 (0x0100) |
| TIFF Type | SHORT or LONG |
| Count | 1 |
| ImageIO Key | -- (not in TIFF dictionary; use `kCGImagePropertyPixelWidth`) |
| Description | Number of columns (pixels per row) in the image |
| Typical Values | Any positive integer |

### ImageLength

| Field | Value |
|-------|-------|
| Tag ID | 257 (0x0101) |
| TIFF Type | SHORT or LONG |
| Count | 1 |
| ImageIO Key | -- (not in TIFF dictionary; use `kCGImagePropertyPixelHeight`) |
| Description | Number of rows in the image |
| Typical Values | Any positive integer |

### BitsPerSample

| Field | Value |
|-------|-------|
| Tag ID | 258 (0x0102) |
| TIFF Type | SHORT |
| Count | SamplesPerPixel |
| ImageIO Key | -- (not in TIFF dictionary; use `kCGImagePropertyDepth`) |
| Description | Number of bits per component. One value per channel |
| Typical Values | `[8, 8, 8]` for 8-bit RGB; `[16, 16, 16]` for 16-bit; `[8]` for grayscale |

### Compression

| Field | Value |
|-------|-------|
| Tag ID | 259 (0x0103) |
| TIFF Type | SHORT |
| Count | 1 |
| ImageIO Key | `kCGImagePropertyTIFFCompression` |
| Description | Compression scheme used on the image data |

**Compression Values:**

| Value | Scheme | Notes |
|-------|--------|-------|
| 1 | No compression | Uncompressed (baseline TIFF) |
| 2 | CCITT modified Huffman RLE | Bi-level images (TIFF baseline 1-D encoding) |
| 3 | CCITT Group 3 fax | T.4 encoding |
| 4 | CCITT Group 4 fax | T.6 encoding |
| 5 | LZW | Lossless; patent-free since 2004 |
| 6 | JPEG (old-style) | Deprecated; do not use for new files |
| 7 | JPEG (new TIFF-JPEG) | Technote 2; modern JPEG-in-TIFF |
| 8 | Deflate (Adobe) | zlib/PNG compression |
| 32773 | PackBits | Apple-created RLE; baseline TIFF |
| 34712 | JPEG 2000 | Extension |
| 34925 | LZMA | Extension |

ImageIO reads all of the above schemes. When writing TIFF, ImageIO typically
uses LZW (5) or PackBits (32773) for lossless compression. For JPEG-in-TIFF,
compression value 7 is used.

### PhotometricInterpretation

| Field | Value |
|-------|-------|
| Tag ID | 262 (0x0106) |
| TIFF Type | SHORT |
| Count | 1 |
| ImageIO Key | `kCGImagePropertyTIFFPhotometricInterpretation` |
| Description | The color space of the image data |

**PhotometricInterpretation Values:**

| Value | Color Space | Description |
|-------|------------|-------------|
| 0 | WhiteIsZero | For bi-level and grayscale: 0 is white, max is black |
| 1 | BlackIsZero | For bi-level and grayscale: 0 is black, max is white |
| 2 | RGB | Full-color image with R, G, B channels |
| 3 | Palette Color | Indexed color using a color map (ColorMap tag required) |
| 4 | Transparency Mask | Defines an irregularly shaped region of another image |
| 5 | Separated (CMYK) | Cyan, Magenta, Yellow, Key (black) |
| 6 | YCbCr | Luminance-chrominance (JPEG images in EXIF) |
| 8 | CIE L\*a\*b\* | CIE 1976 color space |
| 9 | ICC L\*a\*b\* | ICC profile-based L\*a\*b\* |

For photographs, the most common values are 2 (RGB) for TIFF files and 6
(YCbCr) for JPEG EXIF data. DNG files use value 32803 (CFA -- Color Filter
Array) or 34892 (LinearRaw) as DNG-specific extensions.

---

## Descriptive Tags

These tags store human-readable text describing the image, the device that
created it, and the software that processed it.

### Make

| Field | Value |
|-------|-------|
| Tag ID | 271 (0x010F) |
| TIFF Type | ASCII |
| Count | Variable |
| ImageIO Key | `kCGImagePropertyTIFFMake` |
| Description | Manufacturer of the scanner, camera, or device that captured the image |
| iPhone Value | `"Apple"` |
| Other Values | `"Canon"`, `"NIKON CORPORATION"`, `"SONY"`, `"samsung"`, `"Google"` |

Note: Different manufacturers use different capitalization and formatting
conventions. Canon uses `"Canon"`, Nikon uses `"NIKON CORPORATION"` (all caps
with "CORPORATION"), Sony uses `"SONY"`, and Samsung uses lowercase `"samsung"`.
Apple always writes `"Apple"`. These inconsistencies make string matching
unreliable -- use case-insensitive comparison when filtering by manufacturer.

### Model

| Field | Value |
|-------|-------|
| Tag ID | 272 (0x0110) |
| TIFF Type | ASCII |
| Count | Variable |
| ImageIO Key | `kCGImagePropertyTIFFModel` |
| Description | Model name or number of the device |
| iPhone Values | `"iPhone 16 Pro"`, `"iPhone 15 Pro"`, `"iPhone 14"`, `"iPad Pro (12.9-inch) (6th generation)"` |
| Other Values | `"Canon EOS R5"`, `"NIKON Z 9"`, `"ILCE-7RM5"` (Sony A7R V), `"Pixel 8 Pro"` |

The Model string is the marketing name of the device. Sony prefixes with
`"ILCE-"` for mirrorless bodies, Nikon uses spaces and full model names,
Canon includes the entire product line name.

### Software

| Field | Value |
|-------|-------|
| Tag ID | 305 (0x0131) |
| TIFF Type | ASCII |
| Count | Variable |
| ImageIO Key | `kCGImagePropertyTIFFSoftware` |
| Description | Name and version of the software or firmware that created the image |
| iPhone Values | `"18.3.2"`, `"17.4.1"` (iOS writes the OS version number, not an app name) |
| Other Values | `"Adobe Photoshop 25.6"`, `"Lightroom 7.1.2"`, `"GIMP 2.10.36"`, `"Ver.1.40"` (Canon firmware) |

Important: iOS writes the operating system version number (e.g., `"18.3.2"`)
into this field, **not** the name of the capturing app. This means you cannot
determine which app took a photo from the Software tag on iOS. Third-party
apps that write metadata can override this value.

### HostComputer

| Field | Value |
|-------|-------|
| Tag ID | 316 (0x013C) |
| TIFF Type | ASCII |
| Count | Variable |
| ImageIO Key | `kCGImagePropertyTIFFHostComputer` |
| Description | The computer or operating system used to create the image |
| iPhone Values | `"iPhone 16 Pro"`, `"iPhone 15 Pro"` (iOS writes the device model here, duplicating Model) |
| Other Values | `"macOS 14.3"`, typically omitted by non-Apple software |

See [`pitfalls.md`](pitfalls.md#hostcomputer-duplication-on-ios) for the
iOS-specific behavior where this duplicates the Model tag value.

### ImageDescription

| Field | Value |
|-------|-------|
| Tag ID | 270 (0x010E) |
| TIFF Type | ASCII |
| Count | Variable |
| ImageIO Key | `kCGImagePropertyTIFFImageDescription` |
| Description | A string describing the image content |
| Notes | Often empty in camera output. Overlaps with IPTC Caption-Abstract and XMP `dc:description`. See [`pitfalls.md`](pitfalls.md#imagedescription-vs-iptc-caption-vs-xmp-dcdescription) |

This is one of the "triple-stored" fields -- the same concept (image
description/caption) can be stored in TIFF, IPTC, and XMP simultaneously.
The MWG recommends XMP `dc:description` as the preferred source.

### DocumentName

| Field | Value |
|-------|-------|
| Tag ID | 269 (0x010D) |
| TIFF Type | ASCII |
| Count | Variable |
| ImageIO Key | `kCGImagePropertyTIFFDocumentName` |
| Description | The name of the document from which this image was scanned |
| Notes | Primarily used in document imaging and scanning workflows. Rarely present in photographs. May contain the original filename in some workflows |

---

## Orientation and Resolution

### Orientation

| Field | Value |
|-------|-------|
| Tag ID | 274 (0x0112) |
| TIFF Type | SHORT |
| Count | 1 |
| ImageIO Key | `kCGImagePropertyTIFFOrientation` |
| Description | The intended display orientation of the image |

**Orientation Values:**

| Value | Row 0 | Col 0 | Transform to Display | Common Source |
|-------|-------|-------|---------------------|---------------|
| 1 | Top | Left | Normal (no transform) | Landscape default |
| 2 | Top | Right | Horizontal flip | Rare |
| 3 | Bottom | Right | 180 rotation | Camera upside-down |
| 4 | Bottom | Left | Vertical flip | Rare |
| 5 | Left | Top | Transpose (90 CW + H flip) | Rare |
| 6 | Right | Top | 90 clockwise | iPhone portrait (home button bottom) |
| 7 | Right | Bottom | Transverse (90 CW + V flip) | Rare |
| 8 | Left | Bottom | 90 counter-clockwise | Portrait (home button top) |

This tag is **duplicated** as `kCGImagePropertyOrientation` at the top level
of the properties dictionary. Both should have the same value, but see
[`pitfalls.md`](pitfalls.md#orientation-duplication) for the issues this
causes when writing.

For the full orientation reference including visual diagrams and
CGImagePropertyOrientation vs UIImage.Orientation mapping, see
[`../interoperability/orientation-mapping.md`](../interoperability/orientation-mapping.md) and
[`imageio-mapping.md`](imageio-mapping.md#orientation-duplication).

### XResolution

| Field | Value |
|-------|-------|
| Tag ID | 282 (0x011A) |
| TIFF Type | RATIONAL |
| Count | 1 |
| ImageIO Key | `kCGImagePropertyTIFFXResolution` |
| Description | Number of pixels per ResolutionUnit in the image width direction |
| Default | 72/1 (72 DPI) |
| iPhone Value | `72` |
| Print Value | `300` (300 DPI for standard print quality) |

### YResolution

| Field | Value |
|-------|-------|
| Tag ID | 283 (0x011B) |
| TIFF Type | RATIONAL |
| Count | 1 |
| ImageIO Key | `kCGImagePropertyTIFFYResolution` |
| Description | Number of pixels per ResolutionUnit in the image height direction |
| Default | 72/1 (72 DPI) |
| iPhone Value | `72` |
| Print Value | `300` (300 DPI for standard print quality) |

The 72 DPI default is a legacy convention from early Macintosh displays
(72 pixels per inch). It does not represent the actual sensor density of any
modern camera. For digital photos, the resolution tags are essentially
meaningless -- they only matter for print workflows where physical output
size must be calculated from pixel count.

### ResolutionUnit

| Field | Value |
|-------|-------|
| Tag ID | 296 (0x0128) |
| TIFF Type | SHORT |
| Count | 1 |
| ImageIO Key | `kCGImagePropertyTIFFResolutionUnit` |
| Description | The unit of measurement for XResolution and YResolution |
| Default | 2 (inch) |

**ResolutionUnit Values:**

| Value | Unit | Notes |
|-------|------|-------|
| 1 | No absolute unit | Used when aspect ratio matters but physical size does not |
| 2 | Inch | Default. Used by most cameras and software |
| 3 | Centimeter | Used in some European and scientific workflows |

See [`pitfalls.md`](pitfalls.md#resolution-units) for the consequences of
assuming ResolutionUnit=2 without checking.

---

## Authorship Tags

### Artist

| Field | Value |
|-------|-------|
| Tag ID | 315 (0x013B) |
| TIFF Type | ASCII |
| Count | Variable |
| ImageIO Key | `kCGImagePropertyTIFFArtist` |
| Description | Person who created the image |
| Notes | Multiple artists can be separated by semicolons per MWG guidelines. Overlaps with IPTC By-line and XMP `dc:creator`. See [`pitfalls.md`](pitfalls.md#artist-vs-iptc-byline-vs-xmp-dccreator) |

This is one of the "triple-stored" fields. The MWG recommends:
- **Reading:** Prefer XMP `dc:creator`, fallback to IPTC By-line, then EXIF
  Artist
- **Writing:** Update all three to keep them in sync
- **Multiple creators:** XMP `dc:creator` is an ordered array; IPTC By-line
  supports multiple values; EXIF Artist is a single string. Join with
  `"; "` (semicolon-space) for the EXIF field.

### Copyright

| Field | Value |
|-------|-------|
| Tag ID | 33432 (0x8298) |
| TIFF Type | ASCII |
| Count | Variable |
| ImageIO Key | `kCGImagePropertyTIFFCopyright` |
| Description | Copyright notice for the image |

**Copyright Format (EXIF spec):**

The EXIF specification defines a special format for this tag:
- **Photographer only:** `"Photographer Name\0"`
- **Editor only:** `" \0Editor Name\0"` (space + null + editor + null)
- **Both:** `"Photographer Name\0Editor Name\0"` (separated by a null byte)

In practice, most software writes a single copyright string without the
photographer/editor distinction. ImageIO returns a single string. The
null-byte separation format is a historical artifact that is largely ignored
in modern workflows.

Overlaps with IPTC CopyrightNotice and XMP `dc:rights`. See
[`pitfalls.md`](pitfalls.md#copyright-vs-iptc-copyrightnotice-vs-xmp-dcrights).

---

## Timestamp Tags

### DateTime

| Field | Value |
|-------|-------|
| Tag ID | 306 (0x0132) |
| TIFF Type | ASCII |
| Count | 20 |
| ImageIO Key | `kCGImagePropertyTIFFDateTime` |
| Description | Date and time the file was last modified |

**Format:** `"YYYY:MM:DD HH:MM:SS"` -- 19 printable characters plus a null
terminator (20 bytes total).

- Uses 24-hour time
- Colons separate date components (not hyphens)
- A single space separates date and time
- **No timezone information** -- the time is ambiguous without EXIF OffsetTime tags

**Example:** `"2025:03:15 14:30:22"`

**Relationship to EXIF DateTime tags:**

| Tag | Tag ID | Location | ImageIO Dictionary | Meaning |
|-----|--------|----------|-------------------|---------|
| DateTime | 0x0132 | IFD0 | TIFF | File last modified |
| DateTimeOriginal | 0x9003 | ExifIFD | EXIF | Original capture time |
| DateTimeDigitized | 0x9004 | ExifIFD | EXIF | When digitized |

All three use the same `"YYYY:MM:DD HH:MM:SS"` format. For timezone
information, use the EXIF 2.31+ OffsetTime tags (`OffsetTime`,
`OffsetTimeOriginal`, `OffsetTimeDigitized`). iPhone always writes these;
many third-party cameras do not.

For camera photos, DateTime and DateTimeOriginal are often identical (the
file modification time equals the capture time). They diverge when the file
is subsequently edited -- DateTime gets updated but DateTimeOriginal remains
the original capture moment.

---

## Color Tags

These tags describe the colorimetric properties of the image using CIE 1931
chromaticity coordinates. They are relevant when images need accurate color
reproduction and the ICC profile alone is insufficient or absent.

### WhitePoint

| Field | Value |
|-------|-------|
| Tag ID | 318 (0x013E) |
| TIFF Type | RATIONAL |
| Count | 2 |
| ImageIO Key | `kCGImagePropertyTIFFWhitePoint` |
| Description | CIE 1931 xy chromaticity of the image's white point |
| D65 Value | `[3127/10000, 3290/10000]` (x=0.3127, y=0.3290) |
| D50 Value | `[3457/10000, 3585/10000]` (x=0.3457, y=0.3585) |

D65 is the standard illuminant for sRGB and Display P3. D50 is used for
print workflows (ICC profile connection space). iPhone photos with Display P3
color space write D65 white point values.

### PrimaryChromaticities

| Field | Value |
|-------|-------|
| Tag ID | 319 (0x013F) |
| TIFF Type | RATIONAL |
| Count | 6 |
| ImageIO Key | `kCGImagePropertyTIFFPrimaryChromaticities` |
| Description | CIE 1931 xy chromaticities of the three primary colors (R, G, B) |

**Value order:** `[Rx, Ry, Gx, Gy, Bx, By]`

**Common values:**

| Color Space | Red (x, y) | Green (x, y) | Blue (x, y) |
|-------------|-----------|-------------|------------|
| sRGB / BT.709 | 0.640, 0.330 | 0.300, 0.600 | 0.150, 0.060 |
| Display P3 | 0.680, 0.320 | 0.265, 0.690 | 0.150, 0.060 |
| Adobe RGB | 0.640, 0.330 | 0.210, 0.710 | 0.150, 0.060 |

Note how Display P3 has a wider red and green gamut than sRGB (larger red x,
smaller green x, larger green y), while sharing the same blue primary. iPhone
photos captured in HEIC or ProRAW write the Display P3 chromaticities.

### TransferFunction

| Field | Value |
|-------|-------|
| Tag ID | 301 (0x012D) |
| TIFF Type | SHORT |
| Count | 3 x 256 = 768 (or 256 if one channel) |
| ImageIO Key | `kCGImagePropertyTIFFTransferFunction` |
| Description | Transfer function (gamma curve) for the image, mapping stored values to linear light |
| Notes | Each entry is an unsigned 16-bit value. For a standard 2.2 gamma curve, entry `i` equals `round(((i/255)^2.2) * 65535)` |

If only one set of 256 values is provided, it applies to all channels equally.
If three sets of 256 values are provided, they apply to R, G, B respectively.

In practice, most modern workflows rely on ICC profiles for transfer function
information rather than this tag. It is rarely written by cameras and is most
common in scanned images and prepress workflows.

---

## Tiling Tags

These tags describe tile-based image organization (as opposed to strip-based).
Tiling allows random access to image regions without decoding the entire image,
which is critical for large images (satellite imagery, medical imaging, etc.).

### TileWidth

| Field | Value |
|-------|-------|
| Tag ID | 322 (0x0142) |
| TIFF Type | SHORT or LONG |
| Count | 1 |
| ImageIO Key | `kCGImagePropertyTIFFTileWidth` |
| Description | Width of a tile in pixels. Must be a multiple of 16 |
| Availability | macOS 10.11+ (not documented for iOS) |
| Typical Values | 256, 512 |

### TileLength

| Field | Value |
|-------|-------|
| Tag ID | 323 (0x0143) |
| TIFF Type | SHORT or LONG |
| Count | 1 |
| ImageIO Key | `kCGImagePropertyTIFFTileLength` |
| Description | Height of a tile in pixels. Must be a multiple of 16 |
| Availability | macOS 10.11+ (not documented for iOS) |
| Typical Values | 256, 512 |

Tile dimensions must be multiples of 16 for compatibility with JPEG
compression in TIFF. Common configurations are 256x256 and 512x512 pixels.
Pyramidal TIFF files (used in GIS and pathology) use tiling extensively.

---

## Complete ImageIO TIFF Key Summary

All 20 `kCGImagePropertyTIFF*` constants in one table, sorted by tag ID:

| ImageIO Key | TIFF Tag | Tag ID | CFType | Category |
|-------------|----------|--------|--------|----------|
| `kCGImagePropertyTIFFCompression` | Compression | 259 (0x0103) | CFNumber | Structure |
| `kCGImagePropertyTIFFPhotometricInterpretation` | PhotometricInterpretation | 262 (0x0106) | CFNumber | Structure |
| `kCGImagePropertyTIFFDocumentName` | DocumentName | 269 (0x010D) | CFString | Descriptive |
| `kCGImagePropertyTIFFImageDescription` | ImageDescription | 270 (0x010E) | CFString | Descriptive |
| `kCGImagePropertyTIFFMake` | Make | 271 (0x010F) | CFString | Device |
| `kCGImagePropertyTIFFModel` | Model | 272 (0x0110) | CFString | Device |
| `kCGImagePropertyTIFFOrientation` | Orientation | 274 (0x0112) | CFNumber | Orientation |
| `kCGImagePropertyTIFFXResolution` | XResolution | 282 (0x011A) | CFNumber | Resolution |
| `kCGImagePropertyTIFFYResolution` | YResolution | 283 (0x011B) | CFNumber | Resolution |
| `kCGImagePropertyTIFFResolutionUnit` | ResolutionUnit | 296 (0x0128) | CFNumber | Resolution |
| `kCGImagePropertyTIFFTransferFunction` | TransferFunction | 301 (0x012D) | CFArray | Color |
| `kCGImagePropertyTIFFSoftware` | Software | 305 (0x0131) | CFString | Device |
| `kCGImagePropertyTIFFDateTime` | DateTime | 306 (0x0132) | CFString | Timestamp |
| `kCGImagePropertyTIFFArtist` | Artist | 315 (0x013B) | CFString | Authorship |
| `kCGImagePropertyTIFFHostComputer` | HostComputer | 316 (0x013C) | CFString | Device |
| `kCGImagePropertyTIFFWhitePoint` | WhitePoint | 318 (0x013E) | CFArray | Color |
| `kCGImagePropertyTIFFPrimaryChromaticities` | PrimaryChromaticities | 319 (0x013F) | CFArray | Color |
| `kCGImagePropertyTIFFTileWidth` | TileWidth | 322 (0x0142) | CFNumber | Tiling |
| `kCGImagePropertyTIFFTileLength` | TileLength | 323 (0x0143) | CFNumber | Tiling |
| `kCGImagePropertyTIFFCopyright` | Copyright | 33432 (0x8298) | CFString | Authorship |

---

## Tags NOT in the TIFF Dictionary

These common TIFF tags are important for understanding TIFF files but are
**not** exposed through `kCGImagePropertyTIFFDictionary`. ImageIO provides
them through other mechanisms or keeps them internal:

### Exposed Elsewhere

| TIFF Tag | Tag ID | Where ImageIO Exposes It |
|----------|--------|--------------------------|
| ImageWidth | 256 (0x0100) | `kCGImagePropertyPixelWidth` (top-level) |
| ImageLength | 257 (0x0101) | `kCGImagePropertyPixelHeight` (top-level) |
| BitsPerSample | 258 (0x0102) | `kCGImagePropertyDepth` (top-level) |
| SamplesPerPixel | 277 (0x0115) | Implicit in `kCGImagePropertyColorModel` |

### Internal to ImageIO (Not Exposed)

| TIFF Tag | Tag ID | Purpose |
|----------|--------|---------|
| StripOffsets | 273 (0x0111) | Byte offsets to image data strips |
| RowsPerStrip | 278 (0x0116) | Number of rows per strip |
| StripByteCounts | 279 (0x0117) | Byte counts for each strip |
| PlanarConfiguration | 284 (0x011C) | 1=chunky (interleaved), 2=planar |
| TileOffsets | 324 (0x0144) | Byte offsets to tile data |
| TileByteCounts | 325 (0x0145) | Byte counts for each tile |
| ColorMap | 320 (0x0140) | Palette for indexed-color images |

### Sub-IFD Pointers (Followed Automatically)

| TIFF Tag | Tag ID | What ImageIO Does |
|----------|--------|-------------------|
| ExifIFDPointer | 34665 (0x8769) | Follows pointer; EXIF tags in `kCGImagePropertyExifDictionary` |
| GPSInfoIFDPointer | 34853 (0x8825) | Follows pointer; GPS tags in `kCGImagePropertyGPSDictionary` |
| InteropIFDPointer | 40965 (0xA005) | Follows pointer internally; not exposed as a dictionary |

### TIFF Tags Not in Baseline

Some additional tags appear in TIFF files but are not part of the TIFF 6.0
baseline specification:

| Tag | Tag ID | Source | Purpose |
|-----|--------|--------|---------|
| XMP | 700 (0x02BC) | Adobe XMP spec | Embedded XMP packet (XML) |
| IPTC-NAA | 33723 (0x83BB) | IPTC IIM | IPTC metadata record |
| ICC Profile | 34675 (0x8773) | ICC spec | Embedded ICC color profile |
| SubIFDs | 330 (0x014A) | TIFF/EP | Offset to child sub-IFDs |
| DNGVersion | 50706 (0xC612) | Adobe DNG | DNG specification version |
| GeoKeyDirectory | 34735 (0x87AF) | GeoTIFF | Geospatial metadata |

ImageIO reads XMP (tag 700) via `CGImageSourceCopyMetadataAtIndex`, the ICC
profile via `kCGImagePropertyProfileName` and `CGColorSpace`, and IPTC via
`kCGImagePropertyIPTCDictionary`. These are all transparent -- you never
interact with the raw tag numbers.
