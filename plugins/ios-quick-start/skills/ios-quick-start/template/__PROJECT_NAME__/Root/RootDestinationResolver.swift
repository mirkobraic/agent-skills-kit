import SwiftUI
import ViewLayer

struct RootDestinationResolver: View {

    let destination: RootDestination

    init(destination: RootDestination = .featureA(.landing)) {
        self.destination = destination
    }

    var body: some View {
        switch destination {
        case .featureA(let destination):
            FeatureANavigationResolver(destination: destination)
        case .featureB(let destination):
            FeatureBNavigationResolver(destination: destination)
        }
    }

}
