# HEIF / HEIC / HEICS Format Reference

HEIF (High Efficiency Image File Format, ISO/IEC 23008-12) is a container
format built on the ISO Base Media File Format (ISOBMFF, ISO/IEC 14496-12).
Apple adopted HEIF in iOS 11 (2017) as the default capture format, using the
HEVC (H.265) codec variant branded as **HEIC**.

HEIF supports EXIF, XMP, and ICC profiles natively. It does **not** support
IPTC IIM -- use XMP namespaces (`Iptc4xmpCore`, `Iptc4xmpExt`) for editorial
metadata. HEIF is also the container for auxiliary images (depth maps, gain
maps, segmentation mattes), image sequences (Live Photos, bursts), and
spatial photos.

**Critical limitation:** HEIF does not support lossless metadata editing via
`CGImageDestinationCopyImageSource`. Every metadata change requires
re-encoding the image.

---

## ISOBMFF Foundation

HEIF files use the box-based structure defined by ISOBMFF (the same container
format used by MP4/MOV video files). Each box has:

```
[Size: 4 bytes, big-endian] [Type: 4 bytes, FourCC] [Data: Size - 8 bytes]
```

If Size is 1, an 8-byte extended size field follows the type (for boxes > 4 GB).
If Size is 0, the box extends to the end of the file.

### Top-Level Box Hierarchy

```
ftyp        File Type Box -- brands and version compatibility
meta        Meta Box -- the primary container for image items and metadata
  hdlr        Handler Box (handler_type = 'pict' for still images)
  pitm        Primary Item Box -- identifies which item is the main image
  iloc        Item Location Box -- byte ranges for each item in mdat
  iinf        Item Information Box -- item count, types, descriptions
    infe        Item Info Entry (one per item: type, content_type, name)
  iprp        Item Properties Box
    ipco        Item Property Container -- shared property definitions
    ipma        Item Property Association -- links properties to items
  iref        Item Reference Box -- relationships between items
    cdsc        Content Description reference (metadata -> image)
    auxl        Auxiliary reference (aux image -> primary image)
    thmb        Thumbnail reference
    dimg        Derived image reference
  idat        Item Data Box (optional, for small inline items)
mdat        Media Data Box -- actual coded image data, EXIF bytes, XMP bytes
```

For image sequences (HEICS), a `moov` box with timed tracks replaces or
supplements the item-based `meta` box structure.

---

## File Brands (ftyp Box)

The `ftyp` box declares which HEIF profiles the file conforms to. It contains
a major brand, minor version, and a list of compatible brands.

| Brand   | Description                              | File Extension | Codec   |
|---------|------------------------------------------|----------------|---------|
| `mif1`  | HEIF structural brand (still images)     | .heif          | Any     |
| `msf1`  | HEIF structural brand (sequences)        | .heif          | Any     |
| `heic`  | HEVC-coded still image                   | .heic          | HEVC    |
| `heix`  | HEVC-coded still image (extended)        | .heic          | HEVC    |
| `hevc`  | HEVC-coded sequence                      | .heics         | HEVC    |
| `hevx`  | HEVC-coded sequence (extended)           | .heics         | HEVC    |
| `avif`  | AV1-coded still image                    | .avif          | AV1     |
| `avis`  | AV1-coded sequence                       | .avif          | AV1     |
| `miaf`  | MIAF (Multi-Image Application Format)    | various        | Various |

Apple devices produce files with `heic` (still) and `hevc` (sequence) brands.
The compatible brands list typically includes `mif1` and `miaf`.

---

## Item Properties (ipco/ipma)

The `iprp` box system connects item IDs (via `ipma`) to shared property
definitions (in `ipco`). This is how image characteristics are associated
with specific images in the file.

### Key Property Types in ipco

| Property Box | FourCC | Purpose                                  |
|-------------|--------|------------------------------------------|
| `ispe`      | ispe   | Image Spatial Extent (width x height)    |
| `colr`      | colr   | Color information (ICC profile or CICP)  |
| `pixi`      | pixi   | Pixel information (bits per channel)     |
| `hvcC`      | hvcC   | HEVC decoder configuration record        |
| `av1C`      | av1C   | AV1 decoder configuration record (AVIF) |
| `clap`      | clap   | Clean aperture (crop)                    |
| `irot`      | irot   | Image rotation (0, 90, 180, 270 degrees) |
| `imir`      | imir   | Image mirror (horizontal/vertical)       |
| `rloc`      | rloc   | Relative location                        |
| `auxC`      | auxC   | Auxiliary type property (depth, matte)   |

---

## Metadata Storage

### EXIF Data

EXIF metadata is stored as a separate item of type `Exif` in the `meta` box.
The item's data is located via `iloc` and consists of:

```
[Exif header offset: 4 bytes, big-endian, typically 0x00000000]
[TIFF header: 'II' or 'MM' + 0x002A + IFD0 offset]
[IFD entries: IFD0, ExifIFD, GPS IFD, Interop IFD, etc.]
```

The 4-byte Exif header offset field precedes the TIFF structure. This is
different from:
- **JPEG:** Uses `"Exif\0\0"` (6 bytes) in APP1
- **WebP:** May start with `"Exif\0\0"` (6 bytes) in EXIF chunk (per RFC 9649)
- **PNG eXIf:** No prefix at all (starts directly with TIFF header)

EXIF data is linked to the primary image item via an `iref` box with reference
type `cdsc` (content description).

### XMP Data

XMP metadata is stored as an item with content type `application/rdf+xml`
(declared in the `infe` entry). The actual RDF/XML packet is stored in `mdat`
and referenced by `iloc`.

Like EXIF, the XMP item is associated with the primary image via a `cdsc`
reference in the `iref` box.

Because HEIF uses ISOBMFF, there is **no 64 KB segment limit** on XMP data
(unlike JPEG APP1). Large XMP packets can be stored without splitting.

### ICC Profile -- colr Box

ICC profiles are stored in a `colr` (Colour Information) box within the item
properties (`ipco`). The `colr` box supports two color specification types:

| Type   | colour_type | Description                                  |
|--------|-------------|----------------------------------------------|
| `nclx` | nclx        | CICP (Coding-Independent Code Points) -- colour primaries, transfer characteristics, matrix coefficients, full-range flag |
| `prof` | prof        | Full ICC profile data (raw bytes)            |

**Apple's approach:** HEIC files from Apple devices typically use `nclx` for
standard color spaces (sRGB, Display P3) because CICP encoding is more
compact than a full ICC profile. A full ICC profile via `prof` is embedded
when the color space cannot be represented by CICP values.

The `colr` box is an item property associated with image items via `ipma`.
Multiple colr boxes can coexist (e.g., one `nclx` and one `prof`).

---

## Auxiliary Images

One of HEIF's most powerful features is native support for **auxiliary
images** -- supplementary images linked to a primary image that provide
additional data channels.

### Types of Auxiliary Data in Apple's HEIC

| Auxiliary Type                          | Purpose                    | iOS     | ImageIO Constant                                      |
|-----------------------------------------|----------------------------|---------|-------------------------------------------------------|
| Depth Map                               | Per-pixel depth values     | 11.0+   | `kCGImageAuxiliaryDataTypeDepth`                      |
| Disparity Map                           | Stereo disparity           | 11.0+   | `kCGImageAuxiliaryDataTypeDisparity`                  |
| Portrait Effects Matte                  | Person segmentation mask   | 12.0+   | `kCGImageAuxiliaryDataTypePortraitEffectsMatte`       |
| Semantic Segmentation (Skin)            | Skin segmentation          | 13.0+   | `kCGImageAuxiliaryDataTypeSemanticSegmentationSkinMatte` |
| Semantic Segmentation (Hair)            | Hair segmentation          | 13.0+   | `kCGImageAuxiliaryDataTypeSemanticSegmentationHairMatte` |
| Semantic Segmentation (Teeth)           | Teeth segmentation         | 13.0+   | `kCGImageAuxiliaryDataTypeSemanticSegmentationTeethMatte` |
| Semantic Segmentation (Glasses)         | Glasses segmentation       | 15.0+   | `kCGImageAuxiliaryDataTypeSemanticSegmentationGlassesMatte` |
| HDR Gain Map (Apple)                    | SDR-to-HDR gain values     | 14.1+   | `kCGImageAuxiliaryDataTypeHDRGainMap`                 |
| HDR Gain Map (ISO 21496-1)             | Standard HDR gain map      | 18.0+   | `kCGImageAuxiliaryDataTypeISOGainMap`                 |

### How Auxiliary Images Are Stored

Auxiliary images are stored as separate items in the `meta` box with their own:
- `ispe` property (dimensions, which may differ from the primary image)
- `colr` property (color space)
- `pixi` property (bit depth)
- `auxC` property (declares the auxiliary type URN)
- Coded data in `mdat`

They are linked to the primary image via `auxl` (auxiliary) references in `iref`.

### Accessing Auxiliary Data in ImageIO

Auxiliary data uses a **separate API** from the property dictionary system:

```swift
// Read depth map
let depthData = CGImageSourceCopyAuxiliaryDataInfoAtIndex(
    source, 0, kCGImageAuxiliaryDataTypeDepth)

// Write auxiliary data
CGImageDestinationAddAuxiliaryDataInfo(
    destination, kCGImageAuxiliaryDataTypeDepth, depthInfo)
```

See `references/imageio/auxiliary-data.md` for the complete API reference.

---

## Image Sequences (HEICS)

HEIF supports multi-image storage for animations and sequences.

### Use Cases

- **Burst photos** -- Multiple images captured in rapid succession
- **Live Photos** -- Still image + short video clip
- **Animations** -- Frame sequences with timing information

### Storage Model

Sequences use the `moov`/`trak` structure from ISOBMFF (the same timed media
structure used by MP4 video files) rather than the item-based `meta` box.
Each frame has timing information encoded in the track's sample table.

**Live Photos caveat:** Apple Live Photos store the still image as a HEIC
file and the video portion as a separate .mov file; they are linked via a
shared asset identifier (content identifier) in the Photos framework, not
within a single HEICS container.

### ImageIO HEICS Dictionary Keys

Accessed via `kCGImagePropertyHEICSDictionary` (iOS 13.0+):

| Key                                         | Type     | Purpose                      |
|---------------------------------------------|----------|------------------------------|
| `kCGImagePropertyHEICSLoopCount`            | CFNumber | Loop count (0 = infinite)    |
| `kCGImagePropertyHEICSDelayTime`            | CFNumber | Frame delay (seconds)        |
| `kCGImagePropertyHEICSUnclampedDelayTime`   | CFNumber | True frame delay             |
| `kCGImagePropertyHEICSFrameInfoArray`       | CFArray  | Per-frame info               |
| `kCGImagePropertyHEICSCanvasPixelWidth`     | CFNumber | Canvas width                 |
| `kCGImagePropertyHEICSCanvasPixelHeight`    | CFNumber | Canvas height                |

---

## Spatial Photos (iOS 18+)

iOS 18 introduced support for spatial photos captured by Apple Vision Pro and
iPhone 15 Pro/16 series. These are stored as HEIF files containing a stereo
pair of images (left eye and right eye).

Spatial photo metadata is accessed via `kCGImagePropertyGroups` (iOS 18+),
which describes the grouping of the stereo image pair. The group metadata
includes baseline distance, convergence, and other stereoscopic parameters.

---

## Derived Images

HEIF supports non-destructive editing through **derived images**. Editing
operations are stored as transformation properties rather than re-encoded
pixel data:

| Transform Property | FourCC | Description                              |
|--------------------|--------|------------------------------------------|
| `clap`             | clap   | Clean aperture (crop region)             |
| `irot`             | irot   | Rotation (90, 180, 270 degrees)          |
| `imir`             | imir   | Mirror (horizontal or vertical)          |
| `rloc`             | rloc   | Relative location (overlay positioning)  |

These transforms are applied at render time by the decoder, so the original
pixel data remains intact.

---

## No Lossless Metadata Editing

**HEIF/HEIC does not support lossless metadata editing via
`CGImageDestinationCopyImageSource`.**

Unlike JPEG, PNG, and TIFF (where metadata is stored in separate segments or
chunks), HEIF's ISOBMFF structure interleaves metadata locations with box
offsets. Modifying metadata requires rebuilding the box hierarchy and may
change offsets to image data. ImageIO requires full re-encoding:

```swift
// HEIC: metadata change requires re-encode
let destination = CGImageDestinationCreateWithURL(
    outputURL as CFURL, "public.heic" as CFString, 1, nil)!
let image = CGImageSourceCreateImageAtIndex(source, 0, nil)!
CGImageDestinationAddImage(destination, image, updatedProperties as CFDictionary)
CGImageDestinationFinalize(destination)
```

Every metadata edit involves a lossy re-compression cycle (unless using the
Photos framework `PHAsset`, which manages its own metadata layer separately
from the file).

**Hardware encoder requirement:** Creating a HEIC `CGImageDestination`
requires HEVC hardware encoder support. Devices without it (e.g., Macs
without T2 or Apple Silicon) will fail.

---

## Metadata Capacity Summary

| Standard   | Supported | Mechanism                        | Notes                                   |
|------------|-----------|----------------------------------|-----------------------------------------|
| **EXIF**   | Yes       | Exif item + `cdsc` reference     | Full EXIF IFD structure                 |
| **XMP**    | Yes       | mime item + `cdsc` reference     | No size limit (ISOBMFF box)            |
| **IPTC IIM** | No     | --                                | Use XMP `Iptc4xmpCore` instead          |
| **ICC**    | Yes       | `colr` box (prof or nclx)       | Full ICC profile or CICP code points   |
| **GPS**    | Yes       | GPS IFD within EXIF item         | Full GPS support via EXIF              |

---

## ImageIO Dictionaries

### `kCGImagePropertyHEIFDictionary` -- iOS 16.0+

HEIF container-level properties. Available as of iOS 16. Apple's documentation
for the specific keys is minimal.

### `kCGImagePropertyHEICSDictionary` -- iOS 13.0+

HEIF sequence properties (animation timing, loop count). See HEICS Keys table
above.

---

## Apple's HEIC Usage

| Feature                                       | HEIC Behavior                              |
|-----------------------------------------------|--------------------------------------------|
| Default capture format                        | iPhone 7+ (iOS 11+), "High Efficiency"     |
| Portrait mode depth                           | Depth map as auxiliary image                |
| Night mode                                    | CompositeImage EXIF tags (EXIF 2.32+)      |
| HDR (Smart HDR / Photographic Styles)         | Gain map as auxiliary image                 |
| ProRAW                                        | DNG format, not HEIC                       |
| Spatial photos                                | Stereo HEIF (Vision Pro, iPhone 15 Pro+)   |
| Live Photos                                   | Still: HEIC + Video: MOV (separate files)  |
| Burst mode                                    | Individual HEIC files                       |
| Cinematic Photos                              | Depth + disparity auxiliary images          |
| Typical file size (12 MP)                     | 1-3 MB (vs 3-8 MB JPEG equivalent)        |

---

## Key Characteristics for iOS Development

| Property              | Value                                          |
|-----------------------|------------------------------------------------|
| UTI (still)           | `public.heic`                                  |
| UTI (generic)         | `public.heif` (iOS 16+)                        |
| UTI (sequence)        | `public.heics`                                 |
| ImageIO Read          | iOS 11.0+                                      |
| ImageIO Write         | iOS 11.0+ (requires HEVC hardware encoder)     |
| Metadata Standards    | EXIF, XMP, ICC, GPS (no IPTC IIM)             |
| Lossless Meta Edit    | **No**                                         |
| Color Depth           | 8-bit or 10-bit per channel                    |
| Color Models          | RGB (YCbCr internally via HEVC)               |
| Alpha Channel         | Yes (via auxiliary alpha image)                |
| Animation             | Yes (HEICS)                                    |
| Compression           | Lossy (HEVC intra-frame)                       |
| Auxiliary Data        | Depth, disparity, mattes, gain maps           |
| Max Dimensions        | 16384 x 16384 (HEVC Level 6)                  |

---

## Common Gotchas

1. **No lossless metadata editing** -- Every metadata change re-encodes the
   image. Use the Photos framework (`PHAsset`) for metadata operations when
   possible, as it maintains its own metadata layer.

2. **Hardware encoder required** -- Creating a HEIC `CGImageDestination`
   requires HEVC hardware encoder support. Devices without it fail silently
   or return nil.

3. **IPTC IIM not supported** -- HEIF has no mechanism for IPTC IIM records.
   All editorial metadata must use XMP namespaces.

4. **Multiple images per file** -- A single HEIF file can contain multiple
   images (primary, thumbnail, auxiliary, derived). Use
   `kCGImagePropertyPrimaryImage` to identify the main image and
   `kCGImagePropertyImageCount` for the total count.

5. **Exif header offset** -- The EXIF payload in HEIF includes a 4-byte
   offset field before the TIFF header, which differs from JPEG's
   `"Exif\0\0"` prefix. Tools that parse EXIF must handle this correctly.

6. **CICP vs ICC** -- Apple prefers CICP (`nclx`) for standard color spaces
   in HEIC, which is more compact but may not be recognized by tools expecting
   a full ICC profile. When converting to JPEG, ensure the ICC profile is
   properly translated.

7. **File size estimation** -- HEIC files are typically 40-50% smaller than
   equivalent-quality JPEG, but re-encoding for metadata changes may produce
   slightly different file sizes.

---

## Cross-References

- **EXIF tags in HEIF:** `references/exif/technical-structure.md` (format embedding)
- **Auxiliary data API:** `references/imageio/auxiliary-data.md`
- **ImageIO writing patterns:** `references/imageio/cgimagedestination.md`
- **AVIF (same ISOBMFF base):** `references/formats/other-formats.md` (AVIF section)
- **ImageIO format support:** `references/imageio/supported-formats.md`
- **HEICS keys:** `references/imageio/property-keys.md` (HEICS Dictionary)
