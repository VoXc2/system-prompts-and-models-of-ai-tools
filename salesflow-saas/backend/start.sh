#!/bin/sh
# start.sh — Railway-compatible start script
# Uses $PORT from Railway (default 8000 if not set)
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --workers 2
