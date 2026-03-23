# JPEG / JFIF Format Reference

JPEG (Joint Photographic Experts Group) is the most widely used lossy image
format. The JPEG File Interchange Format (JFIF, ITU-T T.871 / ISO/IEC 10918-5)
defines the container that wraps JPEG-compressed image data and metadata.

JPEG supports every metadata standard that ImageIO recognizes: EXIF, XMP,
IPTC IIM, ICC profiles, and GPS. It is one of only three formats (along with
TIFF and PSD) that supports all five. JPEG is also one of only four formats
that support lossless metadata editing via `CGImageDestinationCopyImageSource`.

---

## File Signature

```
FF D8 FF
```

All JPEG files begin with the SOI (Start of Image) marker `FF D8`, immediately
followed by the first marker (typically `FF E0` for JFIF or `FF E1` for Exif).

---

## Marker-Based Structure

A JPEG file is a sequence of **marker segments**. Every marker begins with
`0xFF` followed by a marker code byte. Markers without payload are standalone
(two bytes); markers with payload include a two-byte big-endian length field
(counting itself but not the `0xFF` + marker code).

```
FF <marker> <length_hi> <length_lo> <payload...>
```

**Maximum segment size:** 65,535 bytes (the 2-byte length field). This is the
fundamental constraint driving Extended XMP, multi-segment ICC profiles, and
the practical EXIF size limit.

### Core Marker Types

| Marker  | Hex        | Name                        | Purpose                                        |
|---------|------------|-----------------------------|-------------------------------------------------|
| SOI     | `FF D8`    | Start of Image              | File begins here; no payload                    |
| SOF0    | `FF C0`    | Start of Frame (Baseline)   | Image dimensions, components, 8-bit depth       |
| SOF2    | `FF C2`    | Start of Frame (Progressive)| Progressive encoding parameters                 |
| SOF3    | `FF C3`    | Start of Frame (Lossless)   | Lossless JPEG (rarely used)                     |
| DHT     | `FF C4`    | Define Huffman Table        | Huffman coding tables                           |
| DQT     | `FF DB`    | Define Quantization Table   | Quantization matrices (determines quality)      |
| DRI     | `FF DD`    | Define Restart Interval     | MCU count between restart markers               |
| SOS     | `FF DA`    | Start of Scan               | Begins entropy-coded image data                 |
| RST0-7  | `FF D0-D7` | Restart Markers             | Periodic resynchronization in scan data         |
| COM     | `FF FE`    | Comment                     | Arbitrary text comment (max ~64 KB)             |
| EOI     | `FF D9`    | End of Image                | File ends here; no payload                      |
| APP0    | `FF E0`    | Application Segment 0       | JFIF header                                     |
| APP1    | `FF E1`    | Application Segment 1       | EXIF or XMP (two separate APP1 segments)        |
| APP2    | `FF E2`    | Application Segment 2       | ICC profile or FlashPix                         |
| APP3-12 | `FF E3-EC` | Application Segments 3-12   | Various vendor uses                             |
| APP13   | `FF ED`    | Application Segment 13      | IPTC / Photoshop Image Resources (8BIM)         |
| APP14   | `FF EE`    | Application Segment 14      | Adobe color transform (YCCK, inverted CMYK)     |
| APP15   | `FF EF`    | Application Segment 15      | Reserved                                        |

### Typical JPEG File Layout

```
FF D8                          SOI (Start of Image) -- always first
FF E0 [len] [JFIF header]     APP0: JFIF (version, density, thumbnail)
FF E1 [len] [Exif data]       APP1: EXIF (TIFF structure with IFDs)
FF E1 [len] [XMP data]        APP1: XMP (RDF/XML, separate segment)
FF E1 [len] [ExtXMP data]     APP1: Extended XMP (if XMP > 64 KB)
FF E2 [len] [ICC profile]     APP2: ICC color profile (may span multiple)
FF ED [len] [IPTC/IRB data]   APP13: IPTC IIM via Photoshop 8BIM blocks
FF EE [len] [Adobe data]      APP14: Adobe color transform (optional)
FF DB [len] [quant tables]    DQT: quantization tables
FF C0 [len] [frame header]    SOF0: baseline DCT (or FF C2 for progressive)
FF C4 [len] [huffman tables]  DHT: Huffman tables
FF DA [len] [scan header]     SOS: start of scan
  ... entropy-coded data ...  (restart markers FF D0-D7 may appear)
FF D9                          EOI (End of Image) -- always last
```

---

## APP Marker Details

### APP0 -- JFIF Header (`FF E0`)

The JFIF standard (version 1.02, 1992) requires APP0 to immediately follow SOI.
It identifies the file as JFIF and provides display parameters.

| Field           | Bytes | Description                                    |
|-----------------|-------|------------------------------------------------|
| Identifier      | 5     | `"JFIF\0"` (null-terminated)                   |
| Version         | 2     | Major.Minor (e.g. `01 02` = version 1.02)      |
| Density Unit    | 1     | 0 = no unit (aspect ratio), 1 = DPI, 2 = DPCM |
| X Density       | 2     | Horizontal pixel density (big-endian)           |
| Y Density       | 2     | Vertical pixel density (big-endian)             |
| Thumbnail W     | 1     | Thumbnail width (0 = no thumbnail)              |
| Thumbnail H     | 1     | Thumbnail height (0 = no thumbnail)             |
| Thumbnail Data  | 3*W*H | Uncompressed RGB pixel data                     |

**JFXX Extension:** A second APP0 segment with identifier `"JFXX\0"` may
follow, providing an alternate thumbnail format (JPEG-compressed, palette-based,
or 24-bit RGB).

### APP1 -- EXIF (`FF E1`)

The first APP1 segment typically carries EXIF data. It begins with the
identifier `"Exif\0\0"` (six bytes), followed by a complete TIFF structure
containing IFD0, ExifIFD, GPS IFD, Interop IFD, and optionally IFD1
(thumbnail).

```
FF E1                   APP1 marker
XX XX                   Segment length (big-endian, includes itself)
45 78 69 66 00 00       "Exif\0\0" identifier (6 bytes)
-- TIFF data begins here (offsets are relative to this point) --
  49 49 / 4D 4D         Byte order (II = little-endian, MM = big-endian)
  2A 00 / 00 2A         TIFF magic number (42, byte order dependent)
  XX XX XX XX            Offset to IFD0
  ...                    IFD0 entries
    -> ExifIFD pointer   Sub-IFD with camera settings, timestamps, lens
    -> GPS IFD pointer   Sub-IFD with location data
    -> Interop IFD       Interoperability sub-IFD
  ...                    IFD1 (thumbnail JPEG data, optional)
```

**64 KB limit:** Each APP marker segment can hold at most 65,533 bytes of data
(65,535 minus the 2-byte length field). This constrains the total size of EXIF
data, including the MakerNote and embedded thumbnail. There is **no**
multi-segment extension for EXIF -- if the data exceeds 64 KB, it must be
truncated or the MakerNote/thumbnail may be dropped.

### APP1 -- XMP (`FF E1`)

A second APP1 segment carries XMP data. It is distinguished from EXIF by its
identifier string.

| Field      | Bytes | Description                                        |
|------------|-------|----------------------------------------------------|
| Identifier | 29    | `"http://ns.adobe.com/xap/1.0/\0"` (null-terminated) |
| XMP Packet | N     | UTF-8 encoded RDF/XML                               |

**Maximum payload:** ~65,502 bytes (65,535 minus 2-byte length field minus
29-byte identifier minus 2 bytes overhead). XMP packets exceeding this require Extended XMP.

### APP1 -- Extended XMP

When the XMP packet exceeds the ~65,502 byte limit, the XMP specification (Part 3:
Storage in Files) defines a splitting mechanism:

1. **StandardXMP** -- The main APP1 segment contains a trimmed XMP packet that
   fits within 64 KB. It must include the property `xmpNote:HasExtendedXMP`
   with a 32-character uppercase hex GUID (MD5 of the full extended portion).

2. **ExtendedXMP** -- Additional APP1 segments use the identifier
   `"http://ns.adobe.com/xmp/extension/\0"` (35 bytes: 34 characters + null terminator) followed by:

   | Field              | Bytes | Description                           |
   |--------------------|-------|---------------------------------------|
   | GUID               | 32    | MD5 of full ExtendedXMP (hex ASCII)   |
   | Full extended length | 4   | Total ExtendedXMP size (big-endian)   |
   | Offset             | 4     | Byte offset of this chunk             |
   | Chunk data         | N     | XMP data (~65,400 bytes max per segment) |

Readers must:
- Verify each chunk's GUID matches the `xmpNote:HasExtendedXMP` value
- Reassemble chunks by offset into the full ExtendedXMP serialization
- Merge the ExtendedXMP tree with the StandardXMP tree

**ImageIO handles Extended XMP transparently** when using
`CGImageSourceCopyMetadataAtIndex`. Writing Extended XMP requires careful
management if the total XMP exceeds 64 KB.

### APP2 -- ICC Profile (`FF E2`)

ICC color profiles are stored in APP2 segments with the identifier
`"ICC_PROFILE\0"`. Because profiles may exceed 64 KB, they can span multiple
APP2 segments:

| Field       | Bytes | Description                                |
|-------------|-------|--------------------------------------------|
| Identifier  | 12    | `"ICC_PROFILE\0"`                          |
| Chunk Index | 1     | Current chunk number (1-based)             |
| Chunk Count | 1     | Total number of chunks                     |
| Profile Data| N     | ICC profile data (partial or complete)     |

Readers concatenate all chunks in order to reconstruct the full profile.
Common profiles: sRGB IEC61966-2.1 (~3.1 KB), Display P3 (~500 bytes for
parametric), Adobe RGB (1998) (~560 bytes).

### APP13 -- IPTC / Photoshop Image Resources (`FF ED`)

Adobe Photoshop uses APP13 for storing Image Resource Blocks (IRBs), which
include IPTC IIM data among other resources.

```
FF ED                      APP13 marker
XX XX                      Segment length
"Photoshop 3.0\0"          Identifier (14 bytes)
-- 8BIM resource blocks follow --
```

Each 8BIM resource block has this structure:

| Field     | Bytes | Description                          |
|-----------|-------|--------------------------------------|
| Signature | 4     | `"8BIM"` (always)                    |
| Resource ID | 2   | Identifies the resource type         |
| Name      | Var   | Pascal string (padded to even length)|
| Data Size | 4     | Size of resource data                |
| Data      | N     | Resource data (padded to even length)|

Key resource IDs for metadata:

| ID       | Purpose                                |
|----------|----------------------------------------|
| `0x0404` | **IPTC-IIM record 2 data** (primary)   |
| `0x040C` | Thumbnail (JPEG format)                |
| `0x040F` | ICC profile (alternative to APP2)      |
| `0x0422` | EXIF data (alternative to APP1)        |
| `0x0424` | XMP data (alternative to APP1)         |

IPTC IIM data at resource `0x0404` consists of dataset records:

```
1C <record_number> <dataset_number> <length_hi> <length_lo> <data>
```

ImageIO reads IPTC from this location and exposes it via
`kCGImagePropertyIPTCDictionary`.

### APP14 -- Adobe Color Transform (`FF EE`)

Identified by `"Adobe"` (5 bytes). Contains color transform information
used by Adobe software to correctly interpret CMYK and YCbCr color data.

| Field          | Bytes | Description                        |
|----------------|-------|------------------------------------|
| Identifier     | 5     | `"Adobe"`                          |
| Version        | 2     | DCT encode version                 |
| Flags0         | 2     | Flags                              |
| Flags1         | 2     | Flags                              |
| Color Transform| 1     | 0 = Unknown, 1 = YCbCr, 2 = YCCK  |

This marker is critical for correct CMYK JPEG decoding -- without it, colors
may be inverted.

---

## Metadata Capacity

| Standard   | Supported | Location                   | Max Size          | Multi-Segment     |
|------------|-----------|----------------------------|-------------------|-------------------|
| **EXIF**   | Yes       | APP1 (`Exif\0\0`)          | ~64 KB            | No                |
| **XMP**    | Yes       | APP1 (Adobe namespace)     | ~64 KB standard   | Yes (Extended XMP)|
| **IPTC IIM** | Yes    | APP13 (8BIM `0x0404`)      | ~64 KB            | Theoretically     |
| **ICC**    | Yes       | APP2 (`ICC_PROFILE\0`)     | Unlimited         | Yes (chunked)     |
| **GPS**    | Yes       | GPS IFD within EXIF APP1   | Part of EXIF      | No                |
| **Comment** | Yes      | COM marker                 | ~64 KB            | No                |

JPEG is one of only three formats (alongside TIFF and PSD) that supports all
five major metadata standards simultaneously.

---

## Baseline vs Progressive JPEG

| Property         | Baseline (SOF0, `FF C0`) | Progressive (SOF2, `FF C2`) |
|------------------|--------------------------|------------------------------|
| Scan count       | 1 scan                   | Multiple scans (typically 3-10) |
| Loading behavior | Top-to-bottom, row by row| Full image at increasing quality |
| Encoding         | Sequential DCT           | Progressive DCT              |
| File size        | Slightly larger           | Often 2-10% smaller          |
| Decoding speed   | Faster (single pass)     | Slightly slower (multiple passes) |
| Web experience   | Row-by-row reveal        | Blurry-to-sharp refinement   |
| Bit depth        | 8-bit only               | 8-bit only                   |

**Interleaved vs Non-Interleaved Scans:**
- In baseline JPEG, a single scan contains all color components (Y, Cb, Cr)
  interleaved together.
- In progressive JPEG, DC coefficient scans may be interleaved across
  components, but AC coefficient scans are always non-interleaved (one
  component per scan).

ImageIO reports progressive encoding via `kCGImagePropertyJFIFIsProgressive`.

---

## Lossless Metadata Editing

JPEG's marker-based structure makes it the ideal format for lossless metadata
operations. Because metadata lives in APP markers that are completely separate
from the compressed image data (SOS + entropy-coded bytes), you can add,
replace, or remove APP markers without touching the scan data.

### ImageIO Support

`CGImageDestinationCopyImageSource` (iOS 7.0+ / macOS 10.8+) performs lossless
metadata updates on JPEG:

```swift
// Lossless metadata update -- no image re-encode
let source = CGImageSourceCreateWithURL(inputURL as CFURL, nil)!
let destination = CGImageDestinationCreateWithURL(
    outputURL as CFURL, kUTTypeJPEG, 1, nil)!

let metadata: [CFString: Any] = [
    kCGImageDestinationMetadata: updatedMetadataDict,
    kCGImageDestinationMergeMetadata: true
]

var error: Unmanaged<CFError>?
CGImageDestinationCopyImageSource(
    destination, source, metadata as CFDictionary, &error)
// No need to call CGImageDestinationFinalize -- CopyImageSource does it
```

This copies the compressed data verbatim and only rewrites the metadata
markers. **No generation loss occurs.**

**Supported formats for lossless metadata editing:** JPEG, PNG, TIFF, PSD.
**Not supported:** HEIC, WebP, AVIF, GIF, DNG, RAW.

### Lossless Crop and Rotation

JPEG supports lossless crop (on MCU boundaries, typically 8x8 or 16x16 pixel
blocks) and lossless 90/180/270-degree rotation by rearranging DCT coefficients
without inverse-transform. Tools like `jpegtran` and Better JPEG implement
this. **ImageIO does not provide lossless crop/rotation APIs** -- only metadata
operations are lossless via Apple's framework.

---

## ImageIO Keys: `kCGImagePropertyJFIFDictionary`

Available since iOS 4.0.

| Key                                    | Type      | Purpose                          |
|----------------------------------------|-----------|----------------------------------|
| `kCGImagePropertyJFIFVersion`          | CFArray   | JFIF version (e.g. `[1, 2]`)    |
| `kCGImagePropertyJFIFXDensity`         | CFNumber  | Horizontal pixel density         |
| `kCGImagePropertyJFIFYDensity`         | CFNumber  | Vertical pixel density           |
| `kCGImagePropertyJFIFDensityUnit`      | CFNumber  | 0 = no unit, 1 = DPI, 2 = DPCM  |
| `kCGImagePropertyJFIFIsProgressive`    | CFBoolean | Progressive JPEG flag            |

The JFIF dictionary provides only format-level encoding properties. Camera
settings, timestamps, location, and editorial data are in the EXIF, GPS,
TIFF, IPTC, and XMP dictionaries -- those are cross-format standards, not
JPEG-specific.

---

## Recommended APP Marker Ordering

For maximum compatibility, APP markers should appear in this order after SOI:

1. `APP0` -- JFIF header (required by JFIF spec)
2. `APP1` -- EXIF data
3. `APP1` -- Standard XMP data
4. `APP1` -- Extended XMP segments (if needed)
5. `APP2` -- ICC profile segment(s)
6. `APP13` -- IPTC / Photoshop resources
7. `APP14` -- Adobe color transform (if needed)
8. Other APP markers
9. `DQT`, `SOF`, `DHT`, `SOS` -- image data
10. `EOI`

Most readers are tolerant of different orderings, but placing EXIF APP1
immediately after APP0 (or SOI if no APP0) ensures the widest compatibility.

---

## Key Characteristics for iOS Development

| Property              | Value                                          |
|-----------------------|------------------------------------------------|
| UTI                   | `public.jpeg`                                  |
| ImageIO Read          | iOS 4.0+                                       |
| ImageIO Write         | iOS 4.0+                                       |
| ImageIO Dictionary    | `kCGImagePropertyJFIFDictionary`               |
| Metadata Standards    | EXIF, XMP, IPTC IIM, ICC, GPS (all five)       |
| Lossless Meta Edit    | Yes (`CGImageDestinationCopyImageSource`)       |
| Color Depth           | 8-bit per channel                              |
| Color Models          | Grayscale, RGB (YCbCr internally), CMYK        |
| Alpha Channel         | No                                             |
| Animation             | No                                             |
| Lossy Compression     | Yes (DCT-based, configurable quality)          |
| Max Dimensions        | 65,535 x 65,535 pixels (SOF field limit)       |
| HDR Gain Map          | Yes (iOS 14.1+ via auxiliary data)             |

---

## Common Gotchas

1. **64 KB segment limit** -- Each APP marker segment maxes out at 65,535
   bytes (including the 2-byte length). This affects EXIF (especially with
   large MakerNotes or high-res thumbnails), XMP (requires Extended XMP),
   and ICC profiles (requires multi-segment APP2).

2. **Duplicate APP1 markers** -- EXIF and XMP both use APP1. Readers
   distinguish them by the identifier string (`"Exif\0\0"` vs the Adobe XMP
   namespace URI). Some poorly written tools may confuse them.

3. **JFIF vs Exif conflict** -- Technically, JFIF requires APP0 immediately
   after SOI, while Exif requires APP1 immediately after SOI. They are
   mutually exclusive per spec. In practice, nearly all software tolerates
   both present, and ImageIO handles this gracefully.

4. **IPTC charset ambiguity** -- IPTC IIM `CodedCharacterSet` can indicate
   UTF-8 via the escape sequence `\x1B\x25\x47`, but many tools write Latin-1
   without declaring it. ImageIO assumes UTF-8 when reading, which can cause
   mojibake with improperly encoded data.

5. **Lossy round-trips** -- Re-encoding JPEG (e.g., via `UIImage` ->
   `jpegData(compressionQuality:)`) introduces generation loss. Always use
   `CGImageDestinationCopyImageSource` for metadata-only changes.

6. **APP14 Adobe marker** -- Some JPEGs include an APP14 marker with Adobe
   color transform information (YCCK, inverted CMYK). Without this marker,
   CMYK JPEGs may display with inverted colors.

7. **Orientation** -- EXIF orientation is stored in the TIFF IFD0 within the
   APP1 EXIF segment. Tools that strip EXIF but keep image data lose
   orientation, causing rotated display.

8. **Extended XMP adoption** -- Many tools and libraries do not read Extended
   XMP. If you embed large XMP data (e.g., extensive IPTC Extension or AI
   metadata), verify that your target readers support Extended XMP.

---

## Cross-References

- **EXIF tags:** `references/exif/tag-reference.md`
- **EXIF structure in JPEG:** `references/exif/technical-structure.md`
- **GPS keys:** `references/imageio/property-keys.md` (GPS Dictionary section)
- **IPTC fields:** `references/imageio/property-keys.md` (IPTC Dictionary section)
- **XMP namespaces:** `references/xmp/` (XMP standard reference)
- **ICC profiles:** `references/icc/` (color profiles reference)
- **Lossless editing API:** `references/imageio/cgimagedestination.md`
- **ImageIO format support:** `references/imageio/supported-formats.md`
- **8BIM in PSD:** `references/formats/other-formats.md` (PSD section)
- **All JFIF keys:** `references/imageio/property-keys.md` (JFIF Dictionary)
