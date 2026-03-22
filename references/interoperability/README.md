# Interoperability

Cross-standard synchronization, field mapping, and conflict resolution.

## Planned content

- **Overlapping fields**: fields that exist in multiple standards simultaneously
  - DateTimeOriginal (EXIF, XMP-exif, IPTC IIM)
  - Creator / Artist (TIFF Artist, XMP-dc:creator, IPTC Byline)
  - Copyright (TIFF Copyright, XMP-dc:rights, IPTC CopyrightNotice)
  - Description / Caption (XMP-dc:description, IPTC CaptionAbstract)
  - Keywords (XMP-dc:subject, IPTC Keywords)
- **MWG (Metadata Working Group) guidelines**: reconciliation rules for reading/writing across EXIF, XMP, IPTC
  - Version 2.0 (2010), endorsed by Adobe, Apple, Canon, Microsoft, Nokia, Sony
  - Strict conformance mode behavior
  - IPTCDigest and XMP/IIM sync detection
  - Recommended separator conventions for multi-value fields
  - UTF-8 storage for EXIF ASCII strings
- **ImageIO behavior**: how Apple's framework handles conflicts between dictionaries
- **Common pitfalls**:
  - IPTC IIM charset issues (Latin-1 vs UTF-8)
  - Orientation tag duplication (TIFF vs EXIF)
  - Metadata loss when round-tripping through UIImage or CIImage
  - XMP sidecar vs embedded XMP
