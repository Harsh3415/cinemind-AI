"""
app.py
------
The FastAPI server entry point.

This file:
1. Creates the recommender ONCE when the server starts (not per request)
2. Exposes a /recommend endpoint over HTTP
3. Runs with: uvicorn app:app --reload
"""

import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from recommendation.recommender import MovieRecommender

# --- Create the FastAPI app instance ---
# This 'app' object is what uvicorn looks for when it starts the server.
app = FastAPI(title="CineMind AI API")

# --- CORS setup ---
# CORS = Cross-Origin Resource Sharing. By default, browsers block a
# webpage running on one address (e.g. localhost:3000, your React app)
# from making requests to a server on a different address
# (e.g. localhost:8000, this API) — unless the server explicitly allows it.
# Without this, your future React frontend would NOT be able to call
# this API at all. allow_origins=["*"] means "allow any website to call
# this API" — fine for local development; we'll tighten this before
# deploying to production in Stage 4.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Build the recommender ONCE, when the server starts ---
# This line runs a single time, when uvicorn first loads this file.
# It is NOT re-run on every request, which is exactly what we want —
# building the TF-IDF matrix is slow, so we pay that cost once.
#
# We build an absolute path based on THIS file's location, so the
# server works correctly no matter which folder you launch it from.
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
MOVIES_PATH = os.path.join(THIS_DIR, "..", "dataset", "tmdb_5000_movies.csv")
CREDITS_PATH = os.path.join(THIS_DIR, "..", "dataset", "tmdb_5000_credits.csv")

recommender = MovieRecommender(MOVIES_PATH, CREDITS_PATH)


@app.get("/")
def read_root():
    """
    A simple health-check endpoint. Visiting http://localhost:8000/
    should return this, confirming the server is alive.
    """
    return {"message": "CineMind AI API is running"}


@app.get("/recommend")
def get_recommendations(title: str, top_n: int = 5):
    """
    GET /recommend?title=Avatar&top_n=5

    FastAPI automatically reads 'title' and 'top_n' from the URL's
    query string because they're declared as function parameters here.
    'title: str' means FastAPI will reject the request with a clear
    error if 'title' is missing — we don't have to check that manually.
    """
    results = recommender.recommend(title, top_n=top_n)

    if not results:
        # HTTPException sends a proper HTTP error response (404 Not
        # Found) with a JSON error message, instead of just crashing
        # or silently returning an empty list with a 200 OK status.
        raise HTTPException(
            status_code=404,
            detail=f"Movie '{title}' not found in dataset.",
        )

    return {
        "movie": title,
        "recommendations": results,
    }