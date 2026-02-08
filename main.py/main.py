"""
ReelSense - Entry Point

This script demonstrates how the trained recommender system
can be loaded and used to generate Top-K recommendations.
"""

import pickle
import pandas as pd

# Load data
movies = pd.read_csv("data/raw/movies.csv")
train_df = pd.read_csv("data/processed/train_ratings.csv")

# Load trained SVD model
with open("models/svd_model.pkl", "rb") as f:
    svd = pickle.load(f)

def recommend_for_user(user_id, k=5):
    seen = train_df[train_df["userId"] == user_id]["movieId"].unique()
    all_movies = movies["movieId"].unique()
    unseen = set(all_movies) - set(seen)

    preds = [(m, svd.predict(user_id, m).est) for m in unseen]
    preds.sort(key=lambda x: x[1], reverse=True)

    for movie_id, score in preds[:k]:
        title = movies[movies["movieId"] == movie_id]["title"].values[0]
        print(title, round(score, 2))

if __name__ == "__main__":
    recommend_for_user(user_id=10)

    
 #author: Tarun Chowdary Yegi