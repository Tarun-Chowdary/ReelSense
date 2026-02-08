def get_unseen_movies(user_id, train_df, movies_df):
    seen = train_df[train_df["userId"] == user_id]["movieId"].unique()
    all_movies = movies_df["movieId"].unique()
    return list(set(all_movies) - set(seen))
