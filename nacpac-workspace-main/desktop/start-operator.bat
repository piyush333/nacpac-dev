@echo off
REM NACPAC Operator Machine Startup
REM Run this once on the operator machine to start the app + deploy server

setlocal enabledelayedexpansion

echo.
echo ════════════════════════════════════════════════════════════════
echo   NACPAC Production — Operator Machine Startup
echo ════════════════════════════════════════════════════════════════
echo.

REM Start deploy server in background
echo [1/2] Starting Deploy Server...
start "NACPAC Deploy Server" node deploy-server.js

REM Wait a moment for server to initialize
timeout /t 2 /nobreak

REM Start the app
echo [2/2] Starting NACPAC Production App...
start "NACPAC Production" "NACPAC Production 1.0.0.exe"

echo.
echo ════════════════════════════════════════════════════════════════
echo   ✓ NACPAC is running
echo   ✓ Deploy server is listening
echo   ✓ Ready for OTA updates from remote
echo ════════════════════════════════════════════════════════════════
echo.

timeout /t 3 /nobreak
