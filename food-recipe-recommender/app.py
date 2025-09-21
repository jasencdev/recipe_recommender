"""WSGI entry-point for running the Flask recipe recommender app."""

from __future__ import annotations

from app import app


if __name__ == "__main__":  # pragma: no cover
    app.run(debug=True)
