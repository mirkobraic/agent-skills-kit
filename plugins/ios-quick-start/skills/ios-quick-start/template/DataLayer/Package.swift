// swift-tools-version: 6.2
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "DataLayer",
    platforms: [.iOS(.v26)],
    products: [
        .library(
            name: "DataLayer",
            targets: ["DataLayer"]
        ),
    ],
    dependencies: [
        .package(name: "DomainLayer", path: "../DomainLayer"),
        .package(url: "https://github.com/hmlongco/Factory", .upToNextMajor(from: "2.5.3")),
    ],
    targets: [
        .target(
            name: "DataLayer",
            dependencies: [
                .product(name: "DomainLayer", package: "DomainLayer"),
                .product(name: "FactoryKit", package: "Factory"),
            ]
        ),
        .testTarget(
            name: "DataLayerTests",
            dependencies: ["DataLayer"]
        ),
    ]
)
