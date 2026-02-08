# 🎬 ReelSense

## Explainable, Diversity-aware Movie Recommender

---

## 📌 Overview

ReelSense is an explainable, diversity-aware movie recommendation system built using the **MovieLens Latest Small** dataset.  
Unlike traditional recommender systems that focus only on rating prediction, ReelSense emphasizes:

- Personalized **Top-K recommendations**
- **Explainability** (why a movie is recommended)
- **Diversity and novelty** to reduce popularity bias

The system combines **collaborative filtering**, **content-based modeling**, and **explicit diversity evaluation**, aligning with modern recommender system research and hackathon requirements.

---

## 🎯 Key Features

- ✔ Collaborative Filtering using **Matrix Factorization (SVD)**
- ✔ Hybrid recommender (**CF + Genre-based content similarity**)
- ✔ Natural language explanations for recommendations
- ✔ Time-aware preprocessing (leave-last-one-per-user split)
- ✔ Diversity & novelty evaluation
  - Intra-List Diversity
  - Catalog Coverage
  - Popularity-based Novelty
- ✔ Clean, reproducible ML pipeline using notebooks

---

## 📂 Dataset

**MovieLens Latest Small**

- 100,836 ratings
- 610 users
- 9,742 movies

**Files used:**

- `ratings.csv`
- `movies.csv`
- `tags.csv`
- `links.csv`

Source: https://grouplens.org/datasets/movielens/latest/

---

## 🧹 Data Processing

- Converted timestamps to datetime format
- Applied **time-aware train–test split** (leave-last-one per user)
- Cleaned and standardized movie genres and tags
- Saved processed datasets for reproducibility

This ensures realistic evaluation and prevents temporal data leakage.

---

## 🧠 Methodology

### 1. Collaborative Filtering

- Implemented using **Singular Value Decomposition (SVD)**
- Learns latent user and item representations
- Optimized using RMSE and MAE on a held-out temporal test set

### 2. Hybrid Recommendation

- Combines SVD predicted ratings with **genre-based similarity**
- Genre text is vectorized using TF-IDF
- Final recommendation score is a weighted combination of:
  - Predicted rating (personalization)
  - Content similarity (diversity & relevance)

### 3. Explainability

- Generates human-readable explanations using:

  ReelSense is an explainable, diversity-aware movie recommendation project built on the MovieLens Latest Small dataset. It combines collaborative filtering, content signals, and explicit diversity evaluation to produce accurate, transparent, and less popularity-biased Top-K recommendations.

  ### Key Features
  - **Collaborative filtering (SVD):** Matrix factorization for personalized scores.
  - **Hybrid scoring:** Combines SVD predictions with TF–IDF genre similarity.
  - **Explainability:** Human-readable reasons using past likes and genre overlap.
  - **Diversity & novelty metrics:** Intra-list diversity, catalog coverage, popularity-based novelty.
  - **Time-aware evaluation:** Leave-last-one-per-user split to avoid temporal leakage.

  ### Dataset
  - MovieLens Latest Small (ratings.csv, movies.csv, tags.csv, links.csv)
  - ~100k ratings, ~610 users, ~9.7k movies

  ### Project Structure

  ReelSense/
  - data/
    - raw/
    - processed/
  - models/
    - svd_model.pkl
  - notebooks/
    - 01_eda.ipynb
    - 02_preprocessing.ipynb
    - 03_svd_model.ipynb
    - 04_topk_recommendations.ipynb
    - 05_explainability.ipynb
    - 06_hybrid_recommender.ipynb
    - 07_diversity_metrics.ipynb
  - src/ (utility modules)
  - main.py (demo / example runner)
  - README.md

  ### Getting Started
  1. Create a Python environment (Python 3.11 recommended).
  2. Install dependencies:

  ```bash
  pip install -r requirements.txt
  ```

  3. Run the notebooks in order: EDA → Preprocessing → Model → Hybrid → Metrics.
  4. Optionally run `main.py` to see a demo Top-K recommendation workflow.

  ### Results (summary)
  - SVD provides strong rating predictions on the temporal split.
  - The hybrid approach improves diversity and novelty while maintaining personalization.
  - Explanations help surface why items are recommended (genre and liked examples).

  ### Future Work
  - Add tag or embedding-based content features.
  - Explore session/context-aware models.
  - Optimize long-term engagement with reinforcement learning.

  ### Author

  Tarun Chowdary Yegi

  ***
