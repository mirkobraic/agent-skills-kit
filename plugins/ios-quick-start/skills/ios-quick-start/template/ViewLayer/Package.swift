// swift-tools-version: 6.2
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "ViewLayer",
    platforms: [.iOS(.v26)],
    products: [
        .library(
            name: "ViewLayer",
            targets: ["ViewLayer"]
        ),
    ],
    dependencies: [
        .package(name: "DomainLayer", path: "../DomainLayer"),
        .package(name: "Shared", path: "../Shared"),
        .package(url: "https://github.com/hmlongco/Factory", .upToNextMajor(from: "2.5.3")),
        .package(url: "https://github.com/hmlongco/Navigator", .upToNextMajor(from: "1.4.0"))
    ],
    targets: [
        .target(
            name: "ViewLayer",
            dependencies: [
                .product(name: "DomainLayer", package: "DomainLayer"),
                .product(name: "Shared", package: "Shared"),
                .product(name: "FactoryKit", package: "Factory"),
                .product(name: "NavigatorUI", package: "Navigator")
            ],
            resources: [
                .process("CoreUI/Resources")
            ]
        ),
        .testTarget(
            name: "ViewLayerTests",
            dependencies: ["ViewLayer"]
        ),
    ]
)
