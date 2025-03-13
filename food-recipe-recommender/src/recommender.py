"""Module Imports"""

import joblib
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from src.validation_checks import (
    validate_input_data,
    validate_numeric_range,
    validate_clustering_inputs,
    validate_recipe_df_schema
)


class RecipeRecommender:
    """ K-Nearest Neighbors based recipe recommender system. """
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
        self.scaler = StandardScaler()
        self.kmeans = None  # KNN model will be trained later
        self.feature_names = ['minutes', 'complexity_score']
        self.n_clusters = n_clusters

        # Ensure required columns exist
        if not set(self.feature_names).issubset(self.data.columns):
            raise ValueError(f"Missing required columns: {self.feature_names}")

        # Prepare data and train model
        self._prepare_data()

    def _prepare_data(self):
        """Preprocess the dataset and train the k-means model."""
        # Select relevant features
        self.features = self.data[self.feature_names]

        # Normalize features
        self.features_scaled = pd.DataFrame(
            self.scaler.fit_transform(self.features),
            columns=self.feature_names  # Explicitly set feature names
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
        self.data['cluster'] = self.kmeans.labels_

        # Save the trained model safely
        try:
            joblib.dump(
                self, "/models/recipe_recommender_model.joblib"
            )
            joblib.dump(
                self.scaler, "/models/scaler.joblib"
            )  # Save scaler too
            print("Model and scaler saved successfully")
        except FileNotFoundError as e:
            print(f"Error saving model: {e}")

    def recommend_recipes(self, desired_time, desired_complexity, n_recommendations=5):
        """
        Recommend recipes based on user's preferred time and complexity.

        Args:
            desired_time (int): Preferred cooking time in minutes.
            desired_complexity (int): Preferred complexity score.

        Returns:
            DataFrame: Top K nearest recipes.
        """
                # Validate inputs
        desired_time = validate_numeric_range(desired_time, 0, 300, 'desired cooking time')
        desired_complexity = validate_numeric_range(
            desired_complexity, 0, 100, 'desired complexity')

        if not isinstance(n_recommendations, int) or n_recommendations < 1:
            raise ValueError("Number of recommendations must be a positive integer")

        if self.kmeans is None:
            raise ValueError("kmeans model is not trained yet.")

        # Load the scaler to ensure consistent transformations
        try:
            self.scaler = joblib.load("models/scaler.joblib")
        except FileNotFoundError as e:
            print(f"Error loading scaler: {e}")
            return None

        # Create DataFrame with feature names before scaling
        user_input = pd.DataFrame(
            [[desired_time, desired_complexity]],
            columns=self.feature_names  # Use same feature names as training
        )

        # Scale user input
        user_input_scaled = pd.DataFrame(
            self.scaler.transform(user_input),
            columns=self.feature_names  # Maintain feature names after scaling
        )


        # Find nearest cluster
        cluster = self.kmeans.predict(user_input_scaled)[0]

        # Get recipes from cluster and sort by similarity to preferences
        cluster_recipes = self.data[self.data['cluster'] == cluster].copy()

        # Calculate distance to user preferences for sorting
        cluster_recipes['similarity_distance'] = cluster_recipes.apply(
            lambda x: np.sqrt((x['minutes'] - desired_time)**2 +
                            (x['complexity_score'] - desired_complexity)**2),
            axis=1
        )

        # Sort by similarity and return top n
        recommendations = cluster_recipes.nsmallest(n_recommendations, 'similarity_distance')
        return recommendations
