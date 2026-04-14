import FactoryKit
import DataLayer
import DomainLayer

extension DomainLayerContainer: @retroactive AutoRegistering {

    public func autoRegister() {
        featureAUseCase.register {
            FeatureAUseCase(dataSource: DataLayerContainer.shared.featureADataSource())
        }

        featureBUseCase.register {
            FeatureBUseCase(dataSource: DataLayerContainer.shared.featureBDataSource())
        }
    }

}
