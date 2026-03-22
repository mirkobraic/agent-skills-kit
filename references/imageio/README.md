# ImageIO Framework Reference

Apple's ImageIO framework (`import ImageIO`) — the primary API for reading, writing,
and manipulating image metadata on iOS, macOS, visionOS, and tvOS.

---

## Index

| File | Contents |
|------|----------|
| [cgimagesource.md](cgimagesource.md) | `CGImageSource` — reading images, metadata, thumbnails, animation |
| [cgimagedestination.md](cgimagedestination.md) | `CGImageDestination` — writing images, metadata, auxiliary data |
| [cgimage-metadata.md](cgimage-metadata.md) | `CGImageMetadata` / `CGImageMetadataTag` — XMP tree API |
| [supported-formats.md](supported-formats.md) | All supported formats, UTIs, read/write capabilities |
| [property-keys.md](property-keys.md) | Complete list of `kCGImageProperty*` constants |
| [auxiliary-data.md](auxiliary-data.md) | Depth maps, gain maps, portrait mattes, spatial photos |
| [pitfalls.md](pitfalls.md) | Common pitfalls, thread safety, PhotoKit integration |

---

## Core Types

| Type | Role | iOS |
|------|------|-----|
| `CGImageSource` | Read images and metadata from URLs / Data / DataProvider | 4.0+ |
| `CGImageDestination` | Write images and metadata to URLs / Data / DataConsumer | 4.0+ |
| `CGImageMetadata` | Immutable XMP metadata tree | 7.0+ |
| `CGMutableImageMetadata` | Mutable XMP metadata tree | 7.0+ |
| `CGImageMetadataTag` | Single XMP tag (namespace + prefix + name + type + value) | 7.0+ |

## Two Metadata APIs

ImageIO exposes metadata through **two distinct APIs**:

### 1. Property Dictionaries (EXIF, IPTC, GPS, TIFF, etc.)

Flat key–value dictionaries returned by `CGImageSourceCopyPropertiesAtIndex`.
Each metadata standard has its own dictionary constant (e.g.,
`kCGImagePropertyExifDictionary`). Written back via
`CGImageDestinationAddImage` or `CGImageDestinationCopyImageSource`.

**Strengths:** Simple reads/writes for standard fields.
**Limitation:** Only covers fields Apple has defined constants for.

### 2. XMP Metadata Tree (`CGImageMetadata`)

A tree-structured API for arbitrary XMP namespaces. Read via
`CGImageSourceCopyMetadataAtIndex`, manipulated via
`CGImageMetadataSetTagWithPath` / `CGImageMetadataSetValueWithPath`, and
written via `CGImageDestinationAddImageAndMetadata`.

**Strengths:** Access any XMP namespace including IPTC Extension, Dublin Core,
custom schemas.
**Limitation:** More verbose API; XMP only (not EXIF/IPTC IIM natively, though
bridge functions exist).

### Bridge Functions

Two functions connect the two APIs:
- `CGImageMetadataCopyTagMatchingImageProperty` — maps a property dictionary
  key to its XMP tag equivalent
- `CGImageMetadataSetValueMatchingImageProperty` — sets a value using property
  dictionary naming, automatically mapping to the correct XMP tag

### Cross-API Auto-Synthesis (observed behavior)

In current Apple implementations, the two APIs are often **not siloed on read
or write**:

- **On read:** An image with only IPTC IIM (no XMP) returns synthetic XMP tags
  via `CGImageSourceCopyMetadataAtIndex`. Conversely, an XMP-only image returns
  synthesized IIM values via `CGImageSourceCopyPropertiesAtIndex`. The bridge
  API works in both directions.
- **On write:** `CGImageDestinationCopyImageSource` regenerates IIM/EXIF/TIFF/GPS
  binary segments from the final XMP state. Writing XMP automatically keeps
  property dictionaries in sync (with some exceptions — see
  [cgimagedestination.md](cgimagedestination.md)).

This means either read API can see metadata from both sources, and XMP-based
writes may produce corresponding property dictionaries without explicit
dual-write logic.

> This section describes observed behavior on recent Apple OS releases; Apple
> does not currently document this as a strict cross-format API contract.

## Metadata Writing Patterns

| Pattern | Function | Re-encode? | Formats |
|---------|----------|-----------|---------|
| Write with property dicts | `CGImageDestinationAddImage` | Yes | All writable |
| Write with XMP tree | `CGImageDestinationAddImageAndMetadata` | Yes | All writable |
| Lossless metadata update | `CGImageDestinationCopyImageSource` | **No** | JPEG, PNG, PSD, TIFF |
| Strip metadata | Omit properties or use exclude options | Varies | All |

## Platform Availability

| Platform | Base API | XMP/Metadata API | Animation API | Auxiliary Data |
|----------|----------|-------------------|---------------|----------------|
| iOS | 4.0+ | 7.0+ | 13.0+ | 11.0+ |
| macOS | 10.4+ | 10.8+ | 10.15+ | 10.13+ |
| tvOS | 9.0+ | 9.0+ | 13.0+ | 11.0+ |
| visionOS | 1.0+ | 1.0+ | 1.0+ | 1.0+ |
| watchOS | 2.0+ | 2.0+ | 6.0+ | 4.0+ |
