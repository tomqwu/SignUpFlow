# SignUpFlow - Flutter mobile app

> ## Active development
>
> The responsive **web app** (`/web`, HTMX + FastAPI, same backend) remains
> the primary surface. The Flutter app is maintained and validated locally;
> there are no CI checks, and GitHub Actions does not attest mobile results.
>
> The generated API client in `mobile/api_client/` is current with the checked-in
> OpenAPI snapshot as part of issue #191. Regenerate it after intentional backend
> contract changes:
>
> ```
> make mobile-codegen-preflight  # validate tools, pins, and canonical schema
> make mobile-codegen            # generate twice, then update the full client
> make mobile-codegen-check      # verify drift without changing the worktree
> ```
>
> Generated billing and SMS types do not enable those features. Both remain
> disabled by default and outside the core mobile scheduling flow.

## Current validation status

| Scope | Local result | Command / evidence boundary |
| --- | --- | --- |
| OpenAPI schema and reproducible Dart client | Passed | `make mobile-codegen-check`; wrapper 2.20.2 and generator 7.14.0 |
| Generated Dart package | Passed | `make test-mobile-generated`; 48 non-fatal generator warnings and 692 tests |
| Maintained Flutter app | Passed | `flutter analyze --no-fatal-infos` and `make test-mobile` |
| iOS simulator routes | Passed | `mobile/scripts/run_integration_tests.sh`; login plus invitation/reset deep links |
| Android local artifact | Passed | Debug `flutter build apk --debug --dart-define=API_BASE_URL=http://10.0.2.2:8000` |
| Real iOS/Android devices | Not run | Required before native release acceptance |
| Signed iOS/Android release artifacts | Not run | Requires owner-managed signing material |
| TestFlight, Play, and live backend | Not run | Requires explicit release authorization and external accounts |

Flutter 3.41.9 with Xcode 27 currently hits the upstream multi-architecture
`lipo -verify_arch` simulator-build defect tracked in
[flutter/flutter#188461](https://github.com/flutter/flutter/issues/188461).
The device-specific iOS integration build succeeds; do not interpret that as
a signed device archive or TestFlight result.

## Stack

Flutter + Dart, Riverpod (state), GoRouter (nav), secure storage for the
session token. Talks to the FastAPI backend via the generated
`signupflow_api` Dart client (path dependency at `mobile/api_client/`).

## Develop

```bash
flutter pub get
flutter analyze --no-fatal-infos   # Local analysis (info-level lints non-fatal)
flutter test
./scripts/run_integration_tests.sh # Integration files run sequentially on one device
```

After backend API changes, refresh the client with `make mobile-codegen`
(from the repo root), then run `make mobile-codegen-check` and the contract
snapshot tests. The runner discovers Homebrew OpenJDK and tools on `PATH`;
set `JAVA_BIN`, `NPX`, `FLUTTER`, or `DART` to explicit executable paths when
needed. OpenAPI Generator CLI wrapper 2.20.2 and generator 7.14.0 are pinned.

The generated package contains 138 tracked Markdown documents after removal
of the obsolete `OrganizationCreate` model. Never edit generated code or
documentation by hand; update the canonical snapshot and regenerate instead.

For Flutter basics see the [online documentation](https://docs.flutter.dev/).
