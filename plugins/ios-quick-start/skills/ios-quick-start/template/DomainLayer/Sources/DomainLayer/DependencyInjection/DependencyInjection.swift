import FactoryKit

final public class DomainLayerContainer: SharedContainer {

    public let manager = ContainerManager()
    @TaskLocal public static var shared = DomainLayerContainer()

    // MARK: UseCases
    public var featureAUseCase: Factory<FeatureAUseCaseProtocol> {
        self { fatalError("featureAUseCase not registered") }.singleton
    }

    public var featureBUseCase: Factory<FeatureBUseCaseProtocol> {
        self { fatalError("featureBUseCase not registered") }.singleton
    }

}
