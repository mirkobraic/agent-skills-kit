# XMP Pitfalls and Known Issues

> Part of [XMP Reference](README.md)

Known issues, gotchas, and edge cases when working with XMP metadata -- both at
the standard level and specific to Apple's ImageIO framework.

---

## 1. JPEG 64 KB Size Limit

**Problem:** A JPEG APP1 marker segment has a 2-byte length field, limiting
the XMP packet to ~65,502 bytes. Most photos stay well under this, but
extensive edit history (`xmpMM:History`), face region data
(`Iptc4xmpExt:PersonInImageWDetails`), or dozens of Camera Raw adjustments
can push past the limit.

**What happens:** A tool that writes more than 65,502 bytes of XMP into a
single JPEG APP1 segment produces a corrupt file. Readers that enforce the
segment length will not parse the XMP.

**Correct handling:** The XMP specification defines Extended XMP -- splitting
the packet into Standard XMP and Extended XMP across multiple APP1 segments.
The Standard XMP includes `xmpNote:HasExtendedXMP` with an MD5 digest of the
extended portion. See [`embedding.md`](embedding.md) for full details.

**ImageIO behavior:** ImageIO appears to read Standard XMP from JPEG files
reliably. Reading Extended XMP has been observed to work but is not documented.
Writing Extended XMP via ImageIO is **not** supported -- if the XMP exceeds
the limit, the excess may be silently truncated with no error.

**Mitigation:**
- Keep XMP lean: avoid storing large edit histories or processing logs in the
  embedded XMP
- For large metadata sets, use a sidecar `.xmp` file
- If you need Extended XMP, use ExifTool or the Adobe XMP SDK instead of
  ImageIO
- Monitor your XMP size: serialize to bytes with `CGImageMetadataCreateXMPData`
  and check the length before writing to JPEG

---

## 2. Namespace Prefix Conflicts

**Problem:** XMP namespaces are identified by URI, not by prefix. Different
tools may use different prefixes for the same namespace. For example:

| Tool | Prefix | URI |
|------|--------|-----|
| Adobe apps (modern) | `xmp:` | `http://ns.adobe.com/xap/1.0/` |
| Older Adobe apps | `xap:` | `http://ns.adobe.com/xap/1.0/` |
| Tool X | `xmpBasic:` | `http://ns.adobe.com/xap/1.0/` |

These all refer to the **same namespace**. The prefix is just a serialization
convenience -- it has no semantic meaning.

**What happens:** Tools that compare prefixes instead of URIs will treat
`xmp:CreateDate` and `xap:CreateDate` as different properties, even though
they are identical.

**Correct handling:** Always resolve properties by namespace URI + local name,
never by prefix string alone.

**ImageIO behavior:** ImageIO uses fixed prefixes for its 10 pre-registered
namespaces. When reading, it normalizes prefixes to the canonical ones (e.g.,
`xap:` becomes `xmp:`). When writing, it always uses the canonical prefixes.
Custom namespaces retain whatever prefix was registered.

**Mitigation:**
- Use the `kCGImageMetadataNamespace*` and `kCGImageMetadataPrefix*` constants
  rather than hardcoding prefix strings
- When registering custom namespaces, use the conventional prefix for that
  namespace
- When comparing tags from different sources, compare namespace URIs, not
  prefixes

---

## 3. Language Alternative (langAlt) Handling

**Problem:** Properties like `dc:title`, `dc:description`, `dc:rights`, and
`xmpRights:UsageTerms` are typed as Language Alternatives (`rdf:Alt` with
`xml:lang` qualifiers). Different tools handle these inconsistently:

- Some tools write a single `x-default` entry
- Some tools write `x-default` plus locale-specific entries
- Some tools read only `x-default`, ignoring other languages
- Some tools always create `x-default` as a copy of the first locale entry
- Some tools strip non-`x-default` entries when round-tripping

**ImageIO-specific issue:** Tags created via
`CGImageMetadataTagCreate(.alternateText, CFDictionary)` are accepted by
`CGImageMetadataSetTagWithPath` (returns `true`) but are **silently discarded**
by `CGImageDestinationCopyImageSource`. The tag vanishes from the output file
with no error.

**Workarounds:**
1. Use `CGImageMetadataSetValueWithPath` with a plain `CFString` -- ImageIO
   auto-detects the `langAlt` requirement and creates a proper `x-default`
   entry
2. For multi-language support, parse an XMP snippet via
   `CGImageMetadataCreateFromXMPData` and copy the resulting tag -- these tags
   survive CopyImageSource

See [`imageio-integration.md`](imageio-integration.md) for code examples.

---

## 4. Metadata Loss When Tools Do Not Preserve XMP

**Problem:** Many image processing tools, format converters, and social media
platforms strip XMP metadata entirely:

| Tool / Platform | XMP Behavior |
|-----------------|--------------|
| **UIImage (iOS)** | Destroys all metadata when creating a UIImage and re-encoding |
| **Social media** (Instagram, Twitter/X, Facebook) | Strips most or all XMP on upload |
| **Some format converters** | May not copy XMP when converting between formats |
| **macOS Preview "Export"** | May strip or reduce XMP depending on format |
| **PIL/Pillow (Python)** | Does not preserve XMP by default |
| **ImageMagick** | Preserves XMP with `-profile` flag; default behavior varies |

**ImageIO-specific loss paths:**
- `UIImage` round-trip: creating a `UIImage` from data and writing it back
  **loses all EXIF, XMP, and IPTC metadata** (see `../imageio/pitfalls.md`)
- `CGImageDestinationAddImage` (without metadata parameter): drops metadata
  unless properties are explicitly re-attached
- HEIF/HEIC write: metadata must be explicitly passed to
  `CGImageDestinationAddImageAndMetadata`

**Mitigation:**
- Always use `CGImageDestinationCopyImageSource` for lossless metadata
  preservation (JPEG, PNG, TIFF, PSD)
- When re-encoding, explicitly read metadata from the source and pass it to
  the destination
- Test your pipeline end-to-end: read XMP, process, write, read back, compare

---

## 5. Duplicate Data in EXIF / IPTC IIM / XMP

**Problem:** The same information is often stored in three places simultaneously:

| Field | EXIF Binary | IPTC IIM | XMP |
|-------|-------------|----------|-----|
| **Date created** | `DateTimeOriginal` + `OffsetTimeOriginal` | 2:55 + 2:60 | `photoshop:DateCreated` |
| **Creator** | -- | 2:80 | `dc:creator` |
| **Copyright** | TIFF `Copyright` (0x8298) | 2:116 | `dc:rights` |
| **Description** | TIFF `ImageDescription` (0x010E) | 2:120 | `dc:description` |
| **Keywords** | -- | 2:25 | `dc:subject` |
| **City** | -- | 2:90 | `photoshop:City` |
| **Country** | -- | 2:101 | `photoshop:Country` |

When these fall out of sync, consumers see conflicting metadata.

### MWG (Metadata Working Group) Reconciliation Rules

The MWG established priority guidelines (2008, updated 2010):

**Reading priority:**
1. If EXIF and IIM conflict: prefer EXIF when the IIM checksum matches or is
   absent; prefer IIM when the checksum does not match
2. If XMP and IIM conflict: prefer XMP (it is the more expressive format)
3. If XMP and EXIF conflict: prefer the most recently modified value (check
   `xmp:ModifyDate` vs EXIF `DateTime`)

**Writing rule:** When updating a field, write to **all three** locations
(EXIF, IIM, XMP) to maintain sync. This is called "synchronized writing."

**ImageIO auto-synthesis (read):** Apple synthesizes across APIs on read,
presenting a merged view. On write, updating via one API does **not**
automatically update the others -- you must explicitly write to each.

**Mitigation:**
- For new code, prefer the XMP path (it works in all formats)
- When writing editorial metadata, write to both IPTC IIM and XMP for
  maximum compatibility with legacy tools
- Use ExifTool's `-overwrite_original -all= -tagsfromfile @ -all:all`
  pattern to re-synchronize all metadata

---

## 6. Sidecar vs Embedded: Priority Ambiguity

**Problem:** When both a sidecar `.xmp` file and embedded XMP exist, there is
no universal rule for which takes priority. Different applications use
different policies (see [`embedding.md`](embedding.md) for a per-application
table).

**Common confusion:**
- User edits in Lightroom (updates sidecar), then opens in another tool that
  reads only embedded metadata -- sees stale data
- User embeds metadata with ExifTool, then opens in Lightroom which prefers
  its sidecar/catalog -- sees outdated metadata

**ImageIO behavior:** ImageIO reads **only embedded** metadata. It has no
concept of sidecar files. To use sidecar data, you must read it manually with
`CGImageMetadataCreateFromXMPData` and merge it.

**Mitigation:**
- Establish a clear policy for your workflow: embedded or sidecar, not both
- If using sidecars, periodically sync sidecar data into the embedded
  metadata for portability
- For iOS apps, always use embedded metadata since ImageIO does not support
  sidecars

---

## 7. UTF-8 Encoding Requirements

**Problem:** The XMP specification requires UTF-8 encoding (or UTF-16/UTF-32
with BOM). However, some tools produce XMP with:

- Latin-1 (ISO 8859-1) encoded text without proper XML encoding
- Windows-1252 characters in place of Unicode
- Raw bytes without XML character escaping
- Invalid byte sequences in metadata fields

**What happens:** An XML parser encounters invalid UTF-8 and either rejects
the entire XMP packet or replaces characters with the Unicode replacement
character (U+FFFD), corrupting the data.

**Mitigation:**
- Always produce valid UTF-8 when writing XMP
- Use XML character entities for characters that XML does not allow in content
  (`&amp;`, `&lt;`, `&gt;`, `&apos;`, `&quot;`)
- When reading XMP from unknown sources, validate UTF-8 before parsing
- ImageIO's `CGImageMetadataCreateFromXMPData` will return `nil` for invalid
  XML/XMP data -- check the return value

---

## 8. Whitespace and Formatting Differences

**Problem:** Different XMP writers produce different XML formatting:

- Adobe apps: pretty-printed with indentation
- ExifTool: compact with minimal whitespace
- ImageIO: its own formatting when serializing via `CGImageMetadataCreateXMPData`
- Some tools: add or remove XML comments

**What happens:**
- Binary comparison of XMP packets shows differences even when the metadata
  content is identical
- Diff tools flag false changes
- In-place editing may fail if the reformatted XMP is larger than the
  original + padding

**Implications for in-place editing:** When a tool reads XMP, modifies one
property, and writes back, it may reformat the entire XML. If the reformatted
version is larger than the original packet (content + padding), the tool must
rewrite the containing file rather than updating in place.

**Mitigation:**
- Do not rely on byte-level comparison of XMP packets for change detection
- Use semantic comparison (parse both, compare property values)
- When round-tripping XMP through ImageIO, expect the formatting to change
- Ensure adequate padding (2-4 KB) for in-place edits

---

## 9. XMP Properties Not Visible in All Applications

**Problem:** Custom or less common XMP namespaces may not be displayed by all
applications:

| Namespace | Visible in Lightroom | Visible in Apple Photos | Visible in Bridge |
|-----------|---------------------|------------------------|-------------------|
| `dc:` (title, keywords) | Yes | Partially (keywords via iCloud sync) | Yes |
| `xmp:` (rating) | Yes | No | Yes |
| `crs:` (Camera Raw) | Yes (native) | No | No |
| `Iptc4xmpCore:` | Yes | No | Yes |
| `Iptc4xmpExt:` | Yes | No | Yes |
| `plus:` (licensing) | Partially | No | Partially |
| `custom:` | No (unless plugin) | No | No |

**What happens:** Users set metadata in one application and expect to see it
in another, but the other application does not know how to display the custom
namespace's properties.

**Mitigation:**
- Use standard namespaces for maximum interoperability
- For custom data, store it in custom namespaces but also write key fields to
  standard namespaces
- Document which applications will display your custom metadata

---

## 10. XMP Packet Wrapper Missing or Malformed

**Problem:** Some tools produce XMP data without the proper packet wrapper
(`<?xpacket ...?>` processing instructions), or with malformed wrappers:

- Missing `begin` attribute
- Wrong or missing `id` value (should be `W5M0MpCehiHzreSzNTczkc9d`)
- Missing `end` processing instruction
- `end="r"` in a format that supports in-place editing (prevents modification)
- `end="w"` in PNG (should be `"r"` because CRC protects the data)

**What happens:**
- Packet scanners (used as fallback by some tools) cannot locate the XMP
- In-place editing tools may refuse to update the packet or may corrupt it
- Some readers may still parse the XMP correctly by looking for `<x:xmpmeta>`
  or `<rdf:RDF>` directly

**ImageIO behavior:** `CGImageMetadataCreateFromXMPData` accepts XMP both
with and without the packet wrapper. It is relatively lenient about wrapper
format. `CGImageMetadataCreateXMPData` always produces properly wrapped output.

---

## 11. Date Format Inconsistencies

**Problem:** XMP dates use ISO 8601, but with variable precision:

```
"2024"                          -- year only
"2024-06"                       -- year and month
"2024-06-15"                    -- full date
"2024-06-15T14:30:00"           -- date + local time (no timezone!)
"2024-06-15T14:30:00+05:30"     -- date + time + timezone
"2024-06-15T14:30:00.123+05:30" -- date + time + subseconds + timezone
"2024-06-15T14:30:00Z"          -- date + time + UTC
```

When comparing timestamps from different sources:
- EXIF binary `DateTimeOriginal` has no timezone (naive) -- XMP version should
  have timezone folded in
- If an EXIF `OffsetTime*` tag was absent, the XMP datetime may lack timezone
  information, making comparison ambiguous
- Subsecond precision varies (0, 3, or 6 decimal places)
- Some tools write `"2024-06-15T14:30:00.00"` (trailing zeros), others do not

**Duplicate date fields with different semantics:**
- `xmp:CreateDate` -- creation date of this digital rendition
- `photoshop:DateCreated` -- intellectual creation date (intended for IPTC)
- `exif:DateTimeOriginal` -- capture date from the camera

These often have the same value but may diverge after editing, format
conversion, or metadata merging.

**Mitigation:**
- Always include timezone when writing dates
- Parse dates with a library that handles ISO 8601 variable precision
- When comparing dates, normalize to UTC before comparison
- Be aware that `xmp:CreateDate`, `photoshop:DateCreated`, and
  `exif:DateTimeOriginal` may represent the same instant but with different
  precision or formatting

---

## 12. Auto-Synthesis Can Mask Missing Data

**Problem:** ImageIO's auto-synthesis (see
[`imageio-integration.md`](imageio-integration.md)) can give the false
impression that metadata exists when it is actually synthesized from another
source.

**Example scenario:**
1. An image has EXIF data but no XMP packet
2. `CGImageSourceCopyMetadataAtIndex` returns XMP tags (synthesized from EXIF)
3. Developer assumes the image has XMP
4. Image is processed by a tool that only reads XMP (not EXIF)
5. That tool sees no XMP (because there is no actual XMP packet in the file)

**Mitigation:**
- Do not assume that tags returned by `CGImageSourceCopyMetadataAtIndex`
  correspond to an actual XMP packet in the file
- To check for a real XMP packet, serialize with
  `CGImageMetadataCreateXMPData` and verify the result
- When interoperating with non-Apple tools, ensure the actual XMP packet
  (not just synthesized data) contains the properties you need

---

## Summary Table

| # | Pitfall | Severity | Affected Formats |
|---|---------|----------|-----------------|
| 1 | JPEG 64 KB XMP limit | High | JPEG only |
| 2 | Namespace prefix conflicts | Medium | All |
| 3 | langAlt handling (ImageIO bug) | High | All (ImageIO write) |
| 4 | Metadata loss in processing | High | All |
| 5 | EXIF/IIM/XMP sync | High | JPEG, TIFF |
| 6 | Sidecar vs embedded priority | Medium | RAW, DNG, JPEG |
| 7 | UTF-8 encoding errors | Medium | All |
| 8 | Whitespace/formatting changes | Low | All |
| 9 | Custom namespaces not displayed | Low | All |
| 10 | Packet wrapper issues | Low | All |
| 11 | Date format inconsistencies | Medium | All |
| 12 | Auto-synthesis masking missing data | Medium | All (ImageIO read) |
