public actor FeatureBUseCase: FeatureBUseCaseProtocol {

    private let dataSource: FeatureBDataSourceProtocol

    public init(dataSource: FeatureBDataSourceProtocol) {
        self.dataSource = dataSource
    }

    public func perform() async throws {
        try await dataSource.fetch()
    }

}
