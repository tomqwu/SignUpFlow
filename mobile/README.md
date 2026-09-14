# SignUpFlow — Flutter mobile app

> ## ▶️ Un-parked
>
> The responsive **web app** (`/web`, HTMX + FastAPI, same backend) is
> the primary, now full-featured surface (auth, volunteer & admin
> workflows, billing/email/SMS status, analytics, notifications). This
> Flutter app is **active again**. Analysis, tests, codegen and native build
> validation run locally; no CI checks. Run `make test-mobile` from the
> repository root. Feature/bug work is welcome.
>
> The generated API client in `mobile/api_client/` is current with the checked-in
> OpenAPI snapshot as part of issue #191. Regenerate it after intentional backend
> contract changes:
>
> ```
> make mobile-codegen   # needs a JDK 17 (openapi-generator-cli)
> ```
>
> Generated billing and SMS types do not enable those features. Both remain
> disabled by default and outside the core mobile scheduling flow.

## Stack

Flutter + Dart, Riverpod (state), GoRouter (nav), secure storage for the
session token. Talks to the FastAPI backend via the generated
`signupflow_api` Dart client (path dependency at `mobile/api_client/`).

## Develop

```bash
flutter pub get
flutter analyze --no-fatal-infos   # Local analysis (info-level lints non-fatal)
flutter test
```

After backend API changes, refresh the client with `make mobile-codegen`
(from the repo root) and re-run the contract snapshot tests first.

For Flutter basics see the [online documentation](https://docs.flutter.dev/).
