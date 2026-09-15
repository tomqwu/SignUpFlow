# Tool Safety Ledger

This ledger is the current contract for repository scripts and database tools. A
retired entry point exits with status 2 before reading credentials, contacting a
service, starting a container, changing a database, deleting a file, or signaling a
process. Do not bypass a refusal by copying the old command from historical docs.

| Tool | Status | Supported scope or replacement | Owner |
|---|---|---|---|
| `scripts/QUICK_DEMO.sh` | Retired | Run `make test-all`; use `docs/playbooks/README.md` for scenarios. | Testing |
| `scripts/backup_database.sh` | Supported local SQLite | Delegates to `sqlite_recovery.py backup`; requires an owned workspace, explicit source, separate mode-`0600` key, and new bundle name. | Data platform |
| `scripts/build-binary.sh` | Retired | Artifact construction remains in #265. | Release |
| `scripts/capture_playbook_screenshots.py` | Supported | Run through `make capture-screenshots`; owns its server, ports, database, and output manifest. | Web testing |
| `scripts/check_test_docstrings.py` | Supported read-only | Pass an explicit source directory; reports only. | Testing |
| `scripts/check_test_status.sh` | Supported | Runs `make test-e2e`; `--dry-run` prints the command. | Testing |
| `scripts/cleanup_and_test.sh` | Supported | Compatibility wrapper for `make test-all`; performs no cleanup. | Testing |
| `scripts/cleanup_maintenance.sh` | Retired | Remove only artifacts owned by the command that created them. | Developer tooling |
| `scripts/cleanup_servers.sh` | Retired | Stop only a PID recorded by the owning launcher. | Developer tooling |
| `scripts/email_smoke.py` | Supported live opt-in | Requires `--allow-live-send`; provider acceptance also requires owner authorization. | Messaging |
| `scripts/migrate_add_role_to_assignments.py` | Retired | Current Alembic initial revision already owns the field. | Data platform |
| `scripts/migrate_assignments.py` | Retired | Use the current Alembic graph against an approved target. | Data platform |
| `scripts/migrate_invitations.py` | Retired | Current Alembic initial revision already owns the tables and fields. | Data platform |
| `scripts/migrate_passwords_to_bcrypt.py` | Retired | Use password reset; bulk default-password replacement is forbidden. | Security |
| `scripts/migrate_timezone.py` | Retired | Current Alembic initial revision already owns the field. | Data platform |
| `scripts/migrate_vacation_reason.py` | Retired | Current Alembic initial revision already owns the field. | Data platform |
| `scripts/agent_runner.py` | Supported | Finite plan/review/build runner; requires an explicit versioned work item and current local evidence for builders. | Agent tooling |
| `scripts/agent_tool_guard.py` | Internal support | Enforces mode-specific Git/GitHub commands and owned-path staging. | Agent tooling |
| `scripts/ralph-loop-gemini.sh` | Supported | Gemini adapter for `agent_runner.py`; no auto-approval or model switching. | Agent tooling |
| `scripts/ralph-loop.sh` | Supported | Claude adapter for `agent_runner.py`; no auto-approval or model switching. | Agent tooling |
| `scripts/restore_database.sh` | Supported local SQLite | Delegates to `sqlite_recovery.py restore`; authenticates and integrity-checks the bundle before atomically publishing a new isolated database. | Data platform |
| `scripts/retired_tool.py` | Internal support | Emits deterministic refusal messages for retired entry points. | Developer tooling |
| `scripts/run_local_validation.py` | Supported | Run through `make test-all`; owns unique logs/JUnit/report artifacts. | Testing |
| `scripts/run_load_validation.py` | Supported local opt-in | Run through `make test-load`; starts and stops one owned loopback server, verifies its exact source SHA, uses fictional tenant data, and writes raw samples plus threshold results to a unique report directory. Remote release-candidate use requires an approved profile, exact expected SHA, and an explicit authorization flag. | Testing |
| `scripts/run_postgres_validation.py` | Supported | Run through `make test-postgres`; owns one loopback-only, tmpfs PostgreSQL container and unique report directory. | Testing |
| `scripts/run_redis_validation.py` | Supported | Run through `make test-redis`; owns one authenticated loopback-only, tmpfs Redis container and proves shared quotas, tenant-scoped event delivery, and broker recovery in a unique report directory. | Testing |
| `scripts/run_security_validation.py` | Supported local opt-in | Run through `make test-security` after a same-SHA `make test-artifact`; scans a committed archive and exact retained image with a pinned container, no Docker socket, and owned temporary cache. | Security |
| `scripts/run_sqlite_recovery_drill.py` | Supported local opt-in | Run through `make test-recovery`; owns fictional SQLite files and source-bound report/JUnit/log artifacts, destroys its temporary key, and performs no cutover. | Data platform |
| `scripts/run_staging_acceptance.py` | Supported remote opt-in | Run through `make test-staging` only after deployment authorization; requires an HTTPS origin, exact deployed SHA, approval reference, and explicit remote flag, then runs every selected pluggable API playbook plus browser-cookie checks with generated credentials. | Release |
| `scripts/sqlite_recovery.py` | Supported local SQLite | Initializes marker-bound workspaces, generates a separate key, creates/verifies encrypted WAL-consistent bundles, and restores only to a new owned destination. | Data platform |
| `scripts/validate_production_artifact.py` | Supported local opt-in | Run through `make test-artifact`; owns one private Docker network and disposable datastore/runtime containers, retains the SHA-labeled image and report. | Release |
| `scripts/seed_sms_templates.py` | Retired | Paid SMS remains disabled and tracked in #257. | Messaging |
| `scripts/test_docker_setup.sh` | Retired | Use documented Docker targets individually against an owned Compose project. | Developer tooling |
| `scripts/validate_email_system.sh` | Retired | Use local capture tests; live provider acceptance requires explicit authorization. | Messaging |
| `tools/db_interactive.py` | Supported read-only | Requires an explicit existing non-symlink SQLite file; SQL is read-only. | Data platform |
| `tools/db_viewer.py` | Supported read-only | Requires an explicit existing non-symlink SQLite file; SQL is read-only. | Data platform |
| `tools/sqlite_readonly.py` | Internal support | Shared path, query, and read-only connection enforcement. | Data platform |
| `make stop`, `make restart` | Retired | Stop or restart only from the terminal that owns `make run`. | Developer tooling |
| `make clean`, `make clean-weekly`, `make clean-all` | Retired | Commands clean their own unique artifacts; broad deletion is unsupported. | Developer tooling |
| `make clean-docker`, `make clean-docker-all` | Retired | Use `make down`; volume/image deletion needs a separate explicit action. | Developer tooling |

## Safety Rules

- Never signal a process by name or shared port. Record and verify the child PID.
- Never clear global temporary paths, live SQLite WAL/SHM files, or unowned logs.
- Never install packages, start services, or load provider credentials from a validation helper.
- On interruption, terminate only the child process group created by the current validator.
- Run schema changes only through Alembic against an explicit approved database URL.
- Treat provider, recovery, artifact, Docker, and agent-runner work as separate authorized scopes.
