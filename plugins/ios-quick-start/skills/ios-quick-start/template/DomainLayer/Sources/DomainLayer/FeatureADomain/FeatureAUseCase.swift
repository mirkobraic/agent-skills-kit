public actor FeatureAUseCase: FeatureAUseCaseProtocol {

    private let dataSource: FeatureADataSourceProtocol

    public init(dataSource: FeatureADataSourceProtocol) {
        self.dataSource = dataSource
    }

    public func perform() async throws {
        try await dataSource.fetch()
    }

}
