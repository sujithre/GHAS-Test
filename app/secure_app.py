"""
GHAS demo - the remediated versions of the flaws in vulnerable_app.py.

Use this file in the demo to contrast "before and after" once CodeQL has
raised its alerts. Each function mirrors a vulnerable route and shows the
pattern that makes the alert go away.
"""

import hashlib
import html
import os
import secrets
import sqlite3
import subprocess
from pathlib import Path
from urllib.parse import urlparse

import requests
import yaml

ALLOWED_FILE_ROOT = Path("/var/demo/files").resolve()
ALLOWED_FETCH_HOSTS = {"api.partner.example.com"}


def lookup_user(connection: sqlite3.Connection, username: str):
    """Fix for py/sql-injection: parameterised query.

    The driver sends the value separately from the statement, so it can never
    be parsed as SQL.
    """
    cursor = connection.cursor()
    cursor.execute("SELECT id, email FROM users WHERE username = ?", (username,))
    return cursor.fetchall()


def ping_host(host: str) -> str:
    """Fix for py/command-line-injection: no shell, validated argument list."""
    if not all(part.isdigit() and 0 <= int(part) <= 255 for part in host.split(".")):
        raise ValueError("host must be a dotted-quad IPv4 address")

    completed = subprocess.run(
        ["ping", "-c", "1", host],
        shell=False,
        capture_output=True,
        check=False,
        timeout=10,
    )
    return completed.stdout.decode("utf-8", errors="replace")


def greet(name: str) -> str:
    """Fix for py/reflective-xss: escape before interpolating into HTML."""
    return f"<h1>Hello, {html.escape(name)}!</h1>"


def resolve_download(filename: str) -> Path:
    """Fix for py/path-injection: resolve, then confirm containment."""
    candidate = (ALLOWED_FILE_ROOT / filename).resolve()
    if not candidate.is_relative_to(ALLOWED_FILE_ROOT):
        raise ValueError("path escapes the allowed directory")
    return candidate


def fetch_url(url: str) -> str:
    """Fix for py/full-ssrf: allowlist the destination host."""
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_FETCH_HOSTS:
        raise ValueError("destination is not on the allowlist")
    return requests.get(url, timeout=10).text


def load_config(document: bytes):
    """Fix for py/unsafe-deserialization: SafeLoader builds plain data only."""
    return yaml.safe_load(document)


def hash_password(password: str, salt: bytes | None = None) -> tuple[bytes, bytes]:
    """Fix for py/weak-sensitive-data-hashing: slow, salted KDF.

    Nothing about the password is logged.
    """
    salt = salt or os.urandom(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return digest, salt


def generate_reset_token() -> str:
    """Fix for py/insecure-randomness: cryptographically secure source."""
    return secrets.token_hex(32)


def get_api_key() -> str:
    """Fix for py/hardcoded-credentials: read the value from the environment.

    In production this comes from a secret manager such as Azure Key Vault or
    GitHub Actions secrets, never from source control.
    """
    api_key = os.environ.get("PARTNER_API_KEY")
    if not api_key:
        raise RuntimeError("PARTNER_API_KEY is not configured")
    return api_key
