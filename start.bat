@echo off
REM SonAI — One-command local startup for Windows
REM Starts the FastAPI backend and Vite frontend in parallel.
REM
REM Prerequisites:
REM   - Python 3.12 with uv installed (https://docs.astral.sh/uv/)
REM   - Node.js 18+ with pnpm installed (https://pnpm.io/)
REM   - Run "uv sync" and "cd frontend && pnpm install" once before first use.
REM
REM Usage:
REM   start.bat          — start backend + frontend
REM   start.bat --setup  — install deps then start

setlocal

if "%1"=="--setup" (
    echo [SonAI] Installing Python dependencies...
    uv sync
    if errorlevel 1 (
        echo [SonAI] ERROR: uv sync failed. Is uv installed?
        exit /b 1
    )
    echo [SonAI] Installing frontend dependencies...
    pushd frontend
    pnpm install
    if errorlevel 1 (
        echo [SonAI] ERROR: pnpm install failed. Is pnpm installed?
        popd
        exit /b 1
    )
    popd
    echo [SonAI] Dependencies installed.
    echo.
)

echo [SonAI] Starting backend on http://localhost:8000 ...
start "SonAI Backend" cmd /k "uv run uvicorn backend.main:app --reload --port 8000"

REM Give the backend a moment to bind the port before the frontend proxy connects.
timeout /t 2 /nobreak >nul

echo [SonAI] Starting frontend on http://localhost:5173 ...
pushd frontend
pnpm dev
popd
