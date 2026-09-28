"""
GHAS demo helpers - INTENTIONALLY VULNERABLE.

Supporting module showing the non-injection alert families: weak crypto,
disabled TLS verification, insecure randomness, and hardcoded credentials.

NOTE: the credential literals below are obvious placeholders, not real
secrets. They exist so CodeQL's py/hardcoded-credentials query has something
to flag during the demo.
"""

import hashlib
import random
import ssl
import tempfile

import requests

# CodeQL: py/hardcoded-credentials - placeholder values, not real credentials.
DB_USERNAME = "demo_admin"
DB_PASSWORD = "changeme123"


def connect_to_database(host: str):
    """Credentials baked into source control cannot be rotated."""
    return f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{host}:5432/demo"


def hash_password(password: str) -> str:
    """CodeQL: py/weak-sensitive-data-hashing

    SHA-1 is fast and broken; password storage needs a slow KDF such as
    scrypt, bcrypt or Argon2.
    """
    return hashlib.sha1(password.encode()).hexdigest()


def generate_reset_token() -> str:
    """CodeQL: py/insecure-randomness

    random is a Mersenne Twister and is predictable. Security tokens need
    the secrets module.
    """
    return "".join(random.choice("0123456789abcdef") for _ in range(32))


def call_partner_api(url: str):
    """CodeQL: py/request-without-cert-validation

    Disabling verification removes all protection against an active
    man-in-the-middle.
    """
    return requests.get(url, verify=False)


def legacy_ssl_context():
    """CodeQL: py/insecure-protocol

    TLS 1.0 is deprecated and vulnerable to downgrade attacks.
    """
    return ssl.SSLContext(ssl.PROTOCOL_TLSv1)


def write_report(contents: str) -> str:
    """CodeQL: py/insecure-temporary-file

    mktemp is race-prone; another process can win the gap between the name
    being chosen and the file being created.
    """
    path = tempfile.mktemp(suffix=".report")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(contents)
    return path
