#!/bin/sh
set -e
echo "[dealix] PORT=$PORT"
echo "[dealix] DATABASE_URL prefix: $(echo ${DATABASE_URL:-NOT_SET} | cut -d: -f1)"
echo "[dealix] Testing imports..."
python3 -c "
try:
    from app.main import app
    print(f'[dealix] OK — {len(app.routes)} routes')
except Exception as e:
    print(f'[dealix] IMPORT FAILED: {e}')
    import traceback
    traceback.print_exc()
    exit(1)
" 2>&1
echo "[dealix] Starting uvicorn on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --workers 1 --log-level info
