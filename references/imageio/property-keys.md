# CGImageProperties — Complete Key Reference

Every `kCGImageProperty*` constant defined in `CGImageProperties.h`, organized
by dictionary. All keys available since iOS 4.0 unless noted otherwise.

---

## Top-Level Keys

These keys appear at the root level of the dictionary returned by
`CGImageSourceCopyPropertiesAtIndex`.

### Image Dimensions & Format

| Key | Type | Purpose |
|-----|------|---------|
| `kCGImagePropertyPixelWidth` | CFNumber | Width in pixels |
| `kCGImagePropertyPixelHeight` | CFNumber | Height in pixels |
| `kCGImagePropertyDPIWidth` | CFNumber | Horizontal resolution (DPI) |
| `kCGImagePropertyDPIHeight` | CFNumber | Vertical resolution (DPI) |
| `kCGImagePropertyDepth` | CFNumber | Bits per component |
| `kCGImagePropertyOrientation` | CFNumber (1–8) | EXIF orientation tag |
| `kCGImagePropertyIsFloat` | CFBoolean | Floating-point pixel components |
| `kCGImagePropertyIsIndexed` | CFBoolean | Indexed (palette) color |
| `kCGImagePropertyHasAlpha` | CFBoolean | Has alpha channel |

### Color

| Key | Type | Purpose |
|-----|------|---------|
| `kCGImagePropertyColorModel` | CFString | Color model (see values below) |
| `kCGImagePropertyProfileName` | CFString | ICC profile name (e.g. "sRGB") |
| `kCGImagePropertyNamedColorSpace` | CFString | Named color space |

#### Color Model Values

| Constant | Value |
|----------|-------|
| `kCGImagePropertyColorModelRGB` | `"RGB"` |
| `kCGImagePropertyColorModelGray` | `"Gray"` |
| `kCGImagePropertyColorModelCMYK` | `"CMYK"` |
| `kCGImagePropertyColorModelLab` | `"Lab"` |

### File & Multi-Image

| Key | Type | Purpose | iOS |
|-----|------|---------|-----|
| `kCGImagePropertyFileSize` | CFNumber | File size in bytes | 4.0+ |
| `kCGImagePropertyFileContentsDictionary` | CFDictionary | File-level info | 11.0+ |
| `kCGImagePropertyImageCount` | CFNumber | Total images in container | 11.0+ |
| `kCGImagePropertyPrimaryImage` | CFNumber | Primary image index | 11.0+ |
| `kCGImagePropertyImages` | CFArray | Per-image property dicts | 11.0+ |
| `kCGImagePropertyThumbnailImages` | CFArray | Thumbnail images | 11.0+ |
| `kCGImagePropertyPixelFormat` | CFNumber | Format of individual pixels | 11.0+ |
| `kCGImagePropertyWidth` | CFNumber | Width in image coordinate space | 11.0+ |
| `kCGImagePropertyHeight` | CFNumber | Height in image coordinate space | 11.0+ |
| `kCGImagePropertyBytesPerRow` | CFNumber | Total bytes in each row | 11.0+ |

---

## EXIF Orientation Values

| Value | Constant | Visual Transformation |
|-------|----------|----------------------|
| 1 | `kCGImagePropertyOrientationUp` | Normal (no transform) |
| 2 | `kCGImagePropertyOrientationUpMirrored` | Horizontal flip |
| 3 | `kCGImagePropertyOrientationDown` | 180° rotation |
| 4 | `kCGImagePropertyOrientationDownMirrored` | Vertical flip |
| 5 | `kCGImagePropertyOrientationLeftMirrored` | 90° CCW + horizontal flip |
| 6 | `kCGImagePropertyOrientationRight` | 90° clockwise |
| 7 | `kCGImagePropertyOrientationRightMirrored` | 90° CW + horizontal flip |
| 8 | `kCGImagePropertyOrientationLeft` | 90° counter-clockwise |

---

## EXIF Dictionary (`kCGImagePropertyExifDictionary`)

### Camera & Exposure

| Key | Type | EXIF Tag |
|-----|------|----------|
| `kCGImagePropertyExifExposureTime` | CFNumber | ExposureTime (seconds) |
| `kCGImagePropertyExifFNumber` | CFNumber | FNumber (f-stop) |
| `kCGImagePropertyExifExposureProgram` | CFNumber | ExposureProgram (0–8 enum) |
| `kCGImagePropertyExifSpectralSensitivity` | CFString | SpectralSensitivity |
| `kCGImagePropertyExifISOSpeedRatings` | CFArray | ISOSpeedRatings |
| `kCGImagePropertyExifSensitivityType` | CFNumber | SensitivityType |
| `kCGImagePropertyExifStandardOutputSensitivity` | CFNumber | StandardOutputSensitivity |
| `kCGImagePropertyExifRecommendedExposureIndex` | CFNumber | RecommendedExposureIndex |
| `kCGImagePropertyExifISOSpeed` | CFNumber | ISO speed value |
| `kCGImagePropertyExifISOSpeedLatitudeyyy` | CFNumber | ISO speed latitude yyy |
| `kCGImagePropertyExifISOSpeedLatitudezzz` | CFNumber | ISO speed latitude zzz |
| `kCGImagePropertyExifExposureIndex` | CFNumber | Exposure index |
| `kCGImagePropertyExifExposureMode` | CFNumber | ExposureMode (0=Auto, 1=Manual, 2=Auto bracket) |
| `kCGImagePropertyExifOECF` | CFData | Opto-Electronic Conversion Function |

### Brightness & Metering

| Key | Type | EXIF Tag |
|-----|------|----------|
| `kCGImagePropertyExifShutterSpeedValue` | CFNumber | ShutterSpeedValue (APEX) |
| `kCGImagePropertyExifApertureValue` | CFNumber | ApertureValue (APEX) |
| `kCGImagePropertyExifBrightnessValue` | CFNumber | BrightnessValue (APEX) |
| `kCGImagePropertyExifExposureBiasValue` | CFNumber | ExposureBiasValue (EV) |
| `kCGImagePropertyExifMaxApertureValue` | CFNumber | MaxApertureValue |
| `kCGImagePropertyExifMeteringMode` | CFNumber | MeteringMode (1–6, 255) |
| `kCGImagePropertyExifFlash` | CFNumber | Flash (bitfield) |
| `kCGImagePropertyExifFlashEnergy` | CFNumber | Flash energy (BCPS) |
| `kCGImagePropertyExifLightSource` | CFNumber | LightSource (0–255 enum) |
| `kCGImagePropertyExifGainControl` | CFNumber | GainControl (0–4) |
| `kCGImagePropertyExifSubjectDistance` | CFNumber | Distance to subject (meters) |
| `kCGImagePropertyExifSubjectArea` | CFArray | Subject area coordinates |
| `kCGImagePropertyExifSubjectLocation` | CFArray | Subject location (x, y) |
| `kCGImagePropertyExifSensingMethod` | CFNumber | SensingMethod (1–8 enum) |
| `kCGImagePropertyExifSpatialFrequencyResponse` | CFData | Spatial frequency response |
| `kCGImagePropertyExifDeviceSettingDescription` | CFData | Device-specific settings |
| `kCGImagePropertyExifCFAPattern` | CFData | Color filter array pattern |

### Focal Length & Lens

| Key | Type | EXIF Tag |
|-----|------|----------|
| `kCGImagePropertyExifFocalLength` | CFNumber | FocalLength (mm) |
| `kCGImagePropertyExifFocalLenIn35mmFilm` | CFNumber | FocalLengthIn35mmFilm |
| `kCGImagePropertyExifLensSpecification` | CFArray (4 rationals) | LensSpecification [min FL, max FL, min FN, max FN] |
| `kCGImagePropertyExifLensMake` | CFString | LensMake |
| `kCGImagePropertyExifLensModel` | CFString | LensModel |
| `kCGImagePropertyExifLensSerialNumber` | CFString | LensSerialNumber |

### Image Dimensions & Color

| Key | Type | EXIF Tag |
|-----|------|----------|
| `kCGImagePropertyExifPixelXDimension` | CFNumber | PixelXDimension |
| `kCGImagePropertyExifPixelYDimension` | CFNumber | PixelYDimension |
| `kCGImagePropertyExifColorSpace` | CFNumber | ColorSpace (1=sRGB, 65535=Uncalibrated) |
| `kCGImagePropertyExifComponentsConfiguration` | CFData | ComponentsConfiguration |
| `kCGImagePropertyExifCompressedBitsPerPixel` | CFNumber | CompressedBitsPerPixel |
| `kCGImagePropertyExifGamma` | CFNumber | Gamma |

### Date & Time

| Key | Type | Format |
|-----|------|--------|
| `kCGImagePropertyExifDateTimeOriginal` | CFString | `"YYYY:MM:DD HH:MM:SS"` |
| `kCGImagePropertyExifDateTimeDigitized` | CFString | `"YYYY:MM:DD HH:MM:SS"` |
| `kCGImagePropertyExifSubsecTime` | CFString | Fractional seconds for DateTime |
| `kCGImagePropertyExifSubsecTimeOriginal` | CFString | Fractional seconds for DateTimeOriginal |
| `kCGImagePropertyExifSubsecTimeDigitized` | CFString | Fractional seconds for DateTimeDigitized |
| `kCGImagePropertyExifOffsetTime` | CFString | UTC offset (e.g. `"+05:30"`) |
| `kCGImagePropertyExifOffsetTimeOriginal` | CFString | UTC offset for DateTimeOriginal |
| `kCGImagePropertyExifOffsetTimeDigitized` | CFString | UTC offset for DateTimeDigitized |

> **OffsetTime* keys** are EXIF 2.31+ (2016) additions. iPhone photos always
> populate these. Many third-party cameras omit them.

### Scene & Processing

| Key | Type | EXIF Tag |
|-----|------|----------|
| `kCGImagePropertyExifWhiteBalance` | CFNumber | WhiteBalance (0=Auto, 1=Manual) |
| `kCGImagePropertyExifDigitalZoomRatio` | CFNumber | DigitalZoomRatio |
| `kCGImagePropertyExifSceneCaptureType` | CFNumber | SceneCaptureType (0–3) |
| `kCGImagePropertyExifSceneType` | CFNumber | SceneType |
| `kCGImagePropertyExifSubjectDistRange` | CFNumber | SubjectDistanceRange (0–3) |
| `kCGImagePropertyExifContrast` | CFNumber | Contrast (0–2) |
| `kCGImagePropertyExifSaturation` | CFNumber | Saturation (0–2) |
| `kCGImagePropertyExifSharpness` | CFNumber | Sharpness (0–2) |
| `kCGImagePropertyExifCustomRendered` | CFNumber | CustomRendered (0=Normal, 1=Custom) |
| `kCGImagePropertyExifFileSource` | CFNumber | FileSource |
| `kCGImagePropertyExifRelatedSoundFile` | CFString | Related sound file |
| `kCGImagePropertyExifFocalPlaneXResolution` | CFNumber | Focal plane X resolution |
| `kCGImagePropertyExifFocalPlaneYResolution` | CFNumber | Focal plane Y resolution |
| `kCGImagePropertyExifFocalPlaneResolutionUnit` | CFNumber | Focal plane resolution unit |

### Composite Images (EXIF 2.32+)

| Key | Type | Purpose |
|-----|------|---------|
| `kCGImagePropertyExifCompositeImage` | CFNumber | CompositeImage flag (1–3) |
| `kCGImagePropertyExifSourceImageNumberOfCompositeImage` | CFNumber | Number of source images |
| `kCGImagePropertyExifSourceExposureTimesOfCompositeImage` | CFData | Exposure times of source images |

### Version & Identity

| Key | Type | Purpose |
|-----|------|---------|
| `kCGImagePropertyExifVersion` | CFArray | EXIF version (e.g. [2,3,2]) |
| `kCGImagePropertyExifFlashPixVersion` | CFArray | FlashPix version |
| `kCGImagePropertyExifMakerNote` | CFData | Opaque MakerNote blob |
| `kCGImagePropertyExifUserComment` | CFString | User comment |
| `kCGImagePropertyExifImageUniqueID` | CFString | Unique image identifier |
| `kCGImagePropertyExifCameraOwnerName` | CFString | Camera owner |
| `kCGImagePropertyExifBodySerialNumber` | CFString | Camera body serial number |
| `kCGImagePropertyExifInteroperabilityDictionary` | CFDictionary | Interop IFD sub-dictionary |

> **Deprecated:** `kCGImagePropertyExifSubsecTimeOrginal` (misspelled) has been replaced by
> `kCGImagePropertyExifSubsecTimeOriginal` (corrected spelling).

---

## EXIF Auxiliary Dictionary (`kCGImagePropertyExifAuxDictionary`)

| Key | Type | Purpose |
|-----|------|---------|
| `kCGImagePropertyExifAuxLensInfo` | CFArray (4 rationals) | Lens info [min FL, max FL, min FN, max FN] |
| `kCGImagePropertyExifAuxLensModel` | CFString | Lens model name |
| `kCGImagePropertyExifAuxLensID` | CFNumber | Lens identifier |
| `kCGImagePropertyExifAuxLensSerialNumber` | CFString | Lens serial number |
| `kCGImagePropertyExifAuxSerialNumber` | CFString | Camera serial number |
| `kCGImagePropertyExifAuxImageNumber` | CFNumber | Image number |
| `kCGImagePropertyExifAuxFlashCompensation` | CFNumber | Flash compensation value |
| `kCGImagePropertyExifAuxOwnerName` | CFString | Camera owner name |
| `kCGImagePropertyExifAuxFirmware` | CFString | Firmware version |

---

## GPS Dictionary (`kCGImagePropertyGPSDictionary`)

### Coordinates

| Key | Type | Purpose |
|-----|------|---------|
| `kCGImagePropertyGPSLatitude` | CFNumber | Latitude (absolute value, degrees) |
| `kCGImagePropertyGPSLatitudeRef` | CFString | `"N"` or `"S"` |
| `kCGImagePropertyGPSLongitude` | CFNumber | Longitude (absolute value, degrees) |
| `kCGImagePropertyGPSLongitudeRef` | CFString | `"E"` or `"W"` |
| `kCGImagePropertyGPSAltitude` | CFNumber | Altitude in meters |
| `kCGImagePropertyGPSAltitudeRef` | CFNumber | 0 = above sea level, 1 = below |

> **Important:** ImageIO uses absolute values + reference letters.
> A point at -122.4194° W longitude is stored as
> `GPSLongitude: 122.4194, GPSLongitudeRef: "W"`.

### Movement & Direction

| Key | Type | Purpose |
|-----|------|---------|
| `kCGImagePropertyGPSSpeed` | CFNumber | Speed of GPS receiver |
| `kCGImagePropertyGPSSpeedRef` | CFString | `"K"` (km/h), `"M"` (mph), `"N"` (knots) |
| `kCGImagePropertyGPSTrack` | CFNumber | Direction of movement (degrees) |
| `kCGImagePropertyGPSTrackRef` | CFString | `"T"` (true) or `"M"` (magnetic) |
| `kCGImagePropertyGPSImgDirection` | CFNumber | Direction the image faces (degrees) |
| `kCGImagePropertyGPSImgDirectionRef` | CFString | `"T"` (true) or `"M"` (magnetic) |

### Destination

| Key | Type | Purpose |
|-----|------|---------|
| `kCGImagePropertyGPSDestLatitude` | CFNumber | Destination latitude |
| `kCGImagePropertyGPSDestLatitudeRef` | CFString | `"N"` or `"S"` |
| `kCGImagePropertyGPSDestLongitude` | CFNumber | Destination longitude |
| `kCGImagePropertyGPSDestLongitudeRef` | CFString | `"E"` or `"W"` |
| `kCGImagePropertyGPSDestBearing` | CFNumber | Bearing to destination (degrees) |
| `kCGImagePropertyGPSDestBearingRef` | CFString | `"T"` or `"M"` |
| `kCGImagePropertyGPSDestDistance` | CFNumber | Distance to destination |
| `kCGImagePropertyGPSDestDistanceRef` | CFString | `"K"` (km), `"M"` (miles), `"N"` (knots) |

### Timing

| Key | Type | Purpose |
|-----|------|---------|
| `kCGImagePropertyGPSTimeStamp` | CFString | UTC time (`"HH:MM:SS.SS"`) |
| `kCGImagePropertyGPSDateStamp` | CFString | Date (`"YYYY:MM:DD"`) |

### Quality & System

| Key | Type | Purpose |
|-----|------|---------|
| `kCGImagePropertyGPSStatus` | CFString | `"A"` (active) or `"V"` (void) |
| `kCGImagePropertyGPSMeasureMode` | CFString | `"2"` (2D) or `"3"` (3D) |
| `kCGImagePropertyGPSSatellites` | CFString | Satellite info |
| `kCGImagePropertyGPSDOP` | CFNumber | Dilution of precision |
| `kCGImagePropertyGPSMapDatum` | CFString | Geodetic datum (e.g. `"WGS-84"`) |
| `kCGImagePropertyGPSVersionID` | CFArray | GPS IFD version |
| `kCGImagePropertyGPSProcessingMethod` | CFString | Processing method description |
| `kCGImagePropertyGPSHPositioningError` | CFNumber | Horizontal positioning error (meters) |

---

## TIFF Dictionary (`kCGImagePropertyTIFFDictionary`)

| Key | Type | Purpose |
|-----|------|---------|
| `kCGImagePropertyTIFFMake` | CFString | Camera manufacturer |
| `kCGImagePropertyTIFFModel` | CFString | Camera model |
| `kCGImagePropertyTIFFOrientation` | CFNumber (1–8) | Image orientation |
| `kCGImagePropertyTIFFXResolution` | CFNumber | X resolution |
| `kCGImagePropertyTIFFYResolution` | CFNumber | Y resolution |
| `kCGImagePropertyTIFFResolutionUnit` | CFNumber | 1=None, 2=Inch, 3=Centimeter |
| `kCGImagePropertyTIFFCompression` | CFNumber | Compression scheme |
| `kCGImagePropertyTIFFPhotometricInterpretation` | CFNumber | Color model encoding |
| `kCGImagePropertyTIFFDateTime` | CFString | File modification date |
| `kCGImagePropertyTIFFImageDescription` | CFString | Image description |
| `kCGImagePropertyTIFFDocumentName` | CFString | Document name |
| `kCGImagePropertyTIFFSoftware` | CFString | Software used |
| `kCGImagePropertyTIFFArtist` | CFString | Creator/artist |
| `kCGImagePropertyTIFFCopyright` | CFString | Copyright notice |
| `kCGImagePropertyTIFFHostComputer` | CFString | Computer used to create |
| `kCGImagePropertyTIFFWhitePoint` | CFArray | White point chromaticity |
| `kCGImagePropertyTIFFPrimaryChromaticities` | CFArray | Primary chromaticities |
| `kCGImagePropertyTIFFTransferFunction` | CFArray | Transfer function |
| `kCGImagePropertyTIFFTileWidth` | CFNumber | Tile width (macOS 10.11+) |
| `kCGImagePropertyTIFFTileLength` | CFNumber | Tile height (macOS 10.11+) |

---

## IPTC Dictionary (`kCGImagePropertyIPTCDictionary`)

### Core Fields

| Key | Type | Purpose |
|-----|------|---------|
| `kCGImagePropertyIPTCObjectName` | CFString | Title / object name |
| `kCGImagePropertyIPTCObjectTypeReference` | CFString | Object type reference |
| `kCGImagePropertyIPTCObjectAttributeReference` | CFString | Object attribute reference |
| `kCGImagePropertyIPTCCaptionAbstract` | CFString | Caption / description (preferred over `Caption`) |
| `kCGImagePropertyIPTCHeadline` | CFString | Short synopsis / headline |
| `kCGImagePropertyIPTCKeywords` | CFArray | Keywords (array of strings) |
| `kCGImagePropertyIPTCCategory` | CFString | Subject category |
| `kCGImagePropertyIPTCSupplementalCategory` | CFArray | Supplemental categories |
| `kCGImagePropertyIPTCSubjectReference` | CFArray | Subject reference codes |
| `kCGImagePropertyIPTCScene` | CFArray | Scene codes |
| `kCGImagePropertyIPTCStarRating` | CFNumber | Star rating |
| `kCGImagePropertyIPTCLanguageIdentifier` | CFString | Language identifier (ISO 639) |

### Creator & Attribution

| Key | Type | Purpose |
|-----|------|---------|
| `kCGImagePropertyIPTCCredit` | CFString | Credit line |
| `kCGImagePropertyIPTCSource` | CFString | Source |
| `kCGImagePropertyIPTCByline` | CFString | Creator / author |
| `kCGImagePropertyIPTCBylineTitle` | CFString | Creator's job title |
| `kCGImagePropertyIPTCContact` | CFString | Contact information |
| `kCGImagePropertyIPTCWriterEditor` | CFString | Caption writer / editor |
| `kCGImagePropertyIPTCCopyrightNotice` | CFString | Copyright notice |
| `kCGImagePropertyIPTCCreatorContactInfo` | CFDictionary | Creator contact info (sub-dictionary) |

### Location

| Key | Type | Purpose |
|-----|------|---------|
| `kCGImagePropertyIPTCContentLocationCode` | CFArray | Location codes (ISO 3166) |
| `kCGImagePropertyIPTCContentLocationName` | CFArray | Location names |
| `kCGImagePropertyIPTCSubLocation` | CFString | Sub-location |
| `kCGImagePropertyIPTCCity` | CFString | City |
| `kCGImagePropertyIPTCProvinceState` | CFString | State / province |
| `kCGImagePropertyIPTCCountryPrimaryLocationCode` | CFString | Country code (ISO 3166) |
| `kCGImagePropertyIPTCCountryPrimaryLocationName` | CFString | Country name |

### Dates & Status

| Key | Type | Purpose |
|-----|------|---------|
| `kCGImagePropertyIPTCDateCreated` | CFString | Creation date (`"YYYYMMDD"`) |
| `kCGImagePropertyIPTCTimeCreated` | CFString | Creation time (`"HHMMSS±HHMM"`) |
| `kCGImagePropertyIPTCDigitalCreationDate` | CFString | Digital creation date |
| `kCGImagePropertyIPTCDigitalCreationTime` | CFString | Digital creation time |
| `kCGImagePropertyIPTCExpirationDate` | CFString | Expiration date |
| `kCGImagePropertyIPTCExpirationTime` | CFString | Expiration time |
| `kCGImagePropertyIPTCReleaseDate` | CFString | Release date |
| `kCGImagePropertyIPTCReleaseTime` | CFString | Release time |
| `kCGImagePropertyIPTCEditStatus` | CFString | Edit status |
| `kCGImagePropertyIPTCEditorialUpdate` | CFString | Editorial update |
| `kCGImagePropertyIPTCUrgency` | CFString | Urgency (1–8) |

### Instructions & Usage

| Key | Type | Purpose |
|-----|------|---------|
| `kCGImagePropertyIPTCSpecialInstructions` | CFString | Special handling instructions |
| `kCGImagePropertyIPTCRightsUsageTerms` | CFString | Rights usage terms |
| `kCGImagePropertyIPTCReferenceService` | CFString | Reference service |
| `kCGImagePropertyIPTCReferenceDate` | CFString | Reference date |
| `kCGImagePropertyIPTCReferenceNumber` | CFString | Reference number |

### Image Type

| Key | Type | Purpose |
|-----|------|---------|
| `kCGImagePropertyIPTCImageType` | CFString | Image type code |
| `kCGImagePropertyIPTCImageOrientation` | CFString | Image orientation (L/P/S) |
| `kCGImagePropertyIPTCOriginalTransmissionReference` | CFString | Job/transmission ID |
| `kCGImagePropertyIPTCFixtureIdentifier` | CFString | Fixture identifier |
| `kCGImagePropertyIPTCActionAdvised` | CFString | Action advised |
| `kCGImagePropertyIPTCOriginatingProgram` | CFString | Originating program |
| `kCGImagePropertyIPTCProgramVersion` | CFString | Program version |
| `kCGImagePropertyIPTCObjectCycle` | CFString | Object cycle |

### Creator Contact Info Sub-Dictionary (`kCGImagePropertyIPTCCreatorContactInfo`)

| Key | Type | Purpose |
|-----|------|---------|
| `kCGImagePropertyIPTCContactInfoCity` | CFString | Contact city |
| `kCGImagePropertyIPTCContactInfoCountry` | CFString | Contact country |
| `kCGImagePropertyIPTCContactInfoAddress` | CFString | Contact address |
| `kCGImagePropertyIPTCContactInfoPostalCode` | CFString | Contact postal code |
| `kCGImagePropertyIPTCContactInfoStateProvince` | CFString | Contact state/province |
| `kCGImagePropertyIPTCContactInfoEmails` | CFArray | Contact emails |
| `kCGImagePropertyIPTCContactInfoPhones` | CFArray | Contact phone numbers |
| `kCGImagePropertyIPTCContactInfoWebURLs` | CFArray | Contact web URLs |

> **IPTC Extension:** Apple defines 173+ `kCGImagePropertyIPTCExt*` keys covering the full
> IPTC Photo Metadata Extension standard (artwork, people, organizations, events,
> linked encoded rights, audio/video metadata, etc.). These keys are accessible via
> the `kCGImagePropertyIPTCDictionary` and via XMP using
> `kCGImageMetadataNamespaceIPTCExtension` / `kCGImageMetadataPrefixIPTCExtension`.
> See Apple's "IPTC Extension Dictionary Keys" documentation for the full list.

---

## JFIF Dictionary (`kCGImagePropertyJFIFDictionary`)

| Key | Type | Purpose |
|-----|------|---------|
| `kCGImagePropertyJFIFVersion` | CFArray | JFIF version (e.g. [1, 2]) |
| `kCGImagePropertyJFIFXDensity` | CFNumber | Horizontal pixel density |
| `kCGImagePropertyJFIFYDensity` | CFNumber | Vertical pixel density |
| `kCGImagePropertyJFIFDensityUnit` | CFNumber | 0=no unit, 1=DPI, 2=dots/cm |
| `kCGImagePropertyJFIFIsProgressive` | CFBoolean | Progressive JPEG flag |

---

## PNG Dictionary (`kCGImagePropertyPNGDictionary`)

| Key | Type | Purpose |
|-----|------|---------|
| `kCGImagePropertyPNGGamma` | CFNumber | Gamma value |
| `kCGImagePropertyPNGInterlaceType` | CFNumber | Interlace type |
| `kCGImagePropertyPNGChromaticities` | CFDictionary | Chromaticity values |
| `kCGImagePropertyPNGCompressionFilter` | CFNumber | Compression filter (macOS 10.11+) |
| `kCGImagePropertyPNGAuthor` | CFString | Author (tEXt chunk) |
| `kCGImagePropertyPNGCopyright` | CFString | Copyright (tEXt chunk) |
| `kCGImagePropertyPNGCreationTime` | CFString | Creation time (tEXt chunk) |
| `kCGImagePropertyPNGDescription` | CFString | Description (tEXt chunk) |
| `kCGImagePropertyPNGModificationTime` | CFString | Modification time (tIME chunk) |
| `kCGImagePropertyPNGSoftware` | CFString | Software (tEXt chunk) |
| `kCGImagePropertyPNGTitle` | CFString | Title (tEXt chunk) |
| `kCGImagePropertyPNGsRGBIntent` | CFNumber | sRGB rendering intent |
| `kCGImagePropertyPNGTransparency` | CFArray | Transparency info (tRNS chunk) |
| `kCGImagePropertyPNGComment` | CFString | Comment (tEXt chunk) |
| `kCGImagePropertyPNGDisclaimer` | CFString | Disclaimer (tEXt chunk) |
| `kCGImagePropertyPNGWarning` | CFString | Warning (tEXt chunk) |
| `kCGImagePropertyPNGSource` | CFString | Source (tEXt chunk) |
| `kCGImagePropertyPNGXPixelsPerMeter` | CFNumber | X pixels per meter (pHYs chunk) |
| `kCGImagePropertyPNGYPixelsPerMeter` | CFNumber | Y pixels per meter (pHYs chunk) |

### APNG Keys (within PNG dictionary)

| Key | Type | Purpose |
|-----|------|---------|
| `kCGImagePropertyAPNGLoopCount` | CFNumber | Animation loop count (0 = infinite) |
| `kCGImagePropertyAPNGDelayTime` | CFNumber | Frame delay (seconds, clamped) |
| `kCGImagePropertyAPNGUnclampedDelayTime` | CFNumber | True frame delay (not clamped) |
| `kCGImagePropertyAPNGFrameInfoArray` | CFArray | Frame information array |
| `kCGImagePropertyAPNGCanvasPixelWidth` | CFNumber | Canvas width in pixels |
| `kCGImagePropertyAPNGCanvasPixelHeight` | CFNumber | Canvas height in pixels |

---

## GIF Dictionary (`kCGImagePropertyGIFDictionary`)

| Key | Type | Purpose |
|-----|------|---------|
| `kCGImagePropertyGIFLoopCount` | CFNumber | Animation loop count (0 = infinite) |
| `kCGImagePropertyGIFDelayTime` | CFNumber | Frame delay (seconds, clamped to ≥0.1) |
| `kCGImagePropertyGIFUnclampedDelayTime` | CFNumber | True frame delay (not clamped) |
| `kCGImagePropertyGIFImageColorMap` | CFData | Per-frame color table |
| `kCGImagePropertyGIFHasGlobalColorMap` | CFBoolean | Has global color map |
| `kCGImagePropertyGIFCanvasPixelWidth` | CFNumber | Canvas width in pixels |
| `kCGImagePropertyGIFCanvasPixelHeight` | CFNumber | Canvas height in pixels |
| `kCGImagePropertyGIFFrameInfoArray` | CFArray | Frame information array |

> Use `kCGImagePropertyGIFUnclampedDelayTime` for accurate animation timing.
> The clamped `DelayTime` rounds values <0.1s up to 0.1s (matching browser behavior).

---

## WebP Dictionary (`kCGImagePropertyWebPDictionary`) — iOS 14.0+

| Key | Type | Purpose |
|-----|------|---------|
| `kCGImagePropertyWebPLoopCount` | CFNumber | Animation loop count |
| `kCGImagePropertyWebPDelayTime` | CFNumber | Frame delay (seconds, clamped) |
| `kCGImagePropertyWebPUnclampedDelayTime` | CFNumber | True frame delay (not clamped) |
| `kCGImagePropertyWebPFrameInfoArray` | CFArray | Frame information array |
| `kCGImagePropertyWebPCanvasPixelWidth` | CFNumber | Canvas width in pixels |
| `kCGImagePropertyWebPCanvasPixelHeight` | CFNumber | Canvas height in pixels |

---

## HEICS Dictionary (`kCGImagePropertyHEICSDictionary`) — iOS 13.0+

| Key | Type | Purpose |
|-----|------|---------|
| `kCGImagePropertyHEICSLoopCount` | CFNumber | Animation loop count |
| `kCGImagePropertyHEICSDelayTime` | CFNumber | Frame delay (seconds) |
| `kCGImagePropertyHEICSUnclampedDelayTime` | CFNumber | True frame delay (not clamped) |
| `kCGImagePropertyHEICSFrameInfoArray` | CFArray | Frame information array |
| `kCGImagePropertyHEICSCanvasPixelWidth` | CFNumber | Canvas width in pixels |
| `kCGImagePropertyHEICSCanvasPixelHeight` | CFNumber | Canvas height in pixels |

---

## DNG Dictionary (`kCGImagePropertyDNGDictionary`)

| Key | Type | Purpose |
|-----|------|---------|
| `kCGImagePropertyDNGVersion` | CFArray | DNG version [major, minor, ...] |
| `kCGImagePropertyDNGBackwardVersion` | CFArray | Minimum reader version |
| `kCGImagePropertyDNGUniqueCameraModel` | CFString | Camera model identifier |
| `kCGImagePropertyDNGLocalizedCameraModel` | CFString | Localized camera model |
| `kCGImagePropertyDNGCameraSerialNumber` | CFString | Camera serial number |
| `kCGImagePropertyDNGLensInfo` | CFArray (4 rationals) | Lens info |
| `kCGImagePropertyDNGLensMake` | CFString | Lens manufacturer |
| `kCGImagePropertyDNGLensModel` | CFString | Lens model |
| `kCGImagePropertyDNGAsShotNeutral` | CFArray | As-shot white balance |
| `kCGImagePropertyDNGAnalogBalance` | CFArray | Analog balance |
| `kCGImagePropertyDNGPrivateData` | CFData | Private manufacturer data |
| `kCGImagePropertyDNGActiveArea` | CFArray | Active sensor area |
| `kCGImagePropertyDNGBaselineExposure` | CFNumber | Baseline exposure compensation |
| `kCGImagePropertyDNGBaselineNoise` | CFNumber | Baseline noise level |
| `kCGImagePropertyDNGBaselineSharpness` | CFNumber | Baseline sharpness |
| `kCGImagePropertyDNGOriginalRawFileData` | CFData | Original raw file data |
| `kCGImagePropertyDNGOriginalRawFileDigest` | CFData | MD5 digest of original |

---

## 8BIM Dictionary (`kCGImageProperty8BIMDictionary`)

Adobe Photoshop resources:

| Key | Type | Purpose |
|-----|------|---------|
| `kCGImageProperty8BIMVersion` | CFNumber | Photoshop version |
| `kCGImageProperty8BIMLayerNames` | CFArray | Layer name strings |
| `kCGImageProperty8BIMLayerInfo` | CFData | Layer info data |

---

## OpenEXR Dictionary (`kCGImagePropertyOpenEXRDictionary`)

Available since iOS 11.3.

| Key | Type | Purpose |
|-----|------|---------|
| `kCGImagePropertyOpenEXRAspectRatio` | CFNumber | Pixel aspect ratio |

---

## Format-Specific Dictionaries (Minimal Keys)

These dictionaries exist but have very few documented public keys:

| Dictionary | iOS | Notes |
|------------|-----|-------|
| `kCGImagePropertyRawDictionary` | 4.0+ | Generic RAW properties |
| `kCGImagePropertyCIFFDictionary` | 4.0+ | Canon legacy (CIFF) format |
| `kCGImagePropertyHEIFDictionary` | 16.0+ | HEIF container properties |
| `kCGImagePropertyHEICSDictionary` | 13.0+ | HEIF sequence properties |
| `kCGImagePropertyWebPDictionary` | 14.0+ | WebP properties |
| `kCGImagePropertyTGADictionary` | 14.0+ | TGA properties |
| `kCGImagePropertyAVISDictionary` | 16.0+ | AV1 image sequence properties |

---

## Manufacturer MakerNote Dictionaries

Vendor-specific capture data embedded in the MakerNote EXIF tag.
Keys within these dictionaries are vendor-specific and partially documented.

| Dictionary | Vendor | iOS | Key Count |
|------------|--------|-----|-----------|
| `kCGImagePropertyMakerCanonDictionary` | Canon | 4.0+ | 100+ |
| `kCGImagePropertyMakerNikonDictionary` | Nikon | 4.0+ | 100+ |
| `kCGImagePropertyMakerMinoltaDictionary` | Minolta / Sony | 4.0+ | ~50 |
| `kCGImagePropertyMakerFujiDictionary` | Fujifilm | 4.0+ | ~50 |
| `kCGImagePropertyMakerOlympusDictionary` | Olympus | 4.0+ | ~50 |
| `kCGImagePropertyMakerPentaxDictionary` | Pentax | 4.0+ | ~50 |
| `kCGImagePropertyMakerAppleDictionary` | Apple (iPhone/iPad) | 7.0+ | ~30 |

> Canon and Nikon have the most fully documented key sets in Apple's headers.
> Apple's MakerNote includes processing flags, depth data references, and
> computational photography metadata.
