"""Module Imports"""

import joblib
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors


class RecipeRecommender:
    """ K-Nearest Neighbors based recipe recommender system. """
    def __init__(self, recipes_df, k=5):
        """
        Initialize the KNN-based recipe recommendation system.

        Args:
            recipes_df (DataFrame): Preprocessed recipes DataFrame.
            k (int): Number of neighbors to use in KNN (default: 5).
        """
        self.k = k
        self.data = recipes_df.copy()  # Store dataset
        self.scaler = StandardScaler()
        self.knn = None  # KNN model will be trained later
        self.feature_names = ['minutes', 'complexity_score']

        # Ensure required columns exist
        required_columns = {"minutes", "complexity_score"}
        if not required_columns.issubset(self.data.columns):
            raise ValueError(
                f"Dataset must contain the following columns: {required_columns}"
            )

        # Prepare data and train model
        self._prepare_data()

    def _prepare_data(self):
        """Preprocess the dataset and train the KNN model."""
        # Select relevant features
        self.features = self.data[self.feature_names]

        # Normalize features
        self.features_scaled = pd.DataFrame(
            self.scaler.fit_transform(self.features),
            columns=self.feature_names  # Explicitly set feature names
        )

        self._train_knn()

    def _train_knn(self):
        """
        Train the K-Nearest Neighbors model.
        """
        self.knn = NearestNeighbors(n_neighbors=self.k, metric="euclidean")
        self.knn.fit(self.features_scaled)

        # Save the trained model safely
        try:
            joblib.dump(
                self, "food-recipe-recommender/models/recipe_recommender_model.joblib"
            )
            joblib.dump(
                self.scaler, "food-recipe-recommender/models/scaler.joblib"
            )  # Save scaler too
            print("Model and scaler saved successfully")
        except FileNotFoundError as e:
            print(f"Error saving model: {e}")

    def recommend_recipes(self, desired_time, desired_complexity):
        """
        Recommend recipes based on user's preferred time and complexity.

        Args:
            desired_time (int): Preferred cooking time in minutes.
            desired_complexity (int): Preferred complexity score.

        Returns:
            DataFrame: Top K nearest recipes.
        """
        if self.knn is None:
            raise ValueError("KNN model is not trained yet.")

        # Load the scaler to ensure consistent transformations
        try:
            self.scaler = joblib.load("food-recipe-recommender/models/scaler.joblib")
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


        # Find K nearest neighbors
        distances, indices = self.knn.kneighbors(user_input_scaled, n_neighbors=self.k)

        # Retrieve recommended recipes
        recommendations = self.data.iloc[indices[0]].copy()
        recommendations.loc[:, "similarity_distance"] = distances[
            0
        ]  # Add similarity score

        return recommendations
