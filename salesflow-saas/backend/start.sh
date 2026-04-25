#!/bin/sh
echo "[dealix] Starting on port ${PORT:-8000}..."
echo "[dealix] Python: $(python3 --version)"
echo "[dealix] Testing imports..."
python3 -c "from app.main import app; print(f'[dealix] Routes: {len(app.routes)}'); print('[dealix] Import OK')" 2>&1 || { echo "[dealix] IMPORT FAILED"; exit 1; }
echo "[dealix] Launching uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --workers 1 --timeout-keep-alive 30
