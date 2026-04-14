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
