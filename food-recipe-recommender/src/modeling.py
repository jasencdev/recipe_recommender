import joblib
import pandas as pd
import numpy as np
import ast
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

class RecipeRecommender:
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

        # Ensure required columns exist
        required_columns = {'minutes', 'complexity_score'}
        if not required_columns.issubset(self.data.columns):
            raise ValueError(f"Dataset must contain the following columns: {required_columns}")
        
        # Prepare data and train model
        self._prepare_data()

    def _prepare_data(self):
        """
        Preprocess the dataset and train the KNN model.
        """
        # Select relevant features
        self.features = self.data[['minutes', 'complexity_score']]

        # Normalize features
        self.features_scaled = pd.DataFrame(self.scaler.fit_transform(self.features), columns=self.features.columns)
        
        # Convert back to DataFrame to retain feature names
        self.features_scaled = pd.DataFrame(self.features_scaled, columns=['minutes', 'complexity_score'])

        # Train the KNN model
        self._train_knn()

    def _train_knn(self):
        """
        Train the K-Nearest Neighbors model.
        """
        self.knn = NearestNeighbors(n_neighbors=self.k, metric='euclidean')
        self.knn.fit(self.features_scaled)

        # Save the trained model safely
        try:
            joblib.dump(self, 'food-recipe-recommender/models/recipe_recommender_model.joblib')
            joblib.dump(self.scaler, 'food-recipe-recommender/models/scaler.joblib')  # Save scaler too
            print("Model and scaler saved successfully")
        except Exception as e:
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
            self.scaler = joblib.load('food-recipe-recommender/models/scaler.joblib')
        except Exception as e:
            print(f"Error loading scaler: {e}")
            return None

        # Scale user input to match feature space
        user_input_scaled = self.scaler.transform([[desired_time, desired_complexity]])
        user_input_scaled = pd.DataFrame(user_input_scaled, columns=['minutes', 'complexity_score'])

        # Find K nearest neighbors
        distances, indices = self.knn.kneighbors(user_input_scaled, n_neighbors=self.k)

        # Retrieve recommended recipes
        recommendations = self.data.iloc[indices[0]].copy()
        recommendations.loc[:, 'similarity_distance'] = distances[0]  # Add similarity score

        return recommendations
