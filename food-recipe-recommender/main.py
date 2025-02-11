"""Module Imports"""

from src.preprocessing import (
    load_data,
    summary_data,
    preprocess_data,
    plot_preparation_time,
    plot_ratings_distribution,
    plot_ingredients_distribution,
    plot_correlation_heatmap,
    plot_review_sentiment,
    plot_prep_time_vs_ingredients,
    plot_most_used_ingredients,
)
from src.features import select_features
from src.modeling import RecipeRecommender  # Import the KNN-based recommendation system


def main():
    """Main script to execute the recipe recommendation system."""
    ################################
    # Load the Data
    ################################
    recipes, interactions = load_data()

    # Drop missing values in recipes
    recipes_cleaned = recipes.dropna()

    ################################
    # Sanitize the Recipes Data
    ################################

    # Drop recipes with preparation times over 180 minutes
    recipes_cleaned = recipes_cleaned[recipes['minutes'] <= 180]

    # Summarize data for an initial understanding
    summary_data(recipes_cleaned, interactions)

    ################################
    # Exploratory Data Analysis
    ################################

    # Generate visualizations
    plot_preparation_time(recipes_cleaned)
    plot_ratings_distribution(interactions)
    plot_ingredients_distribution(recipes_cleaned)
    plot_correlation_heatmap(recipes_cleaned)
    plot_review_sentiment(interactions)

    ################################
    # Preprocess the Data
    ################################

    # Preprocess the dataset
    recipes_cleaned, interactions_cleaned = preprocess_data(recipes, interactions)

    # Visualize Preparation Time vs Number of Ingredients
    plot_prep_time_vs_ingredients(recipes_cleaned)

    # Visualize Most Used Ingredients
    plot_most_used_ingredients(recipes_cleaned)

    # Feature selection
    selected_features = select_features(recipes_cleaned, interactions_cleaned)

    # Print the first few rows to verify
    print("Selected Features Sample:")
    print(selected_features.head())

    # Sanity check
    # sanity_check(selected_features)

    ### 🔹 Integrating KNN-Based Recommendation System ###

    # Initialize the Recipe Recommender
    recommender = RecipeRecommender(
        selected_features, n_clusters=8
    )  # k=5: Number of recommendations to make

    # Ask for user input (simulating with predefined values)
    desired_time = 30  # Example: User wants a 30-minute recipe
    desired_complexity = 50  # Example: User wants a medium complexity recipe

    # Get recipe recommendations
    recommendations = recommender.recommend_recipes(desired_time, desired_complexity)

    # Display recommendations
    print("\nRecommended Recipes:")
    print(recommendations[["minutes", "complexity_score", "similarity_distance"]])


if __name__ == "__main__":
    main()
