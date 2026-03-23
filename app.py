import hashlib
import os
import requests
from flask import Flask, Blueprint, render_template, request

app = Flask(__name__)

HIBP_USER_AGENT = os.getenv("HIBP_USER_AGENT", "ryanhenson-pwned-password")
PWNED_BASE_URL = "https://api.pwnedpasswords.com/range/"

# Health check for ALB
@app.route("/health")
def health():
    return {"status": "ok"}, 200

bp = Blueprint("pwned_password", __name__, url_prefix="/tools/pwned-password")

@bp.route("/", methods=["GET"], strict_slashes=False)
def home():
    return render_template("index.html")

@bp.route("/check", methods=["POST"])
def check_password():
    password = request.form.get("password", "")

    if not password:
        return render_template("index.html", error="Please enter a password.")

    # Hash the password with SHA-1, split into prefix + suffix
    sha1 = hashlib.sha1(password.encode("utf-8"), usedforsecurity=False).hexdigest().upper()
    prefix = sha1[:5]
    suffix = sha1[5:]

    # Send only the prefix to HIBP — the full hash never leaves this server
    headers = {
        "user-agent": HIBP_USER_AGENT,
        "Add-Padding": "true",
    }

    try:
        response = requests.get(f"{PWNED_BASE_URL}{prefix}", headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        return render_template("index.html", error=f"Could not reach HIBP API: {e}")

    # Each line is SUFFIX:COUNT — padding entries have count 0
    count = 0
    for line in response.text.splitlines():
        line_suffix, _, line_count = line.partition(":")
        if line_suffix == suffix and int(line_count) > 0:
            count = int(line_count)
            break

    return render_template("index.html", checked=True, count=count)

app.register_blueprint(bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)  # nosec B104
