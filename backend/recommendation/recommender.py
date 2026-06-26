"""
recommender.py
---------------
The core recommendation engine.

Pipeline:
1. Take the 'tags' column (one text blob per movie) from data_prep.py
2. Convert each movie's tags into a numeric vector using TF-IDF
3. Compute cosine similarity between every pair of movie vectors
4. Given a movie title, return the N most similar movies

Run this file directly to test it:
    python recommendation/recommender.py
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from data_prep import load_and_clean_data


class MovieRecommender:
    def __init__(self, movies_path, credits_path):
        # Load and clean the data once when the recommender is created
        self.df = load_and_clean_data(movies_path, credits_path)

        # --- TF-IDF step ---
        # TfidfVectorizer turns each movie's "tags" string into a row of
        # numbers (a vector). Each number represents how important a
        # particular word is to that movie, relative to all movies.
        #
        # stop_words="english" removes common, meaningless words like
        # "the", "a", "is" — they appear everywhere and add no signal.
        #
        # max_features=5000 keeps only the 5000 most informative words
        # across the whole dataset, instead of every unique word ever
        # seen (some of which could be typos or junk appearing once).
        self.vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
        self.tfidf_matrix = self.vectorizer.fit_transform(self.df["tags"])

        # --- Cosine similarity step ---
        # This computes, for every pair of movies, a score between 0
        # and 1 representing how similar their tag vectors are.
        # 1 = identical tags, 0 = no overlap at all.
        # The result is a square matrix: similarity_matrix[i][j] is the
        # similarity between movie i and movie j.
        self.similarity_matrix = cosine_similarity(self.tfidf_matrix)

        # Build a quick lookup: movie title (lowercase) -> row index.
        # We need this because cosine_similarity gives us numbers by
        # row position, but users will search by title (text).
        self.title_to_index = {
            title.lower(): index
            for index, title in enumerate(self.df["title"])
        }

    def recommend(self, movie_title, top_n=5):
        """
        Given a movie title, return the top_n most similar movies.
        Returns an empty list if the title isn't found in the dataset.
        """
        key = movie_title.lower().strip()

        if key not in self.title_to_index:
            return []

        movie_index = self.title_to_index[key]

        # Get this movie's similarity score against every other movie
        scores = list(enumerate(self.similarity_matrix[movie_index]))

        # Sort by similarity score, highest first
        scores.sort(key=lambda pair: pair[1], reverse=True)

        # Skip the first result — it's always the movie itself
        # (similarity with itself is always 1.0, the maximum possible)
        top_matches = scores[1: top_n + 1]

        recommendations = [
            {
                "title": self.df.iloc[index]["title"],
                "similarity_score": round(float(score), 4),
            }
            for index, score in top_matches
        ]

        return recommendations


if __name__ == "__main__":
    # Quick manual test when running this file directly
    recommender = MovieRecommender(
        "../dataset/tmdb_5000_movies.csv",
        "../dataset/tmdb_5000_credits.csv",
    )

    test_title = "Avatar"
    print(f"Movies similar to '{test_title}':\n")

    results = recommender.recommend(test_title, top_n=5)

    if not results:
        print(f"'{test_title}' not found in dataset.")
    else:
        for movie in results:
            print(f"  {movie['title']}  (score: {movie['similarity_score']})")