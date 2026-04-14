import FactoryKit
import DomainLayer

final public class DataLayerContainer: SharedContainer {

    public let manager = ContainerManager()
    public static let shared = DataLayerContainer()

    public var featureADataSource: Factory<FeatureADataSourceProtocol> {
        self { FeatureADataSource() }.singleton
    }

    public var featureBDataSource: Factory<FeatureBDataSourceProtocol> {
        self { FeatureBDataSource() }.singleton
    }

}
