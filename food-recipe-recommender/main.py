from src.preprocessing import (
    load_data,
    preprocess_data,
    plot_preparation_time,
    plot_ratings_distribution,
    plot_ingredients_distribution,
    plot_correlation_heatmap,
    plot_review_sentiment
)
from src.feature_engineering import engineer_features
from src.feature_selection import select_features
from src.modeling import create_recommendation_label, train_test_split_data, train_model, evaluate_model
from src.validation_checks import (
    check_class_distribution,
    check_data_leakage,
    inspect_feature_correlations,
    cross_validate_model,
    manually_review_predictions
)
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

    # # Generate visualizations
    # plot_preparation_time(recipes_filtered)
    # plot_ratings_distribution(interactions)
    # plot_ingredients_distribution(recipes_filtered)
    # plot_correlation_heatmap(recipes_filtered)
    # plot_review_sentiment(interactions)

    ###########################
    # Feature Engineering
    ###########################

    # For demonstration, you may optionally define user ingredients.
    # For example: user_ingredients = ['tomato', 'basil', 'garlic']
    user_ingredients = None  # Replace with a list of ingredients as needed

    # Generate new features
    recipes, interactions = engineer_features(recipes_filtered, interactions, user_ingredients=user_ingredients)

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

    # Load the saved feature set and create binary target based on ingredient match
    selected_features = pd.read_csv("selected_features.csv")
    selected_features = create_recommendation_label(selected_features)  # creates a 'recommended' column
    target_column = 'recommended'

    ###########################
    # Split Data for Modeling
    ###########################

    # Split into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split_data(selected_features, target_column)

    ###########################
    # Validation Checks
    ###########################

    # 1. Check Class Distribution
    print("\n--- Class Distribution Check ---")
    check_class_distribution(y_train, y_test)

    # 2. Check Data Leakage
    print("\n--- Data Leakage Check ---")
    check_data_leakage(X_train, X_test)

    # 3. Inspect Feature Correlations
    print("\n--- Feature Correlations ---")
    inspect_feature_correlations(selected_features, target_column)

    ###########################
    # Train and Evaluate Model
    ###########################

    # Train the model
    model = train_model(X_train, y_train)
    print("\n--- Model Training Completed ---")

    # Evaluate the model
    evaluate_model(model, X_test, y_test)

    # 4. Cross-Validation
    print("\n--- Cross-Validation ---")
    cross_validate_model(model, X_train, y_train)

    # 5. Manual Prediction Review
    print("\n--- Sample Prediction Review ---")
    manually_review_predictions(model, X_test, y_test)
