"""Module Imports"""

from pathlib import Path
from typing import Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from modules.validation_checks import (
    validate_clustering_inputs,
    validate_input_data,
    validate_numeric_range,
    validate_recipe_df_schema,
)


class RecipeRecommender:
    """K-Nearest Neighbors based recipe recommender system."""

    def __init__(self, recipes_df, n_clusters=6):
        """
        Initialize the KNN-based recipe recommendation system.

        Args:
            recipes_df (DataFrame): Preprocessed recipes DataFrame.
            k (int): Number of neighbors to use in KNN (default: 5).
        """
        validate_recipe_df_schema(recipes_df)
        validate_input_data(recipes_df)
        validate_clustering_inputs(n_clusters, len(recipes_df))

        self.data = recipes_df.copy()  # Store dataset

        # Add ingredient_count column if it doesn't exist
        if "ingredient_count" not in self.data.columns:
            self.data["ingredient_count"] = self.data["ingredients"].apply(self._count_ingredients)
        self.scaler = StandardScaler()
        self.kmeans = None  # KNN model will be trained later
        self.feature_names = ["minutes", "complexity_score", "ingredient_count"]
        self.n_clusters = n_clusters

        # Ensure required columns exist
        if not set(self.feature_names).issubset(self.data.columns):
            raise ValueError(f"Missing required columns: {self.feature_names}")

        # Prepare data and train model
        self._prepare_data()

    def _count_ingredients(self, ingredients):
        """Count the number of ingredients in an ingredient string or list."""
        if not isinstance(ingredients, str) or not ingredients:
            return 0
        try:
            import json

            if ingredients.startswith("["):
                return len(json.loads(ingredients))
            else:
                return len([item.strip() for item in ingredients.split(",") if item.strip()])
        except (json.JSONDecodeError, ValueError):
            return len([item.strip() for item in ingredients.split(",") if item.strip()])

    def _prepare_data(self):
        """Preprocess the dataset and train the k-means model."""
        # Select relevant features
        self.features = self.data[self.feature_names]

        # Normalize features
        self.features_scaled = pd.DataFrame(
            self.scaler.fit_transform(self.features),
            columns=self.feature_names,  # Explicitly set feature names
        )

        self._train_kmeans()

    def _train_kmeans(self):
        """
        Train the k-means model.
        """
        # Train k-means
        self.kmeans = KMeans(n_clusters=self.n_clusters, random_state=42)
        self.kmeans.fit(self.features_scaled)

        # Add cluster assignments to data
        self.data["cluster"] = self.kmeans.labels_

        # Side-effectful saving removed here; persist explicitly via save() method

    def recommend_recipes(
        self, desired_time, desired_complexity, desired_ingredients, n_recommendations=20
    ):
        """
        Recommend recipes based on user's preferred time, complexity, and ingredient count.

        Args:
            desired_time (int): Preferred cooking time in minutes.
            desired_complexity (int): Preferred complexity score.
            desired_ingredients (int): Preferred number of ingredients.

        Returns:
            DataFrame: Top K nearest recipes.
        """
        # Validate inputs
        desired_time = validate_numeric_range(desired_time, 0, 300, "desired cooking time")
        desired_complexity = validate_numeric_range(
            desired_complexity, 0, 100, "desired complexity"
        )
        desired_ingredients = validate_numeric_range(
            desired_ingredients, 1, 50, "desired ingredients"
        )

        if not isinstance(n_recommendations, int) or n_recommendations < 1:
            raise ValueError("Number of recommendations must be a positive integer")

        if self.kmeans is None:
            raise ValueError("kmeans model is not trained yet.")

        # Use in-memory scaler prepared during training

        # Create DataFrame with feature names before scaling
        user_input = pd.DataFrame(
            [[desired_time, desired_complexity, desired_ingredients]],
            columns=self.feature_names,  # Use same feature names as training
        )

        # Scale user input
        user_input_scaled = pd.DataFrame(
            self.scaler.transform(user_input),
            columns=self.feature_names,  # Maintain feature names after scaling
        )

        # Find nearest cluster
        cluster = self.kmeans.predict(user_input_scaled)[0]

        # Get recipes from cluster and sort by similarity to preferences
        cluster_recipes = self.data[self.data["cluster"] == cluster].copy()

        # Calculate distance to user preferences for sorting
        cluster_recipes["similarity_distance"] = cluster_recipes.apply(
            lambda x: np.sqrt(
                (x["minutes"] - desired_time) ** 2
                + (x["complexity_score"] - desired_complexity) ** 2
                + (x["ingredient_count"] - desired_ingredients) ** 2
            ),
            axis=1,
        )

        # Sort by similarity and return top n
        recommendations = cluster_recipes.nsmallest(n_recommendations, "similarity_distance")

        # Include detailed ingredients if available
        columns_to_return = ["name", "minutes", "complexity_score", "similarity_distance"]
        if "detailed_ingredients" in recommendations.columns:
            columns_to_return.append("detailed_ingredients")
        if "food_recipe_id" in recommendations.columns:
            columns_to_return.insert(0, "food_recipe_id")

        return recommendations[columns_to_return]

    def save(self, base_dir: Optional[Path] = None):
        """Persist model artifacts explicitly.
        Saves the recommender and scaler under models/.
        """
        try:
            models_dir = (base_dir or Path(__file__).resolve().parents[2]) / "models"
            models_dir.mkdir(parents=True, exist_ok=True)
            joblib.dump(self, models_dir / "recipe_recommender_model.joblib")
            joblib.dump(self.scaler, models_dir / "scaler.joblib")
        except Exception as e:
            raise RuntimeError(f"Failed to save model artifacts: {e}") from e

    def search_recipes(self, search_query, n_results=20):
        """
        Search recipes by name or ingredients.

        Args:
            search_query (str): Query string to search for in recipe names and ingredients.
            n_results (int): Maximum number of results to return.

        Returns:
            DataFrame: Matching recipes sorted by relevance.
        """
        if not isinstance(search_query, str) or not search_query.strip():
            raise ValueError("Search query must be a non-empty string")

        if not isinstance(n_results, int) or n_results < 1:
            raise ValueError("Number of results must be a positive integer")

        search_query = search_query.lower().strip()

        # Search in recipe names and ingredients
        matches = self.data[
            self.data["name"].str.lower().str.contains(search_query, na=False)
            | self.data["ingredients"].str.lower().str.contains(search_query, na=False)
        ].copy()

        if matches.empty:
            return matches

        # Score matches by relevance (name matches get higher score)
        matches["relevance_score"] = 0
        name_matches = matches["name"].str.lower().str.contains(search_query, na=False)
        matches.loc[name_matches, "relevance_score"] += 2

        ingredient_matches = matches["ingredients"].str.lower().str.contains(search_query, na=False)
        matches.loc[ingredient_matches, "relevance_score"] += 1

        # Sort by relevance score and return top n
        search_results = matches.nlargest(n_results, "relevance_score")
        return search_results
