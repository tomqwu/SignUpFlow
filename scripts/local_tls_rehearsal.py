"""Owned loopback TLS termination for production-artifact rehearsal."""

from __future__ import annotations

import hashlib
import http.client
import ipaddress
import os
import socket
import ssl
import threading
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import TracebackType
from typing import Any

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

_HOP_BY_HOP_HEADERS = frozenset(
    {
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailer",
        "transfer-encoding",
        "upgrade",
    }
)


@dataclass(frozen=True)
class TLSMaterial:
    """Short-lived certificate paths for one local rehearsal."""

    ca_certificate: Path
    server_certificate: Path
    server_key: Path
    ca_sha256: str
    hostname: str

    @classmethod
    def create(cls, directory: Path, *, hostname: str) -> TLSMaterial:
        """Create a one-day CA and loopback server certificate."""
        directory.mkdir(parents=True, exist_ok=True)
        now = datetime.now(UTC)
        ca_key = ec.generate_private_key(ec.SECP256R1())
        ca_name = x509.Name(
            [x509.NameAttribute(NameOID.COMMON_NAME, "SignUpFlow local rehearsal CA")]
        )
        ca_certificate = (
            x509.CertificateBuilder()
            .subject_name(ca_name)
            .issuer_name(ca_name)
            .public_key(ca_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now - timedelta(minutes=1))
            .not_valid_after(now + timedelta(days=1))
            .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
            .add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    content_commitment=False,
                    key_encipherment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    key_cert_sign=True,
                    crl_sign=True,
                    encipher_only=False,
                    decipher_only=False,
                ),
                critical=True,
            )
            .sign(ca_key, hashes.SHA256())
        )

        server_key = ec.generate_private_key(ec.SECP256R1())
        server_name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, hostname)])
        server_certificate = (
            x509.CertificateBuilder()
            .subject_name(server_name)
            .issuer_name(ca_name)
            .public_key(server_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now - timedelta(minutes=1))
            .not_valid_after(now + timedelta(hours=1))
            .add_extension(
                x509.SubjectAlternativeName(
                    [
                        x509.DNSName(hostname),
                        x509.IPAddress(ipaddress.ip_address("127.0.0.1")),
                    ]
                ),
                critical=False,
            )
            .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
            .add_extension(
                x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]),
                critical=False,
            )
            .sign(ca_key, hashes.SHA256())
        )

        ca_path = directory / "local-rehearsal-ca.pem"
        certificate_path = directory / "local-rehearsal-server.pem"
        key_path = directory / "local-rehearsal-server.key"
        ca_bytes = ca_certificate.public_bytes(serialization.Encoding.PEM)
        ca_path.write_bytes(ca_bytes)
        certificate_path.write_bytes(server_certificate.public_bytes(serialization.Encoding.PEM))
        key_path.write_bytes(
            server_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )
        os.chmod(key_path, 0o600)
        return cls(
            ca_certificate=ca_path,
            server_certificate=certificate_path,
            server_key=key_path,
            ca_sha256=hashlib.sha256(ca_bytes).hexdigest(),
            hostname=hostname,
        )


def verify_cookie_security(
    set_cookie_headers: list[str],
    cookie_name: str,
    *,
    http_only: bool,
) -> dict[str, Any]:
    """Require the production attributes for one browser cookie."""
    matches = [
        value
        for value in set_cookie_headers
        if value.split("=", 1)[0].strip().lower() == cookie_name.lower()
    ]
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one {cookie_name} Set-Cookie header")
    attributes = [part.strip().lower() for part in matches[0].split(";")[1:]]
    secure = "secure" in attributes
    observed_http_only = "httponly" in attributes
    same_site = next(
        (value.split("=", 1)[1] for value in attributes if value.startswith("samesite=")),
        None,
    )
    path = next(
        (value.split("=", 1)[1] for value in attributes if value.startswith("path=")),
        None,
    )
    if not secure or observed_http_only != http_only or same_site != "lax" or path != "/":
        raise RuntimeError(f"{cookie_name} does not have the required production attributes")
    return {
        "secure": secure,
        "http_only": observed_http_only,
        "same_site": same_site,
        "path": path,
    }


class LoopbackTLSProxy:
    """Terminate HTTPS on loopback and proxy to one loopback HTTP port."""

    def __init__(self, *, backend_port: int, material: TLSMaterial) -> None:
        if not 1 <= backend_port <= 65535:
            raise ValueError("TLS rehearsal backend port must be valid")
        self.backend_port = backend_port
        self.material = material
        self._server: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None

    @property
    def port(self) -> int:
        if self._server is None:
            raise RuntimeError("TLS rehearsal proxy is not running")
        return int(self._server.server_address[1])

    @property
    def url(self) -> str:
        return f"https://127.0.0.1:{self.port}"

    def __enter__(self) -> LoopbackTLSProxy:
        backend_port = self.backend_port
        hostname = self.material.hostname

        class ProxyHandler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def _proxy(self) -> None:
                length = int(self.headers.get("Content-Length", "0"))
                body = self.rfile.read(length) if length else None
                headers = {
                    key: value
                    for key, value in self.headers.items()
                    if key.lower() not in _HOP_BY_HOP_HEADERS
                    and key.lower() not in {"content-length", "host", "x-forwarded-for"}
                }
                headers.update(
                    {
                        "Host": hostname,
                        "X-Forwarded-For": "127.0.0.1",
                        "X-Forwarded-Host": hostname,
                        "X-Forwarded-Proto": "https",
                    }
                )
                connection = http.client.HTTPConnection("127.0.0.1", backend_port, timeout=30)
                try:
                    connection.request(self.command, self.path, body=body, headers=headers)
                    response = connection.getresponse()
                    payload = response.read()
                    self.send_response(response.status, response.reason)
                    for key, value in response.getheaders():
                        if key.lower() not in _HOP_BY_HOP_HEADERS | {"content-length"}:
                            self.send_header(key, value)
                    self.send_header("Content-Length", str(len(payload)))
                    self.end_headers()
                    self.wfile.write(payload)
                finally:
                    connection.close()

            def do_DELETE(self) -> None:  # noqa: N802
                self._proxy()

            def do_GET(self) -> None:  # noqa: N802
                self._proxy()

            def do_HEAD(self) -> None:  # noqa: N802
                self._proxy()

            def do_PATCH(self) -> None:  # noqa: N802
                self._proxy()

            def do_POST(self) -> None:  # noqa: N802
                self._proxy()

            def do_PUT(self) -> None:  # noqa: N802
                self._proxy()

            def log_message(self, format: str, *args: object) -> None:
                return

        server = ThreadingHTTPServer(("127.0.0.1", 0), ProxyHandler)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.load_cert_chain(
            certfile=self.material.server_certificate,
            keyfile=self.material.server_key,
        )
        server.socket = context.wrap_socket(server.socket, server_side=True)
        self._server = server
        self._thread = threading.Thread(target=server.serve_forever, daemon=True)
        self._thread.start()
        return self

    def negotiated_protocol(self) -> dict[str, str]:
        """Perform a verified handshake and report its TLS version and cipher."""
        context = ssl.create_default_context(cafile=self.material.ca_certificate)
        with socket.create_connection(("127.0.0.1", self.port), timeout=10) as raw_socket:
            with context.wrap_socket(
                raw_socket,
                server_hostname=self.material.hostname,
            ) as tls_socket:
                cipher = tls_socket.cipher()
                return {
                    "version": tls_socket.version() or "unknown",
                    "cipher": cipher[0] if cipher else "unknown",
                }

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()
        if self._thread is not None:
            self._thread.join(timeout=5)
        self._server = None
        self._thread = None
