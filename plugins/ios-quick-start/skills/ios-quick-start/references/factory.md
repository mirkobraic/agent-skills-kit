# Factory (FactoryKit)

- Package: `https://github.com/hmlongco/Factory`, product `FactoryKit`.
- Used in DomainLayer, DataLayer, and ViewLayer.

## Shape

Each layer that participates in DI owns a `SharedContainer` subclass declared in `DependencyInjection/DependencyInjection.swift`. The container is the registry of everything that layer exposes to others.

### DomainLayerContainer

Defines protocol-typed factories with a `fatalError` default body. Real implementations are registered by the app target at boot time. Marked `@TaskLocal` on `shared` so tests can swap the container in parallel with `DomainLayerContainer.$shared.withValue(...)`.

```swift
import FactoryKit

final public class DomainLayerContainer: SharedContainer {

    public let manager = ContainerManager()
    @TaskLocal public static var shared = DomainLayerContainer()

    public var featureAUseCase: Factory<FeatureAUseCaseProtocol> {
        self { fatalError("featureAUseCase not registered") }.singleton
    }
}
```

### DataLayerContainer

Defines concrete implementations of the protocols in DomainLayer's `Contract/` folders. Not `@TaskLocal` — DataLayer's internal wiring is stable across tests.

```swift
import FactoryKit
import DomainLayer

final public class DataLayerContainer: SharedContainer {

    public let manager = ContainerManager()
    public static let shared = DataLayerContainer()

    public var featureADataSource: Factory<FeatureADataSourceProtocol> {
        self { FeatureADataSource() }.singleton
    }
}
```

### App target composition

The app target owns one file, `DomainLayerContainer+AutoRegistering.swift`, which bridges the two:

```swift
import FactoryKit
import DataLayer
import DomainLayer

extension DomainLayerContainer: @retroactive AutoRegistering {

    public func autoRegister() {
        featureAUseCase.register {
            FeatureAUseCase(dataSource: DataLayerContainer.shared.featureADataSource())
        }
    }
}
```

`AutoRegistering.autoRegister()` is called by Factory the first time the container is accessed. This is why the app target does not need any explicit bootstrap call — the `@Injected` property wrapper triggers it.

## Using dependencies

Inside a view model:

```swift
import Observation
import FactoryKit
import DomainLayer

@Observable @MainActor
final class FeatureAViewModel {

    @ObservationIgnored @Injected(\DomainLayerContainer.featureAUseCase) var useCase
}
```

Use `@Injected` with the key path through the container. Never reach into `DataLayerContainer` from a ViewModel — ViewModels depend only on DomainLayer protocols.

## Rules of thumb

- DomainLayer publishes **protocols**, DataLayer publishes **concrete types**.
- DomainLayer factories `fatalError` by default — if you ever hit that fatalError at runtime, the app target's `autoRegister()` forgot to register the binding.
- Mark long-lived dependencies with `.singleton`. Per-call types (e.g. a fresh encoder each time) can use the default scope.
- Test overrides: `DomainLayerContainer.$shared.withValue(testContainer) { ... }` for swapping the whole container.
