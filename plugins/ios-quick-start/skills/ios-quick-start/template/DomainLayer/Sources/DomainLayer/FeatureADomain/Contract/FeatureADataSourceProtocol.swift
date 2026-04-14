public protocol FeatureADataSourceProtocol: Sendable {

    func fetch() async throws

}
