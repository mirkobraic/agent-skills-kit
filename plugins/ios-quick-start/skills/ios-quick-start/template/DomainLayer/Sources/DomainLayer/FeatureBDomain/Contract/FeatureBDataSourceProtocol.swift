public protocol FeatureBDataSourceProtocol: Sendable {

    func fetch() async throws

}
