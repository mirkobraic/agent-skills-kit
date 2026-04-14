# Repository Guidelines

## Project Structure & Module Organization

- `__PROJECT_NAME__/` is the app target. SwiftUI entry point is `__PROJECT_NAME__App.swift`, app routing is under `__PROJECT_NAME__/Root/`, and the Factory auto-registration lives in `__PROJECT_NAME__/DependencyResolver/`.
- `Shared/`, `DomainLayer/`, `DataLayer/`, and `ViewLayer/` are local Swift Package modules, each with its own `Package.swift` and `Sources/` tree. Tests live under each package's `Tests/` directory.
- App-level tests are in `__PROJECT_NAME__Tests/`; app-level UI tests are in `__PROJECT_NAME__UITests/`.
- UI resources are packaged in `ViewLayer/Sources/ViewLayer/CoreUI/Resources/`.
- Dependency direction is strict: `DataLayer` and `ViewLayer` depend on `DomainLayer`; `DomainLayer` does not depend on `ViewLayer` or `DataLayer`. `Shared` has no internal dependencies.
- Inside each layer, every feature has its own folder. Features within a layer do not import each other. Shared code within a layer goes into `Core/` (or `CoreUI/` in `ViewLayer`). This keeps features promotable to standalone SPM modules later.

## Build, Test, and Development Commands

App build (Xcode scheme is `__PROJECT_NAME__`):

```
xcodebuild -project __PROJECT_NAME__.xcodeproj \
           -scheme __PROJECT_NAME__ \
           -destination 'platform=iOS Simulator,name=iPhone 17' \
           build
```

App tests (unit + UI via the app scheme):

```
xcodebuild -project __PROJECT_NAME__.xcodeproj \
           -scheme __PROJECT_NAME__ \
           -destination 'platform=iOS Simulator,name=iPhone 17' \
           test
```

Package tests:

```
swift test --package-path DomainLayer
swift test --package-path DataLayer
swift test --package-path ViewLayer
swift test --package-path Shared
```

## Coding Style & Naming Conventions

- Swift style follows standard Swift conventions: 4‑space indentation, braces on the same line.
- Types are `UpperCamelCase` (e.g. `RootDestinationResolver`); functions and variables are `lowerCamelCase`.
- File names mirror the primary type they declare (e.g. `FeatureAView.swift`).
- Keep lines under 200 characters. Do not break function signatures or initializer calls across lines unless the single-line form would exceed that limit. When wrapping is needed, use one argument per line with the closing delimiter outdented to match the opening statement.
- Omit the `return` keyword where Swift allows it.
- In tests, use backtick-quoted function names so they can contain spaces.

## View & Feature Patterns

- For data loaded from external sources, keep `state` and `model` properties on the view model.
- Keep view `body` slim: extract pieces into private extensions, and split larger sub-trees into their own views.
- View models are `@Observable @MainActor`. Dependencies arrive via `@Injected(\DomainLayerContainer.<useCase>)`.

Example:

```swift
@Observable @MainActor
final class FeatureAViewModel {

    @ObservationIgnored @Injected(\DomainLayerContainer.featureAUseCase) var useCase

    var state: LoadingState = .initial

    func load() async {
        // fetch data, update state
    }
}

struct FeatureAView: View {

    @State var viewModel = FeatureAViewModel()

    var body: some View {
        content
    }
}

private extension FeatureAView {

    var content: some View {
        Text("Feature A")
    }
}
```

## Testing Guidelines

- Testing uses XCTest across the app and the packages.
- Keep unit tests for domain and data logic inside each package's `Tests/` directory. UI tests live in `__PROJECT_NAME__UITests/`.

## Commit & Pull Request Guidelines

- Commit history uses short, imperative summaries (e.g. "Implement …", "Improve …").
- Keep commit messages under ~70 characters; include scope in the summary if helpful.
- PRs should include a clear description, testing notes (what ran), and screenshots for UI changes.

## Architecture Notes

- Dependency injection is centralised under each layer's `DependencyInjection/` folder and uses Factory (`FactoryKit`).
- `DomainLayerContainer` exposes protocols with `fatalError` defaults; the app target registers real implementations in `__PROJECT_NAME__/DependencyResolver/DomainLayerContainer+AutoRegistering.swift`.
- Navigation uses Navigator (`NavigatorUI`). One `NavigationProvidedDestination` enum per feature lives in `ViewLayer/Sources/ViewLayer/CoreUI/NavigationDestination/`. `RootDestination` composes them. Each feature's `NavigationResolver` maps its destination cases to concrete views.

## Future-Proofing & Extensibility

- Always consider how future requirements will affect the code being written. Design every abstraction so that the next feature or format change is easy to integrate, not a refactor.
- Prefer generic, reusable designs over narrow, use-case-specific ones. If something works for one variant today, make sure it can accommodate new variants without requiring structural changes.

## Agent Instructions

- Only run a build when the user explicitly says "build and validate".
- If the build fails, pause, inspect the error, and attempt a fix or a well-reasoned retry.
- After two failed attempts, stop and report the errors with the exact log tail. Do not revert changes; ask for guidance first.
