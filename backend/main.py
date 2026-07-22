"""
ReelSense API
=============
Serves Top-K recommendations from your trained SVD model (models/svd_model.pkl),
plus lightweight genre-based explanations and diversity/novelty metrics for
each recommendation list.

Run:
    cd backend
    uvicorn main:app --reload --port 8000

Expects (relative to project root, one level up from this file):
    data/raw/movies.csv
    data/processed/train_ratings.csv
    models/svd_model.pkl   (a trained `surprise` SVD model, as in 03_svd_model.ipynb)
"""

import pickle
import math
from pathlib import Path
from collections import Counter
from itertools import combinations
from functools import lru_cache

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
MODELS = ROOT / "models"
FRONTEND = ROOT / "frontend"

app = FastAPI(title="ReelSense API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Load data + model once at startup
# ---------------------------------------------------------------------------

def _load():
    movies_path = DATA_RAW / "movies.csv"
    ratings_path = DATA_PROCESSED / "train_ratings.csv"
    model_path = MODELS / "svd_model.pkl"
    links_path = DATA_RAW / "links.csv"  # optional, used only for poster lookups

    missing = [p for p in [movies_path, ratings_path, model_path] if not p.exists()]
    if missing:
        missing_list = "\n  - ".join(str(p) for p in missing)
        raise RuntimeError(
            "ReelSense couldn't find required files. Copy your project's data/model "
            f"into this folder structure. Missing:\n  - {missing_list}"
        )

    movies = pd.read_csv(movies_path)
    ratings = pd.read_csv(ratings_path)
    with open(model_path, "rb") as f:
        svd = pickle.load(f)

    tmdb_map = {}
    imdb_map = {}
    if links_path.exists():
        links = pd.read_csv(links_path)
        for _, row in links.iterrows():
            mid = int(row["movieId"])
            if pd.notna(row.get("tmdbId")):
                tmdb_map[mid] = int(row["tmdbId"])
            if pd.notna(row.get("imdbId")):
                imdb_map[mid] = f"tt{int(row['imdbId']):07d}"

    return movies, ratings, svd, tmdb_map, imdb_map


try:
    MOVIES, RATINGS, SVD, TMDB_MAP, IMDB_MAP = _load()
    LOAD_ERROR = None
except Exception as e:  # keep server up so the frontend can show a clear message
    MOVIES, RATINGS, SVD, TMDB_MAP, IMDB_MAP = None, None, None, {}, {}
    LOAD_ERROR = str(e)

if MOVIES is not None:
    MOVIES["genres_list"] = MOVIES["genres"].fillna("").apply(
        lambda g: [x for x in g.split("|") if x and x != "(no genres listed)"]
    )
    MOVIE_LOOKUP = MOVIES.set_index("movieId").to_dict("index")
    POPULARITY = RATINGS["movieId"].value_counts()
    MAX_POP = int(POPULARITY.max()) if len(POPULARITY) else 1
else:
    MOVIE_LOOKUP, POPULARITY, MAX_POP = {}, pd.Series(dtype=int), 1


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _require_loaded():
    if LOAD_ERROR:
        raise HTTPException(status_code=503, detail=LOAD_ERROR)


def _genre_set(movie_id: int) -> set:
    row = MOVIE_LOOKUP.get(movie_id)
    return set(row["genres_list"]) if row else set()


def _jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 0.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def _novelty(movie_id: int) -> float:
    """0 = everyone has seen it, 1 = nobody has (higher = more novel)."""
    count = int(POPULARITY.get(movie_id, 0))
    return 1.0 - (math.log1p(count) / math.log1p(MAX_POP) if MAX_POP else 0)


def _explain(user_liked_genres: Counter, movie_id: int, example_title: str | None) -> str:
    genres = _genre_set(movie_id)
    if not genres:
        return "Recommended based on your overall rating pattern."
    overlap = [g for g in genres if user_liked_genres.get(g, 0) > 0]
    overlap = sorted(overlap, key=lambda g: -user_liked_genres[g])[:2]
    if overlap and example_title:
        return f"Because you enjoyed {', '.join(overlap)} movies like \u201c{example_title}\u201d."
    if overlap:
        return f"Matches genres you rate highly: {', '.join(overlap)}."
    return "A diversity pick — outside your usual genres, to broaden your recommendations."


@lru_cache(maxsize=2048)
def _user_genre_profile(user_id: int):
    user_ratings = RATINGS[RATINGS["userId"] == user_id]
    if user_ratings.empty:
        return Counter(), None
    liked = user_ratings[user_ratings["rating"] >= user_ratings["rating"].median()]
    liked = liked.sort_values("rating", ascending=False)
    genre_counter = Counter()
    for mid in liked["movieId"]:
        genre_counter.update(_genre_set(mid))
    top_title = None
    if not liked.empty:
        top_movie = MOVIE_LOOKUP.get(liked.iloc[0]["movieId"])
        top_title = top_movie["title"] if top_movie else None
    return genre_counter, top_title


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/api/health")
def health():
    return {"ok": LOAD_ERROR is None, "error": LOAD_ERROR}


# ---------------------------------------------------------------------------
# Quiz-based cold-start recommender
# ---------------------------------------------------------------------------
# No user history needed: score every movie from genre match + quality +
# popularity/novelty, all driven by the quiz answers. This solves the classic
# "new user" cold-start problem that pure collaborative filtering can't.

MOOD_TO_GENRES = {
    "feel_good": ["Comedy", "Animation", "Children", "Family"],
    "intense": ["Action", "Thriller", "Crime"],
    "thoughtful": ["Drama", "Mystery", "Documentary"],
    "scared": ["Horror", "Thriller"],
    "romantic": ["Romance", "Drama"],
}

GENRE_CHOICES = ["Action", "Comedy", "Drama", "Sci-Fi", "Horror", "Romance", "Adventure", "Animation"]

ERA_RANGES = {
    "classics": (0, 1979),
    "80s_90s": (1980, 1999),
    "2000s_2010s": (2000, 2016),
    "new": (2017, 2100),
    "no_preference": (0, 2100),
}

_YEAR_RE = None
import re as _re
_YEAR_RE = _re.compile(r"\((\d{4})\)\s*$")


def _movie_year(title: str):
    if not title:
        return None
    m = _YEAR_RE.search(title)
    return int(m.group(1)) if m else None


@lru_cache(maxsize=1)
def _movie_stats():
    """Average rating + rating count per movie, computed once."""
    agg = RATINGS.groupby("movieId")["rating"].agg(["mean", "count"])
    return agg.to_dict("index")


class QuizAnswers:
    def __init__(self, mood, genre, pace, era, discovery):
        self.mood = mood
        self.genre = genre
        self.pace = pace
        self.era = era
        self.discovery = discovery


@app.post("/api/quiz-recommend")
def quiz_recommend(answers: dict, k: int = Query(10, ge=1, le=30)):
    _require_loaded()

    mood = answers.get("mood")
    genre = answers.get("genre")
    era = answers.get("era", "no_preference")
    discovery = answers.get("discovery", "mix")  # "popular" | "hidden" | "mix"

    wanted_genres = set(MOOD_TO_GENRES.get(mood, []))
    if genre:
        wanted_genres.add(genre)
    # "Sci-Fi" in our genre choices maps to MovieLens's "Sci-Fi" tag directly.

    stats = _movie_stats()
    lo, hi = ERA_RANGES.get(era, (0, 2100))

    scored = []
    for movie_id, row in MOVIE_LOOKUP.items():
        genres = set(row["genres_list"])
        if not genres:
            continue

        year = _movie_year(row["title"])
        if year is not None and not (lo <= year <= hi):
            continue

        genre_overlap = genres & wanted_genres
        if wanted_genres and not genre_overlap:
            continue  # keep results on-theme; skip total mismatches

        genre_score = len(genre_overlap) / max(len(wanted_genres), 1)

        s = stats.get(movie_id)
        avg_rating, count = (s["mean"], s["count"]) if s else (0.0, 0)
        quality_score = avg_rating / 5.0
        novelty_score = _novelty(movie_id)
        popularity_score = 1 - novelty_score

        if discovery == "popular":
            exposure_score = popularity_score
        elif discovery == "hidden":
            exposure_score = novelty_score
        else:
            exposure_score = 0.5 * popularity_score + 0.5 * novelty_score

        # require a minimum vote count for "popular" picks, otherwise allow rarely-rated movies
        if discovery == "popular" and count < 3:
            continue

        total = 0.5 * genre_score + 0.3 * quality_score + 0.2 * exposure_score
        scored.append((movie_id, total, genre_overlap, avg_rating, count))

    scored.sort(key=lambda x: x[1], reverse=True)
    top = scored[:k]

    mood_label = mood.replace("_", " ") if mood else None
    items = []
    for movie_id, total, overlap, avg_rating, count in top:
        row = MOVIE_LOOKUP[movie_id]
        overlap_list = sorted(overlap)
        if overlap_list:
            reason = f"Matches your {mood_label or 'pick'} mood and love of {', '.join(overlap_list[:2])}."
        else:
            reason = f"A well-reviewed pick that fits what you're after."
        if discovery == "hidden" and count < 20:
            reason += " A hidden gem — not many have seen this one."
        elif discovery == "popular" and count >= 20:
            reason += " A crowd favorite."

        items.append({
            "movieId": int(movie_id),
            "title": row["title"],
            "genres": row["genres_list"],
            "avgRating": round(float(avg_rating), 2) if count else None,
            "ratingCount": int(count),
            "matchScore": round(float(total) * 100, 1),
            "explanation": reason,
            "tmdbId": TMDB_MAP.get(int(movie_id)),
            "imdbId": IMDB_MAP.get(int(movie_id)),
        })

    genre_sets = [set(it["genres"]) for it in items]
    pairs = list(combinations(genre_sets, 2))
    intra_list_diversity = (1 - sum(_jaccard(a, b) for a, b in pairs) / len(pairs)) if pairs else 0.0

    return {
        "recommendations": items,
        "metrics": {
            "intraListDiversity": round(intra_list_diversity, 3),
            "catalogCoverage": round(len(items) / len(MOVIE_LOOKUP), 5) if MOVIE_LOOKUP else 0,
        },
    }


@app.get("/api/users")
def list_users(limit: int = 200):
    _require_loaded()
    ids = sorted(RATINGS["userId"].unique().tolist())
    return {"users": ids[:limit], "total": len(ids)}


@app.get("/api/movie/{movie_id}")
def get_movie(movie_id: int):
    _require_loaded()
    row = MOVIE_LOOKUP.get(movie_id)
    if not row:
        raise HTTPException(status_code=404, detail="Movie not found")
    return {
        "movieId": movie_id,
        "title": row["title"],
        "genres": row["genres_list"],
        "ratingCount": int(POPULARITY.get(movie_id, 0)),
    }


@app.get("/api/recommend/{user_id}")
def recommend(user_id: int, k: int = Query(10, ge=1, le=50)):
    _require_loaded()

    if user_id not in set(RATINGS["userId"].unique()):
        raise HTTPException(status_code=404, detail=f"No user with id {user_id} in the training set")

    seen = set(RATINGS[RATINGS["userId"] == user_id]["movieId"].unique())
    all_movies = MOVIES["movieId"].unique()
    unseen = [m for m in all_movies if m not in seen]

    preds = [(m, SVD.predict(user_id, m).est) for m in unseen]
    preds.sort(key=lambda x: x[1], reverse=True)
    top = preds[:k]

    genre_counter, example_title = _user_genre_profile(user_id)

    items = []
    for movie_id, score in top:
        row = MOVIE_LOOKUP.get(movie_id, {})
        items.append({
            "movieId": int(movie_id),
            "title": row.get("title", "Unknown"),
            "genres": row.get("genres_list", []),
            "predictedRating": round(float(score), 3),
            "novelty": round(_novelty(movie_id), 3),
            "explanation": _explain(genre_counter, movie_id, example_title),
            "tmdbId": TMDB_MAP.get(int(movie_id)),
            "imdbId": IMDB_MAP.get(int(movie_id)),
        })

    # Diversity metrics for this specific Top-K list
    genre_sets = [set(it["genres"]) for it in items]
    pairs = list(combinations(genre_sets, 2))
    if pairs:
        avg_similarity = sum(_jaccard(a, b) for a, b in pairs) / len(pairs)
        intra_list_diversity = 1 - avg_similarity
    else:
        intra_list_diversity = 0.0

    avg_novelty = sum(it["novelty"] for it in items) / len(items) if items else 0.0
    coverage = len(items) / len(all_movies) if len(all_movies) else 0.0

    return {
        "userId": user_id,
        "k": k,
        "recommendations": items,
        "metrics": {
            "intraListDiversity": round(intra_list_diversity, 3),
            "avgNovelty": round(avg_novelty, 3),
            "catalogCoverage": round(coverage, 5),
        },
    }


# ---------------------------------------------------------------------------
# Serve the frontend
# ---------------------------------------------------------------------------

@app.get("/")
def index():
    return FileResponse(FRONTEND / "index.html")

app.mount("/static", StaticFiles(directory=str(FRONTEND)), name="static")