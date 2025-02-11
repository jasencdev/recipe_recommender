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

# Global variables to store model state
FEATURE_NAMES = ['minutes', 'complexity_score']
N_CLUSTERS = 8

def initialize_recommender(recipes_df, n_clusters=8):
    """
    Initialize the recipe recommendation system by preparing data and training the model.
    
    Args:
        recipes_df (DataFrame): Preprocessed recipes DataFrame
        n_clusters (int): Number of clusters for KMeans (default: 8)
    
    Returns:
        tuple: (preprocessed_data, trained_kmeans_model, fitted_scaler)
    """
    # Validate inputs
    validate_recipe_df_schema(recipes_df)
    validate_input_data(recipes_df)
    validate_clustering_inputs(n_clusters, len(recipes_df))

    # Create a copy of the input data
    data = recipes_df.copy()

    # Ensure required columns exist
    if not set(FEATURE_NAMES).issubset(data.columns):
        raise ValueError(f"Missing required columns: {FEATURE_NAMES}")

    # Prepare data and train model
    return prepare_data(data, n_clusters)

def prepare_data(data, n_clusters):
    """
    Preprocess the dataset and train the k-means model.
    
    Args:
        data (DataFrame): Input recipe data
        n_clusters (int): Number of clusters for KMeans
    
    Returns:
        tuple: (preprocessed_data, trained_kmeans_model, fitted_scaler)
    """
    # Initialize scaler
    scaler = StandardScaler()

    # Select and scale features
    features = data[FEATURE_NAMES]
    features_scaled = pd.DataFrame(
        scaler.fit_transform(features),
        columns=FEATURE_NAMES
    )

    # Train model
    kmeans_model = train_kmeans(features_scaled, n_clusters)

    # Add cluster assignments to data
    data['cluster'] = kmeans_model.labels_

    # Save models
    save_models(kmeans_model, scaler)

    return data, kmeans_model, scaler

def train_kmeans(features_scaled, n_clusters):
    """
    Train the k-means clustering model.
    
    Args:
        features_scaled (DataFrame): Scaled feature data
        n_clusters (int): Number of clusters
    
    Returns:
        KMeans: Trained k-means model
    """
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    kmeans.fit(features_scaled)
    return kmeans

def save_models(kmeans_model, scaler):
    """
    Save the trained models to disk.
    
    Args:
        kmeans_model (KMeans): Trained k-means model
        scaler (StandardScaler): Fitted scaler
    """
    try:
        joblib.dump(
            kmeans_model,
            "food-recipe-recommender/models/recipe_recommender_model.joblib"
        )
        joblib.dump(
            scaler,
            "food-recipe-recommender/models/scaler.joblib"
        )
        print("Model and scaler saved successfully")
    except FileNotFoundError as e:
        print(f"Error saving model: {e}")

def recommend_recipes(data, kmeans_model, scaler, desired_time, desired_complexity, n_recommendations=5):
    """
    Recommend recipes based on user's preferred time and complexity.
    
    Args:
        data (DataFrame): Preprocessed recipe data with cluster assignments
        kmeans_model (KMeans): Trained k-means model
        scaler (StandardScaler): Fitted scaler
        desired_time (int): Preferred cooking time in minutes
        desired_complexity (int): Preferred complexity score
        n_recommendations (int): Number of recipes to recommend
    
    Returns:
        DataFrame: Top N recommended recipes
    """
    # Validate inputs
    desired_time = validate_numeric_range(desired_time, 0, 30, 'desired cooking time')
    desired_complexity = validate_numeric_range(
        desired_complexity, 0, 50, 'desired complexity'
    )

    if not isinstance(n_recommendations, int) or n_recommendations < 1:
        raise ValueError("Number of recommendations must be a positive integer")

    if kmeans_model is None:
        raise ValueError("kmeans model is not trained yet.")

    # Create and scale user input
    user_input = pd.DataFrame(
        [[desired_time, desired_complexity]],
        columns=FEATURE_NAMES
    )
    user_input_scaled = pd.DataFrame(
        scaler.transform(user_input),
        columns=FEATURE_NAMES
    )

    # Find nearest cluster
    cluster = kmeans_model.predict(user_input_scaled)[0]

    # Get recipes from cluster and calculate similarities
    cluster_recipes = data[data['cluster'] == cluster].copy()
    cluster_recipes['similarity_distance'] = cluster_recipes.apply(
        lambda x: np.sqrt(
            (x['minutes'] - desired_time)**2 +
            (x['complexity_score'] - desired_complexity)**2
        ),
        axis=1
    )

    # Return top N recommendations
    return cluster_recipes.nsmallest(n_recommendations, 'similarity_distance')
