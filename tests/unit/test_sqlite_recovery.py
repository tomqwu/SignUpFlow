"""Safety and integrity contracts for the owned SQLite recovery tool."""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path

import pytest

from scripts.sqlite_recovery import (
    RecoveryError,
    create_backup,
    generate_key,
    initialize_workspace,
    main,
    restore_backup,
    verify_backup,
)

CURRENT_HEAD = "f8a1b2c3d4e5"


def _source_database(path: Path, *, revision: str = CURRENT_HEAD) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    assert connection.execute("PRAGMA journal_mode=WAL").fetchone() == ("wal",)
    connection.execute("CREATE TABLE alembic_version (version_num TEXT PRIMARY KEY)")
    connection.execute("INSERT INTO alembic_version VALUES (?)", (revision,))
    connection.execute("CREATE TABLE sentinel (value TEXT NOT NULL)")
    connection.execute("INSERT INTO sentinel VALUES ('main-file')")
    connection.commit()
    connection.execute("INSERT INTO sentinel VALUES ('committed-in-wal')")
    connection.commit()
    assert Path(f"{path}-wal").stat().st_size > 0
    return connection


def _owned_recovery_material(tmp_path: Path) -> tuple[Path, Path]:
    workspace = tmp_path / "recovery"
    key = tmp_path / "recovery.key"
    initialize_workspace(workspace)
    generate_key(key)
    assert key.stat().st_mode & 0o777 == 0o600
    return workspace, key


def test_committed_wal_row_survives_encrypted_backup_and_restore(tmp_path: Path) -> None:
    source = tmp_path / "source.sqlite"
    writer = _source_database(source)
    workspace, key = _owned_recovery_material(tmp_path)
    try:
        backup = create_backup(workspace, source, key, "wal-snapshot")
    finally:
        writer.close()

    metadata = json.loads((backup.bundle_path / "metadata.json").read_text())
    assert metadata["database"]["alembic_heads"] == [CURRENT_HEAD]
    assert metadata["encryption"]["algorithm"] == "AES-256-GCM"
    assert metadata["payload"]["plaintext_sha256"]
    assert metadata["payload"]["ciphertext_sha256"]
    assert "key" not in json.dumps(metadata).lower()
    assert not list(backup.bundle_path.glob("*.sqlite"))

    verified = verify_backup(workspace, backup.bundle_path, key)
    restored = restore_backup(workspace, backup.bundle_path, key, "restored")

    assert verified.plaintext_sha256 == metadata["payload"]["plaintext_sha256"]
    assert restored.database_path == workspace / "restores" / "restored.sqlite"
    assert restored.receipt_path.is_file()
    with sqlite3.connect(restored.database_path) as connection:
        assert connection.execute("PRAGMA integrity_check").fetchone() == ("ok",)
        assert connection.execute("SELECT value FROM sentinel ORDER BY rowid").fetchall() == [
            ("main-file",),
            ("committed-in-wal",),
        ]
        assert connection.execute("SELECT version_num FROM alembic_version").fetchone() == (
            CURRENT_HEAD,
        )


@pytest.mark.parametrize("member", ["payload.bin", "metadata.json"])
def test_corrupt_or_mismatched_bundle_is_rejected_before_target_creation(
    tmp_path: Path, member: str
) -> None:
    source = tmp_path / "source.sqlite"
    writer = _source_database(source)
    workspace, key = _owned_recovery_material(tmp_path)
    try:
        bundle = create_backup(workspace, source, key, "corrupt-me").bundle_path
    finally:
        writer.close()

    path = bundle / member
    if member == "payload.bin":
        payload = bytearray(path.read_bytes())
        payload[len(payload) // 2] ^= 0x01
        path.write_bytes(payload)
    else:
        metadata = json.loads(path.read_text())
        metadata["database"]["alembic_heads"] = ["wrong-head"]
        path.write_text(json.dumps(metadata), encoding="utf-8")

    target = workspace / "restores" / "must-not-exist.sqlite"
    with pytest.raises(RecoveryError, match="verification"):
        restore_backup(workspace, bundle, key, "must-not-exist")
    assert not target.exists()


def test_restore_refuses_existing_target_without_changing_it(tmp_path: Path) -> None:
    source = tmp_path / "source.sqlite"
    writer = _source_database(source)
    workspace, key = _owned_recovery_material(tmp_path)
    try:
        bundle = create_backup(workspace, source, key, "existing-target").bundle_path
    finally:
        writer.close()

    target = workspace / "restores" / "occupied.sqlite"
    target.write_bytes(b"operator-owned sentinel")

    with pytest.raises(RecoveryError, match="already exists"):
        restore_backup(workspace, bundle, key, "occupied")
    assert target.read_bytes() == b"operator-owned sentinel"
    assert not (workspace / "restores" / "occupied.restore.json").exists()


def test_restore_does_not_overwrite_target_created_during_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "source.sqlite"
    writer = _source_database(source)
    workspace, key = _owned_recovery_material(tmp_path)
    try:
        bundle = create_backup(workspace, source, key, "publication-race").bundle_path
    finally:
        writer.close()

    target = workspace / "restores" / "raced.sqlite"
    real_link = os.link

    def publish_after_operator(*args: object, **kwargs: object) -> None:
        target.write_bytes(b"operator-created-during-restore")
        real_link(*args, **kwargs)

    monkeypatch.setattr("scripts.sqlite_recovery.os.link", publish_after_operator)
    with pytest.raises(RecoveryError, match="already exists"):
        restore_backup(workspace, bundle, key, "raced")

    assert target.read_bytes() == b"operator-created-during-restore"
    assert not (workspace / "restores" / "raced.restore.json").exists()


def test_recovery_refuses_symlinks_and_permissive_key_files(tmp_path: Path) -> None:
    source = tmp_path / "source.sqlite"
    writer = _source_database(source)
    workspace, key = _owned_recovery_material(tmp_path)
    source_link = tmp_path / "source-link.sqlite"
    source_link.symlink_to(source)
    try:
        with pytest.raises(RecoveryError, match="symlink"):
            create_backup(workspace, source_link, key, "linked-source")

        os.chmod(key, 0o644)
        with pytest.raises(RecoveryError, match="permissions"):
            create_backup(workspace, source, key, "weak-key")
    finally:
        writer.close()

    assert not list((workspace / "backups").iterdir())


def test_recovery_refuses_key_material_inside_owned_workspace(tmp_path: Path) -> None:
    source = tmp_path / "source.sqlite"
    writer = _source_database(source)
    workspace, _ = _owned_recovery_material(tmp_path)
    nested_key = workspace / "recovery.key"
    generate_key(nested_key)
    try:
        with pytest.raises(RecoveryError, match="outside the recovery workspace"):
            create_backup(workspace, source, nested_key, "embedded-key")
    finally:
        writer.close()

    assert not list((workspace / "backups").iterdir())


def test_wrong_key_and_unexpected_bundle_members_are_rejected(tmp_path: Path) -> None:
    source = tmp_path / "source.sqlite"
    writer = _source_database(source)
    workspace, key = _owned_recovery_material(tmp_path)
    wrong_key = tmp_path / "wrong.key"
    generate_key(wrong_key)
    try:
        bundle = create_backup(workspace, source, key, "strict-bundle").bundle_path
    finally:
        writer.close()

    with pytest.raises(RecoveryError, match="authentication failed"):
        verify_backup(workspace, bundle, wrong_key)

    (bundle / "operator-note.txt").write_text("unexpected", encoding="utf-8")
    with pytest.raises(RecoveryError, match="unexpected members"):
        verify_backup(workspace, bundle, key)


def test_documented_cli_sequence_supports_dry_run_backup_verify_and_restore(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    source = tmp_path / "source.sqlite"
    writer = _source_database(source)
    workspace = tmp_path / "recovery"
    key = tmp_path / "recovery.key"
    try:
        assert main(["init-workspace", str(workspace)]) == 0
        assert main(["generate-key", str(key)]) == 0
        assert (
            main(
                [
                    "backup",
                    "--workspace",
                    str(workspace),
                    "--source",
                    str(source),
                    "--key-file",
                    str(key),
                    "--name",
                    "cli-sequence",
                    "--dry-run",
                ]
            )
            == 0
        )
        assert not (workspace / "backups" / "cli-sequence.sufbackup").exists()
        assert (
            main(
                [
                    "backup",
                    "--workspace",
                    str(workspace),
                    "--source",
                    str(source),
                    "--key-file",
                    str(key),
                    "--name",
                    "cli-sequence",
                ]
            )
            == 0
        )
    finally:
        writer.close()

    bundle = workspace / "backups" / "cli-sequence.sufbackup"
    shared = ["--workspace", str(workspace), "--bundle", str(bundle), "--key-file", str(key)]
    assert main(["verify", *shared]) == 0
    assert main(["restore", *shared, "--name", "cli-restore", "--dry-run"]) == 0
    assert not (workspace / "restores" / "cli-restore.sqlite").exists()
    assert main(["restore", *shared, "--name", "cli-restore"]) == 0

    output = capsys.readouterr().out
    assert '"mutates": false' in output
    assert '"verified": true' in output
    assert '"cutover": false' in output
    assert (workspace / "restores" / "cli-restore.sqlite").is_file()


def test_wrong_schema_is_rejected_before_bundle_creation(tmp_path: Path) -> None:
    source = tmp_path / "source.sqlite"
    writer = _source_database(source, revision="legacy-head")
    workspace, key = _owned_recovery_material(tmp_path)
    try:
        with pytest.raises(RecoveryError, match="migration head"):
            create_backup(workspace, source, key, "wrong-schema")
    finally:
        writer.close()

    assert not (workspace / "backups" / "wrong-schema.sufbackup").exists()


def test_interrupted_backup_removes_only_its_temporary_artifacts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "source.sqlite"
    writer = _source_database(source)
    workspace, key = _owned_recovery_material(tmp_path)
    unrelated = workspace / "backups" / "operator-note.txt"
    unrelated.write_text("keep", encoding="utf-8")

    def interrupt(*args: object, **kwargs: object) -> bytes:
        raise KeyboardInterrupt

    monkeypatch.setattr("scripts.sqlite_recovery._encrypt_snapshot", interrupt)
    try:
        with pytest.raises(KeyboardInterrupt):
            create_backup(workspace, source, key, "interrupted")
    finally:
        writer.close()

    assert unrelated.read_text(encoding="utf-8") == "keep"
    assert sorted(path.name for path in (workspace / "backups").iterdir()) == ["operator-note.txt"]
