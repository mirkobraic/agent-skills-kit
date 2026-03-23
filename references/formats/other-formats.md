# Other Image Formats Reference

This file covers image formats that have smaller ImageIO footprints or are less
commonly encountered in iOS development: OpenEXR, TGA, 8BIM/PSD, CIFF,
AVIF/AVIS, and JPEG XL.

---

## OpenEXR

OpenEXR is a high-dynamic-range (HDR) raster file format developed by
Industrial Light & Magic (ILM) and now maintained by the Academy Software
Foundation (ASWF). It is the standard format for visual effects, compositing,
and professional HDR imaging.

### File Signature

```
76 2F 31 01
```

### Format Structure

An OpenEXR file consists of two main parts:

1. **Magic number** (4 bytes): `76 2F 31 01`
2. **Version field** (4 bytes): Version number and feature flags
3. **Header(s)**: List of named, typed attributes (variable length)
4. **Offset table**: Scan line or tile offsets for random access
5. **Pixel data**: Compressed image data

For multi-part files (OpenEXR 2.0+), each part has its own header and pixel
data section.

### Version Field Flags

| Bit  | Name           | Purpose                                  |
|------|----------------|------------------------------------------|
| 0-7  | Version number | File format version (currently 2)        |
| 9    | Tiled          | Image is stored as tiles (vs scan lines) |
| 10   | Long names     | Attribute/channel names > 31 characters  |
| 11   | Non-image      | Contains deep data (per-pixel samples)   |
| 12   | Multi-part     | Multiple independent parts               |

### Channel Data Types

OpenEXR supports an arbitrary number of channels with mixed data types:

| Data Type | Name  | Size   | Range / Precision                    |
|-----------|-------|--------|--------------------------------------|
| HALF      | half  | 16-bit | ~6.1e-5 to 6.5e4 (10-bit mantissa, 5-bit exponent) |
| FLOAT     | float | 32-bit | Full IEEE 754 single precision       |
| UINT      | uint  | 32-bit | Unsigned integer (0 to 2^32 - 1)    |

**Standard channel names:**

| Channel | Purpose              | Notes                          |
|---------|----------------------|--------------------------------|
| `R`     | Red                  | Primary image                  |
| `G`     | Green                | Primary image                  |
| `B`     | Blue                 | Primary image                  |
| `A`     | Alpha                | Transparency                   |
| `Z`     | Depth                | Scene depth per pixel          |
| `N`     | Normal               | Surface normal data            |
| `V`     | Velocity             | Motion vectors                 |

Multi-part files use prefixed names (e.g., `diffuse.R`, `specular.G`,
`cryptomatte00.R`).

### Compression Methods

| Method   | Type     | Description                                          |
|----------|----------|------------------------------------------------------|
| NONE     | --       | No compression                                       |
| RLE      | Lossless | Run-length encoding                                  |
| ZIPS     | Lossless | Zlib deflate, one scan line per block                |
| ZIP      | Lossless | Zlib deflate, 16 scan lines per block                |
| PIZ      | Lossless | Wavelet + Huffman (best for grainy/noisy images)     |
| PXR24    | Lossy    | 32-bit float to 24-bit with zlib (lossless for half/uint) |
| B44      | Lossy    | Fixed-rate 4:4 block compression                    |
| B44A     | Lossy    | B44 with flat-area optimization                      |
| DWAA     | Lossy    | DCT-based, 32-scanline blocks                        |
| DWAB     | Lossy    | DCT-based, 256-scanline blocks                       |

PIZ is recommended for images with film grain or sensor noise (35-55%
compression ratio). ZIP is recommended for rendered images without grain.

### Standard Header Attributes

**Required attributes:**

| Attribute           | Type        | Purpose                        |
|---------------------|-------------|--------------------------------|
| `channels`          | chlist      | Channel names and types        |
| `compression`       | compression | Compression method             |
| `dataWindow`        | box2i       | Pixel data bounding box        |
| `displayWindow`     | box2i       | Display viewport               |
| `lineOrder`         | lineOrder   | Scan line storage order        |
| `pixelAspectRatio`  | float       | Pixel aspect ratio             |
| `screenWindowCenter`| v2f         | Screen window center           |
| `screenWindowWidth` | float       | Screen window width            |

**Optional metadata attributes:**

| Attribute           | Type           | Purpose                     |
|---------------------|----------------|-----------------------------|
| `owner`             | string         | Image owner / creator       |
| `comments`          | string         | Free-form comments          |
| `capDate`           | string         | Capture date/time           |
| `utcOffset`         | float          | UTC offset of capture time  |
| `longitude`         | float          | GPS longitude (degrees)     |
| `latitude`          | float          | GPS latitude (degrees)      |
| `altitude`          | float          | GPS altitude (meters)       |
| `focus`             | float          | Focus distance (meters)     |
| `expTime`           | float          | Exposure time (seconds)     |
| `aperture`          | float          | Lens aperture (f-number)    |
| `isoSpeed`          | float          | ISO sensitivity             |
| `chromaticities`    | chromaticities | CIE xy primaries/white point|
| `whiteLuminance`    | float          | White luminance (cd/m^2)    |
| `adoptedNeutral`    | v2f            | White balance neutral point |
| `renderingTransform`| string         | ACES rendering transform    |
| `lookModTransform`  | string         | ACES look modification      |

OpenEXR attributes are **not** mapped to EXIF/XMP/IPTC. They use their own
naming system with their own type system.

### ImageIO Support

| Feature        | Status                                      |
|----------------|---------------------------------------------|
| Read           | iOS 11.3+ / macOS 10.13.4+                 |
| Write          | iOS 11.3+ / macOS 10.13.4+                 |
| UTI            | `com.ilm.openexr-image`                     |
| HDR data       | Float pixel data preserved                  |
| XMP            | May be supported; verify at runtime         |
| ICC            | Via chromaticities attribute conversion      |

**ImageIO dictionary key:**

| Key                                        | Type     | Purpose          |
|--------------------------------------------|----------|------------------|
| `kCGImagePropertyOpenEXRAspectRatio`       | CFNumber | Pixel aspect ratio |

ImageIO exposes only `pixelAspectRatio`. For full attribute access (channels,
compression, custom attributes), use the OpenEXR C++ library directly.

---

## TGA (Truevision Targa)

TGA is a simple raster image format developed by Truevision (later Pinnacle
Systems) in 1984. It is still used in game development and 3D rendering
pipelines due to its simplicity, alpha channel support, and lack of patent
encumbrances.

### File Signature

TGA has no magic number at the beginning of the file. Version 2.0 files can
be identified by the footer signature `"TRUEVISION-XFILE.\0"` at the end of
the file (last 26 bytes).

### Format Structure

A TGA file has up to 5 areas:

1. **Header** (18 bytes, fixed)
2. **Image/Color Map Data** (variable)
3. **Developer Area** (optional, TGA 2.0)
4. **Extension Area** (optional, TGA 2.0)
5. **Footer** (26 bytes, TGA 2.0)

### Header Fields (18 Bytes)

| Field               | Bytes | Offset | Description                      |
|---------------------|-------|--------|----------------------------------|
| ID Length           | 1     | 0      | Length of Image ID field (0-255) |
| Color Map Type      | 1     | 1      | 0 = no map, 1 = has color map   |
| Image Type          | 1     | 2      | See image types below            |
| Color Map Origin    | 2     | 3      | First entry index (little-endian)|
| Color Map Length    | 2     | 5      | Number of entries                |
| Color Map Entry Size| 1     | 7      | Bits per entry (15, 16, 24, 32) |
| X Origin            | 2     | 8      | X coordinate of lower-left corner|
| Y Origin            | 2     | 10     | Y coordinate of lower-left corner|
| Width               | 2     | 12     | Image width in pixels            |
| Height              | 2     | 14     | Image height in pixels           |
| Pixel Depth         | 1     | 16     | Bits per pixel (8, 16, 24, 32)  |
| Image Descriptor    | 1     | 17     | Alpha bits (0-3), origin corner (4-5) |

All multi-byte values are **little-endian**.

### Image Types

| Type | Description                              | Compression |
|------|------------------------------------------|-------------|
| 0    | No image data                            | --          |
| 1    | Uncompressed color-mapped (palette)      | None        |
| 2    | Uncompressed true-color (RGB/RGBA)       | None        |
| 3    | Uncompressed grayscale                   | None        |
| 9    | RLE compressed color-mapped              | RLE         |
| 10   | RLE compressed true-color                | RLE         |
| 11   | RLE compressed grayscale                 | RLE         |

### TGA 2.0 Extension Area

TGA Version 2.0 (identified by a footer containing `"TRUEVISION-XFILE.\0"`)
adds an Extension Area with limited metadata:

| Field              | Size   | Description                              |
|--------------------|--------|------------------------------------------|
| Extension Size     | 2      | Always 495                               |
| Author Name        | 41     | Null-terminated string                   |
| Author Comments    | 324    | Four lines of 81 characters each         |
| Date/Time Stamp    | 12     | Month, day, year, hour, minute, second   |
| Job Name/ID        | 41     | Null-terminated string                   |
| Job Time           | 6      | Hours, minutes, seconds                  |
| Software ID        | 41     | Null-terminated string                   |
| Software Version   | 3      | Version number (x100) and letter         |
| Key Color          | 4      | Background color (ARGB)                  |
| Pixel Aspect Ratio | 4      | Width:Height numerator/denominator       |
| Gamma Value        | 4      | Gamma numerator/denominator              |
| Color Correction   | 4      | Offset to 256-entry correction table     |
| Postage Stamp      | 4      | Offset to thumbnail image                |
| Scan Line Table    | 4      | Offset to scan line offset table         |
| Alpha Type         | 1      | 0=none, 1=undefined, 2=retained, 3=premultiplied |

### Metadata Limitations

| Standard  | Supported | Notes                                  |
|-----------|-----------|----------------------------------------|
| EXIF      | No        | --                                     |
| XMP       | No        | --                                     |
| IPTC IIM  | No        | --                                     |
| ICC       | No        | No color management support            |
| GPS       | No        | --                                     |

TGA provides only the basic fields in the Extension Area (author, date,
software). No standard metadata system is supported.

### ImageIO Support

| Feature        | Status                                      |
|----------------|---------------------------------------------|
| Read           | iOS 14.0+ / macOS 11.0+                    |
| Write          | iOS 14.0+ / macOS 11.0+                    |
| UTI            | `com.truevision.tga-image`                  |
| Dictionary     | `kCGImagePropertyTGADictionary` (minimal keys) |

---

## 8BIM / PSD (Adobe Photoshop)

PSD (Photoshop Document) is Adobe's native layered image format. The "8BIM"
identifier refers to Adobe's Image Resource Block signature, used within PSD
files and also within JPEG APP13 segments for IPTC metadata.

### File Signature

```
38 42 50 53    "8BPS" (Photoshop signature)
```

### PSD File Structure

A PSD file contains 5 major sections in order:

**1. File Header (26 bytes)**

| Field          | Bytes | Description                              |
|----------------|-------|------------------------------------------|
| Signature      | 4     | `"8BPS"` (always)                        |
| Version        | 2     | 1 = PSD, 2 = PSB (large document format) |
| Reserved       | 6     | Must be zero                             |
| Channels       | 2     | Number of channels (1-56)                |
| Height         | 4     | Image height (1 to 30,000 for PSD; 1 to 300,000 for PSB) |
| Width          | 4     | Image width (same limits)                |
| Depth          | 2     | Bits per channel (1, 8, 16, or 32)      |
| Color Mode     | 2     | 0=Bitmap, 1=Grayscale, 2=Indexed, 3=RGB, 4=CMYK, 7=Multichannel, 8=Duotone, 9=Lab |

**2. Color Mode Data** (variable)
- Palette data for indexed color mode
- Duotone data for duotone mode

**3. Image Resources** (variable)
- Collection of 8BIM resource blocks

**4. Layer and Mask Information** (variable)
- Layer records, channel image data, masks, blending modes, effects

**5. Image Data** (variable)
- Composite (flattened) image pixel data
- Compression type + pixel data

### 8BIM Resource Block Structure

```
"8BIM"             Signature (4 bytes, almost always "8BIM")
[Resource ID]      2 bytes (identifies the resource type)
[Name]             Pascal string (padded to even byte boundary)
[Data Size]        4 bytes (size of resource data)
[Data]             Resource data (padded to even byte boundary)
```

Other observed signatures (rare): `"MeSa"` (ImageReady), `"PHUT"`
(PhotoDeluxe), `"AgHg"`, `"DCSR"`.

### Key 8BIM Resource IDs

| ID       | Hex    | Purpose                                     |
|----------|--------|---------------------------------------------|
| 1005     | 0x03ED | Resolution info (DPI, units)               |
| 1011     | 0x03F3 | Color halftoning information               |
| 1013     | 0x03F5 | Color transfer functions                    |
| 1024     | 0x0400 | Layer state information                     |
| 1028     | 0x0404 | **IPTC-IIM metadata** (the primary IPTC storage) |
| 1032     | 0x0408 | Grid and guides information                |
| 1036     | 0x040C | JPEG quality / thumbnail resource          |
| 1039     | 0x040F | **ICC color profile**                      |
| 1044     | 0x0414 | Document-specific IDs seed number          |
| 1049     | 0x0419 | Global altitude                            |
| 1050     | 0x041A | Slices resource                            |
| 1057     | 0x0421 | Version info                               |
| 1058     | 0x0422 | **EXIF data 1** (TIFF IFD0 + ExifIFD)     |
| 1059     | 0x0423 | **EXIF data 3** (additional EXIF)          |
| 1060     | 0x0424 | **XMP metadata** (full RDF/XML packet)     |
| 1061     | 0x0425 | Caption digest (MD5 of IPTC caption)       |
| 1062     | 0x0426 | Print scale                                |
| 1084     | 0x043C | Timeline information                       |
| 1085     | 0x043D | Sheet disclosure                           |

### Metadata in PSD

PSD supports all major metadata standards through 8BIM resource blocks:

| Standard  | Supported | 8BIM Resource ID          | Notes                  |
|-----------|-----------|---------------------------|------------------------|
| EXIF      | Yes       | 0x0422, 0x0423            | Full EXIF IFD data     |
| XMP       | Yes       | 0x0424                    | Full XMP RDF/XML       |
| IPTC IIM  | Yes       | 0x0404                    | Full IPTC IIM records  |
| ICC       | Yes       | 0x040F                    | Full ICC profile       |
| GPS       | Yes       | Within EXIF (0x0422)      | GPS IFD in EXIF data   |

PSD is one of the four formats that support **lossless metadata editing** in
ImageIO (alongside JPEG, PNG, and TIFF).

### ImageIO Keys: `kCGImageProperty8BIMDictionary`

| Key                                    | Type    | Purpose                    |
|----------------------------------------|---------|----------------------------|
| `kCGImageProperty8BIMVersion`          | CFNumber| Photoshop version          |
| `kCGImageProperty8BIMLayerNames`       | CFArray | Layer name strings         |
| `kCGImageProperty8BIMLayerInfo`        | CFData  | Layer info binary data     |

### ImageIO Support

| Feature        | Status                                      |
|----------------|---------------------------------------------|
| Read           | All platforms since iOS 4.0                 |
| Write          | All platforms since iOS 4.0                 |
| UTI            | `com.adobe.photoshop-image`                 |
| Lossless edit  | Yes (`CGImageDestinationCopyImageSource`)   |
| All metadata   | EXIF, XMP, IPTC IIM, ICC, GPS              |

---

## CIFF (Canon Image File Format)

CIFF is Canon's legacy RAW format used by early Canon digital cameras
(2000-2004). It was superseded by CR2 (TIFF-based, 2004) and later CR3
(ISOBMFF-based, 2018).

### File Signature

```
49 49 1A 00 00 00 48 45 41 50 43 43 44 52
"II" + header + "HEAPCCDR"
```

CRW files always begin with this 14-byte sequence. The `"II"` indicates
little-endian byte order.

### Format Structure

CIFF uses a directory-based structure conceptually similar to TIFF but with
a key improvement: **offsets are relative** to the start of each directory's
data block, not absolute from the file start. This makes the format more
robust when sections are moved or resized.

```
File Header
  Byte order: "II" (little-endian) or "MM" (big-endian)
  Header length (offset to root directory data block)
  Type/subtype identifier
  "HEAPCCDR" or "HEAPJPGM" signature (identifies CIFF variant)
Root Directory Block
  [Sub-directories (nested, recursive)]
  [Data values]
  Directory entries (10 bytes each, at end of block)
  Directory entry count (2 bytes)
```

### Directory Entry Format

| Field      | Bytes | Description                           |
|------------|-------|---------------------------------------|
| Tag        | 2     | Tag identifier (type + data location) |
| Size       | 4     | Data size in bytes                    |
| Offset     | 4     | Offset relative to directory data start |

For small values (< 8 bytes), the data is stored directly in the Size and
Offset fields (indicated by bit 14 of the Tag being set to 1 = `0x4000`).

### Tag Categories

CIFF tags are organized by type bits in the tag ID:

| Type Bits (15-13) | Data Type     |
|--------------------|---------------|
| 000                | BYTE or mixed |
| 001                | ASCII string  |
| 010                | SHORT (16-bit)|
| 011                | LONG (32-bit) |
| 100                | Mixed/struct  |
| 101-111            | Sub-directory |

### Metadata

CIFF stores camera settings, white balance, focal length, and other capture
data in its own proprietary tag format. Standard EXIF and TIFF metadata is
also typically present (read from the CIFF tags and translated to standard
IFD format by ImageIO).

### Camera Models Using CIFF

Canon EOS D30, D60, 10D, 300D (Digital Rebel/Kiss Digital), and PowerShot
models: G1, G2, G3, G5, G6, Pro1, Pro90 IS, S30, S40, S45, S50, S60, S70.

### ImageIO Support

| Feature        | Status                                      |
|----------------|---------------------------------------------|
| Read           | iOS 4.0+                                   |
| Write          | No (legacy format, superseded by CR2/CR3)  |
| UTI            | Canon CRW UTI                               |
| Dictionary     | `kCGImagePropertyCIFFDictionary`             |
| Extensions     | .crw, .ciff                                 |
| EXIF metadata  | Yes (translated from CIFF tags)             |

---

## AVIF / AVIS (AV1 Image File Format)

AVIF is an image format based on the AV1 video codec, stored in the HEIF
container (ISOBMFF). It provides better compression efficiency than JPEG and
WebP at equivalent quality. AVIS is the animated/sequence variant.

AVIF is developed by the Alliance for Open Media (AOMedia). The latest
specification is **AVIF v1.2.0** (2025).

### Relationship to HEIF

AVIF and HEIC share the same ISOBMFF container structure. The key difference
is the codec:

| Property          | AVIF               | HEIC               |
|-------------------|--------------------|---------------------|
| Codec             | AV1                | HEVC (H.265)       |
| Container         | ISOBMFF (HEIF)     | ISOBMFF (HEIF)     |
| File brand (ftyp) | `avif` / `avis`    | `heic` / `hevc`    |
| Royalty-free      | **Yes**            | No (HEVC patent pool) |
| iOS read support  | 16.0+              | 11.0+               |
| iOS write support | Uncertain          | 11.0+               |
| Max dimensions    | Varies by AV1 level| 16384 x 16384       |

### Box Structure

AVIF uses the same ISOBMFF box hierarchy as HEIF:

```
ftyp        brand: avif, mif1, miaf
meta
  hdlr        handler: pict
  pitm        primary item ID
  iloc        item locations (byte ranges in mdat)
  iinf        item information entries
  iprp
    ipco        properties: ispe (image size), colr (color), pixi (pixel info), av1C (AV1 config)
    ipma        property -> item associations
  iref        item references (cdsc for metadata, auxl for auxiliary)
mdat        AV1 coded data, EXIF bytes, XMP bytes
```

### Metadata Support

| Standard   | Supported | Mechanism                    | Notes                        |
|------------|-----------|------------------------------|------------------------------|
| **EXIF**   | Yes       | Exif item + cdsc reference   | Same mechanism as HEIF       |
| **XMP**    | Yes       | mime item + cdsc reference   | Same mechanism as HEIF       |
| **IPTC IIM** | No     | --                            | Use XMP namespaces           |
| **ICC**    | Yes       | colr box (prof or nclx)      | CICP preferred over ICC      |
| **GPS**    | Yes       | GPS IFD within EXIF item     | Via EXIF                     |

### Color Space Signaling (CICP)

AVIF commonly uses **CICP** (Coding-Independent Code Points, ITU-T H.273)
values in the `nclx` colr box rather than embedding full ICC profiles:

| CICP Parameter             | Common Values                                |
|----------------------------|----------------------------------------------|
| Colour Primaries           | 1 (BT.709/sRGB), 9 (BT.2020), 12 (Display P3) |
| Transfer Characteristics   | 1 (BT.709), 13 (sRGB), 16 (PQ/HDR10), 18 (HLG) |
| Matrix Coefficients        | 0 (Identity/RGB), 1 (BT.709), 9 (BT.2020)   |

### AVIF v1.2.0 Updates (2025)

- Strengthened conformance requirements
- Clarified mapping between AV1 bitstream metadata and file-level signaling
- Added **sample transforms** for higher bit depths (> AV1's native 12-bit)
- Updated references to latest HEIF, ISOBMFF, and MIAF specifications

### ImageIO Support

| Feature          | Status                                        |
|------------------|-----------------------------------------------|
| Read (still)     | iOS 16.0+ / macOS 13.0+                      |
| Read (sequence)  | iOS 16.0+ / macOS 13.0+                      |
| Write (still)    | Uncertain -- verify at runtime via `CGImageDestinationCopyTypeIdentifiers()` |
| Write (sequence) | Not supported                                 |
| UTI (still)      | `public.avif`                                  |
| UTI (sequence)   | `public.avis`                                  |
| Dictionary       | `kCGImagePropertyAVISDictionary` (iOS 16.0+)  |
| Lossless edit    | No                                             |

The `kCGImagePropertyAVISDictionary` likely mirrors the animation-related
keys from HEICS (loop count, delay time, frame info). Apple's documentation
is minimal.

---

## JPEG XL

JPEG XL (JXL) is a modern image format designed as a next-generation successor
to JPEG. It supports both lossy and lossless compression, progressive decoding,
HDR, wide gamut, animation, and a unique **lossless JPEG recompression**
feature. Apple added read support in iOS 17.

### File Signatures

JPEG XL has two possible file formats:

**Bare codestream:**
```
FF 0A    (2 bytes)
```

**ISOBMFF container:**
```
00 00 00 0C 4A 58 4C 20 0D 0A 87 0A
(12 bytes: box size + "JXL " + signature bytes)
```

### Key Features Comparison

| Feature                  | JPEG XL | JPEG    | WebP    | AVIF    | HEIC    |
|--------------------------|---------|---------|---------|---------|---------|
| Lossy compression        | Yes     | Yes     | Yes     | Yes     | Yes     |
| Lossless compression     | Yes     | No      | Yes     | Yes     | No      |
| Lossless JPEG transcode  | **Yes** | N/A     | No      | No      | No      |
| Progressive decode       | Yes     | Yes     | No      | No      | No      |
| Animation                | Yes     | No      | Yes     | Yes     | Yes     |
| HDR (> 8-bit)           | Yes (32-bit) | No | No      | Yes (12-bit) | Yes (10-bit) |
| Alpha channel           | Yes     | No      | Yes     | Yes     | Yes     |
| Wide gamut              | Yes     | Via ICC | Via ICC | Yes     | Yes     |
| EXIF                    | Yes     | Yes     | Yes     | Yes     | Yes     |
| XMP                     | Yes     | Yes     | Yes     | Yes     | Yes     |
| ICC                     | Yes     | Yes     | Yes     | Yes     | Yes     |
| Max bit depth           | 32      | 8       | 8       | 12+     | 10      |
| Royalty-free            | Yes     | Yes     | Yes     | Yes     | No      |

### Container Format

JPEG XL can exist in two forms:

**1. Bare codestream** (`.jxl`): Just the compressed image data with embedded
ICC profile and orientation. All information needed to render the image is in
the codestream.

**2. ISOBMFF container** (`.jxl`): Wraps the codestream in boxes, enabling
metadata storage:

```
JXL  box    JPEG XL file type signature
ftyp box    File type: brand 'jxl '
jxlc box    Complete JPEG XL codestream
  -- or --
jxlp box(es)  Partial codestream (split across multiple boxes)
[Exif box]    EXIF metadata (4-byte offset + TIFF structure)
[xml  box]    XMP metadata (UTF-8 RDF/XML)
[jumb box]    JUMBF (JPEG Universal Metadata Box Format)
[jbrd box]    JPEG reconstruction data (for lossless JPEG transcode)
[jxli box]    Frame index (for animation keyframes)
[brob box]    Brotli-compressed box (wraps any other box type)
```

### Metadata Boxes

| Box Type | FourCC | Purpose                                       |
|----------|--------|-----------------------------------------------|
| `jxlc`   | jxlc   | Complete JPEG XL codestream                   |
| `jxlp`   | jxlp   | Partial codestream (split across boxes)       |
| `Exif`   | Exif   | EXIF metadata (4-byte offset prefix + TIFF structure) |
| `xml `   | xml    | XMP metadata (UTF-8 RDF/XML)                  |
| `jumb`   | jumb   | JUMBF metadata (JPEG Universal Metadata Box)  |
| `brob`   | brob   | Brotli-compressed box (first 4 bytes = original box type) |
| `jbrd`   | jbrd   | JPEG reconstruction data                       |
| `jxli`   | jxli   | Frame index for animations                     |

**Brotli compression of metadata:** JPEG XL can Brotli-compress its metadata
boxes using `brob` wrappers, significantly reducing EXIF and XMP overhead.
The `brob` box starts with 4 bytes declaring the original box type, followed
by the Brotli-compressed data.

### Lossless JPEG Recompression

A unique JPEG XL feature: existing JPEG files can be **losslessly transcoded**
to JPEG XL, typically achieving ~20% additional size reduction. The original
JPEG can be bit-perfectly reconstructed from the JXL file using the `jbrd`
(JPEG bitstream reconstruction data) box.

This means:
- No quality loss whatsoever (identical JPEG bytes)
- ~20% smaller file size
- Can be reverted to JPEG at any time
- All original JPEG metadata is preserved

### Codestream Features

The codestream itself carries:
- ICC color profiles (Brotli-compressed within the codestream header)
- EXIF orientation (used for correct display without external metadata)
- Animation data (frame timing, blending modes)
- Image dimensions, bit depth, channel count

### ImageIO Support

| Feature          | Status                                        |
|------------------|-----------------------------------------------|
| Read             | iOS 17.0+ / macOS 14.0+                      |
| Write            | Camera capture only (iPhone 16 series, in DNG wrapper) |
| UTI              | `public.jpeg-xl`                               |
| UTType constant  | `UTType.jpegxl` (iOS 18.2+; use UTI string before) |
| Dictionary       | None (no `kCGImagePropertyJPEGXLDictionary`)  |
| HDR decode       | Via `kCGImageSourceDecodeToHDR` (iOS 17+)     |
| Lossless edit    | No (read-only in ImageIO except camera write) |

**iOS 17 note:** Use the UTI string `"public.jpeg-xl"` directly. The
`UTType.jpegxl` constant was not added until iOS 18.2.

**iPhone 16 capture:** iPhone 16 series can capture JPEG XL images, but they
are wrapped in a DNG container rather than standalone .jxl files. The JXL
data is the compressed image payload within DNG using `NewSubFileType` for
JXL (DNG 1.7).

---

## Format Support Summary

| Format   | Read    | Write   | UTI                         | Dictionary                          | Lossless Edit |
|----------|---------|---------|-----------------------------|-------------------------------------|---------------|
| OpenEXR  | 11.3+   | 11.3+   | `com.ilm.openexr-image`    | `kCGImagePropertyOpenEXRDictionary` | No            |
| TGA      | 14.0+   | 14.0+   | `com.truevision.tga-image`  | `kCGImagePropertyTGADictionary`     | No            |
| PSD      | 4.0+    | 4.0+    | `com.adobe.photoshop-image` | `kCGImageProperty8BIMDictionary`    | **Yes**       |
| CRW/CIFF | 4.0+   | No      | Canon CRW UTI               | `kCGImagePropertyCIFFDictionary`    | No            |
| AVIF     | 16.0+   | TBD     | `public.avif`               | `kCGImagePropertyAVISDictionary`    | No            |
| AVIS     | 16.0+   | No      | `public.avis`               | `kCGImagePropertyAVISDictionary`    | No            |
| JPEG XL  | 17.0+   | Limited | `public.jpeg-xl`            | None                                | No            |

---

## Metadata Capabilities Comparison

| Format   | EXIF | XMP      | IPTC IIM | ICC              | GPS              |
|----------|------|----------|----------|------------------|------------------|
| OpenEXR  | No   | Possible | No       | Via chromaticities | Custom attributes |
| TGA      | No   | No       | No       | No               | No               |
| PSD      | Yes  | Yes      | **Yes**  | Yes              | Yes              |
| CRW/CIFF | Yes  | No       | No       | No               | Possible         |
| AVIF     | Yes  | Yes      | No       | Yes (CICP/ICC)   | Yes              |
| AVIS     | Yes  | Yes      | No       | Yes (CICP/ICC)   | Yes              |
| JPEG XL  | Yes  | Yes      | No       | Yes              | Yes              |

PSD is notable as the only format in this group that supports IPTC IIM
(alongside JPEG and TIFF as the only three formats with IPTC IIM support).

---

## Cross-References

- **HEIF container (shared with AVIF):** `references/formats/heif.md`
- **DNG (shared RAW concepts, JXL compression):** `references/formats/dng-raw.md`
- **EXIF tags:** `references/exif/tag-reference.md`
- **ImageIO format support:** `references/imageio/supported-formats.md`
- **Auxiliary data:** `references/imageio/auxiliary-data.md`
- **8BIM in JPEG APP13:** `references/formats/jpeg.md` (APP13 section)
- **All property keys:** `references/imageio/property-keys.md`
