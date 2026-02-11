#!/bin/sh
# Remove packages that cause "No module named 'emergentintegrations'" and reinstall deps.
# Voice uses only OpenAI (openai package). Run from backend: ./fix_voice_env.sh
pip uninstall -y emergentintegrations litellm 2>/dev/null || true
pip install -r requirements.txt
echo "Done. Restart the server (e.g. uvicorn server:app --reload)."
