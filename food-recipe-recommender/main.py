if __name__ == "__main__":
    # Load datasets
    recipes = pd.read_csv('path_to_RAW_recipes.csv')
    interactions = pd.read_csv('path_to_RAW_interactions.csv')

    # Save cleaned data
    recipes_filtered = recipes[recipes['minutes'] <= 180]
    recipes_filtered.to_csv('cleaned_recipes.csv', index=False)
    print("Cleaned recipes saved to 'cleaned_recipes.csv'.")

    # Generate visualizations
    plot_preparation_time(recipes_filtered)
    plot_ratings_distribution(interactions)
    plot_ingredients_distribution(recipes_filtered)
    plot_correlation_heatmap(recipes_filtered)
    plot_review_sentiment(interactions)
