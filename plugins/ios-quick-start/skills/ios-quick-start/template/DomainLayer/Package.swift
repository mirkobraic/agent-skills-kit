// swift-tools-version: 6.2
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "DomainLayer",
    platforms: [.iOS(.v26)],
    products: [
        .library(name: "DomainLayer", targets: ["DomainLayer"]),
    ],
    dependencies: [
        .package(name: "Shared", path: "../Shared"),
        .package(url: "https://github.com/hmlongco/Factory", .upToNextMajor(from: "2.5.3")),
    ],
    targets: [
        .target(
            name: "DomainLayer",
            dependencies: [
                .product(name: "FactoryKit", package: "Factory"),
            ]
        ),
        .testTarget(name: "DomainLayerTests", dependencies: ["DomainLayer"]),
    ]
)
