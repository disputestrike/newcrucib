# Voice transcription (Whisper)

Voice uses **only** the official OpenAI Python package (`openai`). No other LLM or integration layer is used.

## If you see "No module named 'emergentintegrations'"

Your environment has an old package that is not in this project. Clean it:

```bash
cd backend
pip uninstall emergentintegrations litellm -y
pip install -r requirements.txt
```

Then restart the server. Voice will use only `openai.AsyncOpenAI` and Whisper.

## If you see "Transcription unavailable. Check backend logs."

This usually means the **OpenAI package failed to import** in the backend (e.g. not installed or wrong environment).

1. **Install/openai in the backend env:**  
   `cd backend` → `pip install openai` (or `pip install -r requirements.txt`).
2. **Restart the backend** so it loads the `openai` module.
3. **Check backend logs** for the exact `ImportError` (e.g. missing dependency).
4. Ensure **OPENAI_API_KEY** is set (Settings or backend `.env`); without it you get a different message ("OpenAI key needed for voice").
