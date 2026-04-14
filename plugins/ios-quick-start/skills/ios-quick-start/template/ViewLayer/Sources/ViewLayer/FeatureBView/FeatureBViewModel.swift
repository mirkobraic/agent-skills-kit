import Observation
import FactoryKit
import DomainLayer

@Observable @MainActor
final class FeatureBViewModel {

    @ObservationIgnored @Injected(\DomainLayerContainer.featureBUseCase) var useCase

}
