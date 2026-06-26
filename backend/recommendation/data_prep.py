"""
data_prep.py
------------
Loads the raw TMDB CSV files, merges them, parses the messy
JSON-like text columns, and produces a clean DataFrame with one
'tags' column per movie — ready to feed into TF-IDF.

Run this file directly to test it:
    python recommendation/data_prep.py
"""

import ast
import pandas as pd


def parse_names(json_like_string, limit=None):
    """
    Converts a string like:
        '[{"id": 28, "name": "Action"}, {"id": 12, "name": "Adventure"}]'
    into a plain list of names:
        ['Action', 'Adventure']

    `limit` optionally keeps only the first N items (used for cast,
    where we only want the top 3 billed actors, not all 50).
    """
    try:
        items = ast.literal_eval(json_like_string)
    except (ValueError, SyntaxError):
        # If the cell is empty or malformed, treat it as no data
        return []

    names = [item["name"] for item in items]

    if limit is not None:
        names = names[:limit]

    return names


def get_director(crew_json_like_string):
    """
    The 'crew' column contains everyone involved in the movie
    (directors, writers, editors, etc.) as a list of dicts.
    We only want the person whose 'job' is 'Director'.
    """
    try:
        crew = ast.literal_eval(crew_json_like_string)
    except (ValueError, SyntaxError):
        return ""

    for person in crew:
        if person.get("job") == "Director":
            return person["name"]

    return ""  # No director found (rare, but handle it safely)


def load_and_clean_data(movies_path, credits_path):
    """
    Main entry point. Loads both CSVs, merges them, and returns
    a clean DataFrame with columns: id, title, overview, tags
    """
    movies = pd.read_csv(movies_path)
    credits = pd.read_csv(credits_path)

    # Both files have a 'title' column with matching movie titles.
    # We merge ("join") them into a single table on that shared column.
    # Both files ALSO have their own id column (movies.id, credits.movie_id)
    # so pandas would otherwise create confusing 'id_x' / 'id_y' columns.
    # We drop credits' id column before merging and keep movies' id as
    # the single source of truth.
    credits = credits.drop(columns=["movie_id"])
    df = movies.merge(credits, on="title")

    # Keep only the columns we actually need for the recommender.
    # (The dataset has 20+ columns; we don't need budget, revenue, etc.)
    df = df[["id", "title", "overview", "genres", "keywords", "cast", "crew"]]

    # Drop any row missing critical text data — can't build tags without it
    df = df.dropna(subset=["overview"])

    # Parse each messy column into clean Python lists / strings
    df["genres"] = df["genres"].apply(lambda x: parse_names(x))
    df["keywords"] = df["keywords"].apply(lambda x: parse_names(x))
    df["cast"] = df["cast"].apply(lambda x: parse_names(x, limit=3))
    df["director"] = df["crew"].apply(get_director)

    # overview is a sentence (e.g. "In the 22nd century, a paraplegic...").
    # Split it into individual words so it combines evenly with the
    # other list-based columns below.
    df["overview"] = df["overview"].apply(lambda x: x.split())

    # Some names have spaces, e.g. "Sam Worthington". If we don't remove
    # the space, TF-IDF would treat "Sam" and "Worthington" as separate,
    # unrelated words — losing the fact that this exact person matters.
    # Squashing to "SamWorthington" keeps it as one meaningful token.
    def squash_spaces(word_list):
        return [word.replace(" ", "") for word in word_list]

    df["genres"] = df["genres"].apply(squash_spaces)
    df["keywords"] = df["keywords"].apply(squash_spaces)
    df["cast"] = df["cast"].apply(squash_spaces)
    df["director"] = df["director"].apply(lambda x: x.replace(" ", ""))

    # Combine everything into one big list of words per movie, then
    # join into a single space-separated string — this is the final
    # "tag" TF-IDF will analyze.
    df["tags"] = (
        df["overview"]
        + df["genres"]
        + df["keywords"]
        + df["cast"]
        + df["director"].apply(lambda x: [x])  # wrap single string in a list
    )
    df["tags"] = df["tags"].apply(lambda word_list: " ".join(word_list).lower())

    # Final clean table: just what the recommender needs
    final_df = df[["id", "title", "tags"]].reset_index(drop=True)

    return final_df


if __name__ == "__main__":
    # Quick manual test when running this file directly
    result = load_and_clean_data(
        "../dataset/tmdb_5000_movies.csv",
        "../dataset/tmdb_5000_credits.csv",
    )
    print(result.shape)
    print(result.head())
    print("\nExample tag for first movie:\n")
    print(result.iloc[0]["tags"])