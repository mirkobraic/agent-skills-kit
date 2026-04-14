import Observation
import FactoryKit
import DomainLayer

@Observable @MainActor
final class FeatureAViewModel {

    @ObservationIgnored @Injected(\DomainLayerContainer.featureAUseCase) var useCase

}
