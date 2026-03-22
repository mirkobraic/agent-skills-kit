# IPTC Photo Metadata Standard - Overview

## Table of contents

1. Scope and schemas
2. Generic notes
3. What's new in 2025.1
4. Specification table template and data types
5. TechReference (machine-readable spec)
6. XMP namespaces and prefixes
7. Saving metadata values to files
8. Official links

## 1. Scope and schemas

- IPTC Photo Metadata defines properties for photographs and groups them into Administrative, Descriptive, and Rights-related properties.
- The standard is split into two schemas:
  - IPTC Core (IIM heritage, backwards-compatible)
  - IPTC Extension (more granular properties, includes additional rights-related properties from PLUS)
- The standard version 2025.1 includes Core 1.5 and Extension 1.9.

## 1.1 Core vs Extension (what is different)

- IPTC Core is the legacy-compatible set of properties based on the old IPTC IIM standard. These properties are meant to remain interoperable with older software and workflows.
- IPTC Extension adds newer, more granular properties and is where most new properties are introduced. Extension properties are XMP-only (no IIM mapping).
- When a property has both IIM and XMP mappings, treat it as Core and write both for maximum compatibility. If it is Extension-only, write it to XMP.

## 2. Generic notes

- Rights-related metadata values can be affected by laws and regulations in the region of use and by contracts applied to the image.
- Technical metadata (camera maker data, ICC profiles, positioning data, etc.) is outside the IPTC Photo Metadata scope and handled by other standards.

## 3. What's new in 2025.1

- The 2025.1 update adds four new IPTC Extension properties: AI Prompt Information, AI Prompt Writer Name, AI System Used, and AI System Version Used.

## 4. Specification table template and data types

Each property in the specification has a table that can include:

- Name, Definition, Help Text
- User Notes and Implementation Notes
- Label (UI display text)
- Basic Specs (data type and cardinality)
- Controlled Vocabulary notes (if required)
- History notes (when added or changed)
- XMP Specs (namespace prefix and property name; XMP value type)
- IIM Specs (dataset identifier and max bytes for text fields)
- JSON Specs (property name with JSON data type)
- ExifTool tags (non-normative helper row)

Basic data types used in the spec:

- Text, Integer, Decimal, URL, URI, or a Structure
- Cardinality values: 1, 0..1, 0..unbounded, 1..unbounded

Notes about property naming:

- A property marked (legacy) has a better replacement in IPTC Extension and should be phased out.
- A property marked (DEPRECATED) should no longer be used; the spec table notes a replacement.

## 5. TechReference (machine-readable spec)

Use TechReference when you need authoritative, machine-readable details for property names, data types, and XMP/IIM/JSON mappings. These downloads require network access unless you cache them locally.

Downloads for 2025.1:

- JSON: https://iptc.org/std/photometadata/specification/iptc-pmd-techreference_2025.1.json
- YAML: https://iptc.org/std/photometadata/specification/iptc-pmd-techreference_2025.1.yml
- Cached copies (local): `references/iptc-pmd-techreference_2025.1.json`, `references/iptc-pmd-techreference_2025.1.yml`
  - Refresh the cached files when a newer IPTC Photo Metadata version is released.

IPTC also provides documentation on how to use TechReference from the specification site.

## 6. XMP namespaces and prefixes

IPTC Core schema namespaces:

- Iptc4xmpCore: http://iptc.org/std/Iptc4xmpCore/1.0/xmlns/
- dc: http://purl.org/dc/elements/1.1/
- photoshop: http://ns.adobe.com/photoshop/1.0/
- xmpRights: http://ns.adobe.com/xap/1.0/rights/

IPTC Extension schema namespaces:

- Iptc4xmpExt: http://iptc.org/std/Iptc4xmpExt/2008-02-29/
- plus: http://ns.useplus.org/ldf/xmp/1.0/
- xmp: http://ns.adobe.com/xap/1.0/
- xmpRights: http://ns.adobe.com/xap/1.0/rights/
- exif: http://ns.adobe.com/exif/1.0/

## 6.1 What XMP is and how to use it

- XMP (Extensible Metadata Platform) is a standard for embedding metadata as XML in a file, or storing it in a sidecar file when embedding is not possible.
- IPTC Photo Metadata properties are mapped to XMP namespaces. Core properties may also map to IIM, while Extension properties map only to XMP.
- Prefer embedding XMP in the image file whenever the format supports it. For RAW formats that do not support embedded XMP, store an `.xmp` sidecar alongside the image.
- When writing Core properties, store values in both IIM and XMP if possible. When writing Extension properties, store them in XMP only.

## 6.2 RAW + XMP sidecar packaging

- For RAW formats (e.g., NEF, CR2, ARW, DNG), keep the XMP sidecar in the same folder with the same base filename and `.xmp` extension (for example, `IMG_0001.NEF` + `IMG_0001.xmp`).
- When transferring or delivering files, bundle the RAW and `.xmp` together (for example, zip the folder) to avoid separating metadata from the image.

## 7. Saving metadata values to files

- When a property has both IIM and XMP mappings, values should be saved in both formats.
- IPTC Extension properties are XMP-only.

## 8. Official links

- Specification (2025.1): https://www.iptc.org/std/photometadata/specification/IPTC-PhotoMetadata-2025.1.html
- Documentation hub: https://iptc.org/std/photometadata/documentation
- Local reference image: `assets/reference-images/IPTC-PhotometadataRef-Std2024.1.jpg` (visual reference only; older than 2025.1).
