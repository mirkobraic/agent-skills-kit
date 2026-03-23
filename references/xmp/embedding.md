# XMP Embedding in File Formats

> Part of [XMP Reference](README.md)

How XMP metadata is physically stored inside different image and document
formats. Each format has its own embedding mechanism, governed by XMP
Specification Part 3 (Storage in Files).

---

## Format Summary

| Format | Embedding Method | Size Limit | Extended XMP | In-Place Edit | Notes |
|--------|------------------|------------|--------------|---------------|-------|
| **JPEG** | APP1 marker segment | 65,502 bytes (standard) | Yes | Yes (with padding) | Separate APP1 from EXIF |
| **TIFF** | Tag 700 in IFD0 | No practical limit | No | Yes | UNDEFINED type |
| **DNG** | Tag 700 in IFD0 | No practical limit | No | Yes | Same as TIFF (DNG is TIFF-based) |
| **PNG** | iTXt chunk | No practical limit | No | No (CRC integrity) | Keyword: `XML:com.adobe.xmp` |
| **HEIF/HEIC** | Metadata item (ISOBMFF) | No practical limit | No | No (requires re-encode in ImageIO) | `mime` content type in item info |
| **AVIF** | Metadata item (ISOBMFF) | No practical limit | No | No | Same structure as HEIF |
| **WebP** | `XMP ` RIFF chunk | No practical limit | No | Varies | FourCC is `XMP ` (with trailing space) |
| **PDF** | Metadata stream | No practical limit | No | Yes | Referenced from document catalog |
| **PSD** | Image resource 0x0424 | No practical limit | No | Yes | Also supports TIFF-style |
| **GIF** | Application extension | 255 bytes per sub-block | No | No | Rarely used; chained sub-blocks |

---

## JPEG

### Standard XMP (APP1 Marker)

XMP in JPEG is stored in an **APP1 marker segment** (0xFFE1) — the same marker
type used by EXIF, but with a different namespace identifier.

#### Marker Structure

```
FF E1          -- APP1 marker
LL LL          -- Segment length (2 bytes, big-endian, includes length field itself)
68 74 74 70 3A 2F 2F 6E 73 2E 61 64 6F 62 65 2E
63 6F 6D 2F 78 61 70 2F 31 2E 30 2F 00
               -- Namespace: "http://ns.adobe.com/xap/1.0/" + null terminator (29 bytes)
[XMP packet]   -- UTF-8 XMP data (with packet wrapper)
```

**Namespace identifier:** `http://ns.adobe.com/xap/1.0/\0` (29 bytes
including null terminator)

**Distinguishing from EXIF APP1:** EXIF uses the identifier `Exif\0\0` (6
bytes). Readers check the first bytes after the segment length to determine
whether an APP1 segment contains EXIF or XMP.

#### Size Limit

A JPEG marker segment has a 2-byte length field, limiting total segment size
to 65,535 bytes. After subtracting the 2-byte length field and the 29-byte
namespace identifier plus null byte, the maximum XMP packet size is:

```
65,535 - 2 - 29 = 65,504 bytes (theoretical)
65,502 bytes (commonly cited practical limit)
```

Most XMP packets are well under this limit (typically 2-10 KB for normal
photos). Packets exceed 64 KB only with very large metadata sets, extensive
edit histories, or face region data.

#### Placement

The XMP APP1 segment should appear early in the JPEG file, typically after the
EXIF APP1 segment and before the image data (SOS marker). The recommended
order is:

```
SOI (FF D8)
APP0 -- JFIF (if present)
APP1 -- EXIF (FF E1 + "Exif\0\0")
APP1 -- XMP  (FF E1 + "http://ns.adobe.com/xap/1.0/\0")
APP1 -- Extended XMP (if needed, one or more segments)
APP2 -- ICC Profile (if present)
APP13 -- IPTC IIM / Photoshop IRB (if present)
...
DQT, DHT, SOF -- quantization/Huffman tables, frame header
SOS -- Start of Scan (image data)
```

### Extended XMP

When the XMP packet exceeds 65,502 bytes, it is split into **Standard XMP**
and **Extended XMP**:

#### Standard XMP

- Stored in the normal APP1 segment (as above)
- Contains the most important properties (those needed for basic display and
  identification)
- Includes a special property `xmpNote:HasExtendedXMP` whose value is the
  MD5 digest of the full extended XMP serialization (128-bit digest as a
  32-character uppercase hexadecimal ASCII string)

#### Extended XMP

- Stored in one or more additional APP1 segments
- Each segment uses the namespace identifier:
  `http://ns.adobe.com/xmp/extension/\0` (null-terminated, 35 bytes)
- The extended XMP is serialized **without** the packet wrapper
  (`<?xpacket ...?>` header/trailer)
- The serialized text is split into chunks of approximately 65,400 bytes each
  (the upper limit per chunk is 65,458 bytes)

#### Extended XMP Segment Structure

```
FF E1          -- APP1 marker
LL LL          -- Segment length
68 74 74 70 3A 2F 2F 6E 73 2E 61 64 6F 62 65 2E
63 6F 6D 2F 78 6D 70 2F 65 78 74 65 6E 73 69 6F
6E 2F 00       -- "http://ns.adobe.com/xmp/extension/" + null (35 bytes)
[32-byte GUID] -- MD5 digest of full ExtendedXMP (hex string, uppercase A-F, no null termination)
[4-byte length]-- Total length of ExtendedXMP (big-endian uint32)
[4-byte offset]-- Offset of this chunk within the full ExtendedXMP (big-endian uint32)
[chunk data]   -- Portion of the ExtendedXMP serialization
```

Maximum chunk size per segment: 65,458 bytes (65,535 - 2 - 35 - 32 - 4 - 4).

#### Reconciliation

A reader must:
1. Read the Standard XMP and extract `xmpNote:HasExtendedXMP`
2. Scan for Extended XMP APP1 segments whose GUID matches
3. Reassemble chunks by offset into a single byte buffer
4. Parse the reassembled buffer as XMP/RDF XML
5. Merge the parsed extended properties with the Standard XMP

> **ImageIO note:** Apple's ImageIO framework handles Standard XMP
> automatically. Support for Extended XMP reading has been observed but is not
> explicitly documented. Writing Extended XMP via ImageIO is **not** supported —
> if XMP exceeds 64 KB, the excess may be silently truncated.

---

## TIFF

### Tag 700

XMP is stored in **TIFF tag 700** (0x02BC) in IFD0 with type UNDEFINED
(byte array). The value is the complete XMP packet (including packet wrapper).

```
Tag:    700 (0x02BC)
Type:   UNDEFINED (7)
Count:  length of XMP packet in bytes
Value:  UTF-8 encoded XMP packet
IFD:    IFD0 (primary image)
```

There is no practical size limit beyond the TIFF format's 4 GB file offset
constraint (or 8 bytes for BigTIFF).

The XMP packet in TIFF **should** include padding for in-place editing. When
XMP is updated, a tool can rewrite the tag value in place if the new packet
(with reduced padding) fits in the existing allocation.

---

## DNG

DNG files are based on TIFF/EP and use the same **tag 700** mechanism as TIFF.
XMP is stored in IFD0 as an UNDEFINED byte array containing the full XMP
packet.

DNG files commonly contain large XMP payloads because Adobe Camera Raw writes
all processing parameters (`crs:` namespace) directly into the DNG's XMP.
Unlike proprietary RAW files (which use sidecar `.xmp` files), DNG embeds
everything.

---

## PNG

### iTXt Chunk

XMP is embedded in a PNG `iTXt` (International Textual Data) chunk with a
specific keyword.

#### Chunk Structure

```
[4 bytes]  -- Chunk data length (big-endian)
"iTXt"     -- Chunk type (4 bytes)
"XML:com.adobe.xmp"  -- Keyword (null-terminated)
0x00       -- Compression flag (0 = uncompressed)
0x00       -- Compression method
""         -- Language tag (empty, null-terminated)
""         -- Translated keyword (empty, null-terminated)
[XMP data] -- XMP packet (UTF-8)
[4 bytes]  -- CRC-32 checksum
```

**Keyword:** `XML:com.adobe.xmp` — this exact string identifies the chunk as
containing XMP data.

#### Key Constraints

- **Read-only packet:** The packet trailer **must** be `<?xpacket end="r"?>`
  (read-only) because the PNG CRC checksum covers the chunk data. Modifying
  XMP in place would invalidate the CRC.
- **One chunk per file:** There should be at most one iTXt chunk containing
  XMP per PNG file.
- **Placement:** The XMP chunk should appear before the first IDAT (image
  data) chunk. Some Apple and Adobe utilities will not read XMP placed after
  IDAT.
- **No compression:** The XMP data within the iTXt chunk is typically stored
  uncompressed (compression flag = 0), even though the iTXt format supports
  zlib compression.

> **ImageIO note:** Apple's ImageIO reads and writes XMP in PNG via the
> `CGImageMetadata` API. Lossless metadata update via
> `CGImageDestinationCopyImageSource` is supported for PNG.

---

## HEIF / HEIC

### ISOBMFF Metadata Item

HEIF (ISO/IEC 23008-12) is based on the ISO Base Media File Format (ISOBMFF,
ISO/IEC 14496-12). XMP is stored as a **metadata item** associated with an
image item.

#### Storage Structure

```
meta box (container)
+-- hdlr box    -- handler type "pict"
+-- pitm box    -- primary item ID
+-- iloc box    -- item locations (byte offsets and sizes)
+-- iinf box    -- item information
|   +-- infe    -- image item (type "hvc1" or "av01")
|   +-- infe    -- Exif metadata item (type "Exif")
|   +-- infe    -- XMP metadata item (content_type "application/rdf+xml")
+-- iref box    -- item references
|   +-- cdsc    -- "content describes" reference from XMP item -> image item
+-- idat box    -- (if metadata stored inline)
    or mdat box -- (if metadata in media data area)
```

The XMP item:
- Has `content_type` of `application/rdf+xml` in the item information entry
- Is referenced to its parent image item via a `cdsc` (content describes)
  reference in the `iref` box
- The XMP data itself is the UTF-8 XMP packet (some implementations include
  the packet wrapper; others omit it; behavior varies)

> **ImageIO note:** ImageIO reads XMP from HEIF/HEIC files via
> `CGImageSourceCopyMetadataAtIndex`. However, lossless metadata update via
> `CGImageDestinationCopyImageSource` is **not** supported for HEIF — writing
> metadata requires full re-encoding via
> `CGImageDestinationAddImageAndMetadata`.

---

## AVIF

AVIF (AV1 Image File Format) uses the same ISOBMFF-based structure as HEIF.
XMP is stored as a metadata item with the same box structure:

- `infe` entry with `content_type` `"application/rdf+xml"`
- `cdsc` reference from XMP item to image item
- XMP packet data in `mdat` or `idat`

The specification is defined in the AOMedia AV1 Image File Format (AVIF)
specification, which inherits HEIF's metadata handling from ISO/IEC 23008-12.

---

## WebP

### XMP RIFF Chunk

WebP uses the RIFF (Resource Interchange File Format) container. XMP is stored
in a chunk with FourCC `XMP ` (note the trailing ASCII space, 0x20).

#### Chunk Structure

```
"XMP "     -- FourCC (4 bytes, fourth char is space 0x20)
[4 bytes]  -- Chunk data size (little-endian uint32)
[XMP data] -- XMP packet (UTF-8)
[padding]  -- 1 byte if chunk size is odd (RIFF alignment)
```

The `XMP ` chunk is an optional extended chunk in the VP8X-flagged WebP
container. The VP8X chunk header's XMP flag bit must be set if an XMP chunk is
present.

#### Ordering

The WebP container specification (RFC 9649, November 2024) recommends placing
the `XMP ` chunk after the image data chunks, but metadata chunks may appear
in any order in practice.

---

## PDF

### Metadata Stream

In PDF, XMP is stored as a **metadata stream object** referenced from the
document catalog dictionary.

#### Structure

```
% Catalog dictionary
1 0 obj
<< /Type /Catalog
   /Pages 2 0 R
   /Metadata 10 0 R     % Reference to XMP metadata stream
>>
endobj

% Metadata stream
10 0 obj
<< /Type /Metadata
   /Subtype /XML
   /Length 3456
>>
stream
<?xpacket begin="..." id="W5M0MpCehiHzreSzNTczkc9d"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/">
  <rdf:RDF ...>
    ...
  </rdf:RDF>
</x:xmpmeta>
<?xpacket end="w"?>
endstream
endobj
```

Key points:
- The metadata stream has `/Type /Metadata` and `/Subtype /XML`
- It is referenced via the `/Metadata` key in the document catalog
- PDF can also have object-level metadata streams on individual pages, images,
  or other objects
- The XMP packet should include padding for in-place editing
- PDF/A (ISO 19005) **requires** XMP metadata with specific properties
  (`dc:title`, `dc:creator`, `xmp:CreateDate`, `xmp:ModifyDate`,
  `pdf:Producer`, `pdf:PDFVersion`)

---

## PSD (Photoshop Document)

### Image Resource 0x0424

In PSD files, XMP is stored as **Image Resource ID 1060** (0x0424). The image
resource block contains the XMP packet as raw bytes.

PSD also supports TIFF-style tag 700 in some configurations. Adobe apps
typically use the Image Resource method.

---

## GIF

### Application Extension

XMP can technically be stored in a GIF Application Extension block, but this
is extremely rare. The Application Extension uses the application identifier
`XMP Data` and the authentication code `XMP`.

Each sub-block is limited to 255 bytes, so the XMP packet is split across
multiple sub-blocks and must be reassembled by the reader.

In practice, GIF files almost never contain XMP. ImageIO does not read or
write XMP in GIF files.

---

## XMP Packet Wrapper

The packet wrapper is used regardless of embedding format (though some formats
omit it — see per-format notes above).

### Complete Wrapper Format

```
<?xpacket begin="﻿" id="W5M0MpCehiHzreSzNTczkc9d"?>
[x:xmpmeta and rdf:RDF content]
[padding -- XML whitespace (spaces, typically 2-4 KB)]
<?xpacket end="w"?>
```

### Header Processing Instruction

```
<?xpacket begin="﻿" id="W5M0MpCehiHzreSzNTczkc9d"?>
```

| Attribute | Value | Notes |
|-----------|-------|-------|
| `begin` | U+FEFF BOM (or empty string) | UTF-8 BOM = bytes `EF BB BF`; empty = UTF-8 default |
| `id` | `W5M0MpCehiHzreSzNTczkc9d` | Fixed magic string; identical for all XMP packets |

The `begin` attribute **must** come before the `id` attribute. This is a
requirement of the packet scanning algorithm, which searches for the byte
sequence `<?xpacket begin=` followed by the `id` value.

### Trailer Processing Instruction

```
<?xpacket end="w"?>
```

| Value | Meaning |
|-------|---------|
| `w` | Writable — in-place modification is allowed |
| `r` | Read-only — do not modify in place (e.g., PNG with CRC) |

### Padding

Padding consists of XML whitespace characters (spaces, tabs, newlines) placed
between the closing `</x:xmpmeta>` tag and the trailer `<?xpacket end="w"?>`.

**Purpose:** Allows tools to update XMP metadata in place without rewriting
the entire file. If the modified XMP is smaller, excess padding absorbs the
difference. If larger, padding can be consumed.

**Typical size:** 2,048 to 4,096 bytes of space characters.

**When no padding:** If the XMP grows beyond the available space (original
content + padding), the tool must rewrite the file. For JPEG, this means
rewriting the entire file. For TIFF/DNG, only the tag value offset and data
area may need adjustment.

---

## Sidecar .xmp Files

### Purpose

Sidecar files store XMP metadata **externally** alongside the image file. They
are used when:

- The image format is read-only or proprietary (e.g., proprietary RAW files
  like .CR3, .NEF, .ARW)
- The application cannot or should not modify the original file
- Non-destructive editing instructions need to be stored separately

### File Naming Convention

The sidecar file shares the same base name as the image file with a `.xmp`
extension:

```
IMG_1234.CR3       -- Canon RAW file
IMG_1234.xmp       -- XMP sidecar with metadata and processing instructions
```

### File Format

A sidecar `.xmp` file is a complete XMP packet, including the packet wrapper:

```xml
<?xpacket begin="﻿" id="W5M0MpCehiHzreSzNTczkc9d"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/">
  <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <rdf:Description rdf:about=""
        xmlns:xmp="http://ns.adobe.com/xap/1.0/"
        xmlns:crs="http://ns.adobe.com/camera-raw-settings/1.0/"
        xmlns:dc="http://purl.org/dc/elements/1.1/">
      <xmp:Rating>4</xmp:Rating>
      <crs:Temperature>5500</crs:Temperature>
      <crs:Exposure2012>0.50</crs:Exposure2012>
      <dc:subject>
        <rdf:Bag>
          <rdf:li>landscape</rdf:li>
          <rdf:li>sunset</rdf:li>
        </rdf:Bag>
      </dc:subject>
    </rdf:Description>
  </rdf:RDF>
</x:xmpmeta>
<?xpacket end="w"?>
```

### Priority Rules

When both embedded XMP and a sidecar `.xmp` file exist, which takes priority?

| Application | Priority Rule |
|-------------|---------------|
| Adobe Lightroom Classic | Sidecar XMP takes priority for proprietary RAW; embedded for DNG (configurable) |
| Adobe Camera Raw | Sidecar XMP takes priority for proprietary RAW |
| Adobe Bridge | Sidecar XMP takes priority |
| Apple Photos / ImageIO | Reads embedded only; does not read sidecar files |
| ExifTool | Reads both; user specifies which to write |
| Darktable | Sidecar XMP takes priority |
| Capture One | Uses its own catalog; can export sidecar XMP |

> **ImageIO note:** Apple's ImageIO framework does **not** automatically read
> sidecar `.xmp` files. To use sidecar data with ImageIO, read the sidecar
> file manually with `CGImageMetadataCreateFromXMPData` and apply it to the
> image using `CGImageDestinationCopyImageSource` with
> `kCGImageDestinationMergeMetadata`. See
> `../imageio/cgimage-metadata.md` for code examples.

### DNG vs Proprietary RAW

| Format | XMP Storage | Sidecar Needed? |
|--------|-------------|-----------------|
| **DNG** | Embedded (tag 700) | No — XMP is written directly into the DNG file |
| **Canon .CR3 / .CR2** | Sidecar `.xmp` | Yes — proprietary format, cannot embed safely |
| **Nikon .NEF / .NRW** | Sidecar `.xmp` | Yes |
| **Sony .ARW** | Sidecar `.xmp` | Yes |
| **Fuji .RAF** | Sidecar `.xmp` | Yes |
| **Olympus .ORF** | Sidecar `.xmp` | Yes |
| **Panasonic .RW2** | Sidecar `.xmp` | Yes |
| **JPEG / TIFF** | Embedded (APP1 / tag 700) | Rarely — can embed directly |

---

## Packet Scanning

The XMP SDK defines a **packet scanning** algorithm that searches for XMP
packets in arbitrary binary data by looking for the packet header signature:

1. Scan for the byte sequence `<?xpacket begin=`
2. Verify the `id="W5M0MpCehiHzreSzNTczkc9d"` attribute
3. Find the matching `<?xpacket end=` trailer
4. Extract the XMP data between header and trailer

This allows tools to find XMP in files even when they do not understand the
file format's container structure. ExifTool and the Adobe XMP SDK use this
technique as a fallback.

The Adobe XMP Toolkit SDK provides packet scanning via the
`kXMPFiles_OpenUsePacketScanning` flag in the XMPFiles library.

> Packet scanning is a last resort. Format-aware reading (understanding the
> JPEG APP1 structure, TIFF tag 700, PNG iTXt, etc.) is always preferred
> because it correctly handles format-specific constraints like Extended XMP
> in JPEG.
