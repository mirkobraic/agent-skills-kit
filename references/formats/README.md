# Format-Specific Image Metadata

> Part of [iOS Image Metadata Skill](../../SKILL.md) · [References Index](../README.md)

Reference documentation for image file formats supported by Apple's ImageIO
framework, focused on their container structure, metadata embedding mechanisms,
and format-specific ImageIO property keys.

These files cover **how each format stores and organizes data** -- not the
metadata content itself. For metadata standards (EXIF, XMP, IPTC, GPS, ICC),
see the dedicated standard references under `references/exif/`,
`references/xmp/`, `references/iptc/`, `references/gps/`, `references/tiff/`,
and `references/icc/`.

---

## Format Comparison Matrix

### Metadata Support

Which metadata standards can each format carry?

| Format        | EXIF     | XMP          | IPTC IIM | ICC          | GPS          | Lossless Meta Edit |
|---------------|----------|--------------|----------|--------------|--------------|---------------------|
| **JPEG**      | Yes      | Yes          | Yes      | Yes          | Yes          | **Yes**             |
| **TIFF**      | Yes      | Yes          | Yes      | Yes          | Yes          | **Yes**             |
| **PSD**       | Yes      | Yes          | Yes      | Yes          | Yes          | **Yes**             |
| **PNG**       | Limited (eXIf) | Yes (iTXt) | No | Yes (iCCP) | Via XMP/eXIf | **Yes**             |
| **HEIF/HEIC** | Yes      | Yes          | No       | Yes          | Yes          | No                  |
| **DNG**       | Yes      | Yes          | No       | Yes          | Yes          | No                  |
| **Other RAW** | Yes      | Sidecar      | No       | Yes          | Yes          | No (read-only)      |
| **WebP**      | Yes*     | Yes*         | No       | Yes          | Yes*         | No (read-only)      |
| **AVIF**      | Yes      | Yes          | No       | Yes          | Yes          | No                  |
| **JPEG XL**   | Yes      | Yes          | No       | Yes          | Yes          | No (read-only)      |
| **GIF**       | No       | No           | No       | No           | No           | No                  |
| **OpenEXR**   | No       | Possible     | No       | Custom       | Custom       | No                  |
| **TGA**       | No       | No           | No       | No           | No           | No                  |

\* WebP metadata support in ImageIO is not explicitly documented -- verify
EXIF/GPS behavior at runtime on target OS.

> **Key takeaway:** Only JPEG, TIFF, and PSD support all five metadata
> standards. Modern formats (HEIF, WebP, AVIF, JPEG XL) use EXIF and/or XMP.
> IPTC IIM is legacy -- use the XMP path (`Iptc4xmpCore`, `Iptc4xmpExt`) for
> new code.

### Container Architecture

| Format    | Container Type       | Marker/Chunk/Box Structure | Max Segment/Chunk Size |
|-----------|----------------------|---------------------------|------------------------|
| JPEG      | Marker segments      | `FF xx [len] [data]`      | 65,535 bytes           |
| PNG       | Chunk-based          | `[len][type][data][crc]`  | 2^31 - 1 bytes         |
| HEIF/HEIC | ISOBMFF box-based    | `[size][type][data]`      | Unlimited (64-bit ext) |
| GIF       | Block-based          | Sub-blocks (255 bytes max)| 255 bytes per sub-block|
| DNG       | TIFF IFD-based       | IFD entries + offsets     | 4 GB (or 16 EB BigTIFF)|
| WebP      | RIFF chunk-based     | `[fourcc][size][data]`    | ~4 GB per chunk        |
| AVIF      | ISOBMFF box-based    | Same as HEIF              | Unlimited              |
| JPEG XL   | JXL box-based        | `[size][type][data]`      | Unlimited              |
| PSD       | Section-based        | 8BIM resource blocks      | 4 GB per section       |
| OpenEXR   | Attribute + scanline | Header attrs + pixel data | No fixed limit         |
| TGA       | Fixed header + data  | 18-byte header + pixels   | 65,535 x 65,535 pixels |

### Compression Capabilities

| Format    | Lossy | Lossless | HDR (>8-bit) | Alpha | Animation |
|-----------|-------|----------|--------------|-------|-----------|
| JPEG      | Yes   | No*      | No           | No    | No        |
| PNG       | No    | Yes      | Yes (16-bit) | Yes   | Yes (APNG)|
| HEIF/HEIC | Yes   | Yes*****  | Yes (10-bit) | Yes   | Yes (HEICS)|
| GIF       | No    | Yes**    | No           | No*** | Yes       |
| DNG       | Yes   | Yes      | Yes (32-bit) | No    | No        |
| WebP      | Yes   | Yes      | No           | Yes   | Yes       |
| AVIF      | Yes   | Yes      | Yes (12-bit) | Yes   | Yes (AVIS)|
| JPEG XL   | Yes   | Yes      | Yes (32-bit) | Yes   | Yes       |
| PSD       | No    | Yes      | Yes (32-bit) | Yes   | No        |
| OpenEXR   | Both  | Both     | Yes (32-bit) | Yes   | No****    |
| TGA       | No    | Yes (RLE)| No           | Yes   | No        |

\* JPEG has a rarely-used lossless mode (SOF3).
\*\* GIF uses LZW, which is lossless for palette indices but limited to 256 colors.
\*\*\* GIF supports 1-bit transparency (one palette index), not true alpha.
\*\*\*\* OpenEXR supports multi-part files but not timed animation.
\*\*\*\*\* HEVC supports lossless coding, but Apple does not use it for camera capture.

---

## ImageIO Format Dictionaries

Each format has an ImageIO property dictionary for format-specific encoding
properties (not metadata content). These are accessed via
`CGImageSourceCopyPropertiesAtIndex` at the root dictionary level.

| Dictionary                             | Format           | iOS   | Key Count | Reference File     |
|----------------------------------------|------------------|-------|-----------|--------------------|
| `kCGImagePropertyJFIFDictionary`       | JPEG (JFIF)      | 4.0+  | 5         | `jpeg.md`          |
| `kCGImagePropertyPNGDictionary`        | PNG              | 4.0+  | 18+       | `png.md`           |
| `kCGImagePropertyGIFDictionary`        | GIF              | 4.0+  | 8         | `gif.md`           |
| `kCGImagePropertyDNGDictionary`        | DNG              | 4.0+  | 17        | `dng-raw.md`       |
| `kCGImagePropertyRawDictionary`        | Generic RAW      | 4.0+  | Minimal   | `dng-raw.md`       |
| `kCGImageProperty8BIMDictionary`       | Photoshop (8BIM) | 4.0+  | 3         | `other-formats.md` |
| `kCGImagePropertyCIFFDictionary`       | Canon CIFF       | 4.0+  | Minimal   | `other-formats.md` |
| `kCGImagePropertyOpenEXRDictionary`    | OpenEXR          | 11.3+ | 1         | `other-formats.md` |
| `kCGImagePropertyHEICSDictionary`      | HEIF sequences   | 13.0+ | 6         | `heif.md`          |
| `kCGImagePropertyTGADictionary`        | TGA              | 14.0+ | Minimal   | `other-formats.md` |
| `kCGImagePropertyWebPDictionary`       | WebP             | 14.0+ | 6         | `webp.md`          |
| `kCGImagePropertyHEIFDictionary`       | HEIF             | 16.0+ | Minimal   | `heif.md`          |
| `kCGImagePropertyAVISDictionary`       | AV1 Image Seq    | 16.0+ | Minimal   | `other-formats.md` |

---

## Animation Support

| Format          | Animated | ImageIO Read | Animate API | Reference     |
|-----------------|----------|--------------|-------------|---------------|
| GIF             | Yes      | iOS 4.0+     | iOS 13.0+   | `gif.md`      |
| APNG            | Yes      | iOS 13.0+    | iOS 13.0+   | `png.md`      |
| HEICS           | Yes      | iOS 13.0+    | Multi-image | `heif.md`     |
| WebP (animated) | Yes      | iOS 14.0+    | Multi-image | `webp.md`     |
| AVIS            | Yes      | iOS 16.0+    | Multi-image | `other-formats.md` |
| JPEG XL         | Yes      | iOS 17.0+    | TBD         | `other-formats.md` |

---

## Lossless Metadata Editing Support

Only four formats support lossless metadata operations via
`CGImageDestinationCopyImageSource`:

| Format | Why It Works                                          |
|--------|-------------------------------------------------------|
| JPEG   | Metadata in APP markers, separate from scan data      |
| PNG    | Metadata in ancillary chunks, separate from IDAT      |
| TIFF   | IFD-based structure allows metadata IFD updates       |
| PSD    | 8BIM resource blocks separate from image data section |

All other formats (HEIC, WebP, AVIF, GIF, DNG, RAW, OpenEXR, TGA, JPEG XL)
require re-encoding the image data to change metadata.

---

## File Index

| File               | Formats Covered                            |
|--------------------|--------------------------------------------|
| `jpeg.md`          | JPEG/JFIF -- marker structure, APP markers (APP0/APP1/APP2/APP13), EXIF 64 KB limit, Extended XMP, ICC multi-segment, lossless metadata editing, progressive encoding |
| `png.md`           | PNG -- chunk structure (critical + ancillary), tEXt/zTXt/iTXt metadata, XMP via iTXt, iCCP color profiles, eXIf EXIF chunk, APNG animation (acTL/fcTL/fdAT) |
| `heif.md`          | HEIF/HEIC/HEICS -- ISOBMFF box hierarchy (ftyp/meta/iloc/iprp/ipco/ipma), EXIF/XMP as items, colr box (ICC/CICP), auxiliary images (depth/matte/gain map), sequences, spatial photos, no lossless edit |
| `gif.md`           | GIF -- GIF87a/89a structure, Graphic Control Extension, disposal methods (0-3), NETSCAPE loop count, delay time clamping, LZW compression, zero metadata support |
| `dng-raw.md`       | DNG -- version history (1.0-1.7), TIFF/EP structure, color matrices, opcodes (14 types), camera profiles, depth maps, semantic masks, Apple ProRAW, generic RAW format support |
| `webp.md`          | WebP -- RIFF container, VP8/VP8L/VP8X variants, ICCP/EXIF/XMP chunks, ANIM/ANMF animation, chunk ordering (RFC 9649), read-only in ImageIO |
| `other-formats.md` | OpenEXR (HDR channels, compression), TGA (18-byte header, image types), 8BIM/PSD (resource blocks, full metadata), CIFF (Canon legacy), AVIF/AVIS (AV1+ISOBMFF, CICP), JPEG XL (container boxes, lossless JPEG transcode, Brotli metadata) |

---

## iOS Version Timeline

When each format gained ImageIO support:

| iOS Version | Formats Added                                                |
|-------------|--------------------------------------------------------------|
| 4.0         | JPEG, PNG, GIF, TIFF, BMP, ICO, JPEG 2000, PSD, DNG, RAW   |
| 11.0        | HEIC/HEIF read-write                                         |
| 11.3        | OpenEXR read-write                                           |
| 13.0        | HEICS (image sequences), APNG                                |
| 14.0        | WebP read, TGA read-write                                    |
| 16.0        | AVIF/AVIS read, HEIF dictionary, AVIS dictionary             |
| 17.0        | JPEG XL read                                                 |
| 18.0        | JPEG XL camera write (iPhone 16 only), ISO gain map          |

---

## Cross-References

### Metadata Standards (deep dives)
- **EXIF:** `references/exif/` -- tag reference, IFD structure, version history, pitfalls
- **XMP:** `references/xmp/` -- namespaces, embedding, custom metadata
- **IPTC:** `references/iptc/` -- IIM vs Core/Extension, XMP path
- **GPS:** `references/gps/` -- coordinate conventions, accuracy
- **TIFF:** `references/tiff/` -- IFD tags (make/model/orientation)
- **ICC:** `references/icc/` -- color profiles, color spaces

### ImageIO Framework
- **API reference:** `references/imageio/README.md`
- **All property keys:** `references/imageio/property-keys.md`
- **Format support table:** `references/imageio/supported-formats.md`
- **Reading API:** `references/imageio/cgimagesource.md`
- **Writing API:** `references/imageio/cgimagedestination.md`
- **Auxiliary data:** `references/imageio/auxiliary-data.md`
- **Common pitfalls:** `references/imageio/pitfalls.md`

### Related
- **Interoperability:** `references/interoperability/` -- MWG sync, cross-standard mapping
- **MakerNotes:** `references/makers/` -- Apple, Canon, Nikon vendor metadata
