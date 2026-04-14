---
name: ios-quick-start
description: Use when the user wants to scaffold a brand-new iOS app project with a clean three-layer architecture (DomainLayer, DataLayer, ViewLayer + Shared) as local SPM packages, Factory for DI, and Navigator for navigation. Triggers on phrases like "create a new iOS project", "scaffold an iOS app", "use ios-quick-start to create a project named X".
---

# iOS Quick Start

Scaffolds a new iOS app project from a tokenized template. Output is a buildable `.xcodeproj` plus four local SPM packages, wired up with Factory DI and Navigator navigation, with two placeholder features (`FeatureA`, `FeatureB`) you can rename.

## Use For

- Creating a new iOS app project from scratch with the standard three-layer architecture already set up.
- Spinning up a project skeleton that builds on first launch and has DI + navigation wired through.

## Do Not Use For

- Modifying an existing project (no migration logic).
- Adding a single feature to a project that already exists.
- Non-iOS targets (macOS, watchOS, visionOS are out of scope — the template is iOS-only).

## Workflow

1. Parse the desired project name from the user's request. Example: *"Use ios-quick-start to create a new project named 'my cool app'"* → name argument is `"my cool app"`.
2. Determine the destination. Default is the current working directory. Confirm with the user only if the cwd looks wrong for a new iOS project (e.g. inside another git repo).
3. Run the scaffold script:
   ```bash
   python3 <skill-dir>/scripts/scaffold.py "<raw project name>" [--dest <path>]
   ```
   The script handles name normalisation (PascalCase for types/folders, lowercase for bundle ID), token substitution, and `git init` + initial commit.
4. Report back:
   - Final project path
   - Normalised project name (e.g. `"my cool app"` → `MyCoolApp`)
   - Bundle identifier (`com.mirkobraic.mycoolapp`)
   - Any warnings from the script

The script will refuse to overwrite an existing directory. If the user wants to regenerate, they must remove the old one first.

## Output Project Structure

```
<ProjectName>/
├── .gitignore
├── AGENTS.md
├── <ProjectName>.xcodeproj
├── <ProjectName>/              # app target
│   ├── <ProjectName>App.swift
│   ├── Root/                   # RootView + RootDestinationResolver
│   ├── DependencyResolver/     # DomainLayerContainer+AutoRegistering
│   └── Resources/              # Assets.xcassets, Info.plist
├── <ProjectName>Tests/
├── <ProjectName>UITests/
├── Shared/                     # SPM package, no deps
│   └── Sources/Shared/Extensions/
├── DomainLayer/                # SPM package, depends on Shared + FactoryKit
│   └── Sources/DomainLayer/
│       ├── DependencyInjection/
│       ├── FeatureADomain/{UseCase, UseCaseProtocol, Contract/, Models/}
│       └── FeatureBDomain/
├── DataLayer/                  # SPM package, depends on DomainLayer + FactoryKit
│   └── Sources/DataLayer/
│       ├── Core/               # placeholder for shared data infra (e.g. networking)
│       ├── DependencyInjection/
│       ├── FeatureAData/
│       └── FeatureBData/
└── ViewLayer/                  # SPM package, depends on DomainLayer + Shared + FactoryKit + NavigatorUI
    └── Sources/ViewLayer/
        ├── CoreUI/
        │   ├── Components/
        │   ├── Extensions/     # Navigator+RootDestination
        │   ├── NavigationDestination/   # RootDestination + per-feature destination enums
        │   └── Resources/
        ├── FeatureAView/{View, ViewModel, NavigationResolver/}
        └── FeatureBView/
```

Each feature's `NavigationProvidedDestination` enum starts with a single `.landing` case.

## Architecture Rules (enforced by the template)

- **DomainLayer** has no internal dependencies. It defines protocols; DataLayer implements them.
- **DataLayer** depends on DomainLayer only.
- **ViewLayer** depends on DomainLayer + Shared only. Never on DataLayer.
- **Feature folders within a layer do not import each other.** Shared code within a layer goes into `Core` (or `CoreUI` for ViewLayer).
- **Dependency injection** is centralised in each layer's `DependencyInjection/` folder using Factory's `SharedContainer`. The app target composes them via `AutoRegistering` in `DependencyResolver/`.

Full details in `references/architecture.md`.

## Third-Party Dependencies

- **Factory** (`hmlongco/Factory`, product `FactoryKit`) — dependency injection. Used across DomainLayer, DataLayer, and ViewLayer.
- **Navigator** (`hmlongco/Navigator`, product `NavigatorUI`) — navigation. Used only in ViewLayer.

Usage patterns for both are in `references/factory.md` and `references/navigator.md`.

## Updating the Skill

The `template/` directory is a **1:1 mirror** of what gets produced. To change what the skill emits:

- **Add a new file** to every generated project → drop it into the matching `template/...` path.
- **Update an existing file** → edit it in `template/`. Use `__PROJECT_NAME__` and `__PROJECT_NAME_LOWER__` wherever the project name should appear.
- **Add a new feature placeholder** → add folders under `template/DomainLayer/.../FeatureCDomain/`, `template/DataLayer/.../FeatureCData/`, `template/ViewLayer/.../FeatureCView/`, then update `RootDestination.swift`, `RootDestinationResolver.swift`, and the `AutoRegistering` file to include it.

Full editing guide in `references/updating-the-skill.md`.

## Guardrails

- Never run the scaffold script without confirming the resolved destination path with the user if it's ambiguous (e.g. cwd is inside another git repo or contains unrelated files).
- Do not edit a generated project on the user's behalf as part of this skill — once scaffolded, the user drives from there.
- Project names are normalised automatically but always surface the normalised result to the user so they see what Xcode will use.

## References

- `references/architecture.md` — layer responsibilities and dependency direction
- `references/factory.md` — Factory/FactoryKit usage patterns in this template
- `references/navigator.md` — Navigator/NavigatorUI usage patterns
- `references/updating-the-skill.md` — how to modify the template safely
