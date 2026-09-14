# SignUpFlow examples

These examples exercise only the maintained Church and Basketball scheduling surfaces.
Run them with fictional data against a disposable local workspace or loopback server.
They do not contact billing, SMS, or external email providers.

## Six-week CLI workspaces

The two YAML workspaces each contain one primary event and one secondary event per
week for six weeks. They are compact CLI examples, not substitutes for the complete
role-by-role browser and API acceptance playbooks.

```bash
poetry run signupflow solve examples/church
poetry run signupflow solve examples/basketball
```

The module form is supported too:

```bash
poetry run python -m api.cli.main solve examples/church --json-output
```

The command writes `output/solution.json` unless `--json-output` is used. Tests copy
the examples to temporary directories so repository examples stay unchanged.

## Local API workflow

Start the local server with all paid providers disabled, then run the Basketball
bootstrap, invitation, scheduling, solve, and publication example:

```bash
EMAIL_ENABLED=false SMS_ENABLED=false BILLING_ENABLED=false make run
poetry run python examples/api_client_example.py
```

The script accepts only loopback URLs. It creates unique `.example` identities and
uses canonical `/api/v1` routes with real local JWT authorization.

For the full six-week workflows, use the [operational playbooks](../docs/playbooks/README.md).
For current route details, use the [API guide](../docs/API.md).
