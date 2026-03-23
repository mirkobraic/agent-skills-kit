# PNG Format Reference

PNG (Portable Network Graphics) is a lossless raster image format defined by
ISO/IEC 15948 and W3C Recommendation (Fourth Edition). It uses a chunk-based
structure that supports text metadata, ICC profiles, XMP (via iTXt), and
(since the PNG 1.5 extensions) native EXIF data via the eXIf chunk.

PNG does not natively support IPTC IIM. The primary metadata path for PNG is
**XMP via iTXt chunks** and **ICC via iCCP chunks**.

---

## File Signature

```
89 50 4E 47 0D 0A 1A 0A
```

The 8-byte signature serves multiple purposes:

| Byte(s)    | Value        | Purpose                                |
|------------|--------------|----------------------------------------|
| `89`       | High bit set | Detects systems that clear bit 7       |
| `50 4E 47` | `"PNG"`      | ASCII identification                   |
| `0D 0A`    | CR LF        | Detects DOS/Windows line ending conversion |
| `1A`       | Ctrl-Z       | Stops DOS `TYPE` display               |
| `0A`       | LF           | Detects Unix line ending conversion    |

---

## Chunk Structure

Every PNG chunk follows this layout:

| Field     | Bytes | Description                                    |
|-----------|-------|------------------------------------------------|
| Length    | 4     | Data length (big-endian, max 2^31 - 1)         |
| Type      | 4     | ASCII chunk type code (e.g. `IHDR`, `tEXt`)    |
| Data      | N     | Chunk data (length bytes)                       |
| CRC       | 4     | CRC-32 over type + data (not length)           |

**Chunk type naming convention** -- each letter's case is significant:

| Byte Position | Uppercase Meaning | Lowercase Meaning       |
|---------------|-------------------|-------------------------|
| Byte 1, bit 5 | **Critical**      | **Ancillary**           |
| Byte 2, bit 5 | **Public**        | **Private**             |
| Byte 3, bit 5 | Reserved          | (reserved, must be uppercase) |
| Byte 4, bit 5 | **Unsafe to copy**| **Safe to copy**        |

This means: `IHDR` is critical + public, `tEXt` is ancillary + public +
safe-to-copy, `iCCP` is ancillary + public + unsafe-to-copy.

---

## Chunk Ordering

```
PNG Signature (8 bytes)
IHDR                        -- MUST be first chunk
  [cHRM, gAMA, iCCP, sBIT, sRGB]  -- before PLTE and IDAT
  [PLTE]                    -- palette (required for color type 3)
  [bKGD, hIST, tRNS]       -- after PLTE, before IDAT
  [pHYs, sPLT]             -- before IDAT
  [eXIf]                    -- anywhere between IHDR and IEND (not between IDATs)
  [tEXt, zTXt, iTXt]       -- anywhere between IHDR and IEND
  [tIME]                    -- anywhere between IHDR and IEND
IDAT (one or more)          -- MUST be consecutive
  [tEXt, zTXt, iTXt]       -- may also appear after IDAT
IEND                        -- MUST be last chunk
```

---

## Critical Chunks

These chunks are required for correct image reconstruction.

### IHDR -- Image Header

Must be the first chunk. Exactly one per file.

| Field              | Bytes | Values                                      |
|--------------------|-------|---------------------------------------------|
| Width              | 4     | Image width in pixels (1 to 2^31 - 1)      |
| Height             | 4     | Image height in pixels (1 to 2^31 - 1)     |
| Bit Depth          | 1     | 1, 2, 4, 8, or 16                          |
| Color Type         | 1     | See table below                              |
| Compression Method | 1     | 0 (deflate/inflate only)                    |
| Filter Method      | 1     | 0 (adaptive filtering with 5 filter types)  |
| Interlace Method   | 1     | 0 = None, 1 = Adam7                         |

**Color Type and Allowed Bit Depths:**

| Color Type | Name           | Channels | Allowed Bit Depths     |
|------------|----------------|----------|------------------------|
| 0          | Grayscale      | 1        | 1, 2, 4, 8, 16        |
| 2          | RGB            | 3        | 8, 16                  |
| 3          | Indexed (Palette)| 1      | 1, 2, 4, 8            |
| 4          | Grayscale+Alpha| 2        | 8, 16                  |
| 6          | RGBA           | 4        | 8, 16                  |

### PLTE -- Palette

Required for color type 3, optional for types 2 and 6 (as suggested
quantization). Contains 1-256 entries of 3 bytes each (R, G, B).

### IDAT -- Image Data

Contains the compressed (zlib/deflate) filtered image data. Multiple IDAT
chunks must be consecutive. A decoder concatenates all IDAT data and
decompresses as a single stream.

### IEND -- Image End

Must be the last chunk. Contains no data (length = 0). Marks the end of the
PNG datastream.

---

## Metadata Chunks

### tEXt -- Uncompressed Text

Stores a single keyword-value pair as Latin-1 (ISO 8859-1) text. Multiple
tEXt chunks may appear.

```
Keyword (1-79 bytes, Latin-1, case-sensitive)
Null separator (1 byte, 0x00)
Text string (Latin-1, no null terminator)
```

### zTXt -- Compressed Text

Same semantics as tEXt but the text value is zlib-compressed. Preferred for
large text blocks to reduce file size.

```
Keyword (1-79 bytes, Latin-1)
Null separator (1 byte, 0x00)
Compression method (1 byte, always 0 = deflate)
Compressed text (zlib-compressed Latin-1 data)
```

### iTXt -- International Text

Supports **UTF-8** text and language tagging. This is the chunk type used for
XMP metadata embedding.

```
Keyword (1-79 bytes, Latin-1)
Null separator (1 byte, 0x00)
Compression flag (1 byte: 0 = uncompressed, 1 = compressed)
Compression method (1 byte: 0 = deflate)
Language tag (BCP 47 string, e.g. "en", "ja")
Null separator (1 byte, 0x00)
Translated keyword (UTF-8)
Null separator (1 byte, 0x00)
Text (UTF-8, optionally zlib-compressed if compression flag = 1)
```

### Standard Text Keywords

The PNG specification defines these standard keywords:

| Keyword         | Purpose                    | ImageIO Key                          |
|-----------------|----------------------------|--------------------------------------|
| `Title`         | Short title                | `kCGImagePropertyPNGTitle`           |
| `Author`        | Creator name               | `kCGImagePropertyPNGAuthor`          |
| `Description`   | Image description          | `kCGImagePropertyPNGDescription`     |
| `Copyright`     | Copyright notice           | `kCGImagePropertyPNGCopyright`       |
| `Creation Time` | Date of original creation  | `kCGImagePropertyPNGCreationTime`    |
| `Software`      | Software used to create    | `kCGImagePropertyPNGSoftware`        |
| `Disclaimer`    | Legal disclaimer           | `kCGImagePropertyPNGDisclaimer`      |
| `Warning`       | Content warning            | `kCGImagePropertyPNGWarning`         |
| `Source`        | Device or originator       | `kCGImagePropertyPNGSource`          |
| `Comment`       | Miscellaneous comment      | `kCGImagePropertyPNGComment`         |

### XMP in PNG

XMP metadata is stored in an **iTXt chunk** with the keyword
`"XML:com.adobe.xmp"`. The text payload is the complete XMP RDF/XML packet
encoded as UTF-8. The language tag is typically empty, and the compression
flag is typically 0 (uncompressed).

```
Keyword:          "XML:com.adobe.xmp"
Null separator:   0x00
Compression flag: 0x00 (uncompressed)
Compression method: 0x00
Language tag:     "" (empty)
Null separator:   0x00
Translated keyword: "" (empty)
Null separator:   0x00
Text:             <complete XMP RDF/XML packet, UTF-8>
```

Unlike JPEG, there is no 64 KB segment limit -- PNG chunks can hold up to
2^31 - 1 bytes, so Extended XMP splitting is **unnecessary** for PNG.

### iCCP -- ICC Color Profile

Embeds an ICC color profile. Must appear before PLTE and IDAT. At most one
iCCP chunk per file.

```
Profile name (1-79 bytes, Latin-1)
Null separator (1 byte, 0x00)
Compression method (1 byte, always 0 = deflate)
Compressed profile (zlib-compressed ICC profile data)
```

If an iCCP chunk is present, an sRGB chunk **should not** appear (they are
mutually exclusive per the PNG specification). If both are present, iCCP
takes precedence.

### eXIf -- EXIF Data

Registered as a PNG extension chunk in 2017 (PNG Extensions 1.5.0, ratified
by the PNG Development Group). Provides native EXIF embedding.

```
eXIf chunk data = raw EXIF/TIFF structure (no JPEG preamble)
```

Key differences from JPEG EXIF:
- The six-byte JPEG-specific preamble (`"Exif\0\0"`) is **not** included
- The chunk data begins directly with the TIFF byte order mark (`II` or `MM`)
- Maximum size: 2^31 - 1 bytes (PNG chunk limit, far beyond JPEG's 64 KB)
- Only one eXIf chunk is allowed per PNG file
- May appear anywhere between IHDR and IEND (but not between IDAT chunks)

**ImageIO support:** ImageIO can read EXIF data from PNG files. On older
systems, some tools embed EXIF data in non-standard `tEXt` or `zTXt` chunks
with the keyword `"Raw profile type exif"` (a legacy practice that predates
the official eXIf chunk).

---

## Other Ancillary Chunks

### Color and Display

| Chunk  | Purpose                                         | ImageIO Key                              |
|--------|-------------------------------------------------|------------------------------------------|
| `gAMA` | Image gamma (encoded as gamma * 100,000)       | `kCGImagePropertyPNGGamma`               |
| `cHRM` | Primary chromaticities and white point (CIE xy)| `kCGImagePropertyPNGChromaticities`      |
| `sRGB` | sRGB rendering intent (0-3)                     | `kCGImagePropertyPNGsRGBIntent`          |
| `sBIT` | Significant bits per original channel           | --                                        |

**sRGB Intent Values:**

| Value | Rendering Intent          |
|-------|---------------------------|
| 0     | Perceptual                |
| 1     | Relative colorimetric     |
| 2     | Saturation                |
| 3     | Absolute colorimetric     |

### Physical Dimensions

| Chunk  | Purpose                                        | ImageIO Keys                             |
|--------|------------------------------------------------|------------------------------------------|
| `pHYs` | Pixel aspect ratio / physical dimensions       | `kCGImagePropertyPNGXPixelsPerMeter`, `kCGImagePropertyPNGYPixelsPerMeter` |

The pHYs chunk stores pixels per **meter** (not DPI). To convert:
`DPI = pixels_per_meter * 0.0254`.

### Transparency

| Chunk  | Purpose                                        | ImageIO Key                              |
|--------|------------------------------------------------|------------------------------------------|
| `tRNS` | Transparency for palette/grayscale/RGB         | `kCGImagePropertyPNGTransparency`        |

For color types 0 and 2 (grayscale and RGB), tRNS defines a single
transparent color value. For color type 3 (indexed), it provides per-palette
alpha values.

### Time

| Chunk  | Purpose                                        | ImageIO Key                              |
|--------|------------------------------------------------|------------------------------------------|
| `tIME` | Last modification time (UTC, 7 bytes)          | `kCGImagePropertyPNGModificationTime`    |

Format: year (2 bytes), month, day, hour, minute, second (1 byte each).

---

## Animation: APNG

APNG (Animated Portable Network Graphics) extends PNG with three additional
chunk types. APNG files remain valid PNG files -- decoders that do not
understand APNG display the default (first) image, gracefully ignoring the
animation chunks.

Supported by ImageIO since iOS 13.0 via `CGAnimateImageAtURLWithBlock`.

### APNG Chunks

| Chunk  | Full Name          | Purpose                                         |
|--------|--------------------|-------------------------------------------------|
| `acTL` | Animation Control  | Total frame count and loop count                |
| `fcTL` | Frame Control      | Per-frame: dimensions, position, timing, disposal, blending |
| `fdAT` | Frame Data         | Compressed pixel data for subsequent frames     |

### acTL -- Animation Control

Must appear before the first IDAT chunk to signal that this is an APNG file.
Exactly one per file.

| Field      | Bytes | Description                          |
|------------|-------|--------------------------------------|
| num_frames | 4     | Total number of frames               |
| num_plays  | 4     | Loop count (0 = infinite)            |

### fcTL -- Frame Control

Precedes each frame's image data. Fixed data length of 26 bytes.

| Field           | Bytes | Description                              |
|-----------------|-------|------------------------------------------|
| sequence_number | 4     | Sequence number (0-based, incrementing)  |
| width           | 4     | Frame width in pixels                    |
| height          | 4     | Frame height in pixels                   |
| x_offset        | 4     | X position on the canvas                 |
| y_offset        | 4     | Y position on the canvas                 |
| delay_num       | 2     | Frame delay numerator                    |
| delay_den       | 2     | Frame delay denominator (0 defaults to 100) |
| dispose_op      | 1     | Disposal method                          |
| blend_op        | 1     | Blending method                          |

**Frame delay** is `delay_num / delay_den` seconds. If `delay_den` is 0, it
defaults to 100 (so `delay_num` is in hundredths of a second).

**Disposal operations:**

| Value | Name                       | Behavior                                   |
|-------|----------------------------|--------------------------------------------|
| 0     | APNG_DISPOSE_OP_NONE       | Frame remains; next draws over it          |
| 1     | APNG_DISPOSE_OP_BACKGROUND | Clear frame area to fully transparent black|
| 2     | APNG_DISPOSE_OP_PREVIOUS   | Restore to state before this frame         |

**Blending operations:**

| Value | Name                       | Behavior                                   |
|-------|----------------------------|--------------------------------------------|
| 0     | APNG_BLEND_OP_SOURCE       | Overwrite (replace all channels)           |
| 1     | APNG_BLEND_OP_OVER         | Alpha compositing (Porter-Duff over)       |

### fdAT -- Frame Data

Same structure as IDAT but with a 4-byte sequence number prefix. The remaining
bytes are zlib-compressed pixel data for the frame. Multiple fdAT chunks per
frame are allowed (concatenated before decompression).

```
[sequence_number: 4 bytes] [compressed frame data: N bytes]
```

### Sequence Numbering

The first fcTL must have sequence_number 0. All subsequent fcTL and fdAT
chunks must use sequential numbers with no gaps or duplicates. This shared
sequence enables recovery of correct frame ordering even if a PNG-unaware
editor reorders chunks.

### ImageIO APNG Keys

| Key                                        | Type     | Purpose                        |
|--------------------------------------------|----------|--------------------------------|
| `kCGImagePropertyAPNGLoopCount`            | CFNumber | Loop count (0 = infinite)      |
| `kCGImagePropertyAPNGDelayTime`            | CFNumber | Frame delay (seconds, clamped) |
| `kCGImagePropertyAPNGUnclampedDelayTime`   | CFNumber | True frame delay               |
| `kCGImagePropertyAPNGFrameInfoArray`       | CFArray  | Per-frame info                 |
| `kCGImagePropertyAPNGCanvasPixelWidth`     | CFNumber | Canvas width                   |
| `kCGImagePropertyAPNGCanvasPixelHeight`    | CFNumber | Canvas height                  |

---

## Metadata Capacity Summary

| Standard   | Supported | Mechanism                        | Notes                           |
|------------|-----------|----------------------------------|---------------------------------|
| **EXIF**   | Limited   | eXIf chunk (PNG 1.5+, 2017)     | Not universally supported yet   |
| **XMP**    | Yes       | iTXt chunk (`XML:com.adobe.xmp`)| **Primary metadata path** for PNG |
| **IPTC IIM** | No     | --                                | Use XMP `Iptc4xmpCore` instead  |
| **ICC**    | Yes       | iCCP chunk (zlib-compressed)     | Full ICC profile support        |
| **GPS**    | Via XMP/eXIf | XMP `exif:` namespace or eXIf| No dedicated GPS mechanism      |

PNG's primary metadata path is XMP via iTXt. For editorial metadata (title,
description, keywords, copyright), use XMP with `Iptc4xmpCore` and `dc:`
(Dublin Core) namespaces.

---

## Lossless Metadata Editing

PNG supports lossless metadata editing via `CGImageDestinationCopyImageSource`
(iOS 7.0+ / macOS 10.8+). Since PNG metadata chunks are independent of the
compressed pixel data (IDAT), metadata chunks can be added, modified, or
removed without decompressing or recompressing the image data.

```swift
let source = CGImageSourceCreateWithURL(inputURL as CFURL, nil)!
let destination = CGImageDestinationCreateWithURL(
    outputURL as CFURL, kUTTypePNG, 1, nil)!

let metadata: [CFString: Any] = [
    kCGImageDestinationMetadata: updatedMetadata,
    kCGImageDestinationMergeMetadata: true
]

var error: Unmanaged<CFError>?
CGImageDestinationCopyImageSource(
    destination, source, metadata as CFDictionary, &error)
```

---

## ImageIO Keys: `kCGImagePropertyPNGDictionary`

Available since iOS 4.0.

| Key                                        | Type         | Chunk Source | Purpose                    |
|--------------------------------------------|--------------|-------------|----------------------------|
| `kCGImagePropertyPNGGamma`                 | CFNumber     | gAMA        | Gamma value                |
| `kCGImagePropertyPNGInterlaceType`         | CFNumber     | IHDR        | Interlace method (0/1)     |
| `kCGImagePropertyPNGChromaticities`        | CFDictionary | cHRM        | Chromaticity values        |
| `kCGImagePropertyPNGCompressionFilter`     | CFNumber     | --          | Compression filter hint    |
| `kCGImagePropertyPNGAuthor`                | CFString     | tEXt        | Author                     |
| `kCGImagePropertyPNGCopyright`             | CFString     | tEXt        | Copyright                  |
| `kCGImagePropertyPNGCreationTime`          | CFString     | tEXt        | Creation time              |
| `kCGImagePropertyPNGDescription`           | CFString     | tEXt        | Description                |
| `kCGImagePropertyPNGModificationTime`      | CFString     | tIME        | Modification time          |
| `kCGImagePropertyPNGSoftware`              | CFString     | tEXt        | Software                   |
| `kCGImagePropertyPNGTitle`                 | CFString     | tEXt        | Title                      |
| `kCGImagePropertyPNGsRGBIntent`            | CFNumber     | sRGB        | sRGB rendering intent (0-3)|
| `kCGImagePropertyPNGTransparency`          | CFArray      | tRNS        | Transparency info          |
| `kCGImagePropertyPNGComment`               | CFString     | tEXt        | Comment                    |
| `kCGImagePropertyPNGDisclaimer`            | CFString     | tEXt        | Disclaimer                 |
| `kCGImagePropertyPNGWarning`               | CFString     | tEXt        | Warning                    |
| `kCGImagePropertyPNGSource`                | CFString     | tEXt        | Source                     |
| `kCGImagePropertyPNGXPixelsPerMeter`       | CFNumber     | pHYs        | X pixels per meter         |
| `kCGImagePropertyPNGYPixelsPerMeter`       | CFNumber     | pHYs        | Y pixels per meter         |

---

## Key Characteristics for iOS Development

| Property              | Value                                          |
|-----------------------|------------------------------------------------|
| UTI                   | `public.png`                                   |
| ImageIO Read          | iOS 4.0+                                       |
| ImageIO Write         | iOS 4.0+                                       |
| ImageIO Dictionary    | `kCGImagePropertyPNGDictionary`                |
| Metadata Standards    | XMP (iTXt), ICC (iCCP), EXIF (eXIf, limited)  |
| Lossless Meta Edit    | Yes (`CGImageDestinationCopyImageSource`)       |
| Color Depth           | 1, 2, 4, 8, or 16 bits per channel            |
| Color Models          | Grayscale, RGB, Indexed (palette), + Alpha     |
| Alpha Channel         | Yes (types 4 and 6, or via tRNS)              |
| Animation             | Yes (APNG, iOS 13.0+)                          |
| Compression           | Lossless only (deflate/inflate)                |
| Max Dimensions        | 2^31 - 1 pixels per side                       |

---

## Common Gotchas

1. **No IPTC IIM support** -- PNG has no mechanism for IPTC IIM records. Use
   XMP namespaces (`Iptc4xmpCore`, `Iptc4xmpExt`, `dc:`) for editorial
   metadata.

2. **eXIf chunk adoption** -- The eXIf chunk is relatively new (2017). Not all
   tools and libraries support it. Some tools embed EXIF in a non-standard
   `tEXt` or `zTXt` chunk with the keyword `"Raw profile type exif"`.

3. **sRGB vs iCCP conflict** -- The PNG spec says sRGB and iCCP should not
   both appear. If both are present, iCCP takes precedence. Some tools
   write both, which can cause warnings.

4. **Text encoding** -- tEXt and zTXt use Latin-1 (ISO 8859-1). For UTF-8
   text, use iTXt. This matters for non-ASCII characters in author names,
   descriptions, etc.

5. **Gamma correction** -- The gAMA chunk affects how the image is displayed.
   If absent, viewers typically assume sRGB gamma (~2.2). Incorrect gamma
   values cause washed-out or too-dark images. Many tools strip or ignore
   the gAMA chunk.

6. **pHYs is pixels per meter** -- Not DPI. Convert: `DPI = ppm * 0.0254`.
   Setting incorrect pHYs values causes wrong print dimensions.

---

## Cross-References

- **XMP metadata:** `references/xmp/` (XMP standard reference)
- **ICC profiles:** `references/icc/` (color profiles reference)
- **EXIF in PNG:** `references/exif/technical-structure.md` (format embedding)
- **APNG animation API:** `references/imageio/cgimagesource.md` (animation)
- **Lossless editing API:** `references/imageio/cgimagedestination.md`
- **ImageIO format support:** `references/imageio/supported-formats.md`
- **All PNG keys:** `references/imageio/property-keys.md` (PNG Dictionary)
