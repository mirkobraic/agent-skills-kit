# TIFF as a Container Format

> Part of [TIFF Reference](README.md)

TIFF (Tagged Image File Format) is not just an image format -- it is the
**structural foundation** for EXIF metadata in JPEG, DNG, and many RAW
formats. Understanding TIFF structure is essential for understanding how image
metadata works across the Apple ecosystem.

This document covers the binary structure of TIFF files, the IFD system,
byte order, sub-IFD pointers, multi-page TIFF, BigTIFF, and how ImageIO
decomposes the unified TIFF structure into separate property dictionaries.

---

## TIFF Structure Overview

Every TIFF file (and every EXIF block in a JPEG) has the same fundamental
structure:

```
+----------------------------------+
|  TIFF Header (8 bytes)           |
|  +- Byte order (2 bytes)         |
|  +- Magic number 42 (2 bytes)    |
|  +- Offset to IFD0 (4 bytes)     |
+----------------------------------+
|  IFD0 (Primary Image)            |
|  +- Entry count (2 bytes)        |
|  +- Tag entries (12 bytes each)  |
|  +- Next IFD offset (4 bytes) ---+--> IFD1
|  +- Data area                    |
|     +- Make, Model, DateTime...  |
|     +- ExifIFDPointer -----------+--> Exif SubIFD
|     +- GPSInfoIFDPointer --------+--> GPS IFD
+----------------------------------+
|  Exif SubIFD                     |
|  +- Camera settings, exposure... |
|  +- InteropIFDPointer -----------+--> Interoperability IFD
|  +- MakerNote (opaque blob)      |
+----------------------------------+
|  GPS IFD                         |
|  +- Coordinates, altitude, etc.  |
+----------------------------------+
|  Interoperability IFD            |
|  +- File exchange rules          |
+----------------------------------+
|  IFD1 (Thumbnail)                |
|  +- Thumbnail dimensions         |
|  +- Compression type             |
|  +- Thumbnail image data         |
+----------------------------------+
```

---

## TIFF Header

The header is always the first 8 bytes of the TIFF structure:

| Offset | Size | Field | Description |
|--------|------|-------|-------------|
| 0 | 2 bytes | Byte order | `0x4949` ("II") = little-endian; `0x4D4D` ("MM") = big-endian |
| 2 | 2 bytes | Magic number | Always `0x002A` (42) for classic TIFF |
| 4 | 4 bytes | IFD0 offset | Byte offset to the first IFD, usually `0x00000008` |

The magic number 42 is not arbitrary -- it was chosen as "a number with deep
philosophical significance" according to the TIFF 6.0 specification (a
reference to Douglas Adams). BigTIFF uses 43 instead.

### Byte Order

The two-byte byte order marker determines how all multi-byte values in the
entire file are interpreted:

| Marker | Bytes | Name | Origin | Who Uses It |
|--------|-------|------|--------|-------------|
| II | `0x4949` | Little-endian | Intel | iPhones, most digital cameras, Windows software |
| MM | `0x4D4D` | Big-endian | Motorola | Some Ricoh/Pentax cameras, older Kodak, some scanners |

"II" = Intel byte order (least significant byte first).
"MM" = Motorola byte order (most significant byte first).

**iPhones always write little-endian ("II").** A compliant TIFF reader must
handle both byte orders. The byte order applies to every multi-byte value in
the file: tag IDs, type codes, counts, offsets, SHORT values, LONG values,
RATIONAL numerators and denominators.

### Binary Example

A little-endian TIFF header pointing to IFD0 at offset 8:

```
49 49    -- "II" (little-endian)
2A 00    -- Magic number 42 (0x002A in little-endian)
08 00 00 00  -- IFD0 at offset 8 (immediately after header)
```

A big-endian TIFF header:

```
4D 4D    -- "MM" (big-endian)
00 2A    -- Magic number 42 (0x002A in big-endian)
00 00 00 08  -- IFD0 at offset 8
```

---

## IFD Entry Format

Each Image File Directory starts with a 2-byte count of entries, followed by
that many 12-byte tag entries, followed by a 4-byte offset to the next IFD
(or `0x00000000` if this is the last IFD in the chain).

### IFD Layout

```
[2 bytes]  Entry count (N)
[12 bytes] Tag entry 0
[12 bytes] Tag entry 1
  ...
[12 bytes] Tag entry N-1
[4 bytes]  Next IFD offset (or 0x00000000)
```

Total IFD size = 2 + (N x 12) + 4 bytes.

### 12-Byte Tag Entry

Each tag entry:

| Offset | Size | Field | Description |
|--------|------|-------|-------------|
| 0 | 2 bytes | Tag ID | Identifies what kind of data this is (e.g., 271 = Make) |
| 2 | 2 bytes | Data type | One of 12 TIFF data types (see below) |
| 4 | 4 bytes | Count | Number of values of the given type |
| 8 | 4 bytes | Value/Offset | If total data fits in 4 bytes, stored here directly; otherwise, byte offset to data area |

**Tag entries must be sorted in ascending order by tag ID.** This is a TIFF
requirement that enables binary search for tag lookup.

The "fits in 4 bytes" rule: multiply the type size by the count. If the
result is 4 bytes or less, the value is stored directly in the Value/Offset
field (left-justified). If larger, the field contains an offset pointing to
the data stored elsewhere in the file.

### TIFF Data Types

| ID | Name | Size | Description |
|----|------|------|-------------|
| 1 | BYTE | 1 | Unsigned 8-bit integer |
| 2 | ASCII | 1 | 7-bit ASCII, null-terminated. Count includes the null |
| 3 | SHORT | 2 | Unsigned 16-bit integer |
| 4 | LONG | 4 | Unsigned 32-bit integer |
| 5 | RATIONAL | 8 | Two LONGs: numerator / denominator |
| 6 | SBYTE | 1 | Signed 8-bit integer |
| 7 | UNDEFINED | 1 | Arbitrary bytes (meaning defined per tag) |
| 8 | SSHORT | 2 | Signed 16-bit integer |
| 9 | SLONG | 4 | Signed 32-bit integer |
| 10 | SRATIONAL | 8 | Two SLONGs: signed numerator / denominator |
| 11 | FLOAT | 4 | IEEE 754 single-precision |
| 12 | DOUBLE | 8 | IEEE 754 double-precision |

Types 1-5 are from TIFF 5.0 (the "classic five"). Types 6-12 were added in
TIFF 6.0. EXIF 3.0 added type 129 (UTF-8) for new text tags. BigTIFF added
types 16 (LONG8, unsigned 64-bit) and 18 (IFD8, unsigned 64-bit IFD offset).

### Inline vs Offset Data

Examples of when data fits inline (4 bytes or less):

| Type | Count | Total Size | Inline? |
|------|-------|-----------|---------|
| SHORT | 1 | 2 bytes | Yes (2 bytes, left-justified in 4-byte field) |
| SHORT | 2 | 4 bytes | Yes (exactly 4 bytes) |
| SHORT | 3 | 6 bytes | No (offset to data area) |
| LONG | 1 | 4 bytes | Yes (exactly 4 bytes) |
| ASCII | 4 | 4 bytes | Yes (3 chars + null) |
| ASCII | 5 | 5 bytes | No (offset to data area) |
| RATIONAL | 1 | 8 bytes | No (always needs offset) |

---

## IFD0 -- Primary Image

IFD0 is the main Image File Directory. It contains:

1. **TIFF baseline tags** -- ImageWidth, ImageLength, BitsPerSample,
   Compression, PhotometricInterpretation, StripOffsets, RowsPerStrip,
   StripByteCounts, XResolution, YResolution, ResolutionUnit

2. **Descriptive tags** -- Make, Model, Software, DateTime, Artist, Copyright,
   HostComputer, ImageDescription, DocumentName

3. **Color tags** -- WhitePoint, PrimaryChromaticities, TransferFunction

4. **Sub-IFD pointers** -- Links to the Exif SubIFD, GPS IFD, and other
   extended data

ImageIO exposes the descriptive, orientation, resolution, and color tags
through `kCGImagePropertyTIFFDictionary`. The structural tags (strip offsets,
byte counts) are handled internally. See
[`tag-reference.md`](tag-reference.md) for the complete list.

---

## Sub-IFD Pointers

IFD0 contains special tags whose values are byte offsets pointing to
subordinate IFDs. These pointer tags are what make TIFF an extensible
container:

### ExifIFDPointer (Tag 34665 / 0x8769)

Points to the **Exif SubIFD**, which contains all camera-specific capture
data: exposure, ISO, focal length, timestamps, lens info, color space,
MakerNote, and more (~65 tags in EXIF 3.0).

ImageIO follows this pointer automatically and exposes the contents through
`kCGImagePropertyExifDictionary`.

### GPSInfoIFDPointer (Tag 34853 / 0x8825)

Points to the **GPS IFD**, which contains location data: latitude, longitude,
altitude, timestamps, direction, speed (~30 tags).

ImageIO follows this pointer and exposes the contents through
`kCGImagePropertyGPSDictionary`.

### InteroperabilityIFDPointer (Tag 40965 / 0xA005)

Points to the **Interoperability IFD**, which contains file exchange rules
(e.g., `InteroperabilityIndex` = "R98" for sRGB conformance, "R03" for
Adobe RGB). This pointer lives **in the Exif SubIFD**, not in IFD0.

ImageIO follows this pointer internally but does not expose a separate
dictionary for it.

### Sub-IFD Pointer Diagram

```
IFD0
 +-- Tag 34665 (ExifIFDPointer) --> Exif SubIFD
 |                                   +-- Tag 40965 (InteropIFDPointer) --> Interop IFD
 +-- Tag 34853 (GPSInfoIFDPointer) --> GPS IFD
 +-- Next IFD offset --> IFD1 (Thumbnail)
```

### Private Sub-IFDs

The TIFF specification allows any tag to contain an offset to a private
IFD structure. This mechanism is used by:

- **DNG** -- multiple sub-IFDs for different image representations
  (full-res, preview, thumbnail) via the SubIFDs tag (330 / 0x014A)
- **MakerNote** -- some manufacturers (e.g., Olympus, Panasonic) structure
  their MakerNote data as IFDs
- **GeoTIFF** -- geospatial metadata in a GeoKeys structure

---

## IFD1 -- Thumbnail Image

IFD1 is linked from IFD0 via the "next IFD offset" field (the 4-byte value
after the last tag entry in IFD0). It describes an embedded thumbnail image.

**Common thumbnail format:**
- Compression (tag 259) = 6 (JPEG)
- JPEGInterchangeFormat (tag 513 / 0x0201) = offset to thumbnail JPEG data
- JPEGInterchangeFormatLength (tag 514 / 0x0202) = byte count of thumbnail
- Recommended size: 160 x 120 pixels (EXIF spec recommendation)

The thumbnail data is a complete JPEG stream (starting with `0xFFD8`, ending
with `0xFFD9`) embedded within the TIFF structure.

**Privacy note:** Editing software sometimes modifies the main image but
fails to update the thumbnail, potentially leaking pre-edit content
(e.g., a cropped face visible in the unmodified thumbnail). This is a known
privacy risk, especially in social media sharing workflows.

In ImageIO, the thumbnail is accessed via
`CGImageSourceCreateThumbnailAtIndex` rather than through the property
dictionary system.

---

## Multi-Page TIFF

TIFF supports multiple images in a single file through the IFD chain:

```
TIFF Header --> IFD0 --> IFD1 --> IFD2 --> ... --> IFDn (next=0)
```

Each IFD in the chain describes a complete image with its own dimensions,
compression, and pixel data. The chain is followed by the "next IFD offset"
field at the end of each IFD (0 means end of chain).

**Uses:**
- **Fax/document imaging** -- multi-page scanned documents
- **Pyramidal TIFF** -- multiple resolutions of the same image (used in
  GIS and digital pathology)
- **EXIF** -- IFD0 is the main image, IFD1 is the thumbnail (only 2 IFDs)

In ImageIO, `kCGImagePropertyImageCount` reports the total number of images,
and `CGImageSourceCopyPropertiesAtIndex(source, index, nil)` accesses each
page by its zero-based index.

**Important distinction:** Multi-page TIFF (IFD chain) is different from
Sub-IFDs (tag 330). The IFD chain links sibling images at the same level,
while Sub-IFDs create a parent-child hierarchy (used in DNG for different
representations of the same image).

---

## How ImageIO Separates TIFF Tags

When ImageIO reads an image, it parses the entire TIFF structure (all IFDs)
and distributes the tags into separate property dictionaries:

```
TIFF Structure                    ImageIO Property Dictionaries
--------------                    ----------------------------
IFD0:
  Make, Model, DateTime...   -->  kCGImagePropertyTIFFDictionary
  Orientation               -->  kCGImagePropertyTIFFDictionary
                                  + kCGImagePropertyOrientation (top-level)
  ExifIFDPointer -->
    Exif SubIFD:
      ExposureTime, ISO...   -->  kCGImagePropertyExifDictionary
      InteropIFDPointer -->
        Interop IFD          -->  (internal, not exposed)
  GPSInfoIFDPointer -->
    GPS IFD:
      Latitude, Longitude... -->  kCGImagePropertyGPSDictionary

IFD1 (Thumbnail):               (internal, accessed via
  Thumbnail data             -->  CGImageSourceCreateThumbnailAtIndex)

Image dimensions:
  ImageWidth, ImageLength    -->  kCGImagePropertyPixelWidth/Height (top-level)
  BitsPerSample              -->  kCGImagePropertyDepth (top-level)

Color:
  ICC Profile (tag 34675)    -->  kCGImagePropertyProfileName (top-level)

External metadata blocks:
  XMP (tag 700)              -->  CGImageSourceCopyMetadataAtIndex
  IPTC (tag 33723)           -->  kCGImagePropertyIPTCDictionary
```

This separation is why "TIFF tags" and "EXIF tags" appear as separate
dictionaries even though they all live in the same IFD-based structure.
The TIFF dictionary gets the IFD0 descriptive tags; the EXIF dictionary
gets the Exif SubIFD capture tags.

**Key insight:** When you call `CGImageSourceCopyPropertiesAtIndex`, ImageIO
has already done the work of parsing byte order, following offsets, resolving
data types, and sorting tags into dictionaries. You never need to parse
raw IFD entries yourself.

---

## TIFF as Foundation for Other Formats

TIFF is not just a standalone image format -- its IFD structure is the
foundation for metadata in many other formats:

### JPEG EXIF

In JPEG files, the APP1 marker segment (`0xFFE1`) contains a complete
TIFF structure (header + IFDs) after a 6-byte `"Exif\0\0"` preamble.
The TIFF structure inside JPEG holds all EXIF, GPS, and IFD0 metadata.

```
JPEG:
  FFD8 (SOI)
  FFE1 (APP1)        -- size limited to 65,535 bytes (64 KB)
    "Exif\0\0"       -- 6-byte preamble
    +- TIFF Header -+
    |  IFD0          |  <-- Make, Model, DateTime, Orientation
    |  Exif SubIFD   |  <-- Exposure, ISO, timestamps, MakerNote
    |  GPS IFD       |  <-- Location
    |  IFD1          |  <-- Thumbnail
    +----------------+
  FFE1 (APP1) or FFE0 (APP0)
    XMP data (optional, separate APP1 segment)
  FFED (APP13)
    IPTC data (optional)
  FFxx (image data markers)
  FFD9 (EOI)
```

**Size constraint:** All EXIF data must fit in a single APP1 segment:
65,535 bytes (64 KB) maximum. This constrains thumbnail size, MakerNote size,
and total tag count. HEIF, PNG, WebP, and AVIF do not have this limit.

### DNG (Digital Negative)

DNG is based on TIFF/EP (ISO 12234-2) and uses the full TIFF container
structure. A DNG file is literally a TIFF file with additional
DNG-specific tags (tag IDs 50706-50741 and beyond) alongside standard TIFF
and EXIF tags. DNG files use the SubIFDs tag (330) to store multiple image
representations:

```
DNG Structure:
  IFD0 (main): full-resolution CFA/raw data
    SubIFD 0: preview JPEG
    SubIFD 1: thumbnail JPEG
  Exif SubIFD: camera capture metadata
  XMP: processing parameters, Camera Raw settings
```

### Camera RAW Formats

Most camera RAW formats use TIFF-based structures for their metadata,
though the image data encoding is proprietary:

| Format | Extension | Manufacturer | TIFF-Based? |
|--------|-----------|-------------|-------------|
| CR2 | .cr2 | Canon | Yes (TIFF container) |
| CR3 | .cr3 | Canon | No (ISOBMFF container, but EXIF is IFD-based) |
| NEF | .nef | Nikon | Yes (TIFF container) |
| ARW | .arw | Sony | Yes (TIFF container) |
| ORF | .orf | Olympus | Yes (TIFF-like container) |
| RAF | .raf | Fujifilm | Partial (proprietary header + TIFF metadata) |
| RW2 | .rw2 | Panasonic | Yes (TIFF-like container) |
| PEF | .pef | Pentax | Yes (TIFF container) |

### HEIF / HEIC

HEIF uses ISOBMFF (ISO Base Media File Format) as its container, **not**
TIFF. However, EXIF metadata is still stored using the same IFD binary
format, embedded as an item within the ISOBMFF container. The binary
format of the EXIF block itself (header + IFDs) is identical to what
appears in TIFF and JPEG.

```
HEIF Container (ISOBMFF):
  ftyp box: file type
  meta box:
    EXIF item: [TIFF header + IFD0 + Exif SubIFD + GPS IFD]
    XMP item: [XMP packet]
  mdat box: HEVC-encoded image data
```

### PNG

The PNG Extensions specification (2017) introduced the `eXIf` chunk, which contains a raw EXIF block
(TIFF header + IFDs) without the `"Exif\0\0"` preamble. Before this, PNG
had no standard EXIF support (only XMP via iTXt chunks).

---

## BigTIFF

Classic TIFF uses 32-bit offsets, limiting files to approximately **4 GB**.
BigTIFF extends this with 64-bit offsets:

| Feature | Classic TIFF | BigTIFF |
|---------|-------------|---------|
| Magic number | 42 (0x002A) | 43 (0x002B) |
| Header size | 8 bytes | 16 bytes |
| Offset size | 4 bytes (32-bit) | 8 bytes (64-bit) |
| Max file size | ~4 GB | ~18 exabytes |
| IFD entry size | 12 bytes | 20 bytes |
| Entry count field | 2 bytes (max 65,535 entries) | 8 bytes |
| Next IFD pointer | 4 bytes | 8 bytes |
| New data types | -- | LONG8 (16), SLONG8 (17), IFD8 (18) |

### BigTIFF Header (16 bytes)

| Offset | Size | Field | Description |
|--------|------|-------|-------------|
| 0 | 2 bytes | Byte order | "II" or "MM" (same as classic) |
| 2 | 2 bytes | Magic number | 43 (0x002B) |
| 4 | 2 bytes | Offset size | Always 8 (bytes per offset) |
| 6 | 2 bytes | Constant | Always 0 (reserved) |
| 8 | 8 bytes | IFD0 offset | 64-bit offset to first IFD |

### BigTIFF IFD Entry (20 bytes)

| Offset | Size | Field |
|--------|------|-------|
| 0 | 2 bytes | Tag ID |
| 2 | 2 bytes | Data type |
| 4 | 8 bytes | Count |
| 12 | 8 bytes | Value/Offset |

Values that fit in 8 bytes are stored inline; larger values use an 8-byte
offset.

### Apple Support

**Apple's ImageIO does not support BigTIFF.** Files using BigTIFF format
(magic number 43) will fail to open with `CGImageSourceCreateWithURL` --
`CGImageSourceGetStatus` returns `.statusUnknownType`.

This is primarily a concern in:
- Scientific imaging (microscopy, satellite)
- GIS (geospatial raster data)
- Medical imaging (pathology whole-slide images)
- Any workflow producing TIFF files exceeding 4 GB

For BigTIFF support on Apple platforms, use LibTIFF (via C interop) or a
specialized framework. For typical photography workflows, the 4 GB limit
is rarely reached.

---

## Offset Model and Its Implications

All offsets within a TIFF structure are **absolute** -- measured from the
first byte of the TIFF header (the byte order marker). This design has
important consequences:

### 1. Moving Data Invalidates Pointers

If you insert, remove, or relocate any block of data in a TIFF file, all
offsets that pointed past the changed location become invalid. This is why
naive "edit in place" approaches to TIFF metadata modification are fragile.

### 2. MakerNote Fragility

Camera MakerNotes often contain internal offsets relative to the TIFF header
(or sometimes relative to the MakerNote start -- it varies by manufacturer).
If software rearranges the TIFF structure (e.g., stripping GPS data),
MakerNote internal offsets may become corrupted. See
[`../exif/makernote.md`](../exif/makernote.md) for details.

### 3. Lossless Metadata Editing

ImageIO's `CGImageDestinationCopyImageSource` can modify metadata without
re-encoding the image data, but only for JPEG, PNG, TIFF, and PSD formats.
It handles offset fixup internally. For HEIC, there is no lossless metadata
update -- the image must be re-encoded.

### 4. Thumbnail Offset

The thumbnail JPEG data is located at the offset specified by
JPEGInterchangeFormat (tag 513) in IFD1. This offset must be updated if
the thumbnail position changes.

### 5. Data Can Be Anywhere

The TIFF format does not require data to be stored in any particular order
or contiguous with its IFD entry. Data referenced by offsets can be located
anywhere in the file after the header. This flexibility means TIFF files
can have highly fragmented layouts, which tools must handle correctly.

---

## TIFF Structure Validation

When working with TIFF files programmatically (outside of ImageIO), these
are the structural invariants to verify:

| Check | Requirement |
|-------|-------------|
| Byte order | Must be "II" or "MM" |
| Magic number | Must be 42 (classic) or 43 (BigTIFF) |
| IFD0 offset | Must point within file bounds |
| Entry count | Must be reasonable (not millions) |
| Tag order | Must be ascending by tag ID within each IFD |
| Offset values | Must point within file bounds |
| ASCII strings | Must be null-terminated |
| RATIONAL denominator | Must not be zero |
| IFD chain | Must terminate (next IFD = 0) -- no cycles |

ImageIO handles all of these checks internally. These are relevant if you
are implementing a custom TIFF parser or debugging malformed files.
