# PathPilot - Hybrid AI Career Navigator (#BuildHybridAI 2026)

On-device AI (Gemini Nano in Chrome) first, Firebase AI Logic cloud (Gemini) fallback,
rule-based offline mode as the last fallback. Resume analysis uses FastAPI + PyMuPDF.

## 1. Firebase setup (one time)
1. https://console.firebase.google.com -> Add project
2. Build -> AI Logic -> Get started -> choose "Gemini Developer API" -> enable
3. Project settings -> Your apps -> Web (</>) -> register app -> copy firebaseConfig
4. Paste it into app/static/firebase-config.js

## 2. Run (Windows PowerShell)
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    uvicorn app.main:app --reload

## Run (Mac/Linux/Git Bash)
    python3 -m venv venv && source venv/bin/activate
    pip install -r requirements.txt
    uvicorn app.main:app --reload

Open http://localhost:8000 in desktop Chrome. Click "Enable on-device AI" once.
If the device can't run Gemini Nano, the app uses the cloud automatically.

## Security
Firebase web config is not a secret, but in Google Cloud Console > APIs & Services > Credentials
restrict the browser API key to HTTP referrers (localhost + your deployed domain).
