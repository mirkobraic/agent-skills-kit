# Navigator (NavigatorUI)

- Package: `https://github.com/hmlongco/Navigator`, product `NavigatorUI`.
- Used only in ViewLayer (and the app target, which re-uses ViewLayer's types).

## Shape

Navigation is expressed as a tree of `NavigationProvidedDestination` enums — one per feature, plus a top-level `RootDestination` that composes them.

### Per-feature destinations (ViewLayer/CoreUI/NavigationDestination/)

Every feature defines its own destination enum. The template ships with a single `.landing` case per feature:

```swift
import NavigatorUI

public enum FeatureADestination: NavigationProvidedDestination {
    case landing
}
```

Add further cases (`.details(id: UUID)`, etc.) as the feature grows. Default `method` works for plain pushes; override `var method: NavigationMethod` when a case should present as a sheet or full-screen cover.

### RootDestination (ViewLayer/CoreUI/NavigationDestination/)

Composes the feature destinations into a single top-level enum:

```swift
import NavigatorUI

public enum RootDestination: NavigationProvidedDestination {

    case featureA(FeatureADestination)
    case featureB(FeatureBDestination)

    public var method: NavigationMethod {
        switch self {
        case .featureA(let d): d.method
        case .featureB(let d): d.method
        }
    }
}
```

### Navigator typed extension (ViewLayer/CoreUI/Extensions/)

Gives call sites a typed `navigate(to:)` so they don't have to pass `method:` explicitly:

```swift
import NavigatorUI

extension Navigator {

    @MainActor
    public func navigate(to destination: RootDestination) {
        navigate(to: destination, method: destination.method)
    }
}
```

### NavigationResolver per feature (ViewLayer/{Feature}View/NavigationResolver/)

Each feature owns one resolver that maps destination cases to concrete views:

```swift
import SwiftUI
import NavigatorUI

public struct FeatureANavigationResolver: View {

    let destination: FeatureADestination

    public init(destination: FeatureADestination) {
        self.destination = destination
    }

    public var body: some View {
        switch destination {
        case .landing:
            FeatureAView()
        }
    }
}
```

### RootDestinationResolver (app target/Root/)

The app-level resolver dispatches to the per-feature resolvers:

```swift
import SwiftUI
import ViewLayer

struct RootDestinationResolver: View {

    let destination: RootDestination

    init(destination: RootDestination = .featureA(.landing)) {
        self.destination = destination
    }

    var body: some View {
        switch destination {
        case .featureA(let d): FeatureANavigationResolver(destination: d)
        case .featureB(let d): FeatureBNavigationResolver(destination: d)
        }
    }
}
```

### RootView (app target/Root/)

```swift
import SwiftUI
import NavigatorUI
import ViewLayer

struct RootView: View {

    private let navigator = Navigator(configuration: .init(
        restorationKey: nil,
        executionDelay: 0.4,
        verbosity: .none,
        autoDestinationMode: true
    ))

    var body: some View {
        ManagedNavigationStack {
            RootDestinationResolver()
        }
        .onNavigationProvidedView(RootDestination.self) {
            RootDestinationResolver(destination: $0)
        }
        .navigationRoot(navigator)
    }
}
```

`autoDestinationMode: true` + `.onNavigationProvidedView(RootDestination.self)` is what makes `navigator.navigate(to: .featureA(.someCase))` work from anywhere in the view tree.

## Using the navigator

Inside any view:

```swift
@Environment(\.navigator) private var navigator

Button("Open Feature B") {
    navigator.navigate(to: .featureB(.landing))
}
```

## Rules of thumb

- **One destination enum per feature.** Keep cases feature-scoped: `FeatureADestination.details(id:)`, never `RootDestination.featureADetails(id:)`.
- **All destination enums live in `CoreUI/NavigationDestination/`** so any feature can navigate to any other without cross-feature imports.
- **NavigationResolvers live inside the feature folder** (`FeatureAView/NavigationResolver/`) because they map destinations to that feature's concrete views.
- When a new feature is added, update `RootDestination` and `RootDestinationResolver` together.
