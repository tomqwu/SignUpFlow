# SignUpFlow — Flutter mobile app

> ## ▶️ Un-parked — but read the codegen note
>
> The responsive **web app** (`/web`, HTMX + FastAPI, same backend) is
> the primary, now full-featured surface (auth, volunteer & admin
> workflows, billing/email/SMS status, analytics, notifications). This
> Flutter app is **active again**: it has a CI lane (analyze + test on
> GitHub Actions — `.github/workflows/mobile-ci.yml`) and feature/bug
> work is welcome.
>
> **Known gap (tracked in #191):** the generated API client in
> `mobile/api_client/` predates endpoints added during the full-feature
> work — `POST /api/v1/auth/change-password`, the billing router, and
> `/api/sms/*`. Regenerate it before building features that use those:
>
> ```
> make mobile-codegen   # needs a JDK 17 (openapi-generator-cli)
> ```
>
> The OpenAPI snapshot (`tests/contract/openapi.snapshot.json`) is
> already current, so codegen is a clean mechanical step.

## Stack

Flutter + Dart, Riverpod (state), GoRouter (nav), secure storage for the
session token. Talks to the FastAPI backend via the generated
`signupflow_api` Dart client (path dependency at `mobile/api_client/`).

## Develop

```bash
flutter pub get
flutter analyze --no-fatal-infos   # CI gate (info-level lints non-fatal)
flutter test
```

After backend API changes, refresh the client with `make mobile-codegen`
(from the repo root) and re-run the contract snapshot tests first.

For Flutter basics see the [online documentation](https://docs.flutter.dev/).
