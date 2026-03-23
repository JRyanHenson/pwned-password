# pwned-password

A cybersecurity micro-app that checks passwords against the [Have I Been Pwned](https://haveibeenpwned.com) Pwned Passwords API. Deployed as part of the [ryanhenson.io](https://ryanhenson.io/tools/pwned-password/) platform.

Live at: **[ryanhenson.io/tools/pwned-password/](https://ryanhenson.io/tools/pwned-password/)**

## Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, Flask |
| Server | Gunicorn |
| Container | Docker (multi-stage, non-root) |
| Hosting | AWS ECS Fargate |
| Registry | Amazon ECR |
| CI/CD | GitHub Actions |

## How It Works

The app implements [k-anonymity](https://haveibeenpwned.com/API/v3#PwnedPasswords) to check passwords without ever exposing the full password or its hash:

1. The password is hashed with SHA-1 on the server
2. Only the first 5 characters of the hash are sent to the HIBP Pwned Passwords API
3. HIBP returns all hash suffixes matching that prefix (with `Add-Padding: true` to prevent traffic analysis)
4. The full hash is matched locally — nothing sensitive leaves the server

No API key is required. The Pwned Passwords endpoint is free and open.

All routing is prefixed under `/tools/pwned-password/` so the ALB on the main platform can route traffic to this service using path-based rules.

## Local Development

**Requirements:** Python 3.12

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

flask --app app run -p 8001
```

Open [http://localhost:8001/tools/pwned-password/](http://localhost:8001/tools/pwned-password/).

## Running Tests

```bash
pytest -v
```

## Docker

```bash
# Build
docker build -t pwned-password:local .

# Run
docker run -p 8001:8001 pwned-password:local
```

## Security Controls

- Password is never logged, stored, or transmitted — only a 5-character hash prefix is sent to HIBP
- `Add-Padding: true` header prevents traffic analysis of API responses
- Container runs as non-root user (`appuser`, uid 1001)
- Multi-stage Docker build — pip and build tools do not exist in the final image
- `.dockerignore` excludes test files, virtual environment, and git history from the build context
- No API key or secrets required

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `HIBP_USER_AGENT` | No | User-agent string sent to HIBP API (default: `ryanhenson-pwned-password`) |
