# Architecture

Three-layer architecture. Each layer is an independent Swift Package Manager module. A fourth module, `Shared`, provides common utilities.

## Layers

The architecture enforces a strict dependency direction: the outer layers (ViewLayer and DataLayer) depend on the inner layer (DomainLayer), but never on each other. DomainLayer contains pure business logic and defines contracts that DataLayer implements.

Each layer is organised into feature folders. Feature folders within the same layer do not depend on each other. Shared infrastructure within a layer lives in a `Core` (or `CoreUI`) folder.

### Shared

Utility module with no dependencies. Common extensions and helpers that any other module can use.

- `Extensions/` — Swift standard library extensions.

### DomainLayer

Innermost layer. Business logic, use case definitions, domain models. Defines data source contracts (protocols) that DataLayer must implement.

**Dependencies:** FactoryKit.

- `{Feature}Domain/` — use case, use case protocol, `Contract/` subfolder with the data source protocol, `Models/` for domain entities.
- `DependencyInjection/` — Factory container registrations for this layer.

### DataLayer

Implements the contracts defined by DomainLayer. Handles all interaction with external data sources.

**Dependencies:** DomainLayer, FactoryKit.

- `Core/` — shared data infrastructure (e.g. local storage abstractions, networking).
- `{Feature}Data/` — implementation of the corresponding DomainLayer data source contract.
- `DependencyInjection/` — Factory container registrations for this layer.

### ViewLayer

Presentation layer. SwiftUI views, view models, UI components.

**Dependencies:** DomainLayer, Shared, FactoryKit, NavigatorUI.

- `CoreUI/`
  - `Components/` — reusable view components.
  - `NavigationDestination/` — navigation route definitions: one `NavigationProvidedDestination` enum per feature plus a top-level `RootDestination`.
  - `Extensions/` — Navigator framework extensions (e.g. a typed `navigate(to:)` for `RootDestination`).
  - `Resources/` — asset catalogs, colors, localisations, processed via SPM `resources: [.process("CoreUI/Resources")]`.
- `{Feature}View/` — feature screen: view, view model, `NavigationResolver/` subfolder with the feature's navigation resolver.

## App Target

The Xcode app target composes all four modules and is the application entry point.

- `{ProjectName}App.swift` — `@main` App.
- `Root/` — `RootView` and `RootDestinationResolver`.
- `DependencyResolver/` — bootstraps Factory by triggering auto-registration: concrete DataLayer implementations are bound to DomainLayer contracts here.
- `Resources/` — `Assets.xcassets`, `Info.plist`.

## Module Dependency Graph

```
App target → Shared, DomainLayer, DataLayer, ViewLayer
ViewLayer  → DomainLayer, Shared, FactoryKit, NavigatorUI
DataLayer  → DomainLayer, FactoryKit
DomainLayer → FactoryKit
Shared      → (nothing)
```

ViewLayer must never import DataLayer. DomainLayer must never import DataLayer or ViewLayer.

## Why features are separate folders (not sub-packages)

Each feature is kept in its own folder per layer so it can be **promoted to its own SPM module** later without restructuring. That is the reason cross-feature imports within a layer are forbidden: breaking that rule makes future extraction painful.
