"""Module Imports"""

from modules.preprocessing import (
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
from modules.features import select_features
from modules.modeling import (
    optimal_number_of_clusters,
    optimal_silhouette_score,
    train_test_split_data,
)
from modules.validation_checks import check_class_distribution, check_data_leakage
from modules.recommender import RecipeRecommender


def main():
    """Main script to execute the recipe recommendation model."""
    #################################
    # Load the Data
    #################################
    recipes, interactions = load_data()

    # Drop missing values in recipes
    recipes_cleaned = recipes.dropna()

    #################################
    # Sanitize the Recipes Data
    #################################

    # Drop recipes with preparation times over 180 minutes
    recipes_cleaned = recipes_cleaned[recipes_cleaned["minutes"] <= 180]

    # Summarize data for an initial understanding
    summary_data(recipes, interactions)

    #################################
    # Exploratory Data Analysis
    #################################

    # Generate visualizations
    plot_preparation_time(recipes_cleaned)
    plot_ratings_distribution(interactions)
    plot_ingredients_distribution(recipes_cleaned)
    plot_correlation_heatmap(recipes_cleaned)
    plot_review_sentiment(interactions)

    #################################
    # Preprocess the Data
    #################################

    # Preprocess the dataset
    recipes_cleaned, interactions_cleaned = preprocess_data(
        recipes_cleaned, interactions
    )

    # Visualize Preparation Time vs Number of Ingredients
    plot_prep_time_vs_ingredients(recipes_cleaned)

    # Visualize Most Used Ingredients
    plot_most_used_ingredients(recipes_cleaned)

    #################################
    # Feature Engineering & Selection
    #################################

    # Feature selection
    selected_features = select_features(recipes_cleaned, interactions_cleaned)

    # Print the first few rows to verify
    print("Selected Features Sample:")
    print(selected_features.head())

    #################################
    # Find the Optimal k for K-Means
    #################################

    # Find the optimal number of clusters using the Elbow Method
    optimal_number_of_clusters(selected_features)
    # Using the displayed output, the most efficient number of clusters was determined to be 7.

    # Find the optimal number of clusters using the Silhouette Score
    optimal_silhouette_score(selected_features)
    # Using the displayed output, the most efficient number of clusters was determined to be 6.

    #################################
    # Train Modeling
    #################################

    X_train, X_test, y_train, y_test = train_test_split_data(selected_features)

    #################################
    # Evaluation/Validation Checks
    #################################

    # 1. Check Class Distribution
    print("\n--- Class Distribution Check ---")
    check_class_distribution(y_train, y_test)

    # 2. Check Data Leakage
    print("\n--- Data Leakage Check ---")
    check_data_leakage(X_train, X_test)

    #################################
    # Build the Production Pipeline
    #################################

    # Initialize the Recipe Recommender
    recommender = RecipeRecommender(
        selected_features
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
