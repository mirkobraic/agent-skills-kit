# MakerNote (Tag 0x927C)

> Part of [EXIF Reference](README.md)

The MakerNote tag contains vendor-specific binary data in a proprietary format.
Each manufacturer defines their own internal structure. For ImageIO access
details, see [`imageio-mapping.md`](imageio-mapping.md#makernote-access).

---

## Key Characteristics

- **Format is vendor-specific** — Canon, Nikon, Apple, Sony, Fujifilm, etc.
  each use entirely different internal structures
- **Not standardized** — the EXIF spec only defines the tag; the contents are
  proprietary
- **Contains valuable data** — some vendors store ISO, lens info, focus data,
  scene analysis, or processing flags exclusively in MakerNote rather than
  standard EXIF tags
- **Some vendors encrypt portions** (e.g., Nikon encrypts detailed lens data)
- **No XMP representation** — MakerNote has no standard XMP mapping

---

## Offset Fragility

MakerNote data often contains internal byte offsets — either relative to the
start of the TIFF structure or relative to the MakerNote tag itself. When image
editing software rewrites the EXIF data, the MakerNote may be moved to a
different byte position, breaking these internal offsets and rendering the data
unreadable.

**Known offset strategies:**
- **Absolute offsets (from TIFF header):** Used by Canon, Nikon, Olympus. Most
  fragile — any change to preceding data breaks them
- **Relative offsets (from MakerNote start):** Used by Fujifilm, Panasonic.
  More resilient — survives repositioning if the MakerNote itself isn't modified
- **No internal offsets:** Some simpler MakerNotes (e.g., some Samsung models)
  use a flat structure with no internal pointers

**Mitigation:** Microsoft's `OffsetSchema` tag (0xEA1D) records the byte
displacement as a signed 32-bit integer, allowing MakerNote readers to
compensate. This is a Microsoft extension, not part of the official EXIF
standard.

---

## Common MakerNote Formats

| Vendor | Header Signature | Internal Format | Notes |
|--------|-----------------|-----------------|-------|
| **Canon** | None (starts with IFD) | IFD structure | Well-documented, extensive tag set |
| **Nikon** (Type 3) | `"Nikon\0"` + version | IFD with own TIFF header | Has its own byte order marker; partially encrypted |
| **Apple** | `"Apple iOS\0"` | IFD structure | Burst mode, HDR flags, media group UUID, focus/stabilization data |
| **Sony** | Varies by model | IFD or proprietary | Multiple formats across model generations |
| **Fujifilm** | `"FUJIFILM"` + version | IFD with relative offsets | Always little-endian regardless of main TIFF byte order |
| **Olympus** | `"OLYMP\0"` | IFD structure | Nested sub-IFDs for camera settings, focus info, etc. |
| **Panasonic** | `"Panasonic\0"` | IFD structure | Relative offsets |
| **Samsung** | Varies | IFD or flat | Simpler structure on newer models |
| **Pentax** | `"AOC\0"` | IFD structure | |

---

## MakerNote and GPS Stripping

GPS stripping tools (including metadata sanitizers) remove GPS data from the
GPS IFD and corresponding XMP tags, but they do **NOT** filter:

- Proprietary location data embedded in manufacturer MakerNote fields
- Apple's MakerNote which can contain location-related processing metadata
- Custom XMP properties that might contain coordinates

**For complete location removal**, the MakerNote must also be stripped or the
image must be recreated from pixels only with no metadata copy.

---

## Decoded MakerNote Libraries

Major libraries that decode proprietary MakerNote data:

| Library | Language | Notable Vendor Support |
|---------|----------|----------------------|
| **ExifTool** | Perl | Most comprehensive: Canon, Nikon, Sony, Apple, Fujifilm, Olympus, Panasonic, Samsung, Sigma, and many more |
| **Exiv2** | C++ | Canon, Nikon, Fujifilm, Minolta/Sony, Olympus, Panasonic, Pentax, Samsung, Sigma |
| **libexif** | C | Canon, Olympus, Pentax, Fujifilm |

See `../makers/` for vendor-specific key references.
