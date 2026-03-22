# XMP

XMP standard (ISO 16684-1). Extensible namespace-based metadata container.

## ImageIO API surface

Not a property dictionary — accessed via a separate tree-based API:

- `CGImageMetadata` (immutable)
- `CGMutableImageMetadata` (mutable)
- `CGImageMetadataTag`
- `CGImageSourceCopyMetadataAtIndex`
- `CGImageDestinationAddImageAndMetadata`

## Planned content

- RDF/XML serialization model
- Namespace system and standard prefixes (dc, xmp, xmpRights, photoshop, tiff, exif, crs, Iptc4xmpCore, Iptc4xmpExt, plus)
- Value types: simple values, bags, sequences, alternatives, structures
- Embedding locations per format (JPEG APP1, TIFF, PNG iTXt, HEIF, PDF)
- Sidecar `.xmp` files for RAW formats
- Mapping between CGImageMetadata API and the XMP data model
- XMP namespaces and prefixes recognized by ImageIO
