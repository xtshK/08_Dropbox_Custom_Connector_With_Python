# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A FastAPI-based custom connector that wraps the Dropbox Business API for use with Power Automate. It exposes REST endpoints that Power Automate can consume, with support for both single-user (refresh token) and multi-user (OAuth2 Bearer token) modes. All Dropbox clients are rooted to the team namespace so both personal folders and Team Folders are accessible via normal paths.

## Commands

```bash
# Run locally (with hot reload)
python -m app.main
# Or directly:
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Run via Docker
docker compose up --build

# Export Swagger 2.0 spec (for importing into Power Automate)
python scripts/export_swagger.py
# Outputs to swagger/dropbox-connector.swagger.json

# Install dependencies
pip install -r requirements.txt
```

## Architecture

**Dual auth mode** (`app/dependencies.py` + `app/services/dropbox_client.py`): If a request includes a `Bearer` token in the `Authorization` header, it uses that token (multi-user/OAuth2 mode). Otherwise, it falls back to the app-level refresh token from `.env` (single-user mode). The root namespace ID is cached per token to avoid repeated `users_get_current_account` calls.

**Router → Dropbox SDK pattern**: Each router in `app/routers/` directly calls the `dropbox` Python SDK. There is no intermediate service layer—routers receive a `dropbox.Dropbox` client via FastAPI dependency injection (`Depends(get_dbx)`) and call SDK methods directly.

**Routers**: `auth` (connection test), `files` (upload/download), `folders` (CRUD + list + dynamic dropdown options), `sharing` (shared links), `search` (file search), `triggers` (polling trigger for file changes).

**Swagger export pipeline** (`scripts/export_swagger.py`): Reads the FastAPI OpenAPI 3.0 spec, converts it to Swagger 2.0, and injects Power Automate-specific `x-ms-*` extensions (dynamic dropdowns via `x-ms-dynamic-values`, trigger hints via `x-ms-trigger`, visibility controls). The `GetFolderOptions` endpoint is marked `x-ms-visibility: internal` so it powers dropdowns but is hidden from users.

**Polling trigger** (`app/routers/triggers.py`): Implements the Power Automate polling trigger pattern—first call returns 202 with a cursor in the `Location` header; subsequent calls use that cursor to check for changes and return 200 when changes are found.

## Configuration

Environment variables (via `.env`, loaded by pydantic-settings):
- `DROPBOX_APP_KEY`, `DROPBOX_APP_SECRET`, `DROPBOX_REFRESH_TOKEN` — required for single-user mode
- `HOST`, `PORT` — server bind address (defaults: `0.0.0.0`, `8000`)
