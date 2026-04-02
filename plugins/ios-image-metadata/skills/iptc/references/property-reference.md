# IPTC Property Reference

> Derived from IPTC TechReference 2025.1 (Core 1.5, Extension 1.9).
> Source: https://iptc.org/std/photometadata/specification/iptc-pmd-techreference_2025.1.json

---

## IPTC Core Properties (25)

| Property | XMP ID | IIM | Type | Cardinality |
|----------|--------|-----|------|-------------|
| Alt Text (Accessibility) | `Iptc4xmpCore:AltTextAccessibility` | — | struct/AltLang | single |
| Description Writer | `photoshop:CaptionWriter` | 2:122 (32B) | string | single |
| City (legacy) | `photoshop:City` | 2:90 (32B) | string | single |
| Copyright Notice | `dc:rights` | 2:116 (128B) | struct/AltLang | single |
| Country Code (legacy) | `Iptc4xmpCore:CountryCode` | 2:100 (3B) | string | single |
| Country (legacy) | `photoshop:Country` | 2:101 (64B) | string | single |
| Creator's Contact Info | `Iptc4xmpCore:CreatorContactInfo` | — | struct/CreatorContactInfo | single |
| Creator | `dc:creator` | 2:80 (32B) | string | multi |
| Credit Line | `photoshop:Credit` | 2:110 (32B) | string | single |
| Date Created | `photoshop:DateCreated` | 2:55 | string/date-time | single |
| Description | `dc:description` | 2:120 (2000B) | struct/AltLang | single |
| Extended Description (Accessibility) | `Iptc4xmpCore:ExtDescrAccessibility` | — | struct/AltLang | single |
| Headline | `photoshop:Headline` | 2:105 (256B) | string | single |
| Instructions | `photoshop:Instructions` | 2:40 (256B) | string | single |
| Intellectual Genre (legacy) | `Iptc4xmpCore:IntellectualGenre` | 2:04 (64B) | string | single |
| Job Id | `photoshop:TransmissionReference` | 2:103 (32B) | string | single |
| Creator's jobtitle | `photoshop:AuthorsPosition` | 2:85 (32B) | string | single |
| Keywords | `dc:subject` | 2:25 (64B) | string | multi |
| Province or State (legacy) | `photoshop:State` | 2:95 (32B) | string | single |
| Scene Code | `Iptc4xmpCore:Scene` | — | string | multi |
| Source (Supply Chain) | `photoshop:Source` | 2:115 (32B) | string | single |
| Subject Code (legacy) | `Iptc4xmpCore:SubjectCode` | 2:12 (236B) | string | multi |
| Sublocation (legacy) | `Iptc4xmpCore:Location` | 2:92 (32B) | string | single |
| Title | `dc:title` | 2:05 (64B) | struct/AltLang | single |
| Rights Usage Terms | `xmpRights:UsageTerms` | — | struct/AltLang | single |

## IPTC Extension Properties (41)

| Property | XMP ID | IIM | Type | Cardinality |
|----------|--------|-----|------|-------------|
| AI Prompt Information | `Iptc4xmpExt:AIPromptInformation` | — | string | single |
| AI Prompt Writer Name | `Iptc4xmpExt:AIPromptWriterName` | — | string | single |
| AI System Used | `Iptc4xmpExt:AISystemUsed` | — | string | single |
| AI System Version Used | `Iptc4xmpExt:AISystemVersionUsed` | — | string | single |
| CV-Term About Image | `Iptc4xmpExt:AboutCvTerm` | — | struct/CvTerm | multi |
| Additional Model Information | `Iptc4xmpExt:AddlModelInfo` | — | string | single |
| Artwork or Object in the Image | `Iptc4xmpExt:ArtworkOrObject` | — | struct/ArtworkOrObject | multi |
| Contributor | `Iptc4xmpExt:Contributor` | — | struct/EntityWRole | multi |
| Copyright Owner | `plus:CopyrightOwner` | — | struct/CopyrightOwner | multi |
| Data Mining | `plus:DataMining` | — | string/uri | single |
| Digital Image GUID | `Iptc4xmpExt:DigImageGUID` | — | string | single |
| Digital Source Type | `Iptc4xmpExt:DigitalSourceType` | — | string/uri | single |
| Embedded Encoded Rights Expression | `Iptc4xmpExt:EmbdEncRightsExpr` | — | struct/EmbdEncRightsExpr | multi |
| Event Identifier | `Iptc4xmpExt:EventId` | — | string/uri | multi |
| Event Name | `Iptc4xmpExt:Event` | — | struct/AltLang | single |
| Genre | `Iptc4xmpExt:Genre` | — | struct/CvTerm | multi |
| Image Creator | `plus:ImageCreator` | — | struct/ImageCreator | multi |
| Image Rating | `xmp:Rating` | — | number | single |
| Image Region | `Iptc4xmpExt:ImageRegion` | — | struct/ImageRegion | multi |
| Image Supplier Image ID | `plus:ImageSupplierImageID` | — | string | single |
| Licensor | `plus:Licensor` | — | struct/Licensor | multi |
| Linked  Encoded Rights Expression | `Iptc4xmpExt:LinkedEncRightsExpr` | — | struct/LinkedEncRightsExpr | multi |
| Location Created | `Iptc4xmpExt:LocationCreated` | — | struct/Location | multi |
| Location Shown in the Image | `Iptc4xmpExt:LocationShown` | — | struct/Location | multi |
| Max Avail Height | `Iptc4xmpExt:MaxAvailHeight` | — | number/integer | single |
| Max Avail Width | `Iptc4xmpExt:MaxAvailWidth` | — | number/integer | single |
| Minor Model Age Disclosure | `plus:MinorModelAgeDisclosure` | — | string/uri | single |
| Model Age | `Iptc4xmpExt:ModelAge` | — | number/integer | multi |
| Model Release Id | `plus:ModelReleaseID` | — | string | multi |
| Model Release Status | `plus:ModelReleaseStatus` | — | string/uri | single |
| Code of Organisation Featured in the Image | `Iptc4xmpExt:OrganisationInImageCode` | — | string | multi |
| Name of Organisation Featured in the Image | `Iptc4xmpExt:OrganisationInImageName` | — | string | multi |
| Other Constraints | `plus:OtherConstraints` | — | struct/AltLang | single |
| Person Shown in the Image | `Iptc4xmpExt:PersonInImage` | — | string | multi |
| Person Shown in the Image with Details | `Iptc4xmpExt:PersonInImageWDetails` | — | struct/PersonWDetails | multi |
| Product Shown in the Image | `Iptc4xmpExt:ProductInImage` | — | struct/ProductWGtin | multi |
| Property Release Id | `plus:PropertyReleaseID` | — | string | multi |
| Property Release Status | `plus:PropertyReleaseStatus` | — | string/uri | single |
| Image Registry Entry | `Iptc4xmpExt:RegistryId` | — | struct/RegistryEntry | multi |
| Image Supplier | `plus:ImageSupplier` | — | struct/ImageSupplier | multi |
| Web Statement of Rights | `xmpRights:WebStatement` | — | string/uri | single |

---

## Structure Definitions (19)

### AltLang

*Language alternative container (rdf:Alt with xml:lang tags). No named sub-fields.*

### ArtworkOrObject

| Field | XMP ID | Type |
|-------|--------|------|
| Circa Date Created | `Iptc4xmpExt:AOCircaDateCreated` | string |
| Content Description | `Iptc4xmpExt:AOContentDescription` | struct/AltLang |
| Contribution Description | `Iptc4xmpExt:AOContributionDescription` | struct/AltLang |
| Copyright Notice | `Iptc4xmpExt:AOCopyrightNotice` | string |
| Creator ID | `Iptc4xmpExt:AOCreatorId` | string/uri |
| Creator | `Iptc4xmpExt:AOCreator` | string |
| Current Copyright Owner ID | `Iptc4xmpExt:AOCurrentCopyrightOwnerId` | string/uri |
| Current Copyright Owner Name | `Iptc4xmpExt:AOCurrentCopyrightOwnerName` | string |
| Current Licensor ID | `Iptc4xmpExt:AOCurrentLicensorId` | string/uri |
| Current Licensor Name | `Iptc4xmpExt:AOCurrentLicensorName` | string |
| Date Created | `Iptc4xmpExt:AODateCreated` | string/date-time |
| Physical Description | `Iptc4xmpExt:AOPhysicalDescription` | struct/AltLang |
| Source | `Iptc4xmpExt:AOSource` | string |
| Source Inventory Number | `Iptc4xmpExt:AOSourceInvNo` | string |
| Source Inventory URL | `Iptc4xmpExt:AOSourceInvURL` | string/url |
| Style Period | `Iptc4xmpExt:AOStylePeriod` | string |
| Title | `Iptc4xmpExt:AOTitle` | struct/AltLang |

### CopyrightOwner

| Field | XMP ID | Type |
|-------|--------|------|
| Copyright Owner ID | `plus:CopyrightOwnerID` | string |
| Copyright Owner Name | `plus:CopyrightOwnerName` | string |

### CreatorContactInfo

| Field | XMP ID | Type |
|-------|--------|------|
| Address | `Iptc4xmpCore:CiAdrExtadr` | string |
| City | `Iptc4xmpCore:CiAdrCity` | string |
| Country | `Iptc4xmpCore:CiAdrCtry` | string |
| Email address(es) | `Iptc4xmpCore:CiEmailWork` | string |
| Phone number(s) | `Iptc4xmpCore:CiTelWork` | string |
| Postal Code | `Iptc4xmpCore:CiAdrPcode` | string |
| State/Province | `Iptc4xmpCore:CiAdrRegion` | string |
| Web URL(s) | `Iptc4xmpCore:CiUrlWork` | string/url |

### CvTerm

| Field | XMP ID | Type |
|-------|--------|------|
| CV-Term CV ID | `Iptc4xmpExt:CvId` | string/uri |
| CV-Term ID | `Iptc4xmpExt:CvTermId` | string/uri |
| CV-Term name | `Iptc4xmpExt:CvTermName` | struct/AltLang |
| Refined 'about' Relationship of the CV-Term | `Iptc4xmpExt:CvTermRefinedAbout` | string/uri |

### EmbdEncRightsExpr

| Field | XMP ID | Type |
|-------|--------|------|
| Encoded Rights Expression | `Iptc4xmpExt:EncRightsExpr` | string |
| Encoding type | `Iptc4xmpExt:RightsExprEncType` | string |
| Rights Expression Language ID | `Iptc4xmpExt:RightsExprLangId` | string/uri |

### Entity

| Field | XMP ID | Type |
|-------|--------|------|
| Identifier | `xmp:Identifier` | string/uri |
| Name | `Iptc4xmpExt:Name` | struct/AltLang |

### EntityWRole

| Field | XMP ID | Type |
|-------|--------|------|
| Identifier | `xmp:Identifier` | string/uri |
| Name | `Iptc4xmpExt:Name` | struct/AltLang |
| Role | `Iptc4xmpExt:Role` | string |

### ImageCreator

| Field | XMP ID | Type |
|-------|--------|------|
| Image Creator ID | `plus:ImageCreatorID` | string |
| Image Creator Name | `plus:ImageCreatorName` | string |

### ImageRegion

| Field | XMP ID | Type |
|-------|--------|------|
| Other Metadata Property | `` | any |
| Region Name | `Iptc4xmpExt:Name` | struct/AltLang |
| Region Content Type | `Iptc4xmpExt:rCtype` | struct/Entity |
| Region Identifier | `Iptc4xmpExt:rId` | string |
| Region Role | `Iptc4xmpExt:rRole` | struct/Entity |
| Region Boundary | `Iptc4xmpExt:RegionBoundary` | struct/RegionBoundary |

### ImageSupplier

| Field | XMP ID | Type |
|-------|--------|------|
| Image Supplier ID | `plus:ImageSupplierID` | string |
| Image Supplier Name | `plus:ImageSupplierName` | string |

### Licensor

| Field | XMP ID | Type |
|-------|--------|------|
| Licensor Address | `plus:LicensorStreetAddress` | string |
| Licensor Adress Detail | `plus:LicensorExtendedAddress` | string |
| Licensor City | `plus:LicensorCity` | string |
| Licensor Country | `plus:LicensorCountry` | string |
| Licensor Email | `plus:LicensorEmail` | string |
| Licensor ID | `plus:LicensorID` | string |
| Licensor Name | `plus:LicensorName` | string |
| Licensor Postal Code | `plus:LicensorPostalCode` | string |
| Licensor State or Province | `plus:LicensorRegion` | string |
| Licensor Telephone 1 | `plus:LicensorTelephone1` | string |
| Licensor Telephone 2 | `plus:LicensorTelephone2` | string |
| Licensor Telephone Type 1 | `plus:LicensorTelephoneType1` | string/url |
| Licensor Telephone Type 2 | `plus:LicensorTelephoneType2` | string/url |
| Licensor URL | `plus:LicensorURL` | string/url |

### LinkedEncRightsExpr

| Field | XMP ID | Type |
|-------|--------|------|
| Link to Encoded Rights Expression | `Iptc4xmpExt:LinkedRightsExpr` | string/url |
| Encoding type | `Iptc4xmpExt:RightsExprEncType` | string/uri |
| Rights Expression Language ID | `Iptc4xmpExt:RightsExprLangId` | string/uri |

### Location

| Field | XMP ID | Type |
|-------|--------|------|
| City | `Iptc4xmpExt:City` | string |
| Country ISO-Code | `Iptc4xmpExt:CountryCode` | string |
| Country Name | `Iptc4xmpExt:CountryName` | string |
| GPS-Altitude | `exif:GPSAltitude` | number |
| GPS-Altitude Reference | `exif:GPSAltitudeRef` | number |
| GPS-Latitude | `exif:GPSLatitude` | number |
| GPS-Longitude | `exif:GPSLongitude` | number |
| Location Identifier | `Iptc4xmpExt:LocationId` | string/uri |
| Location Name | `Iptc4xmpExt:LocationName` | struct/AltLang |
| Province or State | `Iptc4xmpExt:ProvinceState` | string |
| Sublocation | `Iptc4xmpExt:Sublocation` | string |
| World Region | `Iptc4xmpExt:WorldRegion` | string |

### PersonWDetails

| Field | XMP ID | Type |
|-------|--------|------|
| Characteristics | `Iptc4xmpExt:PersonCharacteristic` | struct/CvTerm |
| Description | `Iptc4xmpExt:PersonDescription` | struct/AltLang |
| Identifier | `Iptc4xmpExt:PersonId` | string/uri |
| Name | `Iptc4xmpExt:PersonName` | struct/AltLang |

### ProductWGtin

| Field | XMP ID | Type |
|-------|--------|------|
| Description | `Iptc4xmpExt:ProductDescription` | struct/AltLang |
| GTIN | `Iptc4xmpExt:ProductGTIN` | string |
| Identifier | `Iptc4xmpExt:ProductId` | string/uri |
| Name | `Iptc4xmpExt:ProductName` | struct/AltLang |

### RegionBoundary

| Field | XMP ID | Type |
|-------|--------|------|
| Rectangle Height | `Iptc4xmpExt:rbH` | number |
| Circle Radius | `Iptc4xmpExt:rbRx` | number |
| Boundary Shape | `Iptc4xmpExt:rbShape` | string |
| Boundary Measuring Unit | `Iptc4xmpExt:rbUnit` | string |
| Polygon Vertices | `Iptc4xmpExt:rbVertices` | struct/RegionBoundaryPoint |
| Rectangle Width | `Iptc4xmpExt:rbW` | number |
| X-Axis Coordinate | `Iptc4xmpExt:rbX` | number |
| Y-Axis Coordinate | `Iptc4xmpExt:rbY` | number |

### RegionBoundaryPoint

| Field | XMP ID | Type |
|-------|--------|------|
| X-Axis Coordinate | `Iptc4xmpExt:rbX` | number |
| Y-Axis Coordinate | `Iptc4xmpExt:rbY` | number |

### RegistryEntry

| Field | XMP ID | Type |
|-------|--------|------|
| Item Id | `Iptc4xmpExt:RegItemId` | string |
| Organisation Id | `Iptc4xmpExt:RegOrgId` | string |
| Role | `Iptc4xmpExt:RegEntryRole` | string/uri |

---

Total: 66 properties (25 Core + 41 Extension), 19 structures.
