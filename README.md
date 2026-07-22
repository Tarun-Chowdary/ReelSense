# ReelSense Web

A full-stack website for your ReelSense recommender: a FastAPI backend that loads your **real trained SVD model** and serves live Top-K recommendations, plus a browser frontend (cinema-ticket themed) that calls it.

```
reelsense-web/
├── backend/
│   ├── main.py            # FastAPI app (predictions, explanations, diversity metrics)
│   └── requirements.txt
├── frontend/
│   └── index.html         # single-file UI, no build step needed
├── data/
│   ├── raw/movies.csv          ← copy from your ReelSense repo
│   └── processed/train_ratings.csv  ← copy from your ReelSense repo
└── models/
    └── svd_model.pkl       ← copy from your ReelSense repo
```

## 1. Copy in your trained artifacts

From your existing `ReelSense` project folder, copy:

```bash
cp ReelSense/data/raw/movies.csv               reelsense-web/data/raw/
cp ReelSense/data/processed/train_ratings.csv  reelsense-web/data/processed/
cp ReelSense/models/svd_model.pkl              reelsense-web/models/
```

(Paths already match your repo layout from `main.py`, so no renaming needed.)

## 2. Install backend dependencies

```bash
cd reelsense-web/backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

> Your `svd_model.pkl` was trained with the `surprise` library (`svd.predict(user_id, movie_id).est`), so `scikit-surprise` is required to unpickle and call it. If pip has trouble building it, install a C++ build tool chain first (on Windows: "Microsoft C++ Build Tools"; on Mac: `xcode-select --install`).

## 3. Run it

```bash
uvicorn main:app --reload --port 8000
```

Open **http://localhost:8000** — the backend serves the frontend directly, so there's nothing else to start.

## What it does

- **`GET /api/users`** — lists user IDs available in your training set, populates the dropdown.
- **`GET /api/recommend/{user_id}?k=10`** — runs your SVD model against every unseen movie for that user, ranks by predicted rating, and returns the Top-K along with:
  - a plain-language **explanation** per movie (genre overlap with that user's highly-rated history)
  - **intra-list diversity**, **average novelty**, and **catalog coverage** for that specific list
- The frontend renders each recommendation as a torn-ticket card: predicted score on the stub, genres as chips, explanation alongside.

## Extending it

- Swap the genre-overlap explanation for your notebook 05's fuller explainability logic — the `_explain()` function in `backend/main.py` is the place to plug it in.
- The hybrid CF+content scoring from notebook 06 can replace the pure-SVD ranking in the `/api/recommend` endpoint if you want the website to reflect the hybrid model instead.
- Deploying: any host that runs a Python process works (Render, Railway, Fly.io, a VPS). Just make sure `data/` and `models/` ship alongside `backend/`.
