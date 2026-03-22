# IPTC Photo Metadata User Guide - Practical Guidance

## Table of contents

1. What the user guide emphasizes
2. Minimal set of metadata properties
3. Controlled vocabularies and value lists
4. Accessibility fields
5. Digital Source Type guidance
6. AI-generated images guidance
7. Preservation guidance
8. Official links

## 1. What the user guide emphasizes

- Photo metadata is embedded in image files and exchanged by applications and services. It is not HTML metadata.
- Metadata should be preserved when images are processed or transformed; avoid stripping it.

## 2. Minimal set of metadata properties

The user guide recommends a minimal set that supports identification, rights, and credit:

- Image Description (Caption)
- Image Creator(s)
- Copyright Owner
- Copyright Notice
- Credit Line
- Date Created

## 3. Controlled vocabularies and value lists

- Some IPTC properties require a controlled vocabulary or value list instead of free text.
- When a vocabulary is required, use the identifier URI (not just a human label).
- Examples include Digital Source Type, Subject Code, and Country Code.
- Controlled vocabularies are published at https://cv.iptc.org/newscodes/ (Digital Source Type at https://cv.iptc.org/newscodes/digitalsourcetype/).

## 4. Accessibility fields

- Alt Text provides a concise text alternative for accessibility. It is intended to be short (the user guide notes 250 characters as a limit, aligned with WCAG guidance).
- Extended Description can provide a longer alternative text for accessibility when Alt Text is too short. It should not simply repeat Alt Text.

## 5. Digital Source Type guidance

- Digital Source Type uses an IPTC controlled vocabulary and identifies the provenance of the image.
- The user guide highlights updates to the controlled vocabulary in 2022 and 2024.
- Use the full URI from the vocabulary as the value.

## 6. AI-generated images guidance

For AI-generated or AI-assisted imagery, the user guide recommends:

- Set Digital Source Type to a relevant AI value from the controlled vocabulary (for example, trainedAlgorithmicMedia or compositeSynthetic).
- Provide AI System Used and AI System Version Used.
- If available, include AI Prompt Information and AI Prompt Writer Name.
- Only set Image Creator when there is a human creator; do not invent a human creator for AI-only images.

## 7. Preservation guidance

- Preserve metadata through editing and export workflows; do not strip IPTC data unless explicitly required.

## 8. Official links

- User guide (intro): https://www.iptc.org/std/photometadata/documentation/userguide/
- Documentation hub: https://iptc.org/std/photometadata/documentation
