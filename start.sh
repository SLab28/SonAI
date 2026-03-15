#!/usr/bin/env bash
# SonAI — One-command local startup (Linux / macOS / WSL)
# Starts the FastAPI backend and Vite frontend in parallel.
#
# Prerequisites:
#   - Python 3.12 with uv installed (https://docs.astral.sh/uv/)
#   - Node.js 18+ with pnpm installed (https://pnpm.io/)
#   - Run "uv sync" and "cd frontend && pnpm install" once before first use.
#
# Usage:
#   ./start.sh          — start backend + frontend
#   ./start.sh --setup  — install deps then start

set -euo pipefail
cd "$(dirname "$0")"

cleanup() {
    echo ""
    echo "[SonAI] Shutting down..."
    kill $BACKEND_PID 2>/dev/null || true
    wait $BACKEND_PID 2>/dev/null || true
    echo "[SonAI] Stopped."
}

if [ "${1:-}" = "--setup" ]; then
    echo "[SonAI] Installing Python dependencies..."
    uv sync
    echo "[SonAI] Installing frontend dependencies..."
    (cd frontend && pnpm install)
    echo "[SonAI] Dependencies installed."
    echo ""
fi

echo "[SonAI] Starting backend on http://localhost:8000 ..."
uv run uvicorn backend.main:app --reload --port 8000 &
BACKEND_PID=$!
trap cleanup EXIT

sleep 2

echo "[SonAI] Starting frontend on http://localhost:5173 ..."
cd frontend && pnpm dev
