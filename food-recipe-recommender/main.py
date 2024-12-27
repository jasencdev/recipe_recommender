from src.preprocessing import (
    load_data,
    preprocess_data,
    plot_preparation_time,
    plot_ratings_distribution,
    plot_ingredients_distribution,
    plot_correlation_heatmap,
    plot_review_sentiment
)
from src.preprocessing import load_data, preprocess_data
from src.feature_engineering import engineer_features
from src.feature_selection import select_features
from src.modeling import train_test_split_data, train_model, evaluate_model
import pandas as pd

if __name__ == "__main__":
    ###########################
    # Load and Preprocess Data
    ###########################

    # Load datasets
    recipes, interactions = load_data()
    print(f"Original dataset size: {len(recipes)} recipes")

    # Clean and preprocess data
    recipes_filtered, interactions = preprocess_data(recipes, interactions)
    print(f"Filtered dataset size: {len(recipes_filtered)} recipes")

    ###########################
    # Exploratory Data Analysis
    ###########################

    # Generate visualizations
    plot_preparation_time(recipes_filtered)
    plot_ratings_distribution(interactions)
    plot_ingredients_distribution(recipes_filtered)
    plot_correlation_heatmap(recipes_filtered)
    plot_review_sentiment(interactions)

    ###########################
    # Feature Engineering
    ###########################

    # Generate new features
    recipes, interactions = engineer_features(recipes_filtered, interactions)

    ###########################
    # Feature Selection
    ###########################

    # Select relevant features for modeling
    selected_features = select_features(recipes)
    selected_features.to_csv("selected_features.csv", index=False)
    print("Selected features saved to 'selected_features.csv'.")

    ###########################
    # Load Selected Features
    ###########################

    # Load the saved feature set and create binary target
    selected_features = pd.read_csv("selected_features.csv")
    selected_features['rating_binary'] = (selected_features['avg_rating'] >= 4.0).astype(int)
    target_column = 'rating_binary'

    ###########################
    # Split Data for Modeling
    ###########################

    # Split into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split_data(selected_features, target_column)

    ###########################
    # Train and Evaluate Model
    ###########################

    # Train the model
    model = train_model(X_train, y_train)
    print("Model training completed.")

    # Evaluate the model
    evaluate_model(model, X_test, y_test)
