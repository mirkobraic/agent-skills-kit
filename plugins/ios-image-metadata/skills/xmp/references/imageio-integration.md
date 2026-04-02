# XMP and Apple ImageIO Integration

> Part of [XMP Reference](README.md)

How Apple's ImageIO framework reads and writes XMP metadata. This file
consolidates all ImageIO-specific XMP behavior in one place. For the full
CGImageMetadata API reference (functions, enums, path syntax, code examples),
see `../imageio/cgimage-metadata.md`.

---

## Two Metadata APIs

ImageIO provides two distinct ways to access metadata. Understanding their
relationship is essential for XMP work:

| API | Returns | Metadata Model | XMP Access |
|-----|---------|----------------|------------|
| `CGImageSourceCopyPropertiesAtIndex` | `CFDictionary` | Flat key-value dictionaries per domain | Indirect -- some XMP values synthesized into property dicts |
| `CGImageSourceCopyMetadataAtIndex` | `CGImageMetadata` | XMP namespace tree | Direct -- full access to any XMP namespace and structure |

The property dictionary API is simpler but limited to predefined keys. The
CGImageMetadata API provides full access to all XMP namespaces, including
custom ones.

### Bridge Functions

Two functions connect the APIs:

| Function | Direction | Purpose |
|----------|-----------|---------|
| `CGImageMetadataCopyTagMatchingImageProperty(_:_:_:)` | Property dict key --> XMP tag | Look up the XMP tag corresponding to a property dictionary key |
| `CGImageMetadataSetValueMatchingImageProperty(_:_:_:_:)` | Property dict key --> XMP write | Write a value using property dictionary naming; ImageIO maps to the correct XMP path |

### Auto-Synthesis (Observed Behavior)

Apple synthesizes metadata across the two APIs on read:

- An image with **only EXIF binary data** (no XMP packet) will return
  synthesized XMP tags via `CGImageSourceCopyMetadataAtIndex`
- An image with **only XMP data** (no EXIF/IIM) will return synthesized
  property dictionary values via `CGImageSourceCopyPropertiesAtIndex`
- An image with **only IPTC IIM data** will return synthesized XMP tags
  including proper `langAlt` structures for `dc:title`, `dc:description`, etc.

This means the two APIs are **not siloed** -- either read path sees metadata
from both sources. The bridge functions work in both directions.

> Observed on macOS 14 (arm64e). Apple does not document this as a strict
> contract, so re-validate on target OS versions.

---

## Core Types

| Type | Purpose | iOS |
|------|---------|-----|
| `CGImageMetadata` | Immutable XMP metadata tree | 7.0+ |
| `CGMutableImageMetadata` | Mutable XMP metadata tree (subtype of CGImageMetadata) | 7.0+ |
| `CGImageMetadataTag` | Single tag: namespace + prefix + name + type + value | 7.0+ |

---

## CGImageMetadataType Enum

Maps XMP data model forms to ImageIO constants:

| Raw Value | Constant | XMP Equivalent | Value Type |
|-----------|----------|----------------|------------|
| -1 | `kCGImageMetadataTypeInvalid` | (invalid) | -- |
| 0 | `kCGImageMetadataTypeDefault` | Simple scalar | `CFString` |
| 1 | `kCGImageMetadataTypeString` | Text string | `CFString` |
| 2 | `kCGImageMetadataTypeArrayUnordered` | `rdf:Bag` | `CFArray` of `CGImageMetadataTag` |
| 3 | `kCGImageMetadataTypeArrayOrdered` | `rdf:Seq` | `CFArray` of `CGImageMetadataTag` |
| 4 | `kCGImageMetadataTypeAlternateArray` | `rdf:Alt` | `CFArray` of `CGImageMetadataTag` |
| 5 | `kCGImageMetadataTypeAlternateText` | `rdf:Alt` + `xml:lang` | `CFDictionary` of `[String: String]` |
| 6 | `kCGImageMetadataTypeStructure` | XMP Structure | `CFDictionary` of `[String: CGImageMetadataTag]` |

---

## Pre-Registered Namespace Constants

These 10 namespaces are automatically registered. Tags using these prefixes
work without calling `CGImageMetadataRegisterNamespaceForPrefix`:

| Namespace Constant | Prefix Constant | Prefix | URI |
|--------------------|-----------------|--------|-----|
| `kCGImageMetadataNamespaceExif` | `kCGImageMetadataPrefixExif` | `exif` | `http://ns.adobe.com/exif/1.0/` |
| `kCGImageMetadataNamespaceExifAux` | `kCGImageMetadataPrefixExifAux` | `aux` | `http://ns.adobe.com/exif/1.0/aux/` |
| `kCGImageMetadataNamespaceExifEX` | `kCGImageMetadataPrefixExifEX` | `exifEX` | `http://cipa.jp/exif/1.0/` |
| `kCGImageMetadataNamespaceDublinCore` | `kCGImageMetadataPrefixDublinCore` | `dc` | `http://purl.org/dc/elements/1.1/` |
| `kCGImageMetadataNamespaceIPTCCore` | `kCGImageMetadataPrefixIPTCCore` | `Iptc4xmpCore` | `http://iptc.org/std/Iptc4xmpCore/1.0/xmlns/` |
| `kCGImageMetadataNamespaceIPTCExtension` | `kCGImageMetadataPrefixIPTCExtension` | `Iptc4xmpExt` | `http://iptc.org/std/Iptc4xmpExt/2008-02-29/` |
| `kCGImageMetadataNamespacePhotoshop` | `kCGImageMetadataPrefixPhotoshop` | `photoshop` | `http://ns.adobe.com/photoshop/1.0/` |
| `kCGImageMetadataNamespaceTIFF` | `kCGImageMetadataPrefixTIFF` | `tiff` | `http://ns.adobe.com/tiff/1.0/` |
| `kCGImageMetadataNamespaceXMPBasic` | `kCGImageMetadataPrefixXMPBasic` | `xmp` | `http://ns.adobe.com/xap/1.0/` |
| `kCGImageMetadataNamespaceXMPRights` | `kCGImageMetadataPrefixXMPRights` | `xmpRights` | `http://ns.adobe.com/xap/1.0/rights/` |

### Namespaces Requiring Manual Registration

Common namespaces **not** pre-registered by ImageIO -- you must call
`CGImageMetadataRegisterNamespaceForPrefix` before writing:

| Prefix | URI | Schema |
|--------|-----|--------|
| `xmpMM` | `http://ns.adobe.com/xap/1.0/mm/` | XMP Media Management |
| `xmpBJ` | `http://ns.adobe.com/xap/1.0/bj/` | XMP Basic Job Ticket |
| `xmpDM` | `http://ns.adobe.com/xmp/1.0/DynamicMedia/` | XMP Dynamic Media |
| `xmpNote` | `http://ns.adobe.com/xmp/note/` | XMP Note (Extended XMP) |
| `crs` | `http://ns.adobe.com/camera-raw-settings/1.0/` | Camera Raw Settings |
| `dng` | `http://ns.adobe.com/dng/1.0/` | DNG |
| `plus` | `http://ns.useplus.org/ldf/xmp/1.0/` | PLUS Licensing |
| `stRef` | `http://ns.adobe.com/xap/1.0/sType/ResourceRef#` | Resource Reference |
| `stEvt` | `http://ns.adobe.com/xap/1.0/sType/ResourceEvent#` | Resource Event |
| `stDim` | `http://ns.adobe.com/xap/1.0/sType/Dimensions#` | Dimensions |
| `stArea` | `http://ns.adobe.com/xmp/sType/Area#` | Area (face regions) |
| `mwg-rs` | `http://www.metadataworkinggroup.com/schemas/regions/` | MWG Regions |

> If you write a tag with an unregistered prefix, `CGImageMetadataSetTagWithPath`
> returns `false` **silently** -- no error, no exception.

---

## Reading XMP

### From an Image File

```swift
import ImageIO

let url = URL(fileURLWithPath: "/path/to/image.jpg")
guard let source = CGImageSourceCreateWithURL(url as CFURL, nil),
      let metadata = CGImageSourceCopyMetadataAtIndex(source, 0, nil) else {
    return
}

// Read a simple string property
let city = CGImageMetadataCopyStringValueWithPath(
    metadata, nil, "photoshop:City" as CFString
)

// Read a tag to inspect its type and value
let titleTag = CGImageMetadataCopyTagWithPath(
    metadata, nil, "dc:title" as CFString
)
if let tag = titleTag {
    let type = CGImageMetadataTagGetType(tag)    // .alternateText
    let value = CGImageMetadataTagCopyValue(tag)  // CFDictionary ["x-default": "..."]
}
```

### From an XMP Sidecar File

```swift
let xmpData = try Data(contentsOf: sidecarURL)
guard let metadata = CGImageMetadataCreateFromXMPData(xmpData as CFData) else {
    return
}

// Same path-based API as embedded metadata
let rating = CGImageMetadataCopyStringValueWithPath(
    metadata, nil, "xmp:Rating" as CFString
)
```

### From Raw XMP XML String

```swift
let xmpXML = """
    <x:xmpmeta xmlns:x="adobe:ns:meta/">
    <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <rdf:Description rdf:about=""
        xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:format>image/jpeg</dc:format>
    </rdf:Description></rdf:RDF></x:xmpmeta>
    """
let metadata = CGImageMetadataCreateFromXMPData(
    Data(xmpXML.utf8) as CFData
)
```

---

## Writing XMP

### Lossless Update (JPEG, PNG, TIFF, PSD Only)

Update metadata without re-encoding pixels:

```swift
let source = CGImageSourceCreateWithURL(inputURL as CFURL, nil)!
let uti = CGImageSourceGetType(source)!
let dest = CGImageDestinationCreateWithURL(
    outputURL as CFURL, uti, 1, nil
)!

let mutable = CGImageMetadataCreateMutable()

// Set a simple property
CGImageMetadataSetValueWithPath(
    mutable, nil,
    "photoshop:City" as CFString,
    "Berlin" as CFString
)

// Set keywords (bag array)
let keywords = ["architecture", "Berlin", "travel"]
let keywordTags = keywords.map { keyword in
    CGImageMetadataTagCreate(
        kCGImageMetadataNamespaceDublinCore,
        kCGImageMetadataPrefixDublinCore,
        "subject" as CFString,
        .string,
        keyword as CFString
    )!
}
let bagTag = CGImageMetadataTagCreate(
    kCGImageMetadataNamespaceDublinCore,
    kCGImageMetadataPrefixDublinCore,
    "subject" as CFString,
    .arrayUnordered,
    keywordTags as CFArray
)!
CGImageMetadataSetTagWithPath(
    mutable, nil, "dc:subject" as CFString, bagTag
)

let options: [CFString: Any] = [
    kCGImageDestinationMetadata: mutable,
    kCGImageDestinationMergeMetadata: kCFBooleanTrue!
]

var error: Unmanaged<CFError>?
let success = CGImageDestinationCopyImageSource(
    dest, source, options as CFDictionary, &error
)
```

### With Re-Encoding (All Formats)

Required for HEIF/HEIC and when also writing pixel data:

```swift
let dest = CGImageDestinationCreateWithURL(
    url as CFURL, "public.heic" as CFString, 1, nil
)!

let mutable = CGImageMetadataCreateMutable()
// ... add tags ...

CGImageDestinationAddImageAndMetadata(dest, cgImage, mutable, nil)
CGImageDestinationFinalize(dest)
```

---

## Writing Language Alternatives (langAlt)

Language alternative properties (`dc:title`, `dc:description`, `dc:rights`,
`xmpRights:UsageTerms`) require special handling due to an ImageIO bug.

### The Problem

Tags created via `CGImageMetadataTagCreate(.alternateText, CFDictionary)` are
accepted by `SetTagWithPath` (returns `true`) but are **silently discarded**
by `CGImageDestinationCopyImageSource`. The tag will not appear in the output
file's XMP.

### Workaround 1: SetValueWithPath (Single Language)

Apple auto-detects that certain fields should be `langAlt` and creates the
correct internal structure:

```swift
CGImageMetadataSetValueWithPath(
    mutable, nil,
    "dc:title" as CFString,
    "My Image Title" as CFString
)
```

This creates a proper `rdf:Alt` with a single `x-default` entry.

### Workaround 2: Parse from XMP Snippet (Multi-Language)

For multiple languages, build an XMP snippet and parse it:

```swift
let xmpSnippet = """
    <x:xmpmeta xmlns:x="adobe:ns:meta/">
    <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <rdf:Description rdf:about=""
        xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:title><rdf:Alt>
    <rdf:li xml:lang="x-default">English title</rdf:li>
    <rdf:li xml:lang="de">Deutscher Titel</rdf:li>
    <rdf:li xml:lang="ja">Japanese title here</rdf:li>
    </rdf:Alt></dc:title>
    </rdf:Description></rdf:RDF></x:xmpmeta>
    """
let tempMeta = CGImageMetadataCreateFromXMPData(
    Data(xmpSnippet.utf8) as CFData
)!
let tag = CGImageMetadataCopyTagWithPath(
    tempMeta, nil, "dc:title" as CFString
)!
CGImageMetadataSetTagWithPath(
    mutableMetadata, nil, "dc:title" as CFString, tag
)
```

Tags created this way survive `CGImageDestinationCopyImageSource`.

> This affects `dc:title`, `dc:description`, `dc:rights`, and
> `xmpRights:UsageTerms` -- the most important editorial fields. Observed on
> macOS 14 (arm64e); re-validate on target OS versions.

---

## Custom Namespace Registration

```swift
let mutable = CGImageMetadataCreateMutable()
var error: Unmanaged<CFError>?

// Register the namespace -- must be done before writing
let success = CGImageMetadataRegisterNamespaceForPrefix(
    mutable,
    "http://ns.adobe.com/camera-raw-settings/1.0/" as CFString,
    "crs" as CFString,
    &error
)

if !success {
    let err = error?.takeRetainedValue()
    print("Registration failed: \(err?.localizedDescription ?? "unknown")")
}
```

### Registration Requirements

- **Namespace URI** must be a valid XML namespace; by convention ends with `/`
  or `#`
- **Prefix** must be a valid XML name (no spaces, starts with letter or `_`)
- Registration is per-`CGMutableImageMetadata` instance -- must be repeated for
  each new mutable metadata object
- Registering an already-registered namespace with a different prefix will fail
- Registering an already-registered namespace with the same prefix is not an
  error (it is a no-op)
- The 10 Apple-provided namespaces cannot be re-registered with different
  prefixes
- If the URI is not registered but the suggested prefix is already in use for
  a different URI, registration will fail

---

## Enumerating All Tags

Walk the complete XMP tag tree:

```swift
let options = [
    kCGImageMetadataEnumerateRecursively: kCFBooleanTrue!
] as CFDictionary

CGImageMetadataEnumerateTagsUsingBlock(
    metadata, nil, options
) { path, tag in
    let ns = CGImageMetadataTagCopyNamespace(tag) as String? ?? ""
    let name = CGImageMetadataTagCopyName(tag) as String? ?? ""
    let type = CGImageMetadataTagGetType(tag)
    let value = CGImageMetadataTagCopyValue(tag)

    switch type {
    case .string, .default:
        print("\(path): \(value as! CFString)")
    case .arrayUnordered, .arrayOrdered, .alternateArray:
        let elements = value as! [CGImageMetadataTag]
        print("\(path): [\(type)] array with \(elements.count) elements")
    case .alternateText:
        let langs = value as! [String: String]
        print("\(path): langAlt \(langs)")
    case .structure:
        let children = value as! [String: CGImageMetadataTag]
        print("\(path): struct with keys: \(children.keys.sorted())")
    default:
        print("\(path): type=\(type.rawValue)")
    }

    return true  // continue enumeration
}
```

---

## Serializing to/from XMP XML

### Metadata -> XMP XML Bytes

```swift
guard let xmpData = CGImageMetadataCreateXMPData(
    metadata, nil
) else {
    print("Serialization failed")
    return
}
let xmlString = String(data: xmpData as Data, encoding: .utf8)!
```

The second parameter accepts options but is currently unused (pass `nil`).
The output includes the `<?xpacket ...?>` wrapper.

### XMP XML Bytes -> Metadata

```swift
let xmpData = try Data(contentsOf: sidecarURL)
guard let metadata = CGImageMetadataCreateFromXMPData(
    xmpData as CFData
) else {
    print("Parse failed -- invalid XMP")
    return
}
```

`CGImageMetadataCreateFromXMPData` returns `nil` if the data is not valid
XMP/RDF. The packet wrapper (`<?xpacket ...?>`) is optional -- the function
accepts both wrapped and unwrapped XMP. It also accepts XMP with or without
the `<x:xmpmeta>` wrapper.

---

## Bridge Function Examples

### Read EXIF Tag via Property Dictionary Naming

```swift
let source = CGImageSourceCreateWithURL(url as CFURL, nil)!
guard let metadata = CGImageSourceCopyMetadataAtIndex(source, 0, nil) else {
    return
}

// Maps kCGImagePropertyExifDictionary + kCGImagePropertyExifDateTimeOriginal
// to the XMP tag at "exif:DateTimeOriginal"
let tag = CGImageMetadataCopyTagMatchingImageProperty(
    metadata,
    kCGImagePropertyExifDictionary,
    kCGImagePropertyExifDateTimeOriginal
)
```

### Write EXIF Value via Property Dictionary Naming

```swift
let mutable = CGImageMetadataCreateMutableCopy(existingMetadata)!

// Sets the value using EXIF dictionary key naming;
// ImageIO maps this to the correct XMP tag path
CGImageMetadataSetValueMatchingImageProperty(
    mutable,
    kCGImagePropertyExifDictionary,
    kCGImagePropertyExifUserComment,
    "Processed with MyApp" as CFTypeRef
)
```

---

## Format-Specific Behavior

| Format | Lossless XMP Update | Read XMP | Write XMP | Extended XMP |
|--------|---------------------|----------|-----------|--------------|
| **JPEG** | Yes (CopyImageSource) | Yes | Yes | Read: likely; Write: no |
| **TIFF** | Yes (CopyImageSource) | Yes | Yes | N/A |
| **PNG** | Yes (CopyImageSource) | Yes | Yes | N/A |
| **PSD** | Yes (CopyImageSource) | Yes | Yes | N/A |
| **DNG** | Yes (CopyImageSource) | Yes | Yes | N/A |
| **HEIF/HEIC** | No (requires re-encode) | Yes | Yes (AddImageAndMetadata) | N/A |
| **WebP** | No (read-only in ImageIO) | Yes (iOS 14+) | No | N/A |
| **AVIF** | No (read-only in ImageIO) | Yes (iOS 16+) | No | N/A |
| **GIF** | No | No XMP | No | N/A |

---

## Key Differences from Direct XMP

| Aspect | Raw XMP Specification | ImageIO Behavior |
|--------|----------------------|------------------|
| **Namespace registration** | Implicit via `xmlns:` in XML | Explicit -- must call `RegisterNamespaceForPrefix` for non-standard namespaces |
| **langAlt creation** | Build `rdf:Alt` with `xml:lang` attributes | `TagCreate(.alternateText, CFDictionary)` accepted but silently dropped by CopyImageSource -- use workarounds |
| **Extended XMP** | Standard JPEG mechanism for >64 KB | Read support likely; write support absent |
| **Sidecar files** | Standard `.xmp` file alongside image | Not auto-detected; must read manually via `CGImageMetadataCreateFromXMPData` |
| **Packet wrapper** | Required for embedded XMP | Automatically added/stripped; transparent to API consumers |
| **Auto-synthesis** | Not part of XMP spec | ImageIO synthesizes across EXIF/IIM/XMP on read |
| **Prefix normalization** | Prefixes are serialization-only; URI is the identifier | ImageIO normalizes to canonical prefixes (e.g., `xap:` becomes `xmp:` on read) |
| **Qualifier support** | Full qualifier model | Only string-type tags can have qualifiers via `CGImageMetadataTagCopyQualifiers` |
