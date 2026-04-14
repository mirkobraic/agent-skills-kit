import SwiftUI
import NavigatorUI

struct FeatureBView: View {

    @State private var viewModel = FeatureBViewModel()

    var body: some View {
        VStack {
            Text("Feature B")
                .font(.largeTitle)
        }
        .padding()
    }

}
