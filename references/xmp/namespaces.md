# XMP Namespaces

> Part of [XMP Reference](README.md)

Complete reference for all standard XMP namespaces, their URIs, prefixes, and
key properties. Namespaces are the organizational unit of XMP — each defines
a set of property names within a unique XML namespace URI.

---

## Namespace Reference Table

### Core XMP Namespaces

| Prefix | Namespace URI | Schema | Origin |
|--------|---------------|--------|--------|
| `dc` | `http://purl.org/dc/elements/1.1/` | Dublin Core | DCMI |
| `xmp` | `http://ns.adobe.com/xap/1.0/` | XMP Basic | Adobe |
| `xmpRights` | `http://ns.adobe.com/xap/1.0/rights/` | XMP Rights Management | Adobe |
| `xmpMM` | `http://ns.adobe.com/xap/1.0/mm/` | XMP Media Management | Adobe |
| `xmpBJ` | `http://ns.adobe.com/xap/1.0/bj/` | XMP Basic Job Ticket | Adobe |
| `xmpDM` | `http://ns.adobe.com/xmp/1.0/DynamicMedia/` | XMP Dynamic Media | Adobe |
| `xmpNote` | `http://ns.adobe.com/xmp/note/` | XMP Note (extended XMP) | Adobe |
| `xmpTPg` | `http://ns.adobe.com/xap/1.0/t/pg/` | XMP Paged-Text | Adobe |
| `xmpidq` | `http://ns.adobe.com/xmp/Identifier/qual/1.0/` | XMP Identifier Qualifier | Adobe |

### Image/Photo Namespaces

| Prefix | Namespace URI | Schema | Origin |
|--------|---------------|--------|--------|
| `photoshop` | `http://ns.adobe.com/photoshop/1.0/` | Adobe Photoshop | Adobe |
| `crs` | `http://ns.adobe.com/camera-raw-settings/1.0/` | Camera Raw Settings | Adobe |
| `tiff` | `http://ns.adobe.com/tiff/1.0/` | TIFF Properties | Adobe (XMP) |
| `exif` | `http://ns.adobe.com/exif/1.0/` | EXIF Properties | Adobe (XMP) |
| `exifEX` | `http://cipa.jp/exif/1.0/` | EXIF Extension (2.31+) | CIPA |
| `aux` | `http://ns.adobe.com/exif/1.0/aux/` | EXIF Auxiliary | Adobe |
| `dng` | `http://ns.adobe.com/dng/1.0/` | DNG Properties | Adobe |

### IPTC Namespaces

| Prefix | Namespace URI | Schema | Origin |
|--------|---------------|--------|--------|
| `Iptc4xmpCore` | `http://iptc.org/std/Iptc4xmpCore/1.0/xmlns/` | IPTC Core | IPTC |
| `Iptc4xmpExt` | `http://iptc.org/std/Iptc4xmpExt/2008-02-29/` | IPTC Extension | IPTC |
| `plus` | `http://ns.useplus.org/ldf/xmp/1.0/` | PLUS License Data Format | PLUS Coalition |

### XMP Structure Type Namespaces

These namespaces define value types (structures) used as field values in other
namespaces. They are not top-level schemas.

| Prefix | Namespace URI | Structure Type |
|--------|---------------|----------------|
| `stRef` | `http://ns.adobe.com/xap/1.0/sType/ResourceRef#` | Resource Reference |
| `stEvt` | `http://ns.adobe.com/xap/1.0/sType/ResourceEvent#` | Resource Event |
| `stDim` | `http://ns.adobe.com/xap/1.0/sType/Dimensions#` | Dimensions |
| `stFnt` | `http://ns.adobe.com/xap/1.0/sType/Font#` | Font |
| `stJob` | `http://ns.adobe.com/xap/1.0/sType/Job#` | Job |
| `stVer` | `http://ns.adobe.com/xap/1.0/sType/Version#` | Version |
| `stArea` | `http://ns.adobe.com/xmp/sType/Area#` | Area (face regions, MWG regions) |

### MWG (Metadata Working Group) Namespaces

| Prefix | Namespace URI | Schema | Origin |
|--------|---------------|--------|--------|
| `mwg-rs` | `http://www.metadataworkinggroup.com/schemas/regions/` | MWG Regions | MWG |
| `mwg-kw` | `http://www.metadataworkinggroup.com/schemas/keywords/` | MWG Keywords | MWG |
| `mwg-coll` | `http://www.metadataworkinggroup.com/schemas/collections/` | MWG Collections | MWG |

### Apple ImageIO Pre-Registered Namespaces

These 10 namespaces have corresponding `kCGImageMetadataNamespace*` /
`kCGImageMetadataPrefix*` constants and are automatically registered. Tags
using these prefixes can be read/written without calling
`CGImageMetadataRegisterNamespaceForPrefix`:

| ImageIO Constant | Prefix | Namespace URI |
|------------------|--------|---------------|
| `kCGImageMetadataNamespaceExif` | `exif` | `http://ns.adobe.com/exif/1.0/` |
| `kCGImageMetadataNamespaceExifAux` | `aux` | `http://ns.adobe.com/exif/1.0/aux/` |
| `kCGImageMetadataNamespaceExifEX` | `exifEX` | `http://cipa.jp/exif/1.0/` |
| `kCGImageMetadataNamespaceDublinCore` | `dc` | `http://purl.org/dc/elements/1.1/` |
| `kCGImageMetadataNamespaceIPTCCore` | `Iptc4xmpCore` | `http://iptc.org/std/Iptc4xmpCore/1.0/xmlns/` |
| `kCGImageMetadataNamespaceIPTCExtension` | `Iptc4xmpExt` | `http://iptc.org/std/Iptc4xmpExt/2008-02-29/` |
| `kCGImageMetadataNamespacePhotoshop` | `photoshop` | `http://ns.adobe.com/photoshop/1.0/` |
| `kCGImageMetadataNamespaceTIFF` | `tiff` | `http://ns.adobe.com/tiff/1.0/` |
| `kCGImageMetadataNamespaceXMPBasic` | `xmp` | `http://ns.adobe.com/xap/1.0/` |
| `kCGImageMetadataNamespaceXMPRights` | `xmpRights` | `http://ns.adobe.com/xap/1.0/rights/` |

---

## Dublin Core (`dc:`)

**URI:** `http://purl.org/dc/elements/1.1/`
**Origin:** Dublin Core Metadata Initiative (DCMI)
**Purpose:** General-purpose descriptive metadata for any resource
**ImageIO:** Pre-registered (`kCGImageMetadataNamespaceDublinCore`)

The Dublin Core namespace is the most widely used metadata schema. In
photography, it carries titles, descriptions, keywords, creator names, and
rights statements.

| Property | XMP Type | Description |
|----------|----------|-------------|
| `dc:title` | Lang Alt | Name given to the resource |
| `dc:description` | Lang Alt | Textual description of the content |
| `dc:creator` | Seq ProperName | Ordered list of creators (first is primary) |
| `dc:subject` | Bag Text | Keywords / descriptive phrases |
| `dc:rights` | Lang Alt | Informal rights statement |
| `dc:date` | Seq Date | Dates associated with lifecycle events |
| `dc:format` | MIMEType | MIME type (e.g., `"image/jpeg"`) |
| `dc:type` | Bag open Choice | Nature or genre (e.g., `"Image"`) |
| `dc:identifier` | Text | Unambiguous resource identifier |
| `dc:source` | Text | Related resource from which this was derived |
| `dc:language` | Bag Locale | Languages of content (RFC 3066 codes) |
| `dc:relation` | Bag Text | Related resources |
| `dc:coverage` | Text | Spatial or temporal scope |
| `dc:contributor` | Bag ProperName | Other contributors (not in `dc:creator`) |
| `dc:publisher` | Bag ProperName | Entities that make the resource available |

**Key photography usage:**
- `dc:title` — image title (displayed in Lightroom, Bridge, Photos)
- `dc:description` — image caption
- `dc:creator` — photographer name
- `dc:subject` — keywords for search and organization
- `dc:rights` — copyright notice text

> `dc:title`, `dc:description`, and `dc:rights` are **language alternative**
> arrays. Most applications read only the `"x-default"` entry. See
> [`pitfalls.md`](pitfalls.md) for ImageIO-specific `langAlt` issues.

---

## XMP Basic (`xmp:`)

**URI:** `http://ns.adobe.com/xap/1.0/`
**Origin:** Adobe
**Purpose:** Basic descriptive properties common to all resources
**ImageIO:** Pre-registered (`kCGImageMetadataNamespaceXMPBasic`)

> The namespace URI uses `xap` (the original internal codename) but the
> standard prefix is `xmp`. Tools that encounter the older `xap:` prefix
> should treat it as equivalent to `xmp:`.

| Property | XMP Type | Description |
|----------|----------|-------------|
| `xmp:CreateDate` | Date | Date/time the resource was originally created |
| `xmp:ModifyDate` | Date | Date/time the resource was last modified |
| `xmp:MetadataDate` | Date | Date/time any metadata was last changed |
| `xmp:CreatorTool` | AgentName | Application that created the resource (e.g., `"Adobe Photoshop 25.0"`) |
| `xmp:Rating` | Real | User rating: `-1` (rejected), `0` (unrated), `1`-`5` (star rating) |
| `xmp:Label` | Text | User-assigned text label (e.g., color label name) |
| `xmp:Identifier` | Bag Text | Unambiguous identifiers; may use `xmpidq:Scheme` qualifier |
| `xmp:BaseURL` | URI | Base URL for relative URLs in the document |
| `xmp:Nickname` | Text | Short informal name |
| `xmp:Thumbnails` | Alt Thumbnail | Alternative thumbnail images |

**Key photography usage:**
- `xmp:CreateDate` — creation timestamp with timezone (ISO 8601)
- `xmp:ModifyDate` — last modification timestamp
- `xmp:CreatorTool` — software that processed the image
- `xmp:Rating` — star rating (1-5 scale, -1 for rejected)

---

## XMP Rights Management (`xmpRights:`)

**URI:** `http://ns.adobe.com/xap/1.0/rights/`
**Origin:** Adobe
**Purpose:** Legal restrictions associated with a resource
**ImageIO:** Pre-registered (`kCGImageMetadataNamespaceXMPRights`)

| Property | XMP Type | Description |
|----------|----------|-------------|
| `xmpRights:Marked` | Boolean | `True` = rights-managed; `False` = public domain; absent = unknown |
| `xmpRights:Owner` | Bag ProperName | Legal owners of the resource |
| `xmpRights:UsageTerms` | Lang Alt | Text instructions on legal usage, in multiple languages |
| `xmpRights:WebStatement` | URI | URL to a rights/license statement |
| `xmpRights:Certificate` | URI | URL to a rights management certificate |

> These properties express rights information but do **not** provide DRM
> enforcement. They are advisory. For machine-readable licensing, combine
> with the `plus:` namespace (PLUS License Data Format).

---

## XMP Media Management (`xmpMM:`)

**URI:** `http://ns.adobe.com/xap/1.0/mm/`
**Origin:** Adobe
**Purpose:** Asset tracking — document identity, versioning, and provenance
**ImageIO:** Requires manual registration

Used primarily by DAM (Digital Asset Management) systems. Tracks document
lineage across edits, conversions, and derivations.

| Property | XMP Type | Description |
|----------|----------|-------------|
| `xmpMM:DocumentID` | GUID | Persistent identifier for the document across all versions |
| `xmpMM:InstanceID` | GUID | Unique identifier for this specific save/version |
| `xmpMM:OriginalDocumentID` | GUID | ID of the original source document (survives format conversions) |
| `xmpMM:DerivedFrom` | ResourceRef (stRef) | Reference to the immediate predecessor resource |
| `xmpMM:History` | Seq ResourceEvent (stEvt) | Ordered list of high-level actions taken on this resource |
| `xmpMM:Ingredients` | Bag ResourceRef (stRef) | Resources incorporated into this document |
| `xmpMM:RenditionClass` | RenditionClass | Rendition type (e.g., `"default"`, `"draft"`, `"thumbnail"`) |
| `xmpMM:RenditionParams` | Text | Additional rendition parameters |
| `xmpMM:VersionID` | Text | Version identifier |
| `xmpMM:Versions` | Seq Version (stVer) | Version history |
| `xmpMM:Manager` | AgentName | DAM system managing this resource |
| `xmpMM:ManageTo` | URI | URI identifying the managed resource |
| `xmpMM:ManageFrom` | ResourceRef (stRef) | Reference to the unmanaged state |
| `xmpMM:ManageUI` | URI | URI for human-readable management interface |
| `xmpMM:LastURL` | URI | URL of last known location |

**Document ID lifecycle:**
1. New file created: `DocumentID` and `InstanceID` assigned
2. File edited and saved: `InstanceID` changes; `DocumentID` stays
3. File "Save As" to new format: new `DocumentID`; `OriginalDocumentID`
   preserves the chain back to the initial file; `DerivedFrom` points to the
   previous version

**Property ownership:**
- `DocumentID`, `RenditionClass`, `RenditionParams`, `VersionID`, `Versions`:
  owned by DAM system for managed files, or by applications for unmanaged files
- `DerivedFrom`: owned by DAM system or application
- `History`: always owned by the application
- `InstanceID`: updated by whichever agent saves the file

---

## XMP Basic Job Ticket (`xmpBJ:`)

**URI:** `http://ns.adobe.com/xap/1.0/bj/`
**Origin:** Adobe
**Purpose:** Link documents to external job management workflows
**ImageIO:** Requires manual registration

| Property | XMP Type | Description |
|----------|----------|-------------|
| `xmpBJ:JobRef` | Bag stJob | External job references (multiple jobs can reference one document) |

### Job Structure (`stJob:`)

| Field | Type | Description |
|-------|------|-------------|
| `stJob:name` | Text | Informal name of the job |
| `stJob:id` | Text | Unique ID for the job |
| `stJob:url` | URI | URL for job management |

---

## XMP Note (`xmpNote:`)

**URI:** `http://ns.adobe.com/xmp/note/`
**Origin:** Adobe
**Purpose:** Internal XMP processing annotations, primarily Extended XMP

| Property | XMP Type | Description |
|----------|----------|-------------|
| `xmpNote:HasExtendedXMP` | Text | MD5 digest (128-bit, 32-char uppercase hex) of the Extended XMP serialization. Present only in Standard XMP when the packet has been split. |

> This property is the link between Standard XMP and Extended XMP in JPEG
> files. See [`embedding.md`](embedding.md) for Extended XMP details.

---

## Photoshop (`photoshop:`)

**URI:** `http://ns.adobe.com/photoshop/1.0/`
**Origin:** Adobe
**Purpose:** Properties from Adobe Photoshop that map to IPTC IIM fields
**ImageIO:** Pre-registered (`kCGImageMetadataNamespacePhotoshop`)

Many of these properties mirror IPTC IIM datasets. They are commonly used
alongside Dublin Core and IPTC Core for editorial metadata.

| Property | XMP Type | IPTC IIM Equivalent | Description |
|----------|----------|---------------------|-------------|
| `photoshop:DateCreated` | Date | 2:55 + 2:60 | Intellectual creation date |
| `photoshop:Headline` | Text | 2:105 | Brief synopsis / headline |
| `photoshop:Credit` | Text | 2:110 | Provider / credit line |
| `photoshop:Source` | Text | 2:115 | Original source / owner |
| `photoshop:Instructions` | Text | 2:40 | Special handling instructions |
| `photoshop:Urgency` | Integer | 2:10 | Priority: 1 (highest) to 8 (lowest), 0 = reserved |
| `photoshop:City` | Text | 2:90 | City of content origin |
| `photoshop:State` | Text | 2:95 | Province/state of content origin |
| `photoshop:Country` | Text | 2:101 | Country name of content origin |
| `photoshop:TransmissionReference` | Text | 2:103 | Original transmission reference |
| `photoshop:Category` | Text | 2:15 | Subject category (deprecated — use `Iptc4xmpCore:SubjectCode`) |
| `photoshop:SupplementalCategories` | Bag Text | 2:20 | Supplemental categories (deprecated) |
| `photoshop:AuthorsPosition` | Text | 2:85 | Creator's job title |
| `photoshop:CaptionWriter` | Text | 2:122 | Writer/editor of the caption |
| `photoshop:ICCProfile` | Text | -- | ICC profile name (informational) |
| `photoshop:ColorMode` | Integer | -- | Color mode: 0=Bitmap, 1=Grayscale, 2=Indexed, 3=RGB, 4=CMYK, 7=Multichannel, 8=Duotone, 9=Lab |
| `photoshop:DocumentAncestors` | Bag Text | -- | Ancestor document identifiers |
| `photoshop:History` | Text | -- | Photoshop edit history |
| `photoshop:SidecarForExtension` | Text | -- | Extension of the file this sidecar relates to |

---

## Camera Raw Settings (`crs:`)

**URI:** `http://ns.adobe.com/camera-raw-settings/1.0/`
**Origin:** Adobe
**Purpose:** Non-destructive processing parameters from Adobe Camera Raw / Lightroom
**ImageIO:** Requires manual registration

This namespace stores parametric editing instructions. Every slider, checkbox,
or adjustment in Lightroom/ACR is recorded here. The properties are
Adobe-specific and not an interoperability standard, but they are ubiquitous in
photography workflows.

### Key Properties (selection)

| Property | Type | Range | Description |
|----------|------|-------|-------------|
| `crs:Version` | Text | -- | Camera Raw version (e.g., `"15.0"`) |
| `crs:ProcessVersion` | Text | -- | Process version (e.g., `"15.4"`) |
| `crs:WhiteBalance` | Text | -- | WB preset (`"As Shot"`, `"Auto"`, `"Daylight"`, etc.) |
| `crs:Temperature` | Integer | 2000-50000 | Color temperature (Kelvin) |
| `crs:Tint` | Integer | -150 to 150 | Tint adjustment |
| `crs:Exposure2012` | Real | -5.0 to 5.0 | Exposure compensation |
| `crs:Contrast2012` | Integer | -100 to 100 | Contrast |
| `crs:Highlights2012` | Integer | -100 to 100 | Highlights recovery |
| `crs:Shadows2012` | Integer | -100 to 100 | Shadow recovery |
| `crs:Whites2012` | Integer | -100 to 100 | White point |
| `crs:Blacks2012` | Integer | -100 to 100 | Black point |
| `crs:Clarity2012` | Integer | -100 to 100 | Clarity (midtone contrast) |
| `crs:Dehaze` | Integer | -100 to 100 | Dehaze amount |
| `crs:Texture` | Integer | -100 to 100 | Texture enhancement |
| `crs:Vibrance` | Integer | -100 to 100 | Vibrance |
| `crs:Saturation` | Integer | -100 to 100 | Saturation |
| `crs:Sharpness` | Integer | 0-150 | Sharpening amount |
| `crs:SharpenRadius` | Real | 0.5-3.0 | Sharpening radius |
| `crs:SharpenDetail` | Integer | 0-100 | Sharpening detail |
| `crs:LuminanceSmoothing` | Integer | 0-100 | Luminance noise reduction |
| `crs:ColorNoiseReduction` | Integer | 0-100 | Color noise reduction |
| `crs:HasCrop` | Boolean | -- | Whether a crop is applied |
| `crs:CropTop` | Real | 0-1 | Crop top (normalized) |
| `crs:CropLeft` | Real | 0-1 | Crop left (normalized) |
| `crs:CropBottom` | Real | 0-1 | Crop bottom (normalized) |
| `crs:CropRight` | Real | 0-1 | Crop right (normalized) |
| `crs:CropAngle` | Real | -- | Crop rotation angle |
| `crs:ToneCurvePV2012` | Seq Text | -- | Tone curve control points |
| `crs:HasSettings` | Boolean | -- | Whether ACR settings are present |
| `crs:RawFileName` | Text | -- | Original RAW filename |
| `crs:LensProfileEnable` | Integer | 0/1 | Lens profile correction enabled |
| `crs:AutoLateralCA` | Integer | 0/1 | Auto chromatic aberration correction |
| `crs:GrainAmount` | Integer | 0-100 | Film grain amount |

> The `crs:` namespace has hundreds of properties covering every aspect of
> Camera Raw processing. Only the most commonly encountered are listed here.
> The full set evolves with each Adobe Camera Raw release. Properties suffixed
> with `2012` use the Process Version 2012+ algorithm (current default).

---

## TIFF Properties (`tiff:`)

**URI:** `http://ns.adobe.com/tiff/1.0/`
**Origin:** Adobe (XMP for TIFF)
**Purpose:** IFD0 tag values expressed in XMP
**ImageIO:** Pre-registered (`kCGImageMetadataNamespaceTIFF`)

These properties map directly to TIFF IFD0 binary tags. For the complete
EXIF binary tag-to-XMP mapping table, see `../exif/xmp-mapping.md`.

| Property | XMP Type | TIFF Tag | Description |
|----------|----------|----------|-------------|
| `tiff:Make` | Text | 0x010F | Camera manufacturer |
| `tiff:Model` | Text | 0x0110 | Camera model |
| `tiff:Orientation` | Integer | 0x0112 | EXIF orientation (1-8) |
| `tiff:Software` | Text | 0x0131 | Processing software |
| `tiff:DateTime` | Date | 0x0132 | File modification date |
| `tiff:Artist` | Text | 0x013B | Creator name |
| `tiff:Copyright` | Text | 0x8298 | Copyright notice |
| `tiff:ImageDescription` | Lang Alt | 0x010E | Image description |
| `tiff:XResolution` | Rational | 0x011A | Horizontal resolution |
| `tiff:YResolution` | Rational | 0x011B | Vertical resolution |
| `tiff:ResolutionUnit` | Integer | 0x0128 | Unit: 2=inch, 3=centimeter |
| `tiff:ImageWidth` | Integer | 0x0100 | Image width in pixels |
| `tiff:ImageLength` | Integer | 0x0101 | Image height in pixels |
| `tiff:BitsPerSample` | Seq Integer | 0x0102 | Bits per component |
| `tiff:Compression` | Integer | 0x0103 | Compression scheme |
| `tiff:PhotometricInterpretation` | Integer | 0x0106 | Color model interpretation |
| `tiff:SamplesPerPixel` | Integer | 0x0115 | Number of components |
| `tiff:PlanarConfiguration` | Integer | 0x011C | Data arrangement |
| `tiff:YCbCrSubSampling` | Seq Integer | 0x0212 | Chroma subsampling |
| `tiff:YCbCrPositioning` | Integer | 0x0213 | Chroma sample position |
| `tiff:TransferFunction` | Seq Integer | 0x012D | Transfer function |
| `tiff:WhitePoint` | Seq Rational | 0x013E | White point chromaticity |
| `tiff:PrimaryChromaticities` | Seq Rational | 0x013F | Primary chromaticities |
| `tiff:ReferenceBlackWhite` | Seq Rational | 0x0214 | Black/white reference |
| `tiff:NativeDigest` | Text | -- | Hash for change detection (Adobe-specific) |

---

## EXIF Properties (`exif:`)

**URI:** `http://ns.adobe.com/exif/1.0/`
**Origin:** Adobe (XMP for EXIF)
**Purpose:** EXIF IFD tag values expressed in XMP
**ImageIO:** Pre-registered (`kCGImageMetadataNamespaceExif`)

Contains ~60 properties mapping to Exif SubIFD binary tags. For the complete
mapping table with all properties, see `../exif/xmp-mapping.md`.

**Key properties (frequently accessed):**

| Property | XMP Type | Description |
|----------|----------|-------------|
| `exif:DateTimeOriginal` | Date | Original capture date (ISO 8601 with timezone) |
| `exif:DateTimeDigitized` | Date | Digitization date |
| `exif:ExposureTime` | Rational | Shutter speed (e.g., `"1/250"`) |
| `exif:FNumber` | Rational | Aperture f-number |
| `exif:ISOSpeedRatings` | Seq Integer | ISO sensitivity values |
| `exif:FocalLength` | Rational | Focal length in mm |
| `exif:FocalLengthIn35mmFilm` | Integer | 35mm equivalent focal length |
| `exif:ExposureProgram` | Integer | Program mode (0-8) |
| `exif:MeteringMode` | Integer | Metering mode (0-6, 255) |
| `exif:Flash` | Structure | Flash status (Fired, Return, Mode, Function, RedEyeMode fields) |
| `exif:WhiteBalance` | Integer | White balance (0=Auto, 1=Manual) |
| `exif:ColorSpace` | Integer | Color space (1=sRGB, 65535=Uncalibrated) |
| `exif:UserComment` | Lang Alt | User comment text |
| `exif:ExifVersion` | Text | EXIF version string (e.g., `"0232"`) |
| `exif:PixelXDimension` | Integer | Valid image width |
| `exif:PixelYDimension` | Integer | Valid image height |
| `exif:GPSLatitude` | Text | GPS latitude (encoded as `"DDD,MM,SS.SSK"`) |
| `exif:GPSLongitude` | Text | GPS longitude (encoded as `"DDD,MM,SS.SSK"`) |
| `exif:GPSAltitude` | Rational | GPS altitude in meters |
| `exif:GPSAltitudeRef` | Integer | 0=above sea level, 1=below |
| `exif:GPSTimeStamp` | Date | GPS UTC time |

> **DateTime note:** In XMP, EXIF DateTimeOriginal is stored as a full ISO
> 8601 string with timezone (e.g., `"2024-06-15T14:30:00+05:30"`). The
> separate EXIF `OffsetTime*` tags are folded into this value — they do not
> exist as separate XMP properties.

---

## EXIF Extension (`exifEX:`)

**URI:** `http://cipa.jp/exif/1.0/`
**Origin:** CIPA (Camera & Imaging Products Association)
**Purpose:** EXIF 2.31+ tags that postdate the original `exif:` namespace
**ImageIO:** Pre-registered (`kCGImageMetadataNamespaceExifEX`)

| Property | XMP Type | EXIF Tag | Description |
|----------|----------|----------|-------------|
| `exifEX:CameraOwnerName` | Text | 0xA430 | Camera owner |
| `exifEX:BodySerialNumber` | Text | 0xA431 | Camera body serial number |
| `exifEX:LensSpecification` | Seq Rational | 0xA432 | [min FL, max FL, min FN, max FN] |
| `exifEX:LensMake` | Text | 0xA433 | Lens manufacturer |
| `exifEX:LensModel` | Text | 0xA434 | Lens model name |
| `exifEX:LensSerialNumber` | Text | 0xA435 | Lens serial number |
| `exifEX:CompositeImage` | Integer | 0xA460 | 0=Unknown, 1=Not composite, 2=General composite, 3=Composite captured simultaneously |
| `exifEX:SourceImageNumberOfCompositeImage` | Seq Integer | 0xA461 | Number of source images |
| `exifEX:SourceExposureTimesOfCompositeImage` | Text | 0xA462 | Source exposure times |

---

## EXIF Auxiliary (`aux:`)

**URI:** `http://ns.adobe.com/exif/1.0/aux/`
**Origin:** Adobe
**Purpose:** Supplementary lens/camera data predating EXIF 2.3
**ImageIO:** Pre-registered (`kCGImageMetadataNamespaceExifAux`)

| Property | XMP Type | exifEX Equivalent | Description |
|----------|----------|-------------------|-------------|
| `aux:LensInfo` | Seq Rational | `exifEX:LensSpecification` | Lens spec [min FL, max FL, min FN, max FN] |
| `aux:Lens` | Text | `exifEX:LensModel` | Lens model name |
| `aux:LensID` | Text | -- | Lens numeric identifier |
| `aux:LensSerialNumber` | Text | `exifEX:LensSerialNumber` | Lens serial number |
| `aux:SerialNumber` | Text | `exifEX:BodySerialNumber` | Camera body serial number |
| `aux:OwnerName` | Text | `exifEX:CameraOwnerName` | Camera owner |
| `aux:ImageNumber` | Integer | -- | Image sequence number |
| `aux:FlashCompensation` | Rational | -- | Flash exposure compensation |
| `aux:Firmware` | Text | -- | Firmware version |
| `aux:ApproximateFocusDistance` | Rational | -- | Approximate focus distance in meters |
| `aux:DistortionCorrectionAlreadyApplied` | Boolean | -- | Lens distortion correction flag |
| `aux:LateralChromaticAberrationCorrectionAlreadyApplied` | Boolean | -- | Lateral CA correction flag |
| `aux:VignetteCorrectionAlreadyApplied` | Boolean | -- | Vignette correction flag |

> When both `aux:` and `exifEX:` versions of a property exist, the `exifEX:`
> (standard CIPA) value takes precedence per MWG guidelines.

---

## IPTC Core (`Iptc4xmpCore:`)

**URI:** `http://iptc.org/std/Iptc4xmpCore/1.0/xmlns/`
**Origin:** IPTC (International Press Telecommunications Council)
**Purpose:** Core editorial metadata for news and stock photography
**ImageIO:** Pre-registered (`kCGImageMetadataNamespaceIPTCCore`)

Properties are grouped into administrative, descriptive, and rights categories.

| Property | XMP Type | Description |
|----------|----------|-------------|
| `Iptc4xmpCore:CountryCode` | Text | ISO 3166-1 alpha-3 country code |
| `Iptc4xmpCore:IntellectualGenre` | Text | Intellectual genre (e.g., `"Current"`, `"Feature"`) |
| `Iptc4xmpCore:Scene` | Bag Text | IPTC Scene codes |
| `Iptc4xmpCore:SubjectCode` | Bag Text | IPTC Subject Reference codes |
| `Iptc4xmpCore:Location` | Text | Sublocation (within city) |
| `Iptc4xmpCore:CreatorContactInfo` | ContactInfo struct | Creator's contact information (see below) |

### CreatorContactInfo Structure

| Field | Type | Description |
|-------|------|-------------|
| `Iptc4xmpCore:CiEmailWork` | Text | Email address |
| `Iptc4xmpCore:CiTelWork` | Text | Phone number |
| `Iptc4xmpCore:CiAdrExtadr` | Text | Street address |
| `Iptc4xmpCore:CiAdrCity` | Text | City |
| `Iptc4xmpCore:CiAdrRegion` | Text | State/province |
| `Iptc4xmpCore:CiAdrPcode` | Text | Postal code |
| `Iptc4xmpCore:CiAdrCtry` | Text | Country |
| `Iptc4xmpCore:CiUrlWork` | Text | Website URL |

---

## IPTC Extension (`Iptc4xmpExt:`)

**URI:** `http://iptc.org/std/Iptc4xmpExt/2008-02-29/`
**Origin:** IPTC
**Purpose:** Extended editorial properties — detailed location, people, artwork, licensing, AI provenance
**ImageIO:** Pre-registered (`kCGImageMetadataNamespaceIPTCExtension`)

| Property | XMP Type | Description |
|----------|----------|-------------|
| `Iptc4xmpExt:PersonInImage` | Bag Text | Simple list of person names |
| `Iptc4xmpExt:PersonInImageWDetails` | Bag PersonDetails struct | Detailed person info (name, ID, description, characteristics) |
| `Iptc4xmpExt:LocationShown` | Bag LocationDetails struct | Where the image content is located |
| `Iptc4xmpExt:LocationCreated` | Bag LocationDetails struct | Where the photo was taken |
| `Iptc4xmpExt:ArtworkOrObject` | Bag ArtworkOrObjectDetails struct | Artwork or objects depicted |
| `Iptc4xmpExt:DigitalImageGUID` | URI | Globally unique image identifier |
| `Iptc4xmpExt:RegistryId` | Bag RegistryEntryDetails struct | Image registry entries |
| `Iptc4xmpExt:Event` | Lang Alt | Event name |
| `Iptc4xmpExt:MaxAvailWidth` | Integer | Maximum available width in pixels |
| `Iptc4xmpExt:MaxAvailHeight` | Integer | Maximum available height in pixels |
| `Iptc4xmpExt:OrganisationInImageName` | Bag Text | Organizations shown in the image |
| `Iptc4xmpExt:OrganisationInImageCode` | Bag Text | Organization identifiers |
| `Iptc4xmpExt:AboutCvTerm` | Bag CVTermDetails struct | Controlled vocabulary terms about the content |
| `Iptc4xmpExt:DigitalSourceType` | URI | How the image was created (see below) |
| `Iptc4xmpExt:ImageSupplier` | Bag ImageSupplierDetails struct | Image supplier information |
| `Iptc4xmpExt:ImageSupplierImageID` | Text | Supplier's image ID |

### DigitalSourceType Values (IPTC NewsCodes)

This property is increasingly important for AI transparency:

| URI | Meaning |
|-----|---------|
| `http://cv.iptc.org/newscodes/digitalsourcetype/digitalCapture` | Photograph from a digital camera |
| `http://cv.iptc.org/newscodes/digitalsourcetype/negativeFilm` | Scanned from negative film |
| `http://cv.iptc.org/newscodes/digitalsourcetype/positiveFilm` | Scanned from positive film |
| `http://cv.iptc.org/newscodes/digitalsourcetype/print` | Scanned from a print |
| `http://cv.iptc.org/newscodes/digitalsourcetype/softwareImage` | Created by software (non-AI) |
| `http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia` | Created using a model trained on sampled content (AI-generated) |
| `http://cv.iptc.org/newscodes/digitalsourcetype/compositeSynthetic` | Composite with synthetic elements |
| `http://cv.iptc.org/newscodes/digitalsourcetype/algorithmicMedia` | Created purely by algorithm without sampled training data |
| `http://cv.iptc.org/newscodes/digitalsourcetype/compositeWithTrainedAlgorithmicMedia` | Composite including AI-generated elements |

### LocationDetails Structure

| Field | Type | Description |
|-------|------|-------------|
| `Iptc4xmpExt:Sublocation` | Text | Specific location name |
| `Iptc4xmpExt:City` | Text | City |
| `Iptc4xmpExt:ProvinceState` | Text | Province or state |
| `Iptc4xmpExt:CountryName` | Text | Country name |
| `Iptc4xmpExt:CountryCode` | Text | ISO 3166-1 country code |
| `Iptc4xmpExt:WorldRegion` | Text | World region |
| `Iptc4xmpExt:LocationId` | Bag URI | Location identifiers (Wikidata, GeoNames) |

---

## PLUS License Data Format (`plus:`)

**URI:** `http://ns.useplus.org/ldf/xmp/1.0/`
**Origin:** PLUS Coalition
**Purpose:** Standardized licensing and rights metadata
**ImageIO:** Requires manual registration

| Property | XMP Type | Description |
|----------|----------|-------------|
| `plus:Version` | Text | PLUS schema version |
| `plus:Licensor` | Seq Licensor struct | Licensor details |
| `plus:LicensorURL` | URI | Licensor website |
| `plus:ModelReleaseStatus` | URI | Model release status code |
| `plus:ModelReleaseID` | Bag Text | Model release identifiers |
| `plus:PropertyReleaseStatus` | URI | Property release status code |
| `plus:PropertyReleaseID` | Bag Text | Property release identifiers |
| `plus:ImageCreator` | Seq ImageCreator struct | Image creator info |
| `plus:CopyrightOwner` | Seq CopyrightOwner struct | Copyright owner info |
| `plus:ImageSupplier` | Seq ImageSupplier struct | Image supplier info |
| `plus:MinorModelAgeDisclosure` | URI | Age range code for minor model |
| `plus:CreditLineRequired` | URI | Whether credit line is required |

### ModelReleaseStatus Values

| URI | Meaning |
|-----|---------|
| `http://ns.useplus.org/ldf/vocab/MR-NON` | Not Applicable |
| `http://ns.useplus.org/ldf/vocab/MR-NAP` | Not Applicable |
| `http://ns.useplus.org/ldf/vocab/MR-UMR` | Unlimited Model Releases |
| `http://ns.useplus.org/ldf/vocab/MR-LMR` | Limited or Incomplete Model Releases |

> The `plus:` namespace requires manual registration in ImageIO:
> `CGImageMetadataRegisterNamespaceForPrefix(metadata,
> "http://ns.useplus.org/ldf/xmp/1.0/" as CFString, "plus" as CFString, &error)`

---

## Structure Type Namespaces

### Resource Reference (`stRef:`)

**URI:** `http://ns.adobe.com/xap/1.0/sType/ResourceRef#`

Used as the value type for `xmpMM:DerivedFrom`, `xmpMM:Ingredients`, etc.

| Field | Type | Description |
|-------|------|-------------|
| `stRef:documentID` | GUID | Referenced document's `xmpMM:DocumentID` |
| `stRef:instanceID` | GUID | Referenced document's `xmpMM:InstanceID` |
| `stRef:originalDocumentID` | GUID | Original document ID |
| `stRef:renditionClass` | RenditionClass | Rendition type |
| `stRef:renditionParams` | Text | Rendition parameters |
| `stRef:manager` | AgentName | DAM system name |
| `stRef:managerVariant` | Text | DAM system variant |
| `stRef:manageTo` | URI | Managed resource URI |
| `stRef:manageUI` | URI | Management UI URI |
| `stRef:versionID` | Text | Version identifier |
| `stRef:filePath` | URI | File path |
| `stRef:lastModifyDate` | Date | Last modification date |
| `stRef:partMapping` | Text | Part mapping specification |

### Resource Event (`stEvt:`)

**URI:** `http://ns.adobe.com/xap/1.0/sType/ResourceEvent#`

Used as the element type in `xmpMM:History` arrays.

| Field | Type | Description |
|-------|------|-------------|
| `stEvt:action` | open Choice | Action taken (`"created"`, `"saved"`, `"converted"`, `"derived"`, `"printed"`, etc.) |
| `stEvt:when` | Date | When the action occurred |
| `stEvt:softwareAgent` | AgentName | Software that performed the action |
| `stEvt:instanceID` | GUID | `xmpMM:InstanceID` at the time of the action |
| `stEvt:parameters` | Text | Additional action parameters |
| `stEvt:changed` | Text | Changed parts (e.g., `"/metadata"`, `"/content"`) |

### Dimensions (`stDim:`)

**URI:** `http://ns.adobe.com/xap/1.0/sType/Dimensions#`

| Field | Type | Description |
|-------|------|-------------|
| `stDim:w` | Real | Width |
| `stDim:h` | Real | Height |
| `stDim:unit` | open Choice | Unit (`"pixel"`, `"inch"`, `"mm"`, etc.) |

### Area (`stArea:`)

**URI:** `http://ns.adobe.com/xmp/sType/Area#`

Used for face/region metadata (MWG Regions specification, used by Lightroom,
Picasa, Windows Photo Gallery).

| Field | Type | Description |
|-------|------|-------------|
| `stArea:x` | Real | Center X coordinate (normalized 0-1) |
| `stArea:y` | Real | Center Y coordinate (normalized 0-1) |
| `stArea:w` | Real | Width (normalized 0-1) |
| `stArea:h` | Real | Height (normalized 0-1) |
| `stArea:d` | Real | Diameter (normalized, for circular regions) |
| `stArea:unit` | Text | Unit type (`"normalized"` is standard) |

---

## Custom Namespace Registration

Any organization can define a custom XMP namespace. A custom namespace requires:

1. **A unique URI** — by convention ending with `/` or `#`
2. **A prefix** — short abbreviation for use in serialization
3. **Property definitions** — names and types for each property

### Example: Registering in ImageIO

```swift
let mutable = CGImageMetadataCreateMutable()
var error: Unmanaged<CFError>?

// Register custom namespace
CGImageMetadataRegisterNamespaceForPrefix(
    mutable,
    "http://example.com/myapp/1.0/" as CFString,   // namespace URI
    "myapp" as CFString,                             // prefix
    &error
)

// Now create and set tags using the custom namespace
let tag = CGImageMetadataTagCreate(
    "http://example.com/myapp/1.0/" as CFString,
    "myapp" as CFString,
    "ProcessingVersion" as CFString,
    .string,
    "2.1" as CFString
)!

CGImageMetadataSetTagWithPath(mutable, nil, "myapp:ProcessingVersion" as CFString, tag)
```

### Conventions for Custom Namespaces

- URI should be a URL you control (prevents collisions)
- URI should end with `/` or `#` (standard XML namespace convention; some
  forms of RDF shorthand concatenate a namespace URI with an element name to
  form a new URI, so the separator is important)
- Prefix should be short, lowercase, and descriptive
- Define property names using camelCase (matching XMP convention)
- Document the namespace schema for interoperability
- In ImageIO, **all non-standard namespaces must be registered** before
  writing; `CGImageMetadataSetTagWithPath` returns `false` silently for
  unregistered namespaces
