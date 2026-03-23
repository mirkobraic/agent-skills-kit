# WebP Format Reference

WebP is a modern image format developed by Google, using a RIFF-based
container to store images compressed with VP8 (lossy), VP8L (lossless), or
both. It supports animation, alpha transparency, and metadata (EXIF, XMP,
ICC). The format is now standardized as **RFC 9649** (IETF, 2024).

WebP is **read-only** in ImageIO (iOS 14.0+). Writing WebP requires
third-party libraries (e.g., libwebp).

---

## File Signature

```
52 49 46 46 XX XX XX XX 57 45 42 50
"RIFF"       [file size]  "WEBP"
```

Every WebP file begins with a 12-byte RIFF header identifying the container
and declaring the total file size.

---

## RIFF Container Structure

WebP files use the RIFF (Resource Interchange File Format) container.

### RIFF Header

| Field       | Bytes | Description                              |
|-------------|-------|------------------------------------------|
| Signature   | 4     | `"RIFF"` (ASCII)                         |
| File Size   | 4     | Total file size minus 8 (little-endian)  |
| Form Type   | 4     | `"WEBP"` (ASCII)                         |

### Chunk Format

Following the header, the file contains one or more **chunks**:

| Field       | Bytes | Description                              |
|-------------|-------|------------------------------------------|
| FourCC      | 4     | Chunk type identifier (e.g. `"VP8 "`)    |
| Chunk Size  | 4     | Size of chunk data (little-endian)       |
| Chunk Data  | N     | Padded to even byte boundary             |

If the chunk data is an odd number of bytes, a single padding byte (0x00) is
added after the data but is not included in the size field.

---

## File Format Variants

### Simple Format (Lossy)

For images without metadata, alpha, or animation -- just lossy VP8 data:

```
RIFF header (12 bytes)
  VP8  chunk       Lossy compressed image data (VP8 bitstream)
```

### Simple Format (Lossless)

For lossless images without metadata or animation:

```
RIFF header (12 bytes)
  VP8L chunk       Lossless compressed image data (VP8L bitstream)
```

### Extended Format (VP8X)

For images with any combination of ICC profile, alpha, EXIF, XMP, or
animation:

```
RIFF header (12 bytes)
  VP8X chunk       Extended features flags and canvas dimensions
  [ICCP chunk]     ICC color profile (optional, before image data)
  [ANIM chunk]     Animation parameters (optional)
  [ANMF chunk]*    Animation frames (one per frame)
    [ALPH chunk]     Alpha data for the frame (VP8 lossy only)
    VP8/VP8L chunk   Image data for the frame
  -- or for non-animated: --
  [ALPH chunk]     Alpha data (VP8 lossy only)
  VP8/VP8L chunk   Image data
  [EXIF chunk]     EXIF metadata (optional, after image data)
  [XMP  chunk]     XMP metadata (optional, after EXIF)
```

---

## VP8X -- Extended Format Chunk

The VP8X chunk declares which optional features are present. It must be the
first chunk after the RIFF header in an extended format file.

| Field         | Bits | Description                              |
|---------------|------|------------------------------------------|
| Reserved      | 2    | Must be 0                                |
| ICC profile   | 1    | File has ICCP chunk                      |
| Alpha         | 1    | File has alpha channel data              |
| EXIF          | 1    | File has EXIF chunk                      |
| XMP           | 1    | File has XMP chunk                       |
| Animation     | 1    | File has ANIM/ANMF chunks               |
| Reserved      | 25   | Must be 0                                |
| Canvas Width  | 24   | Canvas width minus 1 (max 16383)         |
| Canvas Height | 24   | Canvas height minus 1 (max 16383)        |

Total VP8X chunk data: 10 bytes.

---

## Image Data Chunks

### VP8 -- Lossy Image Data

Contains image data compressed with the VP8 video codec (intra-frame mode
only). VP8 is based on block prediction and DCT transform, similar to H.264
intra coding. The compressed data is a single VP8 key frame.

- Color space: YCbCr (converted from RGB)
- Block size: 4x4 and 16x16 macroblocks
- Prediction modes: DC, horizontal, vertical, TrueMotion
- Quality: configurable (0-100, mapped to quantization parameter)

### VP8L -- Lossless Image Data

Contains image data compressed with the VP8L lossless codec, which uses a
series of transforms followed by entropy coding:

1. **Predictor transform** -- spatial prediction from neighboring pixels
2. **Color transform** -- decorrelation of color channels
3. **Subtract green transform** -- reduces redundancy in G channel
4. **Color indexing transform** -- palette for images with few colors

VP8L always operates on ARGB data (alpha is included natively), so a
separate ALPH chunk is not needed.

### ALPH -- Alpha Channel

For lossy VP8 images that need transparency, the alpha channel is stored
separately in an ALPH chunk (VP8 operates on YCbCr without alpha).

| Field          | Bits | Description                          |
|----------------|------|--------------------------------------|
| Reserved       | 2    | Must be 0                            |
| Preprocessing  | 2    | 0 = None, 1 = Level reduction       |
| Filtering      | 2    | 0 = None, 1 = Horizontal, 2 = Vertical, 3 = Gradient |
| Compression    | 2    | 0 = Uncompressed, 1 = Lossless (VP8L)|
| Alpha data     | N    | Alpha channel pixel values           |

VP8L includes alpha natively (ARGB), so ALPH chunks are only used with
lossy VP8 images.

---

## Metadata Chunks

### ICCP -- ICC Color Profile

Contains a full ICC color profile. Must appear before any image data chunks.
At most one ICCP chunk per file.

```
"ICCP"          FourCC (4 bytes)
[Size]          4 bytes (chunk data size, little-endian)
[ICC data]      Raw ICC profile bytes
```

### EXIF -- EXIF Metadata

Contains EXIF data. Must appear after all image data chunks.

```
"EXIF"          FourCC (4 bytes)
[Size]          4 bytes (chunk data size, little-endian)
[EXIF data]     Exif\0\0 + TIFF header + IFD entries
```

**Important:** Per RFC 9649, the EXIF chunk may start with the `"Exif\0\0"`
prefix (JPEG-style), followed by the TIFF byte order mark and IFD structure.
This is different from HEIF (which uses a 4-byte offset prefix) and PNG eXIf
(which starts directly with the TIFF header).

### XMP -- XMP Metadata

Contains XMP data as a UTF-8 encoded RDF/XML packet. Must appear after EXIF
(if both are present).

```
"XMP "          FourCC (4 bytes, note trailing space)
[Size]          4 bytes (chunk data size, little-endian)
[XMP data]      UTF-8 RDF/XML packet
```

The FourCC is `"XMP "` (with a trailing space to make exactly 4 bytes).

---

## Animation

### ANIM -- Animation Parameters

Global animation control. At most one per file.

| Field              | Bytes | Description                          |
|--------------------|-------|--------------------------------------|
| Background Color   | 4     | Default background color (BGRA)      |
| Loop Count         | 2     | 0 = infinite, N = play N times       |

### ANMF -- Animation Frame

One per frame. Contains frame position, dimensions, timing, and embedded
image data (ALPH + VP8/VP8L sub-chunks).

| Field              | Bytes | Description                              |
|--------------------|-------|------------------------------------------|
| Frame X            | 3     | X offset divided by 2 (multiply by 2 for pixels) |
| Frame Y            | 3     | Y offset divided by 2 (multiply by 2 for pixels) |
| Frame Width        | 3     | Width minus 1 (add 1 for pixels)         |
| Frame Height       | 3     | Height minus 1 (add 1 for pixels)        |
| Duration           | 3     | Frame duration in milliseconds           |
| Reserved           | 6 bits| Must be 0                                |
| Blending           | 1 bit | 0 = alpha-blend, 1 = overwrite           |
| Disposal           | 1 bit | 0 = do not dispose, 1 = dispose to background |
| Frame Data         | N     | ALPH + VP8/VP8L for this frame           |

Note: Frame offsets and dimensions use compact 3-byte fields. Offsets are
stored as half-values (multiply by 2) to enable even alignment while saving
bytes.

---

## Chunk Ordering Rules (RFC 9649)

The specification requires this ordering for all reconstruction-related chunks:

**Extended non-animated:**
1. VP8X
2. ICCP (if present) -- before image data
3. ALPH (if lossy + alpha)
4. VP8 or VP8L
5. EXIF (if present) -- after image data
6. XMP (if present) -- after EXIF

**Extended animated:**
1. VP8X
2. ICCP (if present)
3. ANIM
4. ANMF frames (each containing ALPH + VP8/VP8L)
5. EXIF (if present)
6. XMP (if present)

Unknown chunks may appear between known chunks but must not interfere with
the required ordering of reconstruction chunks.

---

## Metadata Capacity Summary

| Standard   | Supported | Mechanism          | Notes                              |
|------------|-----------|--------------------|------------------------------------|
| **EXIF**   | Yes       | EXIF chunk         | Full EXIF IFD structure            |
| **XMP**    | Yes       | XMP chunk          | Full XMP RDF/XML packet            |
| **IPTC IIM** | No     | --                  | Use XMP `Iptc4xmpCore` instead     |
| **ICC**    | Yes       | ICCP chunk         | Full ICC profile                   |
| **GPS**    | Yes       | GPS IFD within EXIF| Via EXIF EXIF chunk                |

**WebP metadata in ImageIO:** Apple does not explicitly document the full
extent of metadata support for WebP in ImageIO. EXIF and GPS properties from
WebP files may be exposed through the standard property dictionaries, but
this should be verified on the target OS version at runtime.

---

## ImageIO Keys: `kCGImagePropertyWebPDictionary`

Available since iOS 14.0.

| Key                                        | Type     | Purpose                        |
|--------------------------------------------|----------|--------------------------------|
| `kCGImagePropertyWebPLoopCount`            | CFNumber | Animation loop count           |
| `kCGImagePropertyWebPDelayTime`            | CFNumber | Frame delay (seconds, clamped) |
| `kCGImagePropertyWebPUnclampedDelayTime`   | CFNumber | True frame delay               |
| `kCGImagePropertyWebPFrameInfoArray`       | CFArray  | Frame information array        |
| `kCGImagePropertyWebPCanvasPixelWidth`     | CFNumber | Canvas width in pixels         |
| `kCGImagePropertyWebPCanvasPixelHeight`    | CFNumber | Canvas height in pixels        |

The WebP dictionary keys mirror the pattern from GIF and APNG: loop count,
delay time, unclamped delay, canvas size, and frame info array.
Format-specific codec properties (VP8 quality, lossless flag) are not exposed.

---

## ImageIO Support Details

| Feature               | Status                                      |
|-----------------------|---------------------------------------------|
| Read support          | iOS 14.0+ / macOS 11.0+                    |
| Write support         | **Not supported** in ImageIO                |
| Animated WebP read    | iOS 14.0+ (multi-image `CGImageSource`)     |
| EXIF metadata read    | Likely supported; verify at runtime         |
| XMP metadata read     | Likely supported; verify at runtime         |
| ICC profile read      | Supported                                   |
| GPS data read         | Likely supported (via EXIF); verify         |
| Lossless metadata edit| Not supported (read-only format)            |

ImageIO uses a hardware-accelerated codec for WebP decoding, which is
significantly faster than the CPU-based libwebp. However, some valid WebP
files (especially edge cases with unusual VP8 features) may fail to decode
on certain OS versions.

---

## Format Comparison: WebP vs Alternatives

| Property       | WebP         | JPEG         | PNG          | AVIF         | HEIC         |
|----------------|--------------|--------------|--------------|--------------|--------------|
| Lossy          | Yes (VP8)    | Yes          | No           | Yes (AV1)    | Yes (HEVC)   |
| Lossless       | Yes (VP8L)   | No           | Yes          | Yes (AV1)    | No           |
| Alpha          | Yes          | No           | Yes          | Yes          | Yes          |
| Animation      | Yes          | No           | Yes (APNG)   | Yes (AVIS)   | Yes (HEICS)  |
| EXIF           | Yes          | Yes          | Limited      | Yes          | Yes          |
| XMP            | Yes          | Yes          | Yes          | Yes          | Yes          |
| ICC            | Yes          | Yes          | Yes          | Yes          | Yes          |
| Max dimensions | 16383x16383  | 65535x65535  | ~2 billion   | Varies       | 16384x16384  |
| ImageIO write  | No           | Yes          | Yes          | Uncertain    | Yes          |
| iOS read       | 14.0+        | 4.0+         | 4.0+         | 16.0+        | 11.0+        |
| Royalty-free   | Yes          | Yes          | Yes          | Yes          | No           |

---

## Key Characteristics for iOS Development

| Property              | Value                                          |
|-----------------------|------------------------------------------------|
| UTI                   | `org.webmproject.webp`                         |
| ImageIO Read          | iOS 14.0+                                      |
| ImageIO Write         | **Not supported**                              |
| ImageIO Dictionary    | `kCGImagePropertyWebPDictionary`               |
| Metadata Standards    | EXIF, XMP, ICC (verify at runtime)             |
| Lossless Meta Edit    | No (read-only format in ImageIO)               |
| Color Depth           | 8-bit per channel                              |
| Color Models          | RGB (YCbCr for VP8, ARGB for VP8L)             |
| Alpha Channel         | Yes (ALPH chunk for VP8, native for VP8L)      |
| Animation             | Yes (ANIM/ANMF chunks)                         |
| Compression           | Lossy (VP8) and/or Lossless (VP8L)             |
| Max Dimensions        | 16,383 x 16,383 pixels                         |

---

## Common Gotchas

1. **Read-only in ImageIO** -- You cannot create WebP files using
   `CGImageDestination`. Use libwebp or a third-party wrapper (SDWebImage,
   Kingfisher) for encoding.

2. **Metadata support uncertainty** -- Apple does not publish a detailed
   metadata capability matrix for WebP. Test EXIF/GPS/XMP access on your
   target OS version at runtime.

3. **Canvas size limits** -- WebP limits canvas dimensions to 16,383 x 16,383
   pixels (VP8X uses 24-bit values minus 1). Images exceeding this cannot
   be stored in WebP.

4. **Animated WebP performance** -- Large animated WebP files may decode
   slowly on older devices, despite hardware acceleration. Consider file size
   and frame count when choosing animated WebP over GIF/APNG.

5. **No lossless metadata editing** -- Since WebP is read-only in ImageIO,
   metadata cannot be modified through Apple's APIs. To modify WebP metadata,
   use libwebp's mux API.

6. **EXIF chunk format** -- The WebP EXIF chunk may include the `"Exif\0\0"`
   prefix (JPEG-style). This differs from HEIF (4-byte offset prefix) and
   PNG eXIf (no prefix).

7. **VP8L always includes alpha** -- VP8L encodes ARGB, meaning lossless
   WebP files always have an alpha channel even if the source image was
   opaque. This can cause unexpected behavior if you check `hasAlpha`.

---

## Cross-References

- **EXIF in WebP:** `references/exif/technical-structure.md` (format embedding)
- **WebP animation API:** `references/imageio/cgimagesource.md` (animation section)
- **AVIF (similar modern format):** `references/formats/other-formats.md` (AVIF section)
- **ImageIO format support:** `references/imageio/supported-formats.md`
- **All WebP keys:** `references/imageio/property-keys.md` (WebP Dictionary)
