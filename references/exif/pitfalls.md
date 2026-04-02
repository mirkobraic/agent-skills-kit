# EXIF Pitfalls & Privacy

> Part of [EXIF Reference](README.md)

> **Guidance, not absolute truth.** The pitfalls below are based on observed
> behavior and community knowledge at the time of writing. Edge cases may vary
> by format, device, or software. Treat these as starting points for
> investigation — always verify and test with real images before relying on any
> assumption documented here.

Known issues, gotchas, and privacy considerations inherent to the EXIF standard.
For ImageIO-specific pitfalls (deprecated key spellings, synthetic properties,
missing constants), see [`imageio-mapping.md`](imageio-mapping.md#imageio-specific-pitfalls).

---

## DateTime Has No Timezone (Pre-2.31)

`DateTimeOriginal` is a naive timestamp — `"2024:06:15 14:30:00"` with no
timezone indicator. The `OffsetTimeOriginal` tag (EXIF 2.31+) was added to
solve this, but many cameras omit it.

- iPhone always writes `OffsetTimeOriginal`
- Many third-party cameras omit it entirely
- Without it, the timezone of the capture time is ambiguous

See [`tag-reference.md`](tag-reference.md#date--time) for the full DateTime
triplet details.

---

## MakerNote Internal Offsets Break on Edit

Editing or rewriting EXIF data can shift the MakerNote's byte position,
breaking its internal offset pointers. This is a fundamental structural
fragility — see [`makernote.md`](makernote.md#offset-fragility) for details and
mitigation strategies.

---

## 64 KB Limit in JPEG

All EXIF data in JPEG must fit in a single APP1 segment (64 KB). Large
MakerNotes or many tags can exceed this limit. Writing large amounts of
metadata may silently truncate. HEIF, PNG, WebP, and AVIF do not have this
constraint.

---

## Orientation Inconsistency

The orientation tag (0x0112) describes how to transform stored pixels for
display but does NOT modify the pixels themselves. Issues arise when:

- Software "bakes in" the rotation (rewrites pixels) but forgets to reset
  orientation to 1
- The thumbnail has different orientation than the main image
- Multiple consumers interpret orientation differently

See [`../interoperability/orientation-mapping.md`](../interoperability/orientation-mapping.md) for the full value table.

---

## ColorSpace Tag Ambiguity

The standard defines only two values: 1 (sRGB) and 65535 (Uncalibrated). Value
2 is used by some tools to signal Adobe RGB, but this is non-standard. When
ColorSpace is 65535, the actual color space must be determined from the ICC
profile.

---

## Privacy Considerations

EXIF data can reveal sensitive information:

| Data | Risk |
|------|------|
| GPS coordinates (separate IFD, but commonly grouped with EXIF) | Exact location disclosure |
| DateTime + OffsetTime | Exact time and timezone of capture |
| Camera serial number / BodySerialNumber | Unique device identification |
| Lens serial number | Equipment identification |
| CameraOwnerName | Personal identity |
| MakerNote | May contain location, device ID, or other PII |
| Thumbnail | May contain pre-edit image content |

### Mitigation

For full anonymization, create a new image from pixels only and include only
the metadata you explicitly choose. Be aware that:

- GPS stripping does not filter MakerNote content — see
  [`makernote.md`](makernote.md#makernote-and-gps-stripping)
- Thumbnails may retain pre-edit content (cropped faces, unblurred details)
- Serial numbers and owner names can fingerprint individual cameras
