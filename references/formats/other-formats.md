# Other Image Formats Reference

Formats with smaller ImageIO footprints: OpenEXR, TGA, 8BIM/PSD, CIFF,
AVIF/AVIS, and JPEG XL.

---

## OpenEXR

HDR raster format from Industrial Light & Magic, standard for VFX and
professional HDR imaging. Supports arbitrary channels (half/float/uint),
multiple compression methods, and multi-part files.

### ImageIO Support

| Feature        | Status                                      |
|----------------|---------------------------------------------|
| Read           | iOS 11.3+ / macOS 10.13.4+                 |
| Write          | iOS 11.3+ / macOS 10.13.4+                 |
| UTI            | `com.ilm.openexr-image`                     |
| HDR data       | Float pixel data preserved                  |

**ImageIO dictionary key:** `kCGImagePropertyOpenEXRAspectRatio` (pixel aspect ratio).
This is the only key ImageIO exposes. For full attribute access, use the OpenEXR C++ library.

### Metadata

OpenEXR has its own attribute system (owner, capDate, GPS, exposure, etc.)
that is **not** mapped to EXIF/XMP/IPTC. ICC is approximated via chromaticities.

---

## TGA (Truevision Targa)

Simple raster format (1984), still used in game dev and 3D pipelines.
Supports alpha, RLE compression, and color-mapped/true-color/grayscale modes.

### ImageIO Support

| Feature        | Status                                      |
|----------------|---------------------------------------------|
| Read           | iOS 14.0+ / macOS 11.0+                    |
| Write          | iOS 14.0+ / macOS 11.0+                    |
| UTI            | `com.truevision.tga-image`                  |
| Dictionary     | `kCGImagePropertyTGADictionary` (minimal keys) |

### Metadata

TGA supports **no standard metadata** (no EXIF, XMP, IPTC, ICC, or GPS).
TGA 2.0 Extension Area provides only basic fields: author, date, software.

---

## 8BIM / PSD (Adobe Photoshop)

Adobe's native layered format. "8BIM" refers to Adobe's Image Resource Block
signature, used within PSD files and in JPEG APP13 segments for IPTC metadata.

### Metadata in PSD

PSD supports **all major metadata standards** through 8BIM resource blocks:

| Standard  | 8BIM Resource ID | Notes                  |
|-----------|------------------|------------------------|
| EXIF      | 0x0422, 0x0423   | Full EXIF IFD data     |
| XMP       | 0x0424           | Full XMP RDF/XML       |
| IPTC IIM  | 0x0404           | Full IPTC IIM records  |
| ICC       | 0x040F           | Full ICC profile       |
| GPS       | Within EXIF      | GPS IFD in EXIF data   |

PSD is one of four formats supporting **lossless metadata editing** in
ImageIO (alongside JPEG, PNG, and TIFF).

### Key 8BIM Resource IDs

| ID   | Purpose                                        |
|------|------------------------------------------------|
| 1005 | Resolution info (DPI, units)                   |
| 1028 | **IPTC-IIM metadata**                          |
| 1039 | **ICC color profile**                          |
| 1058 | **EXIF data** (TIFF IFD0 + ExifIFD)           |
| 1060 | **XMP metadata** (full RDF/XML)                |
| 1061 | Caption digest (MD5 of IPTC caption)           |

### ImageIO Keys: `kCGImageProperty8BIMDictionary`

| Key                                    | Type    | Purpose           |
|----------------------------------------|---------|-------------------|
| `kCGImageProperty8BIMVersion`          | CFNumber| Photoshop version |
| `kCGImageProperty8BIMLayerNames`       | CFArray | Layer name strings|
| `kCGImageProperty8BIMLayerInfo`        | CFData  | Layer info binary |

### ImageIO Support

| Feature        | Status                                      |
|----------------|---------------------------------------------|
| Read           | iOS 4.0+                                    |
| Write          | iOS 4.0+                                    |
| UTI            | `com.adobe.photoshop-image`                 |
| Lossless edit  | Yes (`CGImageDestinationCopyImageSource`)   |
| All metadata   | EXIF, XMP, IPTC IIM, ICC, GPS              |

---

## CIFF (Canon Image File Format)

Canon's legacy RAW format used by early Canon cameras (2000–2004).
Superseded by CR2 (TIFF-based, 2004) and CR3 (ISOBMFF-based, 2018).

Uses a directory-based structure with relative offsets. File signature:
`"II"` + header + `"HEAPCCDR"`. Extensions: `.crw`, `.ciff`.

**Camera models:** Canon EOS D30, D60, 10D, 300D; PowerShot G1–G6, Pro1, S30–S70.

### ImageIO Support

| Feature        | Status                                      |
|----------------|---------------------------------------------|
| Read           | iOS 4.0+                                    |
| Write          | No (legacy format)                          |
| UTI            | Canon CRW UTI                               |
| Dictionary     | `kCGImagePropertyCIFFDictionary`             |
| EXIF metadata  | Yes (translated from CIFF tags)             |

---

## AVIF / AVIS (AV1 Image File Format)

Image format based on AV1 codec in HEIF container (ISOBMFF). Better
compression than JPEG/WebP at equivalent quality. Royalty-free (unlike HEIC).

| Property          | AVIF               | HEIC               |
|-------------------|--------------------|---------------------|
| Codec             | AV1                | HEVC (H.265)       |
| Royalty-free      | **Yes**            | No                  |
| iOS read support  | 16.0+              | 11.0+               |
| iOS write support | Uncertain          | 11.0+               |

### Metadata Support

| Standard   | Supported | Notes                        |
|------------|-----------|------------------------------|
| EXIF       | Yes       | Same mechanism as HEIF       |
| XMP        | Yes       | Same mechanism as HEIF       |
| IPTC IIM   | No        | Use XMP namespaces           |
| ICC        | Yes       | CICP preferred over ICC      |
| GPS        | Yes       | Via EXIF                     |

AVIF commonly uses **CICP** values (ITU-T H.273) rather than full ICC profiles.
Key primaries: 1 (BT.709/sRGB), 9 (BT.2020), 12 (Display P3).

### ImageIO Support

| Feature          | Status                                        |
|------------------|-----------------------------------------------|
| Read (still)     | iOS 16.0+ / macOS 13.0+                      |
| Read (sequence)  | iOS 16.0+ / macOS 13.0+                      |
| Write (still)    | Uncertain — verify at runtime                 |
| UTI (still)      | `public.avif`                                  |
| UTI (sequence)   | `public.avis`                                  |
| Dictionary       | `kCGImagePropertyAVISDictionary` (iOS 16.0+)  |
| Lossless edit    | No                                             |

---

## JPEG XL

Modern format designed as next-generation JPEG successor. Supports lossy and
lossless compression, progressive decoding, HDR, wide gamut, animation, and
**lossless JPEG recompression** (~20% smaller, bit-perfect reconstruction).

### Key Advantages

| Feature                  | JPEG XL | JPEG | WebP | AVIF | HEIC |
|--------------------------|---------|------|------|------|------|
| Lossless compression     | Yes     | No   | Yes  | Yes  | No   |
| Lossless JPEG transcode  | **Yes** | N/A  | No   | No   | No   |
| Progressive decode       | Yes     | Yes  | No   | No   | No   |
| HDR                      | 32-bit  | No   | No   | 12-bit | 10-bit |
| Royalty-free             | Yes     | Yes  | Yes  | Yes  | No   |

### Metadata

JPEG XL in ISOBMFF container supports EXIF (`Exif` box), XMP (`xml` box),
and ICC profiles (in codestream header). Metadata boxes can be
Brotli-compressed via `brob` wrappers.

### ImageIO Support

| Feature          | Status                                        |
|------------------|-----------------------------------------------|
| Read             | iOS 17.0+ / macOS 14.0+                      |
| Write            | Camera capture only (iPhone 16 series, in DNG wrapper) |
| UTI              | `public.jpeg-xl`                               |
| UTType constant  | `UTType.jpegxl` (iOS 18.2+; use UTI string before) |
| Dictionary       | None                                           |
| HDR decode       | Via `kCGImageSourceDecodeToHDR` (iOS 17+)     |
| Lossless edit    | No (read-only except camera write)            |

**iPhone 16 note:** JXL captures are wrapped in DNG, not standalone `.jxl` files.

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

## Metadata Capabilities

| Format   | EXIF | XMP      | IPTC IIM | ICC              | GPS              |
|----------|------|----------|----------|------------------|------------------|
| OpenEXR  | No   | Possible | No       | Via chromaticities | Custom attributes |
| TGA      | No   | No       | No       | No               | No               |
| PSD      | Yes  | Yes      | **Yes**  | Yes              | Yes              |
| CRW/CIFF | Yes  | No       | No       | No               | Possible         |
| AVIF     | Yes  | Yes      | No       | Yes (CICP/ICC)   | Yes              |
| AVIS     | Yes  | Yes      | No       | Yes (CICP/ICC)   | Yes              |
| JPEG XL  | Yes  | Yes      | No       | Yes              | Yes              |

PSD is the only format here with IPTC IIM support (alongside JPEG and TIFF globally).

---

## Cross-References

- **HEIF container (shared with AVIF):** `references/formats/heif.md`
- **DNG (shared RAW concepts, JXL compression):** `references/formats/dng-raw.md`
- **EXIF tags:** `references/exif/tag-reference.md`
- **ImageIO format support:** `references/imageio/supported-formats.md`
- **8BIM in JPEG APP13:** `references/formats/jpeg.md` (APP13 section)
- **All property keys:** `references/imageio/property-keys.md`
