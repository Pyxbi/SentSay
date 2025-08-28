# SentSay Demo (API-First)

A minimal full‑stack prototype that generates emotionally intelligent, copy‑ready replies using Fireworks.

## Stack
- Backend: Python + Flask + CORS
- Frontend: Static HTML/CSS/JS
- LLM: Fireworks `accounts/sentientfoundation/models/dobby-unhinged-llama-3-3-70b-new`

## Setup
1. Create and fill `.env` from `.env.example`:
```
cp .env.example .env
# edit .env and paste your FIREWORKS_API_KEY
```
2. Install deps (Python 3.10+ recommended):
```
pip install -r requirements.txt
```

## Run
```
python app.py
```
Then open `http://localhost:5001/`.

## Environment
- `FIREWORKS_API_KEY` — your Fireworks API key
- `PORT` (default 5001)
- `DEBUG` (true/false)

## Notes
- The `/api/generate` endpoint accepts JSON:
```
{ "message": "idk what to say", "situation": "making weekend plans", "tone": "Flirty" }
```
- Returns:
```
{ "options": ["…", "…", "…"], "raw": "full text" }
```
# SentSay
