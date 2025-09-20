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
from modules.async_ingredient_scraper import AsyncIngredientScraper
import asyncio
import sqlite3
import pandas as pd


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
    # summary_data(recipes, interactions)

    #################################
    # Exploratory Data Analysis
    #################################

    # # Generate visualizations
    # plot_preparation_time(recipes_cleaned)
    # plot_ratings_distribution(interactions)
    # plot_ingredients_distribution(recipes_cleaned)
    # plot_correlation_heatmap(recipes_cleaned)
    # plot_review_sentiment(interactions)

    #################################
    # Preprocess the Data
    #################################

    # Preprocess the dataset
    recipes_cleaned, interactions_cleaned = preprocess_data(
        recipes_cleaned, interactions
    )

    # # Visualize Preparation Time vs Number of Ingredients
    # plot_prep_time_vs_ingredients(recipes_cleaned)

    # # Visualize Most Used Ingredients
    # plot_most_used_ingredients(recipes_cleaned)

    #################################
    # Feature Engineering & Selection
    #################################

    # Feature selection
    selected_features = select_features(recipes_cleaned, interactions_cleaned)

    # Print the first few rows to verify
    # print("Selected Features Sample:")
    # print(selected_features.head())

    #################################
    # Async Ingredient Scraping
    #################################

    print("\n--- Async Ingredient Scraping ---")
    scraper = AsyncIngredientScraper(max_concurrent=10)

    # Show current progress
    stats = scraper.get_progress_stats()
    if stats['completed_recipes'] > 0:
        print(f"\nCurrent Progress:")
        print(f"  Completed: {stats['completed_recipes']}/{stats['total_recipes']}")
        print(f"  Successful: {stats['successful_scrapes']}")
        print(f"  Failed: {stats['failed_scrapes']}")

    # Ask user if they want to scrape ingredients
    scraping_choice = input("\nDo you want to scrape ingredients from Food.com? (y/n): ").strip().lower()

    if scraping_choice == 'y':
        print("\nChoose scraping mode:")
        print("1. Fast scraping (batch size: 50, 1s delay)")
        print("2. Conservative scraping (batch size: 20, 2s delay)")
        print("3. Export current results to CSV")

        mode_choice = input("Enter choice (1-3): ").strip()

        if mode_choice == "1":
            print("Starting fast async scraping...")
            asyncio.run(scraper.scrape_dataset(selected_features, batch_size=50, delay_between_batches=1.0))
        elif mode_choice == "2":
            print("Starting conservative async scraping...")
            asyncio.run(scraper.scrape_dataset(selected_features, batch_size=20, delay_between_batches=2.0))
        elif mode_choice == "3":
            enriched_df = scraper.export_to_csv("enriched_recipes.csv")
            print(f"Exported {len(enriched_df)} enriched recipes")
        else:
            print("Invalid choice, skipping scraping.")

        # Update stats after scraping
        final_stats = scraper.get_progress_stats()
        print(f"\nFinal Stats - Success: {final_stats['successful_scrapes']}, "
              f"Failed: {final_stats['failed_scrapes']}")
    else:
        print("Skipping ingredient scraping.")

    #################################
    # Find the Optimal k for K-Means
    #################################

    # # Find the optimal number of clusters using the Elbow Method
    # optimal_number_of_clusters(selected_features)
    # # Using the displayed output, the most efficient number of clusters was determined to be 7.

    # # Find the optimal number of clusters using the Silhouette Score
    # optimal_silhouette_score(selected_features)
    # # Using the displayed output, the most efficient number of clusters was determined to be 6.

    #################################
    # Load Enriched Ingredients Database
    #################################

    # Connect to the enriched ingredients database and load to DataFrame
    try:
        conn = sqlite3.connect('enriched_ingredients.db')
        enriched_df = pd.read_sql_query("SELECT * FROM enriched_ingredients", conn)
        conn.close()
        print(f"Successfully loaded {len(enriched_df)} enriched ingredients from database")

        # Merge selected_features with enriched ingredients on food_recipe_id
        enriched_features = selected_features.merge(
            enriched_df[['food_recipe_id', 'detailed_ingredients', 'success']],
            on='food_recipe_id',
            how='left'
        )

        # Filter to only include recipes with successfully scraped ingredients
        enriched_features = enriched_features[enriched_features['success'] == True]
        print(f"Successfully merged data: {len(enriched_features)} recipes with enriched ingredients")

    except Exception as e:
        print(f"Error loading enriched ingredients database: {e}")
        enriched_features = selected_features  # Fallback to original features
        print("Using original selected_features without enriched ingredients")

    #################################
    # Train Modeling
    #################################

    X_train, X_test, y_train, y_test = train_test_split_data(enriched_features)

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
        enriched_features
    )  # k=5: Number of recommendations to make

    # Ask for user input (simulating with predefined values)
    desired_time = 30  # Example: User wants a 30-minute recipe
    desired_complexity = 50  # Example: User wants a medium complexity recipe
    desired_ingredients = 10  # Example: User wants a recipe with ~10 ingredients

    # Get recipe recommendations
    recommendations = recommender.recommend_recipes(desired_time, desired_complexity, desired_ingredients)

    # Display recommendations
    print("\nRecommended Recipes:")
    if "detailed_ingredients" in recommendations.columns:
        print("Found recipes with detailed ingredients!")
        for idx, recipe in recommendations.head(3).iterrows():
            print(f"\n--- {recipe['name']} ---")
            print(f"ID: {recipe.get('food_recipe_id', 'N/A')}")
            print(f"Time: {recipe['minutes']} minutes")
            print(f"Complexity: {recipe['complexity_score']}")
            print(f"Similarity: {recipe['similarity_distance']:.2f}")
            if pd.notna(recipe.get('detailed_ingredients')):
                print(f"Detailed Ingredients: {recipe['detailed_ingredients']}")
            print("-" * 50)
    else:
        print(recommendations[["minutes", "complexity_score", "similarity_distance"]])


if __name__ == "__main__":
    main()
