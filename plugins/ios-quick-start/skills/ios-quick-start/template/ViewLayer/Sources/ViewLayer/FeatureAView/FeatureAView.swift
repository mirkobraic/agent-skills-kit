import SwiftUI
import NavigatorUI

struct FeatureAView: View {

    @Environment(\.navigator)
    private var navigator

    @State private var viewModel = FeatureAViewModel()

    var body: some View {
        VStack(spacing: 16) {
            Text("Feature A")
                .font(.largeTitle)

            Button("Open Feature B") {
                navigator.navigate(to: .featureB(.landing))
            }
        }
        .padding()
    }

}
