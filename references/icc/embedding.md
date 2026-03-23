# ICC Profile Embedding in Image Formats

ICC profiles are embedded directly in image files so that any application opening
the file can perform correct color management without external profile files.
Each image format has its own mechanism for carrying the ICC data.

The ICC mime type for standalone profile files is `application/vnd.iccprofile`.

---

## Per-Format Embedding

### JPEG -- APP2 Marker (`ICC_PROFILE`)

JPEG embeds ICC profiles in one or more **APP2 application data markers** with
the identifier string `"ICC_PROFILE\0"`.

**Structure of each APP2 segment:**

```
FF E2              -- APP2 marker
LL LL              -- Length (2 bytes, big-endian, includes itself but not marker)
49 43 43 5F 50 52  -- "ICC_PR"
4F 46 49 4C 45 00  -- "OFILE\0"  (12-byte identifier)
SS                 -- Sequence number (1-based, 1 byte)
NN                 -- Total number of chunks (1 byte)
[profile data]     -- Remaining bytes of this chunk
```

**Chunking for large profiles:**

JPEG markers have a maximum data length of **65,533 bytes** (64 KB minus 2 for
the length field). After subtracting the 14-byte overhead (12 for identifier +
1 sequence + 1 count), each chunk carries up to **65,519 bytes** of profile data.

- **Small profiles** (< 65,519 bytes): Single APP2 segment. Sequence = 1,
  Count = 1. This covers sRGB (~3 KB) and Display P3 profiles.
- **Large profiles** (> 65,519 bytes): Split across multiple APP2 segments.
  Sequence numbers 1..N, all with Count = N. Decoders must reassemble by
  sequence number, not by marker order.
- **Maximum profile size:** 255 chunks x 65,519 bytes = ~16.3 MB. This is
  sufficient for even the largest multi-channel CLUT profiles.

> **Reassembly note:** The ICC specification warns that JPEG markers may not
> appear in file order. Decoders should use the sequence number to reconstruct
> the profile, not assume consecutive APP2 markers are in order.

**Typical sizes in JPEG:**

| Profile | Embedded Size | Chunks Needed |
|---------|---------------|---------------|
| sRGB (built-in) | ~3 KB | 1 |
| Display P3 | ~500 bytes - 4 KB | 1 |
| Adobe RGB (1998) | ~560 bytes | 1 |
| CMYK output profile | 500 KB - 2 MB | 8-31 |

---

### PNG -- `iCCP` Chunk

PNG stores ICC profiles in a dedicated **`iCCP` chunk**, which contains the
profile in compressed form.

**Chunk structure:**

```
[4 bytes]  Length (of data, not including length/type/CRC)
69 43 43 50  "iCCP" -- chunk type
[1-79 bytes] Profile name (Latin-1, null-terminated)
00           Compression method (0 = zlib deflate; only method defined)
[variable]   Compressed ICC profile data (zlib)
[4 bytes]    CRC-32
```

**Key details:**

- The profile data is **zlib-compressed** (same as PNG image data), which
  typically reduces the embedded size by 50-80%.
- Only **one `iCCP` chunk** is allowed per PNG file.
- If an `iCCP` chunk is present, an `sRGB` chunk must NOT also be present
  (they are mutually exclusive per the PNG spec).
- PNG also supports an **`sRGB` chunk** (4 bytes) that signals the image
  uses the sRGB color space without embedding the full profile. The `sRGB`
  chunk contains a single byte indicating the rendering intent (0-3).
- A `gAMA` chunk and `cHRM` chunk can approximate the color space for
  renderers that ignore `iCCP`, but this is a fallback, not a replacement.

### PNG `cICP` Chunk (PNG Third Edition, 2024)

**PNG Third Edition** (W3C Recommendation, 2024) introduced the **`cICP`
chunk** for signaling color space via Coding-Independent Code Points (CICP),
matching the CICP system used in HEIF, AVIF, and JPEG XL.

**Chunk structure:**

```
[4 bytes]  Length (always 4 bytes of data)
63 49 43 50  "cICP" -- chunk type
PP           Colour Primaries (1 byte, ITU-T H.273)
TT           Transfer Characteristics (1 byte, ITU-T H.273)
MM           Matrix Coefficients (1 byte, ITU-T H.273)
FF           Video Full Range Flag (1 byte, 0 or 1)
[4 bytes]    CRC-32
```

The `cICP` chunk adds only **16 bytes total** to the file (4 length + 4 type +
4 data + 4 CRC), compared to hundreds or thousands of bytes for an `iCCP` chunk.

**Common CICP values for `cICP`:**

| Color Space | Primaries | Transfer | Matrix | Full Range |
|-------------|-----------|----------|--------|------------|
| sRGB | 1 | 13 | 0 | 1 |
| Display P3 | 12 | 13 | 0 | 1 |
| Rec. 2020 SDR | 9 | 14 | 0 | 1 |
| Rec. 2020 PQ (HDR) | 9 | 16 | 0 | 1 |
| Rec. 2020 HLG (HDR) | 9 | 18 | 0 | 1 |

**Browser support (as of early 2026):** Chrome/Edge, Firefox, Safari, Servo,
and Ladybird all support `cICP`. Adobe Photoshop and darktable can write `cICP`.

> **Mutual exclusivity:** If `cICP` is present, `iCCP` and `sRGB` chunks
> should not also be present. However, for backward compatibility, some
> encoders write both `cICP` and `iCCP`.

---

### TIFF -- Tag 34675 (`ICCProfile`)

TIFF stores ICC profiles as a single tag in the IFD (Image File Directory).

**Tag details:**

| Field | Value |
|-------|-------|
| Tag number | 34675 (0x8773) |
| Tag name | `ICCProfile` |
| Type | UNDEFINED (byte array) |
| Count | Profile size in bytes |

The tag value is the **raw, uncompressed ICC profile bytes**. Since TIFF
tags can be any length (via strip/tile offsets), there is no chunking needed
and no practical size limit (up to ~4 GB from the 32-bit offset/count fields).

TIFF files may contain multiple IFDs (e.g., full-resolution image + thumbnail).
The ICC profile tag in each IFD applies to that specific image.

---

### HEIF / HEIC -- `colr` Box

HEIF (High Efficiency Image Format) and its HEVC-based variant HEIC store
color information in the **`colr` (colour_information) box** within the
item properties.

**Two encoding modes in `colr`:**

| Type | Code | Description |
|------|------|-------------|
| **nclx** | `'nclx'` | Coding-Independent Code Points (CICP): primaries, transfer function, matrix coefficients, full-range flag. Compact (just a few bytes). |
| **rICC** | `'rICC'` | Restricted ICC profile: only Display/Input/Output class, only recognized ICC color spaces. Raw ICC bytes embedded directly. |
| **prof** | `'prof'` | Unrestricted ICC profile. Any ICC profile, including DeviceLink and NamedColor. Raw ICC bytes. |

**nclx CICP values for common color spaces:**

| Color Space | colour_primaries | transfer_characteristics | matrix_coefficients | full_range_flag |
|-------------|-----------------|--------------------------|---------------------|-----------------|
| sRGB | 1 | 13 | 0 | 1 |
| Display P3 | 12 | 13 | 0 | 1 |
| Rec. 2020 SDR | 9 | 14 | 0 | 1 |
| Rec. 2020 PQ | 9 | 16 | 0 | 1 |
| Rec. 2020 HLG | 9 | 18 | 0 | 1 |

**How iOS handles HEIF color:**

- iPhone-captured HEIC files typically use **nclx** CICP signaling for
  Display P3 (primaries=12, transfer=13, matrix=0, full_range=1) rather than
  embedding a full ICC profile. This is extremely compact (~10 bytes of color
  information).
- When ImageIO reads the file, it resolves the nclx codes to a `CGColorSpace`
  and reports the profile name via `kCGImagePropertyProfileName`.
- Third-party HEIF files may embed a full ICC profile via `rICC` or `prof`.
- If a coded image has no associated CICP colour property, the HEIF spec
  defines defaults: colour_primaries=1, transfer_characteristics=13,
  matrix_coefficients=5 or 6, full_range_flag=1.

> **HEIF vs JPEG size savings:** A Display P3 HEIC with nclx signaling adds
> only ~10 bytes of color information vs ~500 bytes - 4 KB for an ICC profile
> in JPEG.

---

### DNG -- ICC Profile Tags

DNG (Digital Negative) is based on TIFF and supports ICC profiles through two
mechanisms:

| Tag | Number | Description |
|-----|--------|-------------|
| `ICCProfile` | 34675 | Standard TIFF ICC profile tag (same as TIFF) |
| `AsShotICCProfile` | 50831 | ICC profile for as-shot rendering |
| `AsShotPreProfileMatrix` | 50832 | Matrix to apply before the as-shot ICC profile |
| `CurrentICCProfile` | 50833 | ICC profile for the current processing parameters |
| `CurrentPreProfileMatrix` | 50834 | Matrix to apply before the current ICC profile |

In ImageIO, the DNG ICC profiles are accessed via:
- `kCGImagePropertyDNGAsShotICCProfile` (tag 50831)
- `kCGImagePropertyDNGCurrentICCProfile` (tag 50833)
- `kCGImagePropertyDNGCurrentPreProfileMatrix` (tag 50834)

DNG files typically embed the camera profile as a DNG-specific color matrix
(ForwardMatrix, ColorMatrix) rather than an ICC profile, with the ICC profile
reserved for output-referred rendering.

---

### WebP -- `ICCP` Chunk

WebP stores ICC profiles in an **`ICCP` chunk** within the RIFF container.

**Structure (WebP extended format):**

```
RIFF container
+-- WEBP
+-- VP8X (extended header, bit 5 = ICC profile present)
+-- ICCP chunk
|   +-- 4 bytes: "ICCP"
|   +-- 4 bytes: chunk size (little-endian)
|   +-- [raw ICC profile data]
+-- VP8 / VP8L (image data)
+-- ...
```

**Key details:**

- The `VP8X` extended header has a flag bit indicating whether an ICC profile
  is present.
- The ICCP chunk must appear **before** the image data chunk.
- Profile data is **uncompressed** (unlike PNG's zlib-compressed iCCP).
- ImageIO on iOS 14+ reads ICC profiles from WebP files.
- **Write limitation:** ImageIO does not write WebP files (read-only on iOS),
  so writing ICC profiles into WebP requires a third-party encoder.

---

### JPEG XL -- Codestream Header

JPEG XL integrates ICC profiles directly into the codestream, treating color
information as essential image data rather than separate metadata.

**Two color signaling modes:**

| Mode | Description |
|------|-------------|
| **CICP enum** | Compact signaling using enum values similar to CICP (ITU-T H.273) but with separate enums for white point and RGB primaries. Covers sRGB, Display P3, Rec. 2020, and other common spaces with just a few bytes. |
| **Embedded ICC** | Full ICC profile stored in the codestream header, compressed using the JPEG XL entropy coding. Supports arbitrary profiles including CMYK. |

**Key details:**

- The `have_icc` flag in the codestream header indicates whether a full ICC
  profile is present (decoded per Annex B of the spec).
- JPEG XL can compress embedded ICC profiles very efficiently, often reducing
  a ~3 KB sRGB profile to a few hundred bytes.
- When decoding, the ICC profile is either the exact embedded profile or a
  close approximation generated from the CICP-style structured data.
- ImageIO on iOS 17+ reads JPEG XL files including their color information.

---

### GIF -- No ICC Support

GIF does not support ICC profiles. The format predates ICC color management
(GIF89a was standardized in 1989, ICC in 1994).

- GIF colors are stored as indices into a palette of up to 256 RGB values.
- There is no mechanism to embed or reference an ICC profile.
- Renderers assume the palette colors are **sRGB** (or unmanaged device RGB).
- **Practical impact:** GIF images cannot carry wide-gamut color information.

---

### PDF -- `ICCBased` Color Spaces

PDF supports ICC profiles as a first-class color space type:

```
% PDF ICCBased color space
/ColorSpace [/ICCBased <stream ref>]
```

The ICC profile is embedded as a PDF stream object (optionally compressed with
Flate/LZW). PDF supports:

- Multiple ICC profiles per document (one per color space used).
- Output intents (PDF/X, PDF/A) that specify the intended output ICC profile.
- Both v2 and v4 profiles (PDF 2.0 requires v4 support).
- Profile stream objects can be shared across multiple color space references,
  avoiding duplication.

---

### Other Formats

| Format | ICC Support | Mechanism |
|--------|------------|-----------|
| **AVIF** | Yes | `colr` box (same as HEIF): nclx for CICP, rICC/prof for ICC |
| **JPEG 2000** | Yes | Embedded ICC profile in codestream (Colour Specification Box, METH field) |
| **OpenEXR** | Limited | Uses `chromaticities` attribute (not ICC); can store ICC via custom attribute |
| **BMP** | v4/v5 only | BMP v4+ header has `bV4CSType` field and embedded ICC profile offset |
| **PSD** | Yes | ICC profile resource (Photoshop resource ID 0x040F / 1039) |
| **TARGA (TGA)** | No | No metadata mechanism |
| **ICO** | No | No ICC embedding mechanism |

---

## CICP as a Compact ICC Alternative

Coding-Independent Code Points (CICP), defined in ITU-T H.273, provide a
compact way to signal color space using just a few integer code points instead
of embedding a full ICC profile. CICP is now supported across multiple formats:

| Format | CICP Mechanism | When Added |
|--------|---------------|------------|
| HEIF/HEIC | `colr` box type `nclx` | Original spec (ISO 23008-12) |
| AVIF | `colr` box type `nclx` | Original spec |
| PNG | `cICP` chunk | PNG Third Edition (2024) |
| JPEG XL | Codestream enum values | Original spec |
| AV1 video | OBU sequence header | Original spec |
| HEVC video | VUI parameters | H.265 |

**Advantages of CICP over ICC:**

| Aspect | CICP | Embedded ICC |
|--------|------|-------------|
| Size | 4-10 bytes | 500 bytes - 2 MB |
| Parsing complexity | Trivial (integer lookup) | Complex (binary format) |
| Coverage | Well-known spaces only | Arbitrary color spaces |
| HDR signaling | Built-in (PQ, HLG) | Requires specific profile construction |

**Limitation:** CICP can only signal color spaces that have assigned code
points in ITU-T H.273. Custom or unusual color spaces (CMYK, spot colors,
device-specific calibrations) still require a full ICC profile.

---

## Profile Size Considerations

### Impact on File Size

| Scenario | Profile Size | Impact |
|----------|-------------|--------|
| sRGB in JPEG | ~3 KB | Negligible on typical 2-5 MB photo |
| Display P3 in JPEG | ~500 B - 4 KB | Negligible |
| CMYK profile in JPEG | 500 KB - 2 MB | Significant; may exceed image data |
| sRGB in PNG (compressed) | ~500 B - 1.5 KB | Minimal (zlib compressed) |
| CICP in HEIF (nclx) | ~10 B | Essentially zero |
| CICP in PNG (cICP) | 16 B (total chunk) | Essentially zero |

### Minimizing Embedded Profile Size

For workflows where file size matters (web, mobile):

1. **Use minimal sRGB profiles.** The `sRGBz` profile is only 491 bytes vs
   ~3 KB for the standard profile. The
   [Compact-ICC-Profiles](https://github.com/saucecontrol/Compact-ICC-Profiles)
   project provides similarly minimal profiles for sRGB, Display P3, and
   Adobe RGB.

2. **Strip the profile for sRGB content.** If the image is sRGB, many
   renderers will assume sRGB when no profile is present. However, this can
   cause color shifts in color-managed applications that do not assume sRGB.

3. **Use CICP/nclx where supported.** HEIF, AVIF, PNG (3rd ed.), and JPEG XL
   support compact CICP signaling (~4-16 bytes) instead of a full ICC profile.

4. **Compress when possible.** PNG's iCCP chunk uses zlib compression.
   PDF streams can use Flate compression. JPEG XL compresses embedded ICC
   profiles with its own entropy coding.

---

## Stripping Profiles

Removing ICC profiles reduces file size but has trade-offs:

### When Stripping Is Safe

- The image is **known to be sRGB** and will only be displayed in contexts
  that assume sRGB (web browsers, most apps).
- File size reduction is critical (thumbnails, web optimization).

### When Stripping Is Dangerous

- The image is **Display P3 or wider gamut.** Without the profile, a
  color-managed renderer may interpret the wide-gamut values as sRGB,
  resulting in oversaturated or shifted colors.
- The image is **CMYK.** Without a profile, there is no way to correctly
  convert to RGB for display.
- The image is **part of a color-managed workflow** (print, prepress,
  medical imaging, archival).

### Using `kCGImageDestinationOptimizeColorForSharing`

Apple provides a safer alternative to stripping: convert the image to sRGB
before removing the profile. This preserves visual appearance at the cost
of gamut compression:

```swift
let options: [CFString: Any] = [
    kCGImageDestinationOptimizeColorForSharing: true
]
```

This option converts Display P3 (or any wide gamut) to sRGB, embeds the
sRGB profile, and produces a universally compatible image. See
[ImageIO Integration](imageio-integration.md) for details.

---

## Summary Table

| Format | Mechanism | Compressed | Chunked | Max Profile Size | CICP Alt |
|--------|-----------|------------|---------|-----------------|----------|
| **JPEG** | APP2 `ICC_PROFILE` | No | Yes (64 KB chunks) | ~16 MB (255 chunks) | No |
| **PNG** | `iCCP` chunk | Yes (zlib) | No | ~2 GB (PNG chunk limit) | Yes (`cICP`, PNG 3rd ed.) |
| **TIFF** | Tag 34675 | No | No | ~4 GB (TIFF limit) | No |
| **HEIF/HEIC** | `colr` box | No | No | Container limit | Yes (nclx) |
| **DNG** | Tag 34675 + 50833 | No | No | ~4 GB | No |
| **WebP** | `ICCP` chunk | No | No | ~4 GB (RIFF limit) | No |
| **JPEG XL** | Codestream header | Yes (entropy) | No | Format limit | Yes (enum) |
| **GIF** | N/A | N/A | N/A | N/A | No |
| **PDF** | Stream object | Optional (Flate) | No | PDF limit | No |
| **AVIF** | `colr` box | No | No | Container limit | Yes (nclx) |
| **JPEG 2000** | Colour Specification Box | No | No | Format limit | No |
| **BMP** | v4/v5 header | No | No | Header limit | No |
| **PSD** | Resource 0x040F | No | No | Resource limit | No |

---

## Cross-References

- [Profile Basics](profile-basics.md) -- ICC profile binary structure and tags
- [Common Profiles](common-profiles.md) -- sRGB, Display P3, Adobe RGB profile details
- [ImageIO Integration](imageio-integration.md) -- Reading/writing profiles with Apple APIs
- [Pitfalls](pitfalls.md) -- Large profiles, stripping risks, format limitations
- [`imageio/supported-formats.md`](../imageio/supported-formats.md) -- Full format support matrix
