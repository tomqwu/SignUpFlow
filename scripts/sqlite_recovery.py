#!/usr/bin/env python3
"""Create and restore encrypted, WAL-consistent SQLite recovery bundles."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import shutil
import sqlite3
import stat
import sys
import tempfile
import time
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from alembic.script import ScriptDirectory

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_MARKER = ".signupflow-recovery-workspace.json"
BUNDLE_SUFFIX = ".sufbackup"
IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")


class RecoveryError(RuntimeError):
    """Raised when a recovery operation cannot prove its safety contract."""


@dataclass(frozen=True)
class RecoveryWorkspace:
    root: Path
    workspace_id: str

    @property
    def backups(self) -> Path:
        return self.root / "backups"

    @property
    def restores(self) -> Path:
        return self.root / "restores"


@dataclass(frozen=True)
class BackupReceipt:
    bundle_path: Path
    backup_id: str
    plaintext_sha256: str


@dataclass(frozen=True)
class VerifiedBackup:
    bundle_path: Path
    backup_id: str
    plaintext_sha256: str
    created_at: str


@dataclass(frozen=True)
class RestoreReceipt:
    database_path: Path
    receipt_path: Path
    backup_id: str
    plaintext_sha256: str


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _canonical_json(value: dict[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _write_new_file(path: Path, payload: bytes, *, mode: int = 0o600) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
    try:
        with os.fdopen(descriptor, "wb", closefd=False) as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        os.close(descriptor)


def _write_json_new(path: Path, payload: dict[str, Any]) -> None:
    _write_new_file(path, json.dumps(payload, indent=2, sort_keys=True).encode("utf-8") + b"\n")


def _validate_identifier(value: str, label: str) -> str:
    if not IDENTIFIER.fullmatch(value):
        raise RecoveryError(
            f"Unsafe {label}; use 1-64 lowercase letters, digits, dot, dash, or underscore"
        )
    return value


def _reject_symlink(path: Path, label: str) -> None:
    if path.is_symlink():
        raise RecoveryError(f"Refusing {label} symlink: {path}")


def initialize_workspace(path: Path) -> RecoveryWorkspace:
    """Create an empty, marker-bound workspace used only by this recovery tool."""
    path = path.expanduser().absolute()
    if path.exists():
        _reject_symlink(path, "workspace")
        if not path.is_dir():
            raise RecoveryError(f"Workspace is not a directory: {path}")
        if any(path.iterdir()):
            raise RecoveryError(f"Workspace already exists and is not empty: {path}")
    else:
        parent = path.parent
        _reject_symlink(parent, "workspace parent")
        if not parent.is_dir():
            raise RecoveryError(f"Workspace parent does not exist: {parent}")
        path.mkdir(mode=0o700)

    workspace_id = uuid.uuid4().hex
    backups = path / "backups"
    restores = path / "restores"
    backups.mkdir(mode=0o700)
    restores.mkdir(mode=0o700)
    marker = {
        "schema_version": 1,
        "workspace_id": workspace_id,
        "absolute_path": str(path.resolve()),
        "created_at": _utc_now().isoformat(),
    }
    _write_json_new(path / WORKSPACE_MARKER, marker)
    _fsync_directory(path)
    return RecoveryWorkspace(path.resolve(), workspace_id)


def _load_workspace(path: Path) -> RecoveryWorkspace:
    path = path.expanduser().absolute()
    _reject_symlink(path, "workspace")
    if not path.is_dir():
        raise RecoveryError(f"Recovery workspace does not exist: {path}")
    marker_path = path / WORKSPACE_MARKER
    _reject_symlink(marker_path, "workspace marker")
    if not marker_path.is_file():
        raise RecoveryError(f"Recovery workspace marker is missing: {marker_path}")
    try:
        marker = json.loads(marker_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RecoveryError("Recovery workspace marker is invalid") from exc
    if marker.get("schema_version") != 1 or not isinstance(marker.get("workspace_id"), str):
        raise RecoveryError("Recovery workspace marker has an unsupported schema")
    resolved = path.resolve()
    if marker.get("absolute_path") != str(resolved):
        raise RecoveryError("Recovery workspace ownership path no longer matches")
    for child_name in ("backups", "restores"):
        child = resolved / child_name
        _reject_symlink(child, f"workspace {child_name}")
        if not child.is_dir():
            raise RecoveryError(f"Recovery workspace {child_name} directory is missing")
    return RecoveryWorkspace(resolved, marker["workspace_id"])


def generate_key(path: Path) -> Path:
    """Write a new raw 256-bit AES key with owner-only permissions."""
    path = path.expanduser().absolute()
    _reject_symlink(path, "key")
    if path.exists():
        raise RecoveryError(f"Key path already exists: {path}")
    if not path.parent.is_dir():
        raise RecoveryError(f"Key parent does not exist: {path.parent}")
    _write_new_file(path, AESGCM.generate_key(bit_length=256), mode=0o600)
    _fsync_directory(path.parent)
    return path


def _is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _load_key(path: Path, workspace: RecoveryWorkspace | None = None) -> bytes:
    path = path.expanduser().absolute()
    _reject_symlink(path, "key")
    if not path.is_file():
        raise RecoveryError(f"Key file does not exist: {path}")
    file_stat = path.stat()
    mode = stat.S_IMODE(file_stat.st_mode)
    if mode & 0o077:
        raise RecoveryError("Key file permissions must not grant group or other access")
    if hasattr(os, "getuid") and file_stat.st_uid != os.getuid():
        raise RecoveryError("Key file must be owned by the current user")
    resolved = path.resolve()
    if workspace is not None and _is_within(resolved, workspace.root):
        raise RecoveryError("Key file must remain outside the recovery workspace")
    key = path.read_bytes()
    if len(key) != 32:
        raise RecoveryError("Key file must contain exactly 32 raw bytes")
    return key


def _current_migration_heads() -> list[str]:
    script = ScriptDirectory(str(ROOT / "alembic"))
    heads = sorted(script.get_heads())
    if not heads:
        raise RecoveryError("No local Alembic migration head is available")
    return heads


def _open_sqlite_read_only(path: Path) -> sqlite3.Connection:
    uri = f"file:{quote(str(path.resolve()), safe='/')}?mode=ro"
    return sqlite3.connect(uri, uri=True)


def _validate_database(path: Path, expected_heads: list[str]) -> None:
    try:
        with _open_sqlite_read_only(path) as connection:
            integrity = connection.execute("PRAGMA integrity_check").fetchone()
            if integrity != ("ok",):
                raise RecoveryError("SQLite integrity verification failed")
            foreign_keys = connection.execute("PRAGMA foreign_key_check").fetchall()
            if foreign_keys:
                raise RecoveryError("SQLite foreign-key verification failed")
            heads = sorted(
                row[0] for row in connection.execute("SELECT version_num FROM alembic_version")
            )
    except RecoveryError:
        raise
    except sqlite3.Error as exc:
        raise RecoveryError("SQLite schema verification failed") from exc
    if heads != expected_heads:
        raise RecoveryError(
            f"SQLite migration head mismatch; expected {expected_heads}, found {heads}"
        )


def _validate_source(path: Path) -> Path:
    path = path.expanduser().absolute()
    _reject_symlink(path, "source database")
    if not path.is_file():
        raise RecoveryError(f"Source database does not exist: {path}")
    return path


def _snapshot_database(source: Path, destination: Path) -> None:
    source_connection = _open_sqlite_read_only(source)
    destination_connection = sqlite3.connect(destination)
    try:
        source_connection.backup(destination_connection)
        destination_connection.commit()
        destination_connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        journal_mode = destination_connection.execute("PRAGMA journal_mode=DELETE").fetchone()
        if journal_mode != ("delete",):
            raise RecoveryError("SQLite snapshot could not be normalized to a single file")
    except sqlite3.Error as exc:
        raise RecoveryError("SQLite consistent snapshot failed") from exc
    finally:
        destination_connection.close()
        source_connection.close()


def _encrypt_snapshot(snapshot: Path, key: bytes, nonce: bytes, aad: bytes) -> bytes:
    return AESGCM(key).encrypt(nonce, snapshot.read_bytes(), aad)


def _metadata_core(
    *,
    backup_id: str,
    created_at: str,
    workspace_id: str,
    migration_heads: list[str],
    nonce: bytes,
    plaintext_size: int,
    plaintext_sha256: str,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "backup_id": backup_id,
        "created_at": created_at,
        "workspace_id": workspace_id,
        "database": {
            "engine": "sqlite",
            "alembic_heads": migration_heads,
            "integrity_check": "ok",
        },
        "encryption": {
            "algorithm": "AES-256-GCM",
            "nonce_base64": base64.b64encode(nonce).decode("ascii"),
        },
        "payload": {
            "filename": "payload.bin",
            "plaintext_size": plaintext_size,
            "plaintext_sha256": plaintext_sha256,
        },
    }


def _bundle_path(workspace: RecoveryWorkspace, name: str) -> Path:
    return workspace.backups / f"{_validate_identifier(name, 'backup name')}{BUNDLE_SUFFIX}"


def create_backup(
    workspace_path: Path,
    source_path: Path,
    key_path: Path,
    backup_name: str,
) -> BackupReceipt:
    """Create one encrypted bundle from a consistent SQLite backup API snapshot."""
    workspace = _load_workspace(workspace_path)
    source = _validate_source(source_path)
    key = _load_key(key_path, workspace)
    final_bundle = _bundle_path(workspace, backup_name)
    _reject_symlink(final_bundle, "backup bundle")
    if final_bundle.exists():
        raise RecoveryError(f"Backup bundle already exists: {final_bundle}")

    temp_bundle = Path(
        tempfile.mkdtemp(prefix=f".{backup_name}.", suffix=".tmp", dir=workspace.backups)
    )
    snapshot = temp_bundle / "snapshot.sqlite"
    try:
        _snapshot_database(source, snapshot)
        migration_heads = _current_migration_heads()
        _validate_database(snapshot, migration_heads)
        plaintext = snapshot.read_bytes()
        backup_id = uuid.uuid4().hex
        created_at = _utc_now().isoformat()
        nonce = os.urandom(12)
        plaintext_sha256 = _sha256(plaintext)
        core = _metadata_core(
            backup_id=backup_id,
            created_at=created_at,
            workspace_id=workspace.workspace_id,
            migration_heads=migration_heads,
            nonce=nonce,
            plaintext_size=len(plaintext),
            plaintext_sha256=plaintext_sha256,
        )
        aad = _canonical_json(core)
        ciphertext = _encrypt_snapshot(snapshot, key, nonce, aad)
        metadata = {
            **core,
            "authenticated_metadata_sha256": _sha256(aad),
            "payload": {
                **core["payload"],
                "ciphertext_size": len(ciphertext),
                "ciphertext_sha256": _sha256(ciphertext),
            },
        }
        snapshot.unlink()
        _write_new_file(temp_bundle / "payload.bin", ciphertext)
        _write_json_new(temp_bundle / "metadata.json", metadata)
        _fsync_directory(temp_bundle)
        if final_bundle.exists():
            raise RecoveryError(f"Backup bundle already exists: {final_bundle}")
        os.replace(temp_bundle, final_bundle)
        _fsync_directory(workspace.backups)
        return BackupReceipt(final_bundle, backup_id, plaintext_sha256)
    except BaseException:
        if temp_bundle.exists():
            shutil.rmtree(temp_bundle)
        raise


def _validate_bundle_path(workspace: RecoveryWorkspace, bundle_path: Path) -> Path:
    bundle_path = bundle_path.expanduser().absolute()
    _reject_symlink(bundle_path, "backup bundle")
    if bundle_path.parent.resolve() != workspace.backups:
        raise RecoveryError("Backup bundle must be a direct child of the owned workspace")
    if not bundle_path.is_dir() or not bundle_path.name.endswith(BUNDLE_SUFFIX):
        raise RecoveryError(f"Backup bundle does not exist: {bundle_path}")
    return bundle_path


def _read_bundle(
    workspace: RecoveryWorkspace, bundle_path: Path, key: bytes
) -> tuple[bytes, dict[str, Any]]:
    bundle = _validate_bundle_path(workspace, bundle_path)
    metadata_path = bundle / "metadata.json"
    payload_path = bundle / "payload.bin"
    try:
        members = {path.name for path in bundle.iterdir()}
    except OSError as exc:
        raise RecoveryError("Backup verification failed: bundle cannot be read") from exc
    if members != {"metadata.json", "payload.bin"}:
        raise RecoveryError("Backup verification failed: bundle has unexpected members")
    for path, label in ((metadata_path, "metadata"), (payload_path, "payload")):
        _reject_symlink(path, f"backup {label}")
        if not path.is_file():
            raise RecoveryError(f"Backup {label} is missing")
    try:
        metadata: dict[str, Any] = json.loads(metadata_path.read_text(encoding="utf-8"))
        nonce = base64.b64decode(metadata["encryption"]["nonce_base64"], validate=True)
        payload = payload_path.read_bytes()
        backup_id = _validate_identifier(metadata["backup_id"], "backup id")
        created_at = metadata["created_at"]
        parsed_created_at = datetime.fromisoformat(created_at)
        if parsed_created_at.tzinfo is None or parsed_created_at.utcoffset() is None:
            raise ValueError("backup timestamp must include a UTC offset")
        migration_heads = metadata["database"]["alembic_heads"]
        if not isinstance(migration_heads, list) or not all(
            isinstance(head, str) for head in migration_heads
        ):
            raise TypeError("migration heads must be a string list")
        core = _metadata_core(
            backup_id=backup_id,
            created_at=created_at,
            workspace_id=metadata["workspace_id"],
            migration_heads=migration_heads,
            nonce=nonce,
            plaintext_size=metadata["payload"]["plaintext_size"],
            plaintext_sha256=metadata["payload"]["plaintext_sha256"],
        )
    except (KeyError, TypeError, ValueError, OSError, json.JSONDecodeError) as exc:
        raise RecoveryError("Backup verification failed: malformed metadata") from exc
    aad = _canonical_json(core)
    expected_heads = _current_migration_heads()
    checks = (
        metadata.get("schema_version") == 1,
        metadata.get("workspace_id") == workspace.workspace_id,
        metadata.get("database", {}).get("engine") == "sqlite",
        metadata.get("database", {}).get("integrity_check") == "ok",
        metadata.get("encryption", {}).get("algorithm") == "AES-256-GCM",
        metadata.get("authenticated_metadata_sha256") == _sha256(aad),
        metadata.get("payload", {}).get("filename") == "payload.bin",
        metadata.get("payload", {}).get("ciphertext_size") == len(payload),
        metadata.get("payload", {}).get("ciphertext_sha256") == _sha256(payload),
        core["database"]["alembic_heads"] == expected_heads,
        len(nonce) == 12,
    )
    if not all(checks):
        raise RecoveryError("Backup verification failed: metadata or checksum mismatch")
    try:
        plaintext = AESGCM(key).decrypt(nonce, payload, aad)
    except (InvalidTag, ValueError) as exc:
        raise RecoveryError("Backup verification failed: authentication failed") from exc
    if (
        len(plaintext) != core["payload"]["plaintext_size"]
        or _sha256(plaintext) != core["payload"]["plaintext_sha256"]
    ):
        raise RecoveryError("Backup verification failed: plaintext checksum mismatch")
    return plaintext, metadata


def _verify_plaintext(workspace: RecoveryWorkspace, plaintext: bytes, heads: list[str]) -> None:
    descriptor, raw_path = tempfile.mkstemp(prefix=".verify-", suffix=".sqlite", dir=workspace.root)
    path = Path(raw_path)
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(plaintext)
            stream.flush()
            os.fsync(stream.fileno())
        _validate_database(path, heads)
    finally:
        path.unlink(missing_ok=True)


def verify_backup(workspace_path: Path, bundle_path: Path, key_path: Path) -> VerifiedBackup:
    """Authenticate, decrypt, checksum, and integrity-check a recovery bundle."""
    workspace = _load_workspace(workspace_path)
    key = _load_key(key_path, workspace)
    plaintext, metadata = _read_bundle(workspace, bundle_path, key)
    heads = metadata["database"]["alembic_heads"]
    _verify_plaintext(workspace, plaintext, heads)
    return VerifiedBackup(
        bundle_path=bundle_path.expanduser().absolute(),
        backup_id=metadata["backup_id"],
        plaintext_sha256=metadata["payload"]["plaintext_sha256"],
        created_at=metadata["created_at"],
    )


def _restore_paths(workspace: RecoveryWorkspace, restore_name: str) -> tuple[Path, Path]:
    name = _validate_identifier(restore_name, "restore name")
    return (
        workspace.restores / f"{name}.sqlite",
        workspace.restores / f"{name}.restore.json",
    )


def restore_backup(
    workspace_path: Path,
    bundle_path: Path,
    key_path: Path,
    restore_name: str,
) -> RestoreReceipt:
    """Restore a verified bundle to a brand-new isolated database file."""
    started = time.monotonic()
    workspace = _load_workspace(workspace_path)
    key = _load_key(key_path, workspace)
    target, receipt_path = _restore_paths(workspace, restore_name)
    for path, label in ((target, "restore target"), (receipt_path, "restore receipt")):
        _reject_symlink(path, label)
        if path.exists():
            raise RecoveryError(f"{label.capitalize()} already exists: {path}")

    plaintext, metadata = _read_bundle(workspace, bundle_path, key)
    heads = metadata["database"]["alembic_heads"]
    descriptor, raw_temp = tempfile.mkstemp(
        prefix=f".{restore_name}.", suffix=".tmp", dir=workspace.restores
    )
    temp_target = Path(raw_temp)
    published = False
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(plaintext)
            stream.flush()
            os.fsync(stream.fileno())
        _validate_database(temp_target, heads)
        try:
            os.link(temp_target, target, follow_symlinks=False)
        except FileExistsError as exc:
            raise RecoveryError(f"Restore target already exists: {target}") from exc
        published = True
        temp_target.unlink()
        _fsync_directory(workspace.restores)

        restored_at = _utc_now()
        created_at = datetime.fromisoformat(metadata["created_at"])
        receipt = {
            "schema_version": 1,
            "backup_id": metadata["backup_id"],
            "backup_created_at": metadata["created_at"],
            "restored_at": restored_at.isoformat(),
            "restore_duration_ms": round((time.monotonic() - started) * 1000, 3),
            "recovery_point_age_seconds": round((restored_at - created_at).total_seconds(), 3),
            "database_filename": target.name,
            "plaintext_sha256": metadata["payload"]["plaintext_sha256"],
            "alembic_heads": heads,
            "state": "isolated_no_cutover",
            "outbound_delivery": "not_started_by_recovery_tool",
        }
        _write_json_new(receipt_path, receipt)
        _fsync_directory(workspace.restores)
        return RestoreReceipt(
            target,
            receipt_path,
            metadata["backup_id"],
            metadata["payload"]["plaintext_sha256"],
        )
    except BaseException:
        temp_target.unlink(missing_ok=True)
        if published and not receipt_path.exists():
            # The target is already a complete, verified snapshot. Preserve it for
            # operator inspection rather than deleting data after an interruption.
            pass
        raise


def _plan_backup(
    workspace_path: Path, source_path: Path, key_path: Path, name: str
) -> dict[str, Any]:
    workspace = _load_workspace(workspace_path)
    source = _validate_source(source_path)
    _load_key(key_path, workspace)
    target = _bundle_path(workspace, name)
    if target.exists() or target.is_symlink():
        raise RecoveryError(f"Backup bundle already exists: {target}")
    return {
        "operation": "backup",
        "source": str(source),
        "target": str(target),
        "mutates": False,
        "cutover": False,
    }


def _plan_restore(
    workspace_path: Path,
    bundle_path: Path,
    key_path: Path,
    name: str,
) -> dict[str, Any]:
    workspace = _load_workspace(workspace_path)
    target, receipt = _restore_paths(workspace, name)
    if target.exists() or target.is_symlink() or receipt.exists() or receipt.is_symlink():
        raise RecoveryError("Restore target or receipt already exists")
    verified = verify_backup(workspace.root, bundle_path, key_path)
    return {
        "operation": "restore",
        "backup_id": verified.backup_id,
        "source": str(verified.bundle_path),
        "target": str(target),
        "mutates": False,
        "cutover": False,
    }


def _print_json(value: dict[str, Any]) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init-workspace")
    init.add_argument("workspace", type=Path)

    key = commands.add_parser("generate-key")
    key.add_argument("path", type=Path)

    backup = commands.add_parser("backup")
    backup.add_argument("--workspace", type=Path, required=True)
    backup.add_argument("--source", type=Path, required=True)
    backup.add_argument("--key-file", type=Path, required=True)
    backup.add_argument("--name", required=True)
    backup.add_argument("--dry-run", action="store_true")

    verify = commands.add_parser("verify")
    verify.add_argument("--workspace", type=Path, required=True)
    verify.add_argument("--bundle", type=Path, required=True)
    verify.add_argument("--key-file", type=Path, required=True)

    restore = commands.add_parser("restore")
    restore.add_argument("--workspace", type=Path, required=True)
    restore.add_argument("--bundle", type=Path, required=True)
    restore.add_argument("--key-file", type=Path, required=True)
    restore.add_argument("--name", required=True)
    restore.add_argument("--dry-run", action="store_true")

    args = parser.parse_args(argv)
    try:
        if args.command == "init-workspace":
            workspace = initialize_workspace(args.workspace)
            _print_json({"workspace": str(workspace.root), "workspace_id": workspace.workspace_id})
        elif args.command == "generate-key":
            path = generate_key(args.path)
            _print_json({"key_file": str(path), "permissions": "0600"})
        elif args.command == "backup":
            if args.dry_run:
                _print_json(_plan_backup(args.workspace, args.source, args.key_file, args.name))
            else:
                backup_receipt = create_backup(
                    args.workspace, args.source, args.key_file, args.name
                )
                _print_json(
                    {
                        "bundle": str(backup_receipt.bundle_path),
                        "backup_id": backup_receipt.backup_id,
                        "plaintext_sha256": backup_receipt.plaintext_sha256,
                    }
                )
        elif args.command == "verify":
            verified = verify_backup(args.workspace, args.bundle, args.key_file)
            _print_json(
                {
                    "bundle": str(verified.bundle_path),
                    "backup_id": verified.backup_id,
                    "plaintext_sha256": verified.plaintext_sha256,
                    "created_at": verified.created_at,
                    "verified": True,
                }
            )
        elif args.command == "restore":
            if args.dry_run:
                _print_json(_plan_restore(args.workspace, args.bundle, args.key_file, args.name))
            else:
                restore_receipt = restore_backup(
                    args.workspace, args.bundle, args.key_file, args.name
                )
                _print_json(
                    {
                        "database": str(restore_receipt.database_path),
                        "receipt": str(restore_receipt.receipt_path),
                        "backup_id": restore_receipt.backup_id,
                        "plaintext_sha256": restore_receipt.plaintext_sha256,
                        "cutover": False,
                    }
                )
        else:  # pragma: no cover - argparse enforces the command set.
            parser.error("unsupported command")
    except RecoveryError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"ERROR: operating system failure: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print(
            "Interrupted; inspect the owned workspace for complete output and receipt state.",
            file=sys.stderr,
        )
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
