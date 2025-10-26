# Koyeb Deployment Guide

This guide explains how to deploy the Fieldcraft API to [Koyeb](https://www.koyeb.com/) using the provided `Dockerfile` and `koyeb.yaml` manifest.

## Prerequisites
- Koyeb account with the CLI configured (`brew install koyeb-cli` or see the Koyeb docs).
- Container registry access (Koyeb builds directly from GitHub/GitLab, so no manual push is needed if the repository is connected).
- PostgreSQL instance reachable from Koyeb. You can use a managed database (Neon, RDS, etc.) or the Koyeb PostgreSQL add-on.

## 1. Prepare environment secrets

Create Koyeb secrets for every required environment variable. Replace the placeholder values with production-ready secrets.

```bash
koyeb secret create fieldcraft-database-url --value 'postgresql://user:pass@host:5432/db'
koyeb secret create fieldcraft-secret-key --value 'openssl rand -hex 32'
koyeb secret create fieldcraft-anthropic-api-key --value 'sk-ant-...'
koyeb secret create fieldcraft-openai-api-key --value 'sk-...'
koyeb secret create fieldcraft-searchapi-key --value 'your-searchapi-key'  # optional if not using SearchAPI
```

## 2. Configure the deployment manifest

The root-level [`koyeb.yaml`](../../koyeb.yaml) file defines a single web service:

- Builds from the repository with the provided `Dockerfile`.
- Exposes port `8000` and runs `uvicorn` against `app.main:app`.
- Ships with a `/health` HTTP check.
- Maps secrets to the expected environment variables.
- Sets default production values for `ENVIRONMENT` and `DEBUG`.

Update the `source.git.repo` field to point to the repository URL Koyeb should deploy from (HTTPS or SSH).

## 3. Deploy from the CLI

```bash
# First deployment (creates the app if it does not exist)
koyeb app init fieldcraft
koyeb service deploy \
  --app fieldcraft \
  --name fieldcraft-api \
  --manifest ./koyeb.yaml
```

Subsequent deployments only require rerunning `koyeb service deploy` with the manifest after pushing changes.

## 4. Validate the deployment

1. Wait for the build and deployment to finish in the Koyeb dashboard or via `koyeb service describe fieldcraft-api`.
2. Once live, verify the health endpoint: `curl https://<your-app>.koyeb.app/health`.
3. Trigger a smoke request (for example `GET /`) to ensure the service responds with HTTP 200.

## Notes
- Alembic migrations are not automated. If you add migrations, run them via a one-off job or managed workflow before switching traffic.
- `Base.metadata.create_all()` runs on startup, so empty databases automatically receive the current schema. This is convenient for first deployments but plan to replace it with migrations for production.
- Configure observability (Sentry, logs, etc.) through additional environment variables or sidecar services as needed.
