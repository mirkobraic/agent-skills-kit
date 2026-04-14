import NavigatorUI

public enum RootDestination: NavigationProvidedDestination {

    case featureA(FeatureADestination)
    case featureB(FeatureBDestination)

    public var method: NavigationMethod {
        switch self {
        case .featureA(let destination):
            destination.method
        case .featureB(let destination):
            destination.method
        }
    }

}
