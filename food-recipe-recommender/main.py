from src.preprocessing import (
    load_data,
    preprocess_data,
    plot_preparation_time,
    plot_ratings_distribution,
    plot_ingredients_distribution,
    plot_correlation_heatmap,
    plot_review_sentiment
)

if __name__ == "__main__":
    # Load datasets
    recipes, interactions = load_data()
    
    # Clean and preprocess data
    recipes_filtered, interactions = preprocess_data(recipes, interactions)
    
    # Generate visualizations
    plot_preparation_time(recipes_filtered)
    plot_ratings_distribution(interactions)
    plot_ingredients_distribution(recipes_filtered)
    plot_correlation_heatmap(recipes_filtered)
    # plot_review_sentiment(interactions)
