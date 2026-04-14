import SwiftUI
import NavigatorUI

public struct FeatureBNavigationResolver: View {

    let destination: FeatureBDestination

    public init(destination: FeatureBDestination) {
        self.destination = destination
    }

    public var body: some View {
        switch destination {
        case .landing:
            FeatureBView()
        }
    }

}
