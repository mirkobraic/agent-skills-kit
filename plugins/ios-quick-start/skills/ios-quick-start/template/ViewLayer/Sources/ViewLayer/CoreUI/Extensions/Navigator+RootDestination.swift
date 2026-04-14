import NavigatorUI

extension Navigator {

    @MainActor
    public func navigate(to destination: RootDestination) {
        navigate(to: destination, method: destination.method)
    }

}
