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
