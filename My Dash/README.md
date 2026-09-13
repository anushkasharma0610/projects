# My Dash

A personal FastAPI + React dashboard. Each account has isolated notes, dashboard layout, and dark/light preference stored in SQLite.

## Run locally

1. Create and activate a virtual environment, then run `pip install -r requirements.txt`.
2. In `frontend`, run `npm install` then `npm run build`.
3. From the project root, run `uvicorn backend.main:app --reload`.
4. Open `http://127.0.0.1:8000`.

For frontend development, run `npm run dev` inside `frontend`. Vite proxies `/api` to FastAPI at port 8000, so authentication cookies work just as they do in the production build.

The YouTube Music widget deliberately opens searches in the official YouTube Music site; it does not scrape or embed an unofficial player.

The SQLite database (`dashboard.db`) is created automatically and is intentionally ignored from source control.
