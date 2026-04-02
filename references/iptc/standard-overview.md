# IPTC Photo Metadata Standard

## Scope and Schemas

- IPTC Photo Metadata defines properties for photographs grouped into Administrative, Descriptive, and Rights-related properties.
- Split into two schemas:
  - **IPTC Core** (IIM heritage, backwards-compatible)
  - **IPTC Extension** (more granular, XMP-only, includes PLUS rights properties)
- Standard version 2025.1 includes Core 1.5 and Extension 1.9.

### Core vs Extension

- IPTC Core properties are legacy-compatible (based on old IIM). They remain interoperable with older software.
- IPTC Extension adds newer, more granular properties. Extension properties are XMP-only (no IIM mapping).
- When a property has both IIM and XMP mappings, write both for maximum compatibility. Extension-only properties go to XMP only.

### What's New in 2025.1

Four new Extension properties: AI Prompt Information, AI Prompt Writer Name, AI System Used, AI System Version Used.

---

## Data Types and Property Naming

Basic data types: Text, Integer, Decimal, URL, URI, or Structure.
Cardinality: `1`, `0..1`, `0..unbounded`, `1..unbounded`.

- A property marked **(legacy)** has a better replacement in IPTC Extension.
- A property marked **(DEPRECATED)** should no longer be used; the spec notes a replacement.

---

## Property Reference

The complete property reference (all 66 properties + 19 structures with XMP IDs, IIM mappings, types, and cardinality) is in [`property-reference.md`](property-reference.md).

Upstream machine-readable spec (full JSON with help text, user notes, etc.):

- JSON: https://iptc.org/std/photometadata/specification/iptc-pmd-techreference_2025.1.json
- YAML: https://iptc.org/std/photometadata/specification/iptc-pmd-techreference_2025.1.yml

---

## XMP Namespaces and Prefixes

**IPTC Core namespaces:**

- `Iptc4xmpCore`: http://iptc.org/std/Iptc4xmpCore/1.0/xmlns/
- `dc`: http://purl.org/dc/elements/1.1/
- `photoshop`: http://ns.adobe.com/photoshop/1.0/
- `xmpRights`: http://ns.adobe.com/xap/1.0/rights/

**IPTC Extension namespaces:**

- `Iptc4xmpExt`: http://iptc.org/std/Iptc4xmpExt/2008-02-29/
- `plus`: http://ns.useplus.org/ldf/xmp/1.0/
- `xmp`: http://ns.adobe.com/xap/1.0/
- `exif`: http://ns.adobe.com/exif/1.0/

### XMP Usage

- IPTC properties are mapped to XMP namespaces. Core properties may also map to IIM; Extension properties map only to XMP.
- Prefer embedding XMP in the image file. For RAW formats that don't support embedded XMP, use an `.xmp` sidecar (same folder, same base filename).
- When transferring RAW + sidecar, bundle them together to avoid separating metadata from the image.

---

## Minimal Recommended Properties

For identification, rights, and credit:

- Description (Caption)
- Creator(s)
- Copyright Owner
- Copyright Notice
- Credit Line
- Date Created

---

## Controlled Vocabularies

Some properties require a controlled vocabulary URI (not just a human label). Examples: Digital Source Type, Subject Code, Country Code. Published at https://cv.iptc.org/newscodes/.

---

## Accessibility

- **Alt Text** — concise text alternative (~250 char limit, aligned with WCAG).
- **Extended Description** — longer alternative when Alt Text is too short. Should not repeat Alt Text.

---

## AI-Generated Images

- Set **Digital Source Type** to a relevant AI value (e.g., `trainedAlgorithmicMedia`, `compositeSynthetic`).
- Provide **AI System Used** and **AI System Version Used**.
- Include **AI Prompt Information** and **AI Prompt Writer Name** if available.
- Only set Image Creator when there is a human creator.

---

## Preservation

Preserve metadata through editing and export workflows. Do not strip IPTC data unless explicitly required.

---

## Official Links

- Specification (2025.1): https://www.iptc.org/std/photometadata/specification/IPTC-PhotoMetadata-2025.1.html
- User guide: https://www.iptc.org/std/photometadata/documentation/userguide/
- Documentation hub: https://iptc.org/std/photometadata/documentation
- Controlled vocabularies: https://cv.iptc.org/newscodes/
- Local reference image: `assets/reference-images/IPTC-PhotometadataRef-Std2024.1.jpg` (visual reference only; older than 2025.1).
