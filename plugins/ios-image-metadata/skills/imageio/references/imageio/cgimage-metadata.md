# CGImageMetadata — XMP Tree API

The `CGImageMetadata` API provides tree-structured access to XMP metadata.
Unlike the flat property dictionaries (`kCGImagePropertyExifDictionary`, etc.),
this API can read and write **any XMP namespace** — including IPTC Extension,
Dublin Core, XMP Rights, and custom schemas.

All functions in this file require **iOS 7.0+ / macOS 10.8+**.

---

## Container Types

| Type | Purpose |
|------|---------|
| `CGImageMetadata` | Immutable XMP metadata tree |
| `CGMutableImageMetadata` | Mutable XMP metadata tree (subtype of CGImageMetadata) |

---

## Container Functions

### Creation

| Function | Purpose |
|----------|---------|
| `CGImageMetadataCreateMutable()` | Create empty mutable container |
| `CGImageMetadataCreateMutableCopy(_:)` | Deep mutable copy of existing metadata |
| `CGImageMetadataGetTypeID()` | Core Foundation type ID |

### XMP Serialization

| Function | Purpose |
|----------|---------|
| `CGImageMetadataCreateFromXMPData(_:)` | Parse XMP XML bytes → `CGImageMetadata` |
| `CGImageMetadataCreateXMPData(_:_:)` | Serialize metadata → XMP XML bytes |

### Reading Tags

| Function | Purpose |
|----------|---------|
| `CGImageMetadataCopyTags(_:)` | Array of all top-level `CGImageMetadataTag` objects |
| `CGImageMetadataCopyTagWithPath(_:_:_:)` | Get tag at XPath-like path |
| `CGImageMetadataCopyStringValueWithPath(_:_:_:)` | Get string value at path (convenience) |
| `CGImageMetadataEnumerateTagsUsingBlock(_:_:_:_:)` | Iterate tags with callback |

### Writing Tags (requires `CGMutableImageMetadata`)

| Function | Purpose |
|----------|---------|
| `CGImageMetadataSetTagWithPath(_:_:_:_:)` | Set/create tag at path |
| `CGImageMetadataSetValueWithPath(_:_:_:_:)` | Set value at path (creates intermediate tags) |
| `CGImageMetadataRemoveTagWithPath(_:_:_:)` | Remove tag at path |

### Namespace Registration

| Function | Purpose |
|----------|---------|
| `CGImageMetadataRegisterNamespaceForPrefix(_:_:_:_:)` | Associate namespace URI with prefix |

### Bridge Functions (Property Dictionary ↔ XMP)

| Function | Purpose |
|----------|---------|
| `CGImageMetadataCopyTagMatchingImageProperty(_:_:_:)` | Map property dict key → XMP tag |
| `CGImageMetadataSetValueMatchingImageProperty(_:_:_:_:)` | Set value using property dict naming |

> **Read-side auto-synthesis (observed):** Apple currently synthesizes metadata across
> APIs on read. An image with only IPTC IIM data (no XMP packet) will still
> return XMP tags via `CGImageSourceCopyMetadataAtIndex` — Apple promotes IIM
> to synthetic XMP tags, including proper `langAlt` structures for `dc:title`,
> `dc:description`, etc. Conversely, an image with only XMP will return
> synthesized IIM values via `CGImageSourceCopyPropertiesAtIndex`. The bridge
> API works in both cases. This means the two APIs are not siloed — either read
> path sees metadata from both sources. Observed on macOS 14; re-validate on
> target OS versions because Apple does not document this as a strict contract.

---

## CGImageMetadataTag

A single tag in the XMP tree, carrying a namespace, prefix, name, type, and
value.

### Tag Functions

| Function | Purpose |
|----------|---------|
| `CGImageMetadataTagCreate(_:_:_:_:_:)` | Create tag (namespace, prefix, name, type, value) |
| `CGImageMetadataTagCopyNamespace(_:)` | Get namespace URI |
| `CGImageMetadataTagCopyPrefix(_:)` | Get namespace prefix |
| `CGImageMetadataTagCopyName(_:)` | Get property name |
| `CGImageMetadataTagCopyValue(_:)` | Get value (CFTypeRef) |
| `CGImageMetadataTagGetType(_:)` | Get type enum |
| `CGImageMetadataTagCopyQualifiers(_:)` | Get qualifier tags (string-type only) |
| `CGImageMetadataTagGetTypeID()` | Core Foundation type ID |

### CGImageMetadataType Enum

| Value | Constant | XMP Equivalent |
|-------|----------|----------------|
| -1 | `kCGImageMetadataTypeInvalid` | — |
| 0 | `kCGImageMetadataTypeDefault` | Simple scalar |
| 1 | `kCGImageMetadataTypeString` | Text string |
| 2 | `kCGImageMetadataTypeArrayUnordered` | XMP `rdf:Bag` |
| 3 | `kCGImageMetadataTypeArrayOrdered` | XMP `rdf:Seq` |
| 4 | `kCGImageMetadataTypeAlternateArray` | XMP `rdf:Alt` |
| 5 | `kCGImageMetadataTypeAlternateText` | Alternate text (language variants) |
| 6 | `kCGImageMetadataTypeStructure` | XMP Struct |

> Only string-type values (`kCGImageMetadataTypeString`) can have qualifiers.

---

## Namespace Constants (`kCGImageMetadataNamespace*`)

These namespaces are **automatically registered** by Apple. Tags using these
prefixes can be read and written without calling
`CGImageMetadataRegisterNamespaceForPrefix`.

| Constant | Namespace URI | Prefix | Schema |
|----------|---------------|--------|--------|
| `kCGImageMetadataNamespaceExif` | `http://ns.adobe.com/exif/1.0/` | `exif` | EXIF |
| `kCGImageMetadataNamespaceExifAux` | `http://ns.adobe.com/exif/1.0/aux/` | `aux` | EXIF Auxiliary |
| `kCGImageMetadataNamespaceExifEX` | `http://cipa.jp/exif/1.0/` | `exifEX` | EXIF Extension (CIPA) |
| `kCGImageMetadataNamespaceDublinCore` | `http://purl.org/dc/elements/1.1/` | `dc` | Dublin Core |
| `kCGImageMetadataNamespaceIPTCCore` | `http://iptc.org/std/Iptc4xmpCore/1.0/xmlns/` | `Iptc4xmpCore` | IPTC Core |
| `kCGImageMetadataNamespaceIPTCExtension` | `http://iptc.org/std/Iptc4xmpExt/2008-02-29/` | `Iptc4xmpExt` | IPTC Extension |
| `kCGImageMetadataNamespacePhotoshop` | `http://ns.adobe.com/photoshop/1.0/` | `photoshop` | Adobe Photoshop |
| `kCGImageMetadataNamespaceTIFF` | `http://ns.adobe.com/tiff/1.0/` | `tiff` | TIFF |
| `kCGImageMetadataNamespaceXMPBasic` | `http://ns.adobe.com/xap/1.0/` | `xmp` | XMP Basic |
| `kCGImageMetadataNamespaceXMPRights` | `http://ns.adobe.com/xap/1.0/rights/` | `xmpRights` | XMP Rights |

### Namespaces That Require Manual Registration

Any namespace not listed above must be registered before writing. Common
namespaces that require registration:

| Prefix | Namespace URI | Schema |
|--------|---------------|--------|
| `plus` | `http://ns.useplus.org/ldf/xmp/1.0/` | PLUS (licensing) |
| `xmpMM` | `http://ns.adobe.com/xap/1.0/mm/` | XMP Media Management |
| `xmpDM` | `http://ns.adobe.com/xmp/1.0/DynamicMedia/` | XMP Dynamic Media |
| `crs` | `http://ns.adobe.com/camera-raw-settings/1.0/` | Camera Raw Settings |
| `dng` | `http://ns.adobe.com/dng/1.0/` | DNG |
| `stRef` | `http://ns.adobe.com/xap/1.0/sType/ResourceRef#` | XMP Resource Reference |
| `stEvt` | `http://ns.adobe.com/xap/1.0/sType/ResourceEvent#` | XMP Resource Event |

If you attempt to write a tag with an unregistered prefix,
`CGImageMetadataSetTagWithPath` returns `false` silently.

---

## Path Syntax

Paths use an XPath-like syntax where the prefix identifies the XMP namespace
and the name identifies the property within that namespace.

### Simple properties

Format: `"prefix:name"`

```
"dc:title"                    — Dublin Core title
"exif:DateTimeOriginal"       — EXIF original datetime
"photoshop:City"              — Photoshop city
"Iptc4xmpCore:CountryCode"   — IPTC Core country code
```

### Nested structure properties

Format: `"prefix:parent/prefix:child"` — separated by `/`

```
"Iptc4xmpCore:CreatorContactInfo/Iptc4xmpCore:CiEmailWork"   — email within contact info struct
"Iptc4xmpCore:CreatorContactInfo/Iptc4xmpCore:CiAdrCity"     — city within contact info struct
```

The parent tag must be of type `.structure`. Each path segment uses its own
namespace prefix (the child may use a different prefix than the parent).

### Array element access

Format: `"prefix:name[index]"` — **1-based** index

```
"dc:subject[1]"               — first keyword in the bag
"dc:creator[2]"               — second creator in the sequence
```

Accessing the array tag itself (without index) returns the array container tag.
The value of an array tag is a `CFArray` of `CGImageMetadataTag` elements.

### Nested paths into array elements

```
"Iptc4xmpExt:PersonInImageWDetails[1]/Iptc4xmpExt:PersonName"
```

This accesses the `PersonName` property of the first element in the
`PersonInImageWDetails` array, where each element is a structure.

---

## RDF Container Types (Arrays)

XMP defines three container types for multi-value properties. The container
type is specified when creating the array tag via `CGImageMetadataTagCreate`.

| CGImageMetadataType | XMP Container | Semantics | Example Properties |
|---------------------|---------------|-----------|-------------------|
| `.arrayUnordered` | `rdf:Bag` | Unordered set — order has no meaning | `dc:subject` (keywords), `Iptc4xmpExt:PersonInImage` |
| `.arrayOrdered` | `rdf:Seq` | Ordered sequence — order is meaningful | `dc:creator` (first creator is primary) |
| `.alternateArray` | `rdf:Alt` | Alternatives — each element is a variant | Rarely used directly |
| `.alternateText` | `rdf:Alt` with `xml:lang` qualifiers | Language alternatives | `dc:title`, `dc:description`, `dc:rights` |

### Alternate text

Alternate text is a special case of `rdf:Alt` where each element has an
`xml:lang` qualifier. The value passed to `CGImageMetadataTagCreate` is a
`CFDictionary` mapping language codes to strings:

```swift
let tag = CGImageMetadataTagCreate(
    kCGImageMetadataNamespaceDublinCore,
    kCGImageMetadataPrefixDublinCore,
    "title" as CFString,
    .alternateText,
    ["x-default": "Sunset over the ocean", "de": "Sonnenuntergang über dem Meer"] as CFDictionary
)
```

The `"x-default"` key is the language-independent default value. Most
applications read only `"x-default"`.

> **Warning — CopyImageSource silently drops TagCreate alternateText tags.**
> Tags created via `CGImageMetadataTagCreate(.alternateText, CFDictionary)` are
> accepted by `SetTagWithPath` (returns `true`) but are **silently discarded**
> by `CGImageDestinationCopyImageSource`. The tag will not appear in the output
> file's XMP, and no IIM field will be created. This is undocumented Apple
> behavior, not a user error.
>
> **Working alternatives:**
>
> 1. **`SetValueWithPath` with a plain string** — Apple auto-detects the field
>    should be `langAlt` and creates a proper internal structure. Limited to a
>    single `x-default` language:
>    ```swift
>    CGImageMetadataSetValueWithPath(metadata, nil, "dc:title" as CFString, "My Title" as CFString)
>    ```
>
> 2. **Parse from XMP snippet** — for multi-language support, build an
>    XMP/RDF XML string and parse it with `CGImageMetadataCreateFromXMPData`.
>    The resulting tag has the correct internal structure and survives
>    CopyImageSource:
>    ```swift
>    let xmpSnippet = """
>        <x:xmpmeta xmlns:x="adobe:ns:meta/">
>        <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
>        <rdf:Description rdf:about="" xmlns:dc="http://purl.org/dc/elements/1.1/">
>        <dc:title><rdf:Alt>
>        <rdf:li xml:lang="x-default">English title</rdf:li>
>        <rdf:li xml:lang="de">Deutscher Titel</rdf:li>
>        </rdf:Alt></dc:title>
>        </rdf:Description></rdf:RDF></x:xmpmeta>
>        """
>    let tempMeta = CGImageMetadataCreateFromXMPData(Data(xmpSnippet.utf8) as CFData)!
>    let tag = CGImageMetadataCopyTagWithPath(tempMeta, nil, "dc:title" as CFString)!
>    CGImageMetadataSetTagWithPath(mutableMetadata, nil, "dc:title" as CFString, tag)
>    ```
>
> This affects `dc:title`, `dc:description`, and `dc:rights` — the three most
> important IPTC fields that use the `langAlt` type. Observed on macOS 14
> (arm64e); re-validate on target OS versions.

---

## Building Complex Tags

### Scalar tag

The simplest case — a single string, number, or boolean value:

```swift
let tag = CGImageMetadataTagCreate(
    kCGImageMetadataNamespacePhotoshop,   // namespace URI
    kCGImageMetadataPrefixPhotoshop,      // prefix
    "City" as CFString,                   // name
    .string,                             // type
    "Berlin" as CFString                 // value
)!
```

### Structure tag

A structure tag contains named child tags. The value passed to
`CGImageMetadataTagCreate` is a `CFDictionary` where keys are the child
property names (without prefix) and values are `CGImageMetadataTag` objects:

```swift
// Build child tags
let emailTag = CGImageMetadataTagCreate(
    kCGImageMetadataNamespaceIPTCCore,
    kCGImageMetadataPrefixIPTCCore,
    "CiEmailWork" as CFString,
    .string,
    "photographer@example.com" as CFString
)!

let cityTag = CGImageMetadataTagCreate(
    kCGImageMetadataNamespaceIPTCCore,
    kCGImageMetadataPrefixIPTCCore,
    "CiAdrCity" as CFString,
    .string,
    "New York" as CFString
)!

// Build the structure tag — keys are child names, values are child tags
let contactInfo = CGImageMetadataTagCreate(
    kCGImageMetadataNamespaceIPTCCore,
    kCGImageMetadataPrefixIPTCCore,
    "CreatorContactInfo" as CFString,
    .structure,
    ["CiEmailWork": emailTag, "CiAdrCity": cityTag] as CFDictionary
)!

// Set on metadata tree
CGImageMetadataSetTagWithPath(mutable, nil, "Iptc4xmpCore:CreatorContactInfo" as CFString, contactInfo)
```

When reading a structure tag back, `CGImageMetadataTagCopyValue` returns a
`CFDictionary` of `[String: CGImageMetadataTag]`, where each key is the child
name (without prefix).

### Array of scalars

An array tag contains ordered or unordered child tags. The value is a
`CFArray` of `CGImageMetadataTag` objects:

```swift
// Build element tags — each keyword is its own tag
let keywords = ["sunset", "ocean", "photography"].map { keyword in
    CGImageMetadataTagCreate(
        kCGImageMetadataNamespaceDublinCore,
        kCGImageMetadataPrefixDublinCore,
        "subject" as CFString,      // each element uses the parent's name
        .string,
        keyword as CFString
    )!
}

// Build the bag (unordered array)
let subjectTag = CGImageMetadataTagCreate(
    kCGImageMetadataNamespaceDublinCore,
    kCGImageMetadataPrefixDublinCore,
    "subject" as CFString,
    .arrayUnordered,                // rdf:Bag
    keywords as CFArray
)!

CGImageMetadataSetTagWithPath(mutable, nil, "dc:subject" as CFString, subjectTag)
```

When reading an array tag back, `CGImageMetadataTagCopyValue` returns a
`CFArray` of `CGImageMetadataTag` objects.

### Array of structures

Combine the structure and array patterns. Each array element is a structure
tag containing child tags:

```swift
// Build one person structure
func makePersonTag(name: String, description: String) -> CGImageMetadataTag {
    let nameTag = CGImageMetadataTagCreate(
        kCGImageMetadataNamespaceIPTCExtension,
        kCGImageMetadataPrefixIPTCExtension,
        "PersonName" as CFString,
        .string,
        name as CFString
    )!

    let descTag = CGImageMetadataTagCreate(
        kCGImageMetadataNamespaceIPTCExtension,
        kCGImageMetadataPrefixIPTCExtension,
        "PersonDescription" as CFString,
        .string,
        description as CFString
    )!

    return CGImageMetadataTagCreate(
        kCGImageMetadataNamespaceIPTCExtension,
        kCGImageMetadataPrefixIPTCExtension,
        "PersonInImageWDetails" as CFString,
        .structure,
        ["PersonName": nameTag, "PersonDescription": descTag] as CFDictionary
    )!
}

// Build array of person structures
let people = [
    makePersonTag(name: "Jane Doe", description: "Subject"),
    makePersonTag(name: "John Smith", description: "Bystander")
]

let arrayTag = CGImageMetadataTagCreate(
    kCGImageMetadataNamespaceIPTCExtension,
    kCGImageMetadataPrefixIPTCExtension,
    "PersonInImageWDetails" as CFString,
    .arrayUnordered,
    people as CFArray
)!

CGImageMetadataSetTagWithPath(mutable, nil, "Iptc4xmpExt:PersonInImageWDetails" as CFString, arrayTag)
```

### Reading complex tags

When reading back, inspect `CGImageMetadataTagGetType` to determine how to
interpret the value from `CGImageMetadataTagCopyValue`:

| Tag type | Value type returned |
|----------|--------------------|
| `.string` / `.default` | `CFString` |
| `.arrayUnordered` / `.arrayOrdered` / `.alternateArray` | `CFArray` of `CGImageMetadataTag` |
| `.alternateText` | `CFDictionary` of `[String: String]` (lang → text) |
| `.structure` | `CFDictionary` of `[String: CGImageMetadataTag]` (name → tag) |

---

## Embedded Metadata vs XMP Sidecar Files

`CGImageMetadata` can work with metadata in two locations: **embedded** inside
an image file, or in a standalone **XMP sidecar** file (`.xmp`).

### Reading embedded metadata

Extract metadata from an image file using `CGImageSource`:

```swift
let source = CGImageSourceCreateWithURL(imageURL as CFURL, nil)!
guard let metadata = CGImageSourceCopyMetadataAtIndex(source, 0, nil) else { return }

// Navigate to specific tags
let city = CGImageMetadataCopyStringValueWithPath(metadata, nil, "photoshop:City" as CFString)
```

### Writing embedded metadata (lossless)

Update metadata inside an existing image without re-encoding pixels:

```swift
let source = CGImageSourceCreateWithURL(inputURL as CFURL, nil)!
let dest = CGImageDestinationCreateWithURL(outputURL as CFURL, CGImageSourceGetType(source)!, 1, nil)!

// Build metadata
let mutable = CGImageMetadataCreateMutable()
// ... add tags ...

let options: [CFString: Any] = [
    kCGImageDestinationMetadata: mutable,
    kCGImageDestinationMergeMetadata: kCFBooleanTrue!
]

var error: Unmanaged<CFError>?
CGImageDestinationCopyImageSource(dest, source, options as CFDictionary, &error)
```

> Lossless update via `CGImageDestinationCopyImageSource` is supported for
> **JPEG, PNG, PSD, and TIFF** only. HEIC/HEIF requires full re-encoding via
> `CGImageDestinationAddImageAndMetadata`.

### Writing embedded metadata (with re-encoding)

For formats that don't support lossless copy, or when also writing pixels:

```swift
let dest = CGImageDestinationCreateWithURL(url as CFURL, "public.heic" as CFString, 1, nil)!

let mutable = CGImageMetadataCreateMutable()
// ... add tags ...

CGImageDestinationAddImageAndMetadata(dest, cgImage, mutable, nil)
CGImageDestinationFinalize(dest)
```

### Reading an XMP sidecar file

Parse a standalone `.xmp` file into a `CGImageMetadata` tree:

```swift
let xmpData = try Data(contentsOf: sidecarURL)
guard let metadata = CGImageMetadataCreateFromXMPData(xmpData as CFData) else { return }

// Use the same path-based API to read tags
let title = CGImageMetadataCopyStringValueWithPath(metadata, nil, "dc:title" as CFString)
```

### Writing an XMP sidecar file

Serialize a `CGImageMetadata` tree to XMP XML and write it to disk:

```swift
let mutable = CGImageMetadataCreateMutable()
// ... add tags ...

guard let xmpData = CGImageMetadataCreateXMPData(mutable, nil) else { return }
try (xmpData as Data).write(to: sidecarURL)
```

### Merge metadata: read from sidecar, apply to image

```swift
// Read sidecar
let xmpData = try Data(contentsOf: sidecarURL)
guard let sidecarMetadata = CGImageMetadataCreateFromXMPData(xmpData as CFData) else { return }

// Apply to image (lossless)
let source = CGImageSourceCreateWithURL(imageURL as CFURL, nil)!
let dest = CGImageDestinationCreateWithURL(outputURL as CFURL, CGImageSourceGetType(source)!, 1, nil)!

let options: [CFString: Any] = [
    kCGImageDestinationMetadata: sidecarMetadata,
    kCGImageDestinationMergeMetadata: kCFBooleanTrue!
]

var error: Unmanaged<CFError>?
CGImageDestinationCopyImageSource(dest, source, options as CFDictionary, &error)
```

---

## Enumerating All Tags

`CGImageMetadataEnumerateTagsUsingBlock` walks the tag tree recursively.
The callback receives each tag's path and the tag itself:

```swift
let source = CGImageSourceCreateWithURL(url as CFURL, nil)!
guard let metadata = CGImageSourceCopyMetadataAtIndex(source, 0, nil) else { return }

let options = [kCGImageMetadataEnumerateRecursively: kCFBooleanTrue!] as CFDictionary

CGImageMetadataEnumerateTagsUsingBlock(metadata, nil, options) { path, tag in
    let type = CGImageMetadataTagGetType(tag)
    let value = CGImageMetadataTagCopyValue(tag)

    switch type {
    case .string:
        print("\(path): \(value as! CFString)")
    case .arrayUnordered, .arrayOrdered:
        let elements = value as! [CGImageMetadataTag]
        print("\(path): array with \(elements.count) elements")
    case .structure:
        let children = value as! [String: CGImageMetadataTag]
        print("\(path): struct with keys \(children.keys)")
    case .alternateText:
        let langs = value as! [String: String]
        print("\(path): alt-text \(langs)")
    default:
        print("\(path): \(type.rawValue)")
    }

    return true  // continue enumeration
}
```

---

## Usage Examples

### Register a custom namespace and write a tag

```swift
let mutable = CGImageMetadataCreateMutable()
var error: Unmanaged<CFError>?

// Must register before writing — this namespace has no Apple-provided constant
CGImageMetadataRegisterNamespaceForPrefix(
    mutable,
    "http://ns.useplus.org/ldf/xmp/1.0/" as CFString,
    "plus" as CFString,
    &error
)

let tag = CGImageMetadataTagCreate(
    "http://ns.useplus.org/ldf/xmp/1.0/" as CFString,
    "plus" as CFString,
    "Version" as CFString,
    .string,
    "2.0" as CFString
)!

CGImageMetadataSetTagWithPath(mutable, nil, "plus:Version" as CFString, tag)
```

### Bridge: Read EXIF tag via property dictionary naming

```swift
let source = CGImageSourceCreateWithURL(url as CFURL, nil)!
guard let metadata = CGImageSourceCopyMetadataAtIndex(source, 0, nil) else { return }

// Maps kCGImagePropertyExifDictionary + kCGImagePropertyExifDateTimeOriginal
// to the equivalent XMP tag at "exif:DateTimeOriginal"
let tag = CGImageMetadataCopyTagMatchingImageProperty(
    metadata,
    kCGImagePropertyExifDictionary,
    kCGImagePropertyExifDateTimeOriginal
)
```

### Bridge: Set EXIF value via property dictionary naming

```swift
let mutable = CGImageMetadataCreateMutableCopy(existingMetadata)!

CGImageMetadataSetValueMatchingImageProperty(
    mutable,
    kCGImagePropertyExifDictionary,
    kCGImagePropertyExifUserComment,
    "Processed with MyApp" as CFTypeRef
)
```
