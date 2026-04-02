# XMP Data Model and Serialization

> Part of [XMP Reference](README.md)

The XMP data model defines how metadata is structured, typed, and serialized.
This document covers the abstract data model, RDF/XML serialization format,
XMP packet structure, and value types.

---

## Data Model Overview

XMP uses a subset of the W3C Resource Description Framework (RDF) to model
metadata. At its core, XMP makes **statements about resources** using a
subject-predicate-object model:

- **Resource** — the thing being described (an image, document, etc.)
- **Property** — a named attribute of the resource (e.g., `dc:creator`)
- **Value** — the property's value (a string, structure, or array)

All properties are organized into **namespaces**, each identified by a unique
URI and a short prefix. This prevents name collisions between different
metadata schemas.

### Key Principles

- **Namespace isolation** — a property is uniquely identified by its namespace
  URI plus its local name; the prefix is just a serialization convenience
- **Single resource per packet** — an XMP packet describes exactly one resource
  (the file it is embedded in, identified by `rdf:about=""`)
- **No binary values** — all values are serialized as XML text; numeric types
  are string-encoded and must be parsed by consumers
- **Unicode required** — XMP packets must be encoded in UTF-8 (preferred),
  UTF-16, or UTF-32

### Property Forms

Every XMP property value takes one of three forms:

| Form | Description | Example |
|------|-------------|---------|
| **Simple** | A single scalar value (text, integer, date, boolean, URI) | `xmp:Rating` = `"5"` |
| **Structure** | A set of named fields, each with its own value | `Iptc4xmpCore:CreatorContactInfo` with fields `CiEmailWork`, `CiAdrCity`, etc. |
| **Array** | An ordered or unordered collection of values | `dc:subject` = `["sunset", "ocean", "beach"]` |

### Array Variants

| Variant | RDF Element | Semantics | CGImageMetadataType |
|---------|-------------|-----------|---------------------|
| **Unordered (Bag)** | `rdf:Bag` | Set — order has no meaning, duplicates allowed | `.arrayUnordered` |
| **Ordered (Seq)** | `rdf:Seq` | Sequence — order is meaningful | `.arrayOrdered` |
| **Alternative (Alt)** | `rdf:Alt` | Alternatives — each item is a variant of the same value | `.alternateArray` |
| **Language Alternative** | `rdf:Alt` with `xml:lang` | Text alternatives by language; first item is `"x-default"` | `.alternateText` |

---

## Simple Value Types

XMP defines these core value types for simple properties:

| XMP Type | Description | Example |
|----------|-------------|---------|
| **Text** | Unicode string (UTF-8) | `"Sunset over the ocean"` |
| **Integer** | Signed 32-bit integer | `"5"` |
| **Real** | IEEE 754 double | `"3.14"` |
| **Boolean** | `"True"` or `"False"` | `"True"` |
| **Date** | ISO 8601 subset: `YYYY[-MM[-DD[THH:MM[:SS[.sss]][TZD]]]]` | `"2024-06-15T14:30:00+05:30"` |
| **URI** | Absolute URI | `"https://example.com/license"` |
| **Rational** | Two integers separated by `/` (EXIF rationals in XMP) | `"1/250"` |
| **MIMEType** | IANA media type | `"image/jpeg"` |
| **AgentName** | Free-form creator tool name | `"Adobe Photoshop 25.0"` |
| **ProperName** | Proper noun text | `"Jane Photographer"` |
| **RenditionClass** | Rendition designator | `"default"` |
| **GUID** | Globally unique identifier string | `"xmp.did:12345678-1234-1234-1234-123456789abc"` |
| **Locale** | RFC 3066 / BCP 47 language tag | `"en-US"` |
| **open Choice** | One of a predefined set, or any other value | `"created"` (one of defined values, or custom) |
| **closed Choice** | Exactly one of a predefined set | `"pixel"`, `"inch"`, `"mm"` |

> All XMP values are serialized as text in XML. Numeric types are
> string-encoded; consumers must parse them. There is no binary encoding.

### Date Format Details

XMP dates follow an ISO 8601 subset with variable precision:

```
YYYY                           — year only
YYYY-MM                        — year and month
YYYY-MM-DD                     — full date
YYYY-MM-DDThh:mm               — date + time (minute precision)
YYYY-MM-DDThh:mm:ss            — date + time (second precision)
YYYY-MM-DDThh:mm:ss.sTZD      — date + time + subseconds + timezone
```

Where `TZD` is a time zone designator: `Z` (UTC), `+hh:mm`, or `-hh:mm`.

> **Important:** A date without a timezone designator is "local time" with no
> information about which timezone. When mapping from EXIF (which stores naive
> datetimes), the separate `OffsetTime*` EXIF tags are folded into the XMP
> datetime value, producing a timezone-aware string.

---

## Qualifiers

Qualifiers are additional metadata about a property value, rather than about
the resource itself. They refine or annotate a property.

### `xml:lang` Qualifier

The most important qualifier. Used on language alternative arrays (`rdf:Alt`)
to specify the language of each item:

```xml
<dc:title>
  <rdf:Alt>
    <rdf:li xml:lang="x-default">Sunset over the ocean</rdf:li>
    <rdf:li xml:lang="de">Sonnenuntergang ueber dem Meer</rdf:li>
    <rdf:li xml:lang="fr">Coucher de soleil sur l'ocean</rdf:li>
  </rdf:Alt>
</dc:title>
```

Rules for `xml:lang` in XMP:
- Every item in a language alternative array **must** have an `xml:lang`
  qualifier
- Each `xml:lang` value **must** be unique within the array
- The first item **should** use `"x-default"` as the language-neutral default
- Values follow RFC 3066 / BCP 47 language tags (e.g., `"en"`, `"en-US"`,
  `"de"`, `"ja"`, `"x-default"`)

### `rdf:type` Qualifier

Occasionally used to assert the RDF type of a resource. Rarely encountered in
photography metadata.

### General Qualifiers

For qualifiers other than `xml:lang`, RDF serialization wraps the qualified
property in a struct-like construct with a special `rdf:value` field containing
the actual value, and additional fields for each qualifier:

```xml
<exif:UserComment rdf:parseType="Resource">
  <rdf:value>Processed with custom workflow</rdf:value>
  <xmpNote:HasExtendedXMP>true</xmpNote:HasExtendedXMP>
</exif:UserComment>
```

> In Apple's ImageIO, only string-type tags (`kCGImageMetadataTypeString`) can
> have qualifiers, accessible via `CGImageMetadataTagCopyQualifiers`.

---

## RDF/XML Serialization

XMP uses a subset of W3C RDF/XML. A single XMP dataset is serialized as one
`rdf:RDF` element containing one or more `rdf:Description` elements that
describe a single resource (the file).

### Minimal XMP Document

```xml
<x:xmpmeta xmlns:x="adobe:ns:meta/">
  <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <rdf:Description rdf:about=""
        xmlns:dc="http://purl.org/dc/elements/1.1/"
        xmlns:xmp="http://ns.adobe.com/xap/1.0/">
      <dc:format>image/jpeg</dc:format>
      <xmp:Rating>5</xmp:Rating>
    </rdf:Description>
  </rdf:RDF>
</x:xmpmeta>
```

Key points:
- `<x:xmpmeta>` is the root wrapper (namespace `adobe:ns:meta/`)
- `<rdf:RDF>` contains the RDF graph
- `<rdf:Description rdf:about="">` describes the containing file (empty
  `rdf:about` means "this resource")
- Namespace declarations appear as `xmlns:prefix="URI"` attributes
- Simple properties are child elements of `rdf:Description`

### Well-Formedness Requirements

An XMP packet must conform to the well-formedness requirements of the XML
specification, with these exceptions and additions:

- The XML declaration (`<?xml version="1.0"?>`) is optional within an XMP
  packet — the `<?xpacket ...?>` header serves a different purpose (packet
  identification and scanning, not XML version declaration)
- The XMP packet must be valid RDF as well as valid XML
- Different packets in the same file may use different character encodings
- Packets must not nest inside each other

### Serialization of Property Forms

#### Simple Properties

Simple values are serialized either as child elements or as attributes of
`rdf:Description`:

```xml
<!-- As child element (preferred) -->
<xmp:Rating>5</xmp:Rating>

<!-- As attribute (compact form) -->
<rdf:Description xmp:Rating="5"/>
```

#### Structure Properties

Structures are serialized with `rdf:parseType="Resource"` or as a nested
`rdf:Description`:

```xml
<!-- Using parseType="Resource" (preferred, more compact) -->
<Iptc4xmpCore:CreatorContactInfo rdf:parseType="Resource">
  <Iptc4xmpCore:CiEmailWork>photo@example.com</Iptc4xmpCore:CiEmailWork>
  <Iptc4xmpCore:CiAdrCity>New York</Iptc4xmpCore:CiAdrCity>
</Iptc4xmpCore:CreatorContactInfo>

<!-- Using nested rdf:Description (equivalent) -->
<Iptc4xmpCore:CreatorContactInfo>
  <rdf:Description>
    <Iptc4xmpCore:CiEmailWork>photo@example.com</Iptc4xmpCore:CiEmailWork>
    <Iptc4xmpCore:CiAdrCity>New York</Iptc4xmpCore:CiAdrCity>
  </rdf:Description>
</Iptc4xmpCore:CreatorContactInfo>
```

#### Unordered Array (Bag)

```xml
<dc:subject>
  <rdf:Bag>
    <rdf:li>sunset</rdf:li>
    <rdf:li>ocean</rdf:li>
    <rdf:li>photography</rdf:li>
  </rdf:Bag>
</dc:subject>
```

#### Ordered Array (Seq)

```xml
<dc:creator>
  <rdf:Seq>
    <rdf:li>Jane Photographer</rdf:li>
    <rdf:li>John Editor</rdf:li>
  </rdf:Seq>
</dc:creator>
```

#### Language Alternative (Alt with xml:lang)

```xml
<dc:description>
  <rdf:Alt>
    <rdf:li xml:lang="x-default">A beautiful sunset</rdf:li>
    <rdf:li xml:lang="es">Una hermosa puesta de sol</rdf:li>
  </rdf:Alt>
</dc:description>
```

#### Nested Structures in Arrays

```xml
<Iptc4xmpExt:LocationShown>
  <rdf:Bag>
    <rdf:li rdf:parseType="Resource">
      <Iptc4xmpExt:City>Paris</Iptc4xmpExt:City>
      <Iptc4xmpExt:CountryName>France</Iptc4xmpExt:CountryName>
      <Iptc4xmpExt:CountryCode>FR</Iptc4xmpExt:CountryCode>
    </rdf:li>
  </rdf:Bag>
</Iptc4xmpExt:LocationShown>
```

### Multiple `rdf:Description` Elements

A single `rdf:RDF` may contain multiple `rdf:Description` elements, all
describing the same resource. This is semantically equivalent to a single
`rdf:Description` with all properties merged:

```xml
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description rdf:about=""
      xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:format>image/jpeg</dc:format>
  </rdf:Description>
  <rdf:Description rdf:about=""
      xmlns:xmp="http://ns.adobe.com/xap/1.0/">
    <xmp:Rating>5</xmp:Rating>
  </rdf:Description>
</rdf:RDF>
```

Tools that group properties by namespace into separate `rdf:Description`
elements are common (e.g., Adobe Lightroom). Readers must merge all
`rdf:Description` blocks with the same `rdf:about` value.

---

## XMP Packet Structure

When embedded in a file, XMP is wrapped in an **XMP packet** consisting of
four parts: header, body (the `x:xmpmeta` element), padding, and trailer.

### Packet Format

```
<?xpacket begin="<BOM>" id="W5M0MpCehiHzreSzNTczkc9d"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/">
  <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <rdf:Description rdf:about="" ...>
      ... properties ...
    </rdf:Description>
  </rdf:RDF>
</x:xmpmeta>
                                                                        [padding whitespace]
<?xpacket end="w"?>
```

### Header (Processing Instruction)

```
<?xpacket begin="﻿" id="W5M0MpCehiHzreSzNTczkc9d"?>
```

| Attribute | Value | Purpose |
|-----------|-------|---------|
| `begin` | U+FEFF (Unicode BOM) or empty string | Indicates encoding. U+FEFF in UTF-8 = `EF BB BF`. Empty string = UTF-8 (backward compatibility) |
| `id` | `W5M0MpCehiHzreSzNTczkc9d` | **Fixed magic string** — identifies this as an XMP packet. Same value for all XMP packets ever written |

The `id` value `W5M0MpCehiHzreSzNTczkc9d` is a constant defined by the XMP
specification. It serves as a signature that allows packet scanners to locate
XMP data within arbitrary binary files by searching for this byte sequence.

### Body

The `<x:xmpmeta>` element wrapping the `<rdf:RDF>` serialization. This is the
actual metadata content. The `<x:xmpmeta>` wrapper is technically optional
(older tools may use `<xap:xmpmeta>` or omit it entirely), but modern tools
always include it and readers should expect it.

### Padding

After the closing `</x:xmpmeta>` tag, packets typically include **XML
whitespace** (spaces or newlines) as padding. This padding serves a critical
purpose:

- **In-place editing** — tools can modify XMP without rewriting the entire
  file. If modified XMP is smaller than the original, it fits within the
  existing allocation. If larger, the padding absorbs the growth.
- Typical padding: 2-4 KB of space characters (0x20)
- Padding is pure XML whitespace and is ignored by parsers
- When all padding is consumed, in-place editing is no longer possible and the
  tool must rewrite the file

### Trailer (Processing Instruction)

```
<?xpacket end="w"?>
```

| Value | Meaning |
|-------|---------|
| `end="w"` | Writable — tools may modify the packet in place |
| `end="r"` | Read-only — tools must not modify the packet in place (used when integrity checks protect the data, e.g., PNG CRC) |

---

## Character Encoding

XMP packets **must** be encoded in Unicode. The encoding is determined by the
BOM in the `begin` attribute:

| BOM Bytes | Encoding |
|-----------|----------|
| `EF BB BF` | UTF-8 |
| `FE FF` | UTF-16 Big-Endian |
| `FF FE` | UTF-16 Little-Endian |
| `00 00 FE FF` | UTF-32 Big-Endian |
| `FF FE 00 00` | UTF-32 Little-Endian |
| (empty) | UTF-8 (default) |

> **In practice, UTF-8 is used almost universally.** Tools should always write
> UTF-8. Some older tools wrote UTF-16, but this is rare. The XMP Toolkit SDK
> normalizes all input to UTF-8 internally.

---

## Complete Serialization Example

A realistic XMP packet for a photograph:

```xml
<?xpacket begin="﻿" id="W5M0MpCehiHzreSzNTczkc9d"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/">
  <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <rdf:Description rdf:about=""
        xmlns:dc="http://purl.org/dc/elements/1.1/"
        xmlns:xmp="http://ns.adobe.com/xap/1.0/"
        xmlns:xmpRights="http://ns.adobe.com/xap/1.0/rights/"
        xmlns:photoshop="http://ns.adobe.com/photoshop/1.0/"
        xmlns:Iptc4xmpCore="http://iptc.org/std/Iptc4xmpCore/1.0/xmlns/"
        xmlns:exif="http://ns.adobe.com/exif/1.0/"
        xmlns:tiff="http://ns.adobe.com/tiff/1.0/">

      <!-- Simple properties -->
      <xmp:CreatorTool>Adobe Lightroom Classic 13.0</xmp:CreatorTool>
      <xmp:CreateDate>2024-06-15T14:30:00+05:30</xmp:CreateDate>
      <xmp:ModifyDate>2024-06-16T10:00:00+05:30</xmp:ModifyDate>
      <xmp:Rating>4</xmp:Rating>

      <dc:format>image/jpeg</dc:format>

      <photoshop:DateCreated>2024-06-15T14:30:00+05:30</photoshop:DateCreated>
      <photoshop:City>Mumbai</photoshop:City>
      <photoshop:Country>India</photoshop:Country>
      <photoshop:Credit>Jane Photographer / Agency</photoshop:Credit>

      <tiff:Make>Apple</tiff:Make>
      <tiff:Model>iPhone 15 Pro</tiff:Model>
      <tiff:Orientation>1</tiff:Orientation>

      <exif:ExposureTime>1/250</exif:ExposureTime>
      <exif:FNumber>14/5</exif:FNumber>
      <exif:FocalLength>6900/1000</exif:FocalLength>

      <!-- Language alternative -->
      <dc:title>
        <rdf:Alt>
          <rdf:li xml:lang="x-default">Golden Hour at Marine Drive</rdf:li>
        </rdf:Alt>
      </dc:title>

      <dc:description>
        <rdf:Alt>
          <rdf:li xml:lang="x-default">The sun setting over the Arabian Sea as seen from Marine Drive, Mumbai</rdf:li>
        </rdf:Alt>
      </dc:description>

      <dc:rights>
        <rdf:Alt>
          <rdf:li xml:lang="x-default">Copyright 2024 Jane Photographer. All rights reserved.</rdf:li>
        </rdf:Alt>
      </dc:rights>

      <!-- Ordered array (first creator is primary) -->
      <dc:creator>
        <rdf:Seq>
          <rdf:li>Jane Photographer</rdf:li>
        </rdf:Seq>
      </dc:creator>

      <!-- Unordered array (keywords) -->
      <dc:subject>
        <rdf:Bag>
          <rdf:li>sunset</rdf:li>
          <rdf:li>Mumbai</rdf:li>
          <rdf:li>Marine Drive</rdf:li>
          <rdf:li>golden hour</rdf:li>
          <rdf:li>cityscape</rdf:li>
        </rdf:Bag>
      </dc:subject>

      <!-- Rights -->
      <xmpRights:Marked>True</xmpRights:Marked>
      <xmpRights:WebStatement>https://example.com/license</xmpRights:WebStatement>
      <xmpRights:UsageTerms>
        <rdf:Alt>
          <rdf:li xml:lang="x-default">Licensed for editorial use only</rdf:li>
        </rdf:Alt>
      </xmpRights:UsageTerms>

      <!-- Structure -->
      <Iptc4xmpCore:CreatorContactInfo rdf:parseType="Resource">
        <Iptc4xmpCore:CiEmailWork>jane@example.com</Iptc4xmpCore:CiEmailWork>
        <Iptc4xmpCore:CiAdrCity>Mumbai</Iptc4xmpCore:CiAdrCity>
        <Iptc4xmpCore:CiAdrCtry>India</Iptc4xmpCore:CiAdrCtry>
        <Iptc4xmpCore:CiUrlWork>https://janephotographer.example.com</Iptc4xmpCore:CiUrlWork>
      </Iptc4xmpCore:CreatorContactInfo>

    </rdf:Description>
  </rdf:RDF>
</x:xmpmeta>
<?xpacket end="w"?>
```

---

## CGImageMetadataType Mapping

How XMP data model forms map to Apple's `CGImageMetadataType` enum:

| XMP Form | RDF Element | CGImageMetadataType | Value Type in ImageIO |
|----------|-------------|---------------------|-----------------------|
| Simple scalar | text content | `.default` (0) or `.string` (1) | `CFString` |
| Structure | `rdf:Description` / `parseType="Resource"` | `.structure` (6) | `CFDictionary` of `[String: CGImageMetadataTag]` |
| Unordered array | `rdf:Bag` | `.arrayUnordered` (2) | `CFArray` of `CGImageMetadataTag` |
| Ordered array | `rdf:Seq` | `.arrayOrdered` (3) | `CFArray` of `CGImageMetadataTag` |
| Alternative array | `rdf:Alt` | `.alternateArray` (4) | `CFArray` of `CGImageMetadataTag` |
| Language alt | `rdf:Alt` + `xml:lang` | `.alternateText` (5) | `CFDictionary` of `[String: String]` (lang code to text) |

**Distinguishing `.default` from `.string`:** Both represent simple scalar
values and return `CFString`. The `.default` type (0) indicates the parser
could not determine a more specific type; `.string` (1) is explicitly typed.
In practice, treat both identically.

> For ImageIO-specific details on creating and reading these types, see
> [`imageio-integration.md`](imageio-integration.md) and
> `../imageio/cgimage-metadata.md`.
