# Interoperability — Cross-Standard Sync & Mapping

> Part of [iOS Image Metadata Skill](../../SKILL.md) · [References Index](../README.md)

Cross-standard synchronization, field mapping, conflict resolution, and
metadata preservation across EXIF, IPTC IIM, and XMP. This section covers
problems that arise when the same metadata field exists in multiple standards
simultaneously, and how applications (especially Apple ImageIO) handle
the resulting conflicts.

---

## File Index

| File | Contents |
|------|----------|
| [overlapping-fields.md](overlapping-fields.md) | Complete mapping of every field that exists in multiple standards (DateTime, Creator, Copyright, Description, Keywords, Title, Location, etc.) with EXIF/TIFF, IPTC IIM, and XMP locations. Includes IPTC IIM field length limits, multi-value conventions, and a full cross-reference table with MWG preferred sources. |
| [mwg-guidelines.md](mwg-guidelines.md) | Metadata Working Group 2.0 specification: IPTCDigest sync mechanism with all 4 states, reading reconciliation algorithm with pseudocode, predicted-IIM comparison, field-specific rules (Description, Creator, Copyright, DateTime, Keywords, Location), writing rules, multi-value conventions (semicolon quoting for EXIF Artist), UTF-8 recommendation, date/time timezone and precision preservation, strict conformance mode, ExifTool MWG module, MWG 1.0 vs 2.0 changes, edge cases. |
| [imageio-behavior.md](imageio-behavior.md) | How Apple ImageIO handles cross-standard conflicts: auto-synthesis between property dictionaries and XMP, bridge function coverage, type coercion details, CopyImageSource XMP-to-binary sync table, merge vs replace behavior, known sync gaps (date format, IPTCDigest, EXIF binary in merge mode), IPTC IIM creation policy, lossless update internals (JPEG/TIFF segment handling), testing methodology with code, ImageIO vs ExifTool comparison, recommendations for iOS developers. |
| [orientation-mapping.md](orientation-mapping.md) | Three orientation numbering systems (EXIF 1-8, CGImagePropertyOrientation, UIImage.Orientation), complete three-way mapping table, visual ASCII diagrams for all 8 values, mathematical transforms (dihedral group D4), Swift conversion code (all directions), affine transforms for Core Graphics, display size calculation, orientation composition, HEIF orientation abstraction, 6 common pitfalls (raw value confusion, double-rotation, UIImage round-trip, front camera mirroring). |
| [pitfalls.md](pitfalls.md) | 15 interoperability pitfalls: (1) IPTC charset Latin-1 vs UTF-8, (2) UIImage metadata loss with safe alternative, (3) CIImage pipeline loss, (4) social media stripping matrix (14 platforms), (5) sidecar priority confusion, (6) orientation inconsistency, (7) multi-value separator confusion, (8) date format inconsistencies with parsing code, (9) GPS signed vs unsigned with conversion helpers, (10) format conversion metadata tables (JPEG/HEIC/PNG/GIF), (11) ExifTool vs ImageIO defaults, (12) langAlt silent write bug, (13) tag removal in merge mode, (14) HEIC lossless update limitation, (15) clean JPEG phantom EXIF. |

---

## Key Concepts

### The Overlap Problem

Many important metadata fields exist in three places simultaneously:

| Concept | EXIF/TIFF | IPTC IIM | XMP |
|---------|-----------|----------|-----|
| Date taken | `DateTimeOriginal` | `DateCreated` + `TimeCreated` | `photoshop:DateCreated` |
| Creator | `Artist` | `By-line` | `dc:creator` |
| Copyright | `Copyright` | `CopyrightNotice` | `dc:rights` |
| Description | `ImageDescription` | `Caption-Abstract` | `dc:description` |
| Keywords | -- | `Keywords` | `dc:subject` |
| Title | -- | `ObjectName` | `dc:title` |
| City | -- | `City` | `photoshop:City` |

When an application modifies one location but not the others, the metadata
becomes inconsistent. The MWG guidelines define reconciliation rules for
reading and synchronization rules for writing.

### The MWG Solution

The Metadata Working Group (Adobe, Apple, Canon, Microsoft, Nokia, Sony)
published guidelines in 2010 that define:

1. **Reading priority:** XMP is generally preferred; IPTCDigest determines
   whether IPTC IIM or XMP is more trustworthy
2. **Writing rule:** Update all locations when any overlapping field changes
3. **IPTCDigest:** MD5 hash of IPTC IIM block stored in XMP
   (`photoshop:LegacyIPTCDigest`) to detect sync status
4. **Multi-value conventions:** Semicolon-space separation in EXIF Artist
   with quoting rules for names containing semicolons
5. **UTF-8 recommendation:** EXIF "ASCII" fields should accept/write UTF-8

### Apple ImageIO Behavior

ImageIO implements a subset of MWG-like behavior:

- **Auto-synthesis on read:** Both APIs (property dictionaries and XMP tree)
  see metadata from all standards, regardless of original storage format
- **Regeneration on write:** `CGImageDestinationCopyImageSource` rebuilds
  IPTC IIM from XMP state (but not EXIF binary in merge mode)
- **No IPTCDigest:** ImageIO does not check or maintain the IPTCDigest
- **Known gaps:** Date format sync (ISO 8601 not converted to IIM format),
  langAlt tag creation bug, IPTC IIM created even when absent from source

### The Three Orientation Systems

Image orientation involves three numbering systems on Apple platforms:

| System | Values | Gotcha |
|--------|--------|--------|
| EXIF / `CGImagePropertyOrientation` | 1-8 | Same values, same meaning |
| `UIImage.Orientation` | 0-7 | **Different numbering** (`.right` = rawValue 3, but EXIF right = 6) |

Do not use raw `UIImage.Orientation` values as EXIF orientation values.
Convert through `CGImagePropertyOrientation` instead.

---

## Cross-References

| Topic | Location | Relevance |
|-------|----------|-----------|
| EXIF-to-XMP standard mapping | [../exif/xmp-mapping.md](../exif/xmp-mapping.md) | Complete EXIF tag -> XMP path tables (4 namespaces) |
| ImageIO two-API overview | [../imageio/README.md](../imageio/README.md) | Property dicts vs XMP tree, bridge functions |
| XMP bridge functions | [../imageio/cgimage-metadata.md](../imageio/cgimage-metadata.md) | Bridge function details, langAlt bug, path syntax |
| CGImageDestination write behavior | [../imageio/cgimagedestination.md](../imageio/cgimagedestination.md) | Merge vs replace, option keys, sync tables |
| ImageIO pitfalls | [../imageio/pitfalls.md](../imageio/pitfalls.md) | UIImage loss, GPS convention, threading, caching |
| EXIF orientation | [../exif/orientation.md](../exif/orientation.md) | EXIF orientation specification, iPhone defaults |
| IPTC standard overview | [../iptc/README.md](../iptc/README.md) | IPTC IIM and Core/Extension schemas |

---

## When to Use This Section

- **Building a metadata editor:** Read [overlapping-fields.md](overlapping-fields.md)
  to know which fields need multi-location updates, and
  [mwg-guidelines.md](mwg-guidelines.md) for the reconciliation algorithm.
  Pay special attention to the IPTC IIM field length limits table and the
  multi-value field conventions.

- **Debugging metadata inconsistencies:** Check [pitfalls.md](pitfalls.md)
  for common causes (especially pitfalls 1, 8, 11, 12) and
  [imageio-behavior.md](imageio-behavior.md) for ImageIO-specific sync gaps.

- **Handling orientation:** See [orientation-mapping.md](orientation-mapping.md)
  for the three-way conversion table and Swift conversion code. The pitfalls
  section covers double-rotation and UIImage round-trip issues.

- **Converting between formats:** Review [pitfalls.md](pitfalls.md) section
  10 for per-format metadata preservation tables (JPEG, HEIC, PNG, GIF).

- **Comparing ImageIO and ExifTool:** See
  [imageio-behavior.md](imageio-behavior.md) comparison table and
  [pitfalls.md](pitfalls.md) section 11 for reading/writing default
  differences.

- **Implementing MWG conformance on iOS:** Start with
  [mwg-guidelines.md](mwg-guidelines.md) for the full algorithm, then
  check [imageio-behavior.md](imageio-behavior.md) to see which parts
  ImageIO handles automatically and which require manual implementation.

- **Writing metadata that survives round-trips:** Review
  [imageio-behavior.md](imageio-behavior.md) recommendations section and
  [pitfalls.md](pitfalls.md) for the UIImage, CIImage, and format conversion
  pitfalls.
