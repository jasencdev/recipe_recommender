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
from src.modeling import (
    initialize_recommender,
    recommend_recipes
)


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
    recipes_cleaned = recipes_cleaned[recipes['minutes'] <= 180]

    # Summarize data for an initial understanding
    summary_data(recipes_cleaned, interactions)

    #################################
    # Exploratory Data Analysis
    #################################

    # Generate visualizations
    plot_preparation_time(recipes_cleaned)
    plot_ratings_distribution(interactions)
    plot_ingredients_distribution(recipes_cleaned)
    plot_correlation_heatmap(recipes_cleaned)
    # plot_review_sentiment(interactions)

    #################################
    # Preprocess the Data
    #################################

    # Preprocess the dataset
    recipes_cleaned, interactions_cleaned = preprocess_data(recipes_cleaned, interactions)

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
    # Split Data for Modeling
    #################################

    #################################
    # Validation Checks
    #################################

    #################################
    # Train and Evaluate Model
    #################################

    #################################
    # Build the Production Pipeline
    #################################

    # Initialize the recipe recommender system
    data, kmeans_model, scaler = initialize_recommender(selected_features)

    # Recommend recipes
    recommendations = recommend_recipes(
        data,
        kmeans_model,
        scaler,
        desired_time=30,
        desired_complexity=50,
        n_recommendations=5
        )

    # Print the top recommendations
    print("Top Recommendations:")
    print(recommendations)

if __name__ == "__main__":
    main()
