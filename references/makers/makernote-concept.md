# MakerNote Concept

> Part of [Manufacturer MakerNote Dictionaries](README.md)

The MakerNote is a proprietary, vendor-specific metadata container embedded
inside EXIF data. It is the mechanism camera manufacturers use to store
capture information that goes beyond what standard EXIF tags provide.

---

## What MakerNote Is

**EXIF Tag 37500 (0x927C)**, type `UNDEFINED`. The EXIF specification
(CIPA DC-008) allocates this single tag for "a tag for manufacturers of
Exif/DCF writers to record any desired information. The contents are up
to the manufacturer, but this tag shall not be used for any other than
its intended purpose."

In practice, MakerNote is an opaque binary blob whose internal format is
defined entirely by the camera maker. The EXIF standard says nothing about
how to interpret the bytes -- it only reserves the tag number. The tag's
data type is `UNDEFINED` with a variable count (commonly 1 KB to 64 KB,
but can exceed the 64 KB APP1 limit in JPEG when using EXIF offsets into
the file body).

```
EXIF IFD (IFD Exif)
  +-- Tag 0x927C  MakerNote
       Type:   UNDEFINED
       Count:  variable (often 1 KB -- 64 KB)
       Value:  vendor-specific binary data
```

### Why It Exists

Standard EXIF tags cover a broad set of camera settings (exposure, ISO,
focal length, timestamps, etc.), but manufacturers need to store far more:

- **Proprietary shooting modes** (Canon scene modes, Nikon Active D-Lighting,
  Fujifilm Film Simulation)
- **Internal autofocus data** (AF points used, focus distance, AF area mode,
  face/eye detection results)
- **Lens identification** (proprietary lens ID databases, adapter info,
  lens firmware version, lens serial number)
- **Image processing parameters** (noise reduction level, color matrix,
  tone curves, Picture Control / Picture Style settings)
- **Hardware diagnostics** (shutter count, sensor temperature, firmware
  version, battery info)
- **Computational photography flags** (Apple HDR type, burst grouping,
  Live Photo linking, depth references, semantic scene classification)
- **Serial numbers** (body serial, lens serial, internal serial)

Without MakerNote, this data would be lost. Some of it (like shutter count,
lens model, or film simulation) is stored *only* in MakerNote, with no
standard EXIF equivalent.

### What MakerNote Is NOT

- **Not a standard** -- there is no "MakerNote specification" beyond the
  single tag reservation
- **Not portable** -- the same tag ID (e.g., 0x0001) means completely
  different things in Canon vs Nikon vs Apple MakerNotes
- **Not XMP-accessible** -- MakerNote has no standard XMP namespace mapping.
  It exists only in the EXIF binary IFD system
- **Not guaranteed stable** -- manufacturers can and do change MakerNote
  structure between firmware versions and camera models

---

## Structure Variants

Despite MakerNote being a single EXIF tag, manufacturers use several
distinct internal formats. Understanding these is essential for anyone
building MakerNote parsers or working with metadata preservation.

### 1. IFD-Style (Headerless TIFF IFD)

The MakerNote contains one or more IFD (Image File Directory) structures --
the same binary format used by the rest of EXIF. Each entry has a 12-byte
record: tag ID (2 bytes), data type (2 bytes), count (4 bytes), and
value/offset (4 bytes).

**Used by:** Canon, some older Olympus, some Samsung

Canon is the canonical example: the MakerNote starts immediately with an
IFD entry count (no header bytes). The IFD entries point to sub-structures
(CameraSettings, ShotInfo, FocusInfo, ColorData, etc.) using offset
pointers. Because there is no header signature, format detection relies
on the camera Make being "Canon" in the TIFF IFD.

```
Canon MakerNote (no header):
  [IFD entry count: 2 bytes]
  [IFD entry 0: tag=0x0001, type=SHORT, count=N, offset=...]  -> CameraSettings array
  [IFD entry 1: tag=0x0004, type=SHORT, count=N, offset=...]  -> ShotInfo array
  ...
  [IFD data area...]
```

**Offset base:** The start of the main TIFF header (absolute offsets).
This makes Canon MakerNote the most fragile format -- any EXIF
modification that shifts byte positions will break internal pointers.

### 2. Header + Self-Contained TIFF

The MakerNote begins with a vendor-specific signature, followed by its own
complete TIFF header (byte order marker `"MM"` or `"II"` + magic number
`0x002A` + IFD offset). This makes the MakerNote a self-contained TIFF
structure with its own byte order, independent of the main EXIF byte order.

**Used by:** Nikon (Type 3), Fujifilm

Nikon Type 3 MakerNotes are the most common example. They start with
`"Nikon\0"` + version bytes, then a full TIFF header. Internal offsets
are relative to the start of the MakerNote's own TIFF header, making
this format more resilient to repositioning -- as long as the entire
MakerNote block is moved intact.

```
Nikon Type 3 MakerNote:
  "Nikon\0"          (6 bytes, signature)
  0x02 0x10 0x00     (3 bytes, version 2.10)
  --- self-contained TIFF starts here (base offset for internal offsets) ---
  "MM" or "II"       (byte order -- independent of main EXIF)
  0x00 0x2A          (TIFF magic number 42)
  [4-byte offset to IFD0, relative to TIFF header start]
  [IFD entries...]
```

Fujifilm uses `"FUJIFILM"` (8 bytes) + 4-byte version/offset, followed
by IFD entries. Fujifilm always uses **little-endian** byte order
regardless of the main TIFF byte order, and offsets are relative to the
start of the MakerNote data -- making it one of the most robust formats.

```
Fujifilm MakerNote:
  "FUJIFILM"         (8 bytes, signature)
  [4-byte offset to IFD0, relative to "F" of "FUJIFILM"]
  [IFD entries in little-endian...]
```

### 3. Header + IFD (No Own TIFF Header)

A vendor signature/magic bytes followed by IFD entries, but **no**
independent TIFF header. The IFD uses the main EXIF byte order, and
offsets typically reference the main TIFF structure (absolute).

**Used by:** Olympus (`"OLYMP\0"` or `"OLYMPUS\0"`), Panasonic
(`"Panasonic\0"`), Pentax (`"AOC\0"` + byte order bytes)

Olympus is notable for having the most complex sub-structure: five nested
sub-IFDs (Equipment, CameraSettings, RawDevelopment, ImageProcessing,
FocusInfo), each containing dozens of tags. The `"OLYMPUS\0"` variant
(newer cameras) differs from `"OLYMP\0"` in offset base calculation.

```
Olympus MakerNote (newer format):
  "OLYMPUS\0"        (8 bytes, signature)
  0x02 0x00          (version)
  [IFD entries...]
  Tag 0x2010 -> Equipment sub-IFD
  Tag 0x2020 -> CameraSettings sub-IFD
  Tag 0x2030 -> RawDevelopment sub-IFD
  Tag 0x2040 -> ImageProcessing sub-IFD
  Tag 0x2050 -> FocusInfo sub-IFD
```

Pentax uses `"AOC\0"` followed by its own byte order marker (which can
differ from the main TIFF byte order), then standard IFD entries.

### 4. Non-IFD / Flat Binary

Some manufacturers use a flat binary format that is not IFD-based. Byte
positions have fixed meanings, with no tag/type/count structure. Decoding
requires knowing the exact byte layout for each camera model.

**Used by:** Some older Kodak, Ricoh, Casio, and Samsung models

These are the hardest to decode and most fragile to any modification.

### 5. Apple Hybrid (IFD + Binary PLIST Values)

Apple's MakerNote starts with `"Apple iOS\0"` followed by a version byte
and `"MM"` byte order marker, then standard IFD entries. What makes it
unique is that several tag values within the IFD are encoded as **binary
property lists** (bplist) -- Apple's native serialization format. These
contain structured data like CMTime dictionaries and AE analysis matrices.

```
Apple MakerNote:
  "Apple iOS\0"      (10 bytes, signature)
  0x00 0x01          (version)
  "MM"               (byte order: big-endian)
  [IFD entries...]
  Tag 0x0002 value -> bplist (AEMatrix)
  Tag 0x0003 value -> bplist (RunTime / CMTime structure)
  Tag 0x0016 value -> bplist (SceneClassification / Neural Engine results)
  Tag 0x0040 value -> bplist (SemanticStyle / Photographic Styles)
```

---

## The Offset Fragility Problem

The single most significant technical challenge with MakerNote is the
**offset fragility problem**. This is why MakerNote data is frequently
corrupted by image editing software -- and why understanding it matters
for any metadata preservation strategy.

### How Offsets Work in TIFF/EXIF

EXIF data is stored in TIFF format. IFD entries whose data exceeds 4
bytes store their values elsewhere in the file and use a 32-bit
**offset** pointer to locate them. These offsets are typically absolute --
measured from byte 0 of the TIFF header (the start of the EXIF APP1
segment payload in JPEG, or byte 0 of the file in TIFF).

### Why Rewrites Break MakerNote

When image editing software modifies EXIF metadata (adds a tag, changes a
value, strips GPS data), it often needs to **rewrite** the EXIF block. If
the MakerNote is moved to a different byte position during this rewrite,
any absolute offsets *inside* the MakerNote now point to wrong locations:

```
Before rewrite:
  TIFF header at byte 0
  EXIF IFD at byte 8
  MakerNote data at byte 500
  MakerNote internal offset says "sub-structure at byte 800" (absolute)
  -> Correctly points to byte 800

After rewrite (new tag inserted, MakerNote shifts):
  TIFF header at byte 0
  EXIF IFD at byte 8
  [new tag data at byte 500]
  MakerNote data at byte 600          <-- moved by 100 bytes
  MakerNote internal offset STILL says "byte 800"  <-- NOW WRONG
  Actual sub-structure is now at byte 900
```

The result: MakerNote sub-structures (CameraSettings, LensData, AF info,
etc.) become unreadable. The top-level MakerNote IFD entries may still
parse, but any entries that use offsets to point to data will return
garbage.

### Offset Strategies by Vendor

| Strategy | Vendors | Fragility | Details |
|----------|---------|-----------|---------|
| **Absolute offsets** (from TIFF header) | Canon, some Olympus | Most fragile | Any EXIF change that shifts bytes breaks all internal pointers |
| **Header + absolute offsets** | Olympus (`"OLYMP\0"`), Panasonic | Fragile | Signature helps identification but offsets still reference main TIFF |
| **Self-contained TIFF** (own header, relative offsets) | Nikon Type 3 | Resilient if block moved intact | Own byte order; offsets relative to internal TIFF header |
| **Relative offsets** (from MakerNote start) | Fujifilm, some Panasonic | Most resilient | Survives repositioning as long as MakerNote bytes unchanged |
| **No internal offsets** | Some Samsung, flat formats | Immune to repositioning | All data inline; no pointers to break |

### Microsoft OffsetSchema Workaround

Microsoft introduced tag **0xEA1D** (`OffsetSchema`) as a workaround. When
software moves MakerNote data during an EXIF rewrite, it writes this tag
with a **signed 32-bit integer** indicating how many bytes the MakerNote
was displaced from its original position. MakerNote readers can then add
this delta to all internal offsets.

```
EXIF IFD
  +-- Tag 0xEA1D  OffsetSchema = -100
       Meaning: MakerNote was moved 100 bytes earlier than its original position
       Adjustment: Add -100 to all internal absolute offsets
```

This is a **Microsoft extension**, not part of the official EXIF standard.
Not all software writes it, and not all MakerNote decoders read it. It
helps but does not fully solve the problem.

### ExifTool Offset Fixup

ExifTool provides several mechanisms to handle broken MakerNote offsets:

- **`-F` option:** Attempts to fix corrupted offsets by analyzing the
  MakerNote structure and adjusting pointers
- **`-F[N]` option:** Adjusts MakerNote offsets by N bytes (when you
  know the exact displacement)
- **Automatic fixup:** ExifTool tracks MakerNote displacement during
  writes and adjusts internal offsets automatically

---

## MakerNote in ImageIO

Apple's ImageIO framework parses MakerNote data for seven manufacturers
and exposes it as flat `CFDictionary` objects, keyed by numeric tag IDs
(as strings). This is accessed through `CGImageSourceCopyPropertiesAtIndex`.

### Supported Vendors

| Dictionary Constant | Vendor | iOS | Notes |
|---------------------|--------|-----|-------|
| `kCGImagePropertyMakerCanonDictionary` | Canon | 4.0+ | Headerless IFD; absolute offsets |
| `kCGImagePropertyMakerNikonDictionary` | Nikon | 4.0+ | Self-contained TIFF; partial encryption |
| `kCGImagePropertyMakerMinoltaDictionary` | Minolta / Sony | 4.0+ | Shared heritage; model-dependent |
| `kCGImagePropertyMakerFujiDictionary` | Fujifilm | 4.0+ | Relative offsets; always little-endian |
| `kCGImagePropertyMakerOlympusDictionary` | Olympus | 4.0+ | Nested sub-IFDs; absolute offsets |
| `kCGImagePropertyMakerPentaxDictionary` | Pentax | 4.0+ | AOC header; own byte order marker |
| `kCGImagePropertyMakerAppleDictionary` | Apple (iPhone/iPad) | 7.0+ | IFD + bplist values; always written fresh |

### How ImageIO Exposes MakerNote

ImageIO handles the binary parsing internally. The developer receives a
dictionary where:
- **Keys** are string representations of the vendor-specific tag numbers
  (e.g., `"1"`, `"4"`, `"10"`, `"149"`, `"5121"`)
- **Values** are `CFString`, `CFNumber`, `CFArray`, or `CFData` depending
  on the tag's data type
- **Sub-structures** (like Canon CameraSettings or Nikon LensData) may be
  flattened into arrays or remain as opaque `CFData`

```swift
let source = CGImageSourceCreateWithURL(url as CFURL, nil)!
let props = CGImageSourceCopyPropertiesAtIndex(source, 0, nil) as? [String: Any]

// Access Canon MakerNote
if let canon = props?[kCGImagePropertyMakerCanonDictionary as String] as? [String: Any] {
    // Keys are tag IDs as strings: "1", "4", "6", "16", etc.
    let modelID = canon["16"] as? Int  // CanonModelID (tag 0x0010)
}

// Access Apple MakerNote
if let apple = props?[kCGImagePropertyMakerAppleDictionary as String] as? [String: Any] {
    let burstUUID = apple["11"] as? String  // BurstUUID (tag 0x000b)
}
```

**Only ONE vendor dictionary will be non-nil** for any given image. The
Make string in the TIFF IFD determines which parser ImageIO invokes.

### Unsupported Vendors

For cameras not in the seven supported vendors (Samsung, Panasonic, Leica,
Sigma, Ricoh, Hasselblad, Phase One, etc.), ImageIO does **not** parse
the MakerNote. The raw MakerNote bytes are still accessible via
`kCGImagePropertyExifMakerNote` (as `CFData`), but the developer must
parse them manually or use ExifTool/Exiv2.

### No XMP Representation

MakerNote data has no standard XMP mapping. It does not appear in the
`CGImageMetadata` tree API. It exists only in the property dictionary
system. This means:
- MakerNote data cannot be accessed via `CGImageMetadataCopyTagMatchingImageProperty`
- MakerNote data is not included in XMP sidecar files
- Formats that only support XMP (PNG, WebP, AVIF) cannot carry MakerNote

---

## MakerNote and Metadata Preservation

### Writing MakerNote Back

When writing images with `CGImageDestination`, MakerNote dictionaries can
be included in the properties dictionary. ImageIO will re-encode them into
the binary MakerNote format. However:
- **Round-tripping is not guaranteed lossless** -- some vendor-specific
  encoding details may be lost during decode/re-encode
- **Tags not decoded by ImageIO** may be silently dropped
- **Encrypted fields** (Nikon LensData, ColorBalance) are unlikely to be
  preserved correctly through a decode/re-encode cycle

### Lossless Copy

`CGImageDestinationCopyImageSource` (JPEG, PNG, TIFF, PSD only) preserves
the raw EXIF bytes including MakerNote **without re-encoding**, which is
the safest approach for metadata preservation. The raw MakerNote bytes are
copied bit-for-bit.

### Complete Location Removal

GPS stripping tools remove data from the GPS IFD and XMP `exif:GPS*` tags,
but they do **not** filter proprietary location-related data that may be
embedded in MakerNote fields. Known examples:

- Apple MakerNote tags may correlate with location through RunTime and
  AccelerationVector
- Nikon tag 0x0039 (LocationInfo) contains GPS data from the camera
- Pentax stores Hometown/Destination city codes (tags 0x0023, 0x0024)

For complete location removal, the MakerNote must also be stripped, or the
image must be recreated from pixels with no metadata copy.

---

## Vendor-Specific MakerNote Signatures

Complete signature reference used by ExifTool and other decoders for
format detection:

| Vendor | Header Signature | Hex Bytes | Byte Order | Internal Format | Offset Base |
|--------|-----------------|-----------|------------|-----------------|-------------|
| **Canon** | None (IFD starts immediately) | -- | Same as main TIFF | Headerless IFD | Main TIFF header (absolute) |
| **Nikon Type 1** | None | -- | Big-endian | Simple IFD | Main TIFF header |
| **Nikon Type 2** | `"Nikon\0"` + `0x01 0x00` | `4E 69 6B 6F 6E 00 01 00` | Same as main TIFF | IFD after header | Main TIFF header |
| **Nikon Type 3** | `"Nikon\0"` + `0x02 0x10 0x00` | `4E 69 6B 6F 6E 00 02 10 00` | Own TIFF header | Self-contained TIFF | Internal TIFF header |
| **Apple** | `"Apple iOS\0"` + version | `41 70 70 6C 65 20 69 4F 53 00` | Big-endian (`"MM"`) | IFD + bplist values | MakerNote start + 14 |
| **Fujifilm** | `"FUJIFILM"` + 4-byte offset | `46 55 4A 49 46 49 4C 4D` | Always little-endian | IFD with relative offsets | MakerNote start |
| **Olympus (old)** | `"OLYMP\0"` | `4F 4C 59 4D 50 00` | Same as main TIFF | IFD + nested sub-IFDs | Main TIFF header |
| **Olympus (new)** | `"OLYMPUS\0"` + version | `4F 4C 59 4D 50 55 53 00` | Same as main TIFF | IFD + nested sub-IFDs | MakerNote start + 12 |
| **Panasonic** | `"Panasonic\0"` | `50 61 6E 61 73 6F 6E 69 63 00` | Same as main TIFF | IFD with relative offsets | MakerNote start |
| **Pentax** | `"AOC\0"` + byte order | `41 4F 43 00` | Own byte order marker | IFD | Varies by model |
| **Sony** | Varies by model generation | -- | Varies | IFD or proprietary | Model-dependent |
| **Samsung** | Varies | -- | Varies | IFD or flat binary | Model-dependent |
| **Leica** | Multiple formats | `"LEICA\0"`, `"LEICA0\0"`, others | Varies | IFD | Varies (most inconsistent vendor) |
| **Sigma/Foveon** | `"SIGMA\0"` or `"FOVEON\0"` | -- | Same as main TIFF | IFD | Main TIFF header |
| **Ricoh** | `"Rv"` or `"RICOH"` | -- | Varies | IFD or flat | Model-dependent |

> **Leica is the most inconsistent vendor** for MakerNote format. Different
> Leica models use different signatures, different byte orders, and different
> offset bases. ExifTool documents at least 8 distinct Leica MakerNote
> formats.

---

## Decoder Libraries

| Library | Language | MakerNote Support | Encryption | Offset Fixup |
|---------|----------|-------------------|------------|--------------|
| **ExifTool** | Perl | Most comprehensive: 20+ vendors, hundreds of camera models | Nikon (ColorBalance, LensData), Samsung | `-F` option; automatic during writes |
| **Exiv2** | C++ | Canon, Nikon, Fujifilm, Minolta/Sony, Olympus, Panasonic, Pentax, Samsung, Sigma | Nikon (ColorBalance, LensData) | Automatic detection |
| **libexif** | C | Canon, Olympus, Pentax, Fujifilm | None | None |
| **metadata-extractor** | Java/.NET | Canon, Nikon, Sony, Olympus, Fujifilm, Panasonic, Pentax, Apple (with bplist) | None | None |
| **Apple ImageIO** | C/ObjC/Swift | Canon, Nikon, Minolta/Sony, Fujifilm, Olympus, Pentax, Apple | Unknown (likely limited) | Not applicable (read-only parse) |

### ExifTool as Reference Standard

ExifTool (by Phil Harvey) is the de facto reference for MakerNote decoding.
It supports the most vendors, handles the most edge cases (encryption,
format variations across firmware versions, offset fixups), and its source
code serves as the primary documentation for MakerNote formats that have
no official specification.

Key ExifTool source files for MakerNote:

| File | Purpose |
|------|---------|
| `MakerNotes.pm` | Format detection, signature matching, offset handling, vendor routing |
| `Canon.pm` | Canon MakerNote: ~5,000 lines, most extensively documented vendor |
| `Nikon.pm` | Nikon MakerNote: ~8,000 lines, encryption handling, 3 format types |
| `Apple.pm` | Apple MakerNote: bplist decoding, CMTime, Photographic Styles |
| `FujiFilm.pm` | Fujifilm MakerNote: film simulation decode tables |
| `Olympus.pm` | Olympus MakerNote: 5 nested sub-IFDs, art filter values |
| `Sony.pm` | Sony/Minolta MakerNote: ~10,000 lines, most model-variant vendor |
| `Pentax.pm` | Pentax/Ricoh MakerNote: shake reduction, lens lookup tables |

---

## Known Idiosyncrasies

ExifTool maintains a comprehensive list of vendor-specific bugs and edge
cases. Key examples:

| Vendor | Issue |
|--------|-------|
| **Canon 350D** (firmware 1.0.1) | Reports thumbnail size 10 bytes too long, causing data to run off the end of APP1 |
| **Canon 40D** (firmware 1.0.4) | Writes MakerNote IFD entry count one greater than actual, causing decoders to read garbage for the last entry |
| **Nikon Transfer** (v1.3) | Corrupts SubIFD information when processing NEF images |
| **Nikon** | Encrypts ColorBalance (version 200+) and LensData (version 0201+) using serial number + shutter count as keys |
| **Leica** | Most inconsistent vendor: 8+ distinct MakerNote formats across models, different signatures, different offset bases |
| **Sony** | MakerNote data references locations outside the MakerNote block; partial data loss when images rewritten by other software |
| **Samsung** | Some models write flat binary (non-IFD) MakerNote; others use standard IFD |

---

## Cross-References

- [Apple MakerNote](apple.md) -- iPhone/iPad computational photography metadata
- [Canon MakerNote](canon.md) -- Camera settings, lens info, serial numbers
- [Nikon MakerNote](nikon.md) -- Lens data, VR info, encrypted fields
- [Other Vendors](other-vendors.md) -- Fujifilm, Olympus, Minolta/Sony, Pentax
- [EXIF MakerNote overview](../exif/makernote.md) -- MakerNote in the EXIF standard context
- [ImageIO Property Keys](../imageio/property-keys.md) -- All `kCGImageProperty*` constants
- [EXIF Pitfalls](../exif/pitfalls.md) -- MakerNote offset corruption, 64 KB APP1 limit

### External References

- [ExifTool MakerNote Types](https://exiftool.org/makernote_types.html) -- Signatures for 6,940+ camera models from 106 manufacturers
- [ExifTool Idiosyncrasies](https://exiftool.org/idiosyncracies.html) -- Vendor-specific bugs and edge cases
- [Exiv2 MakerNote Documentation](https://exiv2.org/makernote.html) -- Format specifications, automatic detection
- [MakerNote Archive](http://justsolve.archiveteam.org/wiki/MakerNote) -- Archive Team format documentation
- [Nikon NEF Format](http://lclevy.free.fr/nef/) -- Laurent Clevy's reverse-engineered NEF specification
