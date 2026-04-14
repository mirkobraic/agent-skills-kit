# Updating the Skill

The `template/` directory is a **1:1 mirror** of what ends up in the generated project. The scaffold script walks it recursively, substitutes tokens, and writes the result to disk. That means:

> If you can describe the change as "I want this file/folder in every generated project", you just drop it into `template/` at the matching path.

## Tokens

Only two tokens are substituted. They work in **both filenames/folder names and file contents**:

| Token | Replacement | Example |
|---|---|---|
| `__PROJECT_NAME__` | PascalCase project name | `MyCoolApp` |
| `__PROJECT_NAME_LOWER__` | lowercase project name | `mycoolapp` |

`__PROJECT_NAME_LOWER__` is only used inside the bundle identifier today (`com.mirkobraic.__PROJECT_NAME_LOWER__`). Use it anywhere else you want a lowercase form.

## Common edits

### Add a file to `DataLayer/Core/` for every project

1. Create the Swift file under `template/DataLayer/Sources/DataLayer/Core/MyThing.swift`.
2. If it references the app's name, use `__PROJECT_NAME__`. Otherwise write it as normal Swift.
3. No other step — the next `scaffold.py` run will copy it.

### Add a new feature placeholder (`FeatureC`)

The template ships with `FeatureA` and `FeatureB`. To add a third:

1. Add folders and files under:
   - `template/DomainLayer/Sources/DomainLayer/FeatureCDomain/`
   - `template/DataLayer/Sources/DataLayer/FeatureCData/`
   - `template/ViewLayer/Sources/ViewLayer/FeatureCView/`
2. Add a destination enum `template/ViewLayer/Sources/ViewLayer/CoreUI/NavigationDestination/FeatureCDestination.swift`.
3. Add a new case to `template/ViewLayer/Sources/ViewLayer/CoreUI/NavigationDestination/RootDestination.swift`.
4. Add a new branch to the app target's `template/__PROJECT_NAME__/Root/RootDestinationResolver.swift`.
5. Register the new use case in `template/__PROJECT_NAME__/DependencyResolver/DomainLayerContainer+AutoRegistering.swift`.
6. Add the new data source factory to `template/DataLayer/Sources/DataLayer/DependencyInjection/DependencyInjection.swift` and the new use case factory to `template/DomainLayer/Sources/DomainLayer/DependencyInjection/DependencyInjection.swift`.

### Change the bundle identifier prefix

Open `template/__PROJECT_NAME__.xcodeproj/project.pbxproj` and replace `com.mirkobraic` with the new prefix. The lowercase project name is still `__PROJECT_NAME_LOWER__`.

### Change a third-party dependency version

Edit the matching `Package.swift` under `template/<Layer>/Package.swift`. Version pins apply to every generated project going forward.

### Add a new third-party dependency

1. Update the matching `Package.swift` under `template/<Layer>/`.
2. If the dependency is consumed in the app target too, add it as a project-level SPM package inside `project.pbxproj` (the same pattern used for Factory/Navigator today).

### Add a file to the app target

Drop it into `template/__PROJECT_NAME__/`. If it is a Swift source file, also add a matching `PBXFileReference`, `PBXBuildFile`, and `Sources` build-phase entry inside `project.pbxproj` — the script does not regenerate project files, it only does text substitution.

## What the script does NOT do

- It does **not** regenerate or modify `project.pbxproj` beyond token substitution. If you add a new Swift file to the app target, it must already be registered inside the template's `project.pbxproj`.
- It does **not** resolve SPM dependencies. The first time the user opens the generated project, Xcode resolves packages as usual.
- It does **not** validate that the generated project builds — that is the user's first build after scaffolding.

## Testing a change to the template

From the repo root:

```bash
cd /tmp
python3 /Users/bramir/Developer/Personal/agent-skills-kit/plugins/ios-quick-start/skills/ios-quick-start/scripts/scaffold.py "SmokeTest"
open /tmp/SmokeTest/SmokeTest.xcodeproj
```

Then build in Xcode (⌘B). Any build failure usually points at a template edit that forgot one of the steps above.
