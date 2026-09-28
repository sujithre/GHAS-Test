"""
GHAS demo application - INTENTIONALLY VULNERABLE.

Every route below contains a deliberate flaw so that GitHub Advanced Security
code scanning (CodeQL) raises an alert against it. Do not deploy this anywhere.
"""

import hashlib
import logging
import os
import pickle
import sqlite3
import subprocess

import requests
import yaml
from flask import Flask, request, send_file

app = Flask(__name__)
logger = logging.getLogger(__name__)

DB_PATH = "demo.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


@app.route("/user")
def lookup_user():
    """CodeQL: py/sql-injection

    The username is concatenated straight into the SQL text, so a value like
    ' OR '1'='1 changes the meaning of the query.
    """
    username = request.args.get("username", "")
    connection = get_connection()
    cursor = connection.cursor()

    query = "SELECT id, email FROM users WHERE username = '" + username + "'"
    cursor.execute(query)

    return {"results": cursor.fetchall()}


@app.route("/ping")
def ping_host():
    """CodeQL: py/command-line-injection

    Running through a shell means a host value of "8.8.8.8; rm -rf /" executes
    two commands instead of one.
    """
    host = request.args.get("host", "127.0.0.1")
    output = subprocess.check_output("ping -c 1 " + host, shell=True)
    return output.decode("utf-8", errors="replace")


@app.route("/backup")
def run_backup():
    """CodeQL: py/command-line-injection"""
    target = request.args.get("target", "/tmp")
    os.system("tar -czf /tmp/backup.tar.gz " + target)
    return "backup started"


@app.route("/greet")
def greet():
    """CodeQL: py/reflective-xss

    Untrusted input is echoed into the HTML response without escaping.
    """
    name = request.args.get("name", "world")
    return "<h1>Hello, " + name + "!</h1>"


@app.route("/download")
def download_file():
    """CodeQL: py/path-injection

    A filename of ../../etc/passwd escapes the intended directory.
    """
    filename = request.args.get("filename", "readme.txt")
    return send_file(os.path.join("/var/demo/files", filename))


@app.route("/fetch")
def fetch_url():
    """CodeQL: py/full-ssrf

    The server will request any URL the caller supplies, including internal
    metadata endpoints.
    """
    url = request.args.get("url", "")
    response = requests.get(url)
    return response.text


@app.route("/calculate")
def calculate():
    """CodeQL: py/code-injection

    eval on request data is remote code execution.
    """
    expression = request.args.get("expr", "1+1")
    return str(eval(expression))


@app.route("/session", methods=["POST"])
def restore_session():
    """CodeQL: py/unsafe-deserialization

    pickle.loads on attacker-controlled bytes executes arbitrary code.
    """
    blob = request.get_data()
    session = pickle.loads(blob)
    return {"session": str(session)}


@app.route("/config", methods=["POST"])
def load_config():
    """CodeQL: py/unsafe-deserialization

    yaml.load without SafeLoader can instantiate arbitrary Python objects.
    """
    document = request.get_data()
    return {"config": str(yaml.load(document, Loader=yaml.Loader))}


@app.route("/register", methods=["POST"])
def register():
    """CodeQL: py/weak-sensitive-data-hashing and py/clear-text-logging-sensitive-data

    MD5 is unsuitable for password storage, and the password is written to the
    log in clear text.
    """
    password = request.form.get("password", "")
    logger.info("Registering new user with password %s", password)

    digest = hashlib.md5(password.encode()).hexdigest()
    return {"password_hash": digest}


@app.route("/redirect")
def unsafe_redirect():
    """CodeQL: py/url-redirection

    An open redirect lets an attacker send users to a phishing page from a
    link that looks like it belongs to this site.
    """
    from flask import redirect

    return redirect(request.args.get("next", "/"))


if __name__ == "__main__":
    # CodeQL: py/flask-debug - debug mode exposes the Werkzeug console.
    app.run(debug=True, host="0.0.0.0")
