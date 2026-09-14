# Screenshot Evidence

The `current/` directory contains real Chromium captures from the fixture-driven Church
and Basketball Playwright workflows. It is not a mockup gallery. Each domain has the same
eleven asserted states at 360px and 1440px: dashboard, onboarding, qualified directory,
six-week solution, unanswered and accepted commitments, replacement needed and covered,
administrator/member schedule change, and week-seven rollover.

`current/manifest.json` records the exact source commit, fixed scenario clock, browser
version, logical viewport, device scale, PNG dimensions and hash, fixture hash, actor,
scenario, asserted state, caption, and relevant UI source hashes for all 44 images. Unit
validation fails when an image or fixture is missing or altered, relevant UI source drifts,
the matrix is incomplete, or a README caption no longer matches its manifest entry.

## Regenerate

Commit the source state that will be captured, then run:

```bash
SCREENSHOT_SOURCE_REF=$(git rev-parse HEAD) make capture-screenshots
make validate-screenshots
```

The command creates an owned temporary SQLite database, freezes the server clock at
January 9, 2030, runs the four relevant Playwright workflow families for both domains and
viewports, requires all assertions to pass, replaces only `docs/screenshots/current/`, and
writes the manifest. It does not contact email, SMS, billing, Ollama, or other providers.

After capture, inspect every PNG at readable size for clipped or overlapping content,
missing assets, incorrect actors/states, and unsafe data. Commit the generated set and
documentation separately so the manifest can reference the exact captured source commit.

## Retired Images

`legacy/` contains the ten May 2026 walkthrough images formerly embedded in the README.
They are retained only as historical artifacts. They do not represent the current
Church/Basketball scenario matrix and must not be cited as current acceptance evidence.
