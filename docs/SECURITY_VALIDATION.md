# Local Release Security Validation

Security validation runs locally. It does not create a GitHub check, use Ollama,
contact an application provider, or attest a deployment. The release scan uses
[Trivy v0.74.0](https://github.com/aquasecurity/trivy/releases/tag/v0.74.0) from
the immutable image recorded in `scripts/run_security_validation.py`.

## Inventory

The source scan uses a read-only `git archive` of the exact committed revision.
The report hashes these maintained inputs:

| Ecosystem | Inputs | Release interpretation |
|---|---|---|
| Python | `pyproject.toml`, `poetry.lock` | Source and web/API runtime dependencies |
| Dart/Flutter | `mobile/pubspec.yaml`, `mobile/pubspec.lock` | Native client dependencies; not in the web image |
| Ruby/CocoaPods | `mobile/Gemfile*`, `mobile/ios/Podfile*` | Native release tooling and iOS dependencies |
| Gradle/Android | Gradle wrapper and Kotlin build settings | Native Android build inputs |
| Vendored browser code | `web/static/js/alpine.min.js`, `web/static/js/htmx.min.js` | Shipped in the web image and tracked by exact hashes |
| Container | `.dockerignore`, both Dockerfiles, both Compose files, and the retained image identity | Exact web/API release artifact plus maintained local container inputs |
| Publication | `.github/workflows/pages.yml` | Static Pages publication only; actions use reviewed commit SHAs |
| Scanner policy | `security/trivy-secret.yaml` | Keeps built-in rules and scans test paths instead of silently excluding them |

The source result reports discovered locked dependencies, declared licenses, secrets,
and configuration findings. The image result is the release gate for the web/API
artifact and includes OS packages that cannot appear in `pyproject.toml`. Both source
and image CycloneDX JSON documents are retained, and the report lists their image-only
component difference plus known and unknown license declarations. License results are
an inventory for owner review; the repository does not yet define an automatic license
allowlist or denylist, so the runner does not invent one.

## Build Hardening

Both maintained Dockerfiles pin the reviewed multi-architecture
`python:3.11-alpine` manifest by digest and apply available Alpine package upgrades.
The production builder exports Poetry's locked runtime set with hashes into an isolated
virtual environment. The runtime copies only that environment and application files,
then removes `pip`, `setuptools`, and `wheel` from both Python locations. Poetry and
native build tools remain in the discarded builder stage.

The runtime uses PyJWT directly instead of the former `python-jose` dependency chain.
FastAPI, Starlette, multipart handling, cryptography, and affected transitive Python
packages are locked at remediated versions. The mobile release-tool lock uses Fastlane
2.240.0 and Rubyzip 3.6.0. This source inventory is not a native artifact scan; run and
accept a separate mobile artifact validation before any native release.

## Run

Install project dependencies from the lockfile, then pull the scanner by its exact digest:

```bash
docker pull ghcr.io/aquasecurity/trivy@sha256:62b1e65e8869bc4b4c6aa4fa2b21595256c7c2f6018a9d9ad61caf87187c1969
make test-artifact
make test-security
```

`make test-artifact` must pass for the same clean Git SHA and retain its image. The
security runner refuses a stale report, changed image ID, missing scanner, missing or
unusable advisory database, dirty tracked tree, or expired exception. It downloads a
fresh vulnerability database into an owned temporary cache, records its timestamps and
file hashes, then scans with networking disabled. It saves the exact local image to an
owned temporary archive; the scanner never receives the Docker socket.

The runner also creates a generated harmless secret fixture. Detection must fail with
the expected nonzero status, and the same directory must pass after removal. A separate
empty-cache probe must fail when database updates are disabled. Neither raw secret
matches nor generated fixture values are persisted. Reports and SBOMs are written under
`test-artifacts/security-validation/`.

Trivy excludes test paths through a built-in allow rule by default. The committed local
policy disables only that allow rule so test helpers and fixtures are scanned; other
built-in path allowances and skip patterns remain unchanged.

## Release Policy

Unaccepted high or critical findings in the exact image, any detected secret, and high
or critical source configuration findings block this local release result. Source-only
dependency and license findings remain visible but do not silently become claims about
the web image; validate the Flutter artifact separately before a native release. Review
unknown and incompatible license declarations explicitly before release acceptance.

Exceptions live in `security/exceptions.json`. Every exception must identify one exact
finding key and include an owner, rationale, mitigation, and expiry date. Expired,
duplicate, malformed, or no-longer-observed exceptions fail validation. Do not add an
exception merely to obtain a passing result; owner risk acceptance is required.

Run this validation for every release artifact and after any dependency, base-image,
vendored-JavaScript, Dockerfile, scanner-policy, or Pages action change. Refresh the
scanner pin deliberately after reviewing its release and repeat the fixture drills.
Do not treat a prior passing report as current after the advisory database or any input
changes; rerun against the release candidate and record its exact SHA and image ID.
