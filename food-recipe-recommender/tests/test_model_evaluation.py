"""Module Imports"""
import pytest
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
import pandas as pd


@pytest.fixture
def load_data():
    """Fixture to load dataset for model training."""
    recipes = pd.read_csv('food-recipe-recommender/data/RAW_recipes.csv')
    interactions = pd.read_csv('food-recipe-recommender/data/RAW_interactions.csv')
    merged_data = pd.merge(interactions, recipes, left_on='recipe_id', right_on='id', how='inner')  # Update 'id' if it differs
    return merged_data

def test_model_accuracy(load_data):
    """
    Test for Model Accuracy to be at least 80%.
    """
    data = load_data
    x = data[['minutes', 'n_steps', 'n_ingredients']]  # Example features
    y = (data['rating'] >= 4).astype(int)  # Binary classification: high rating or not

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier()
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)

    # Test: Ensure model accuracy is above 80%
    accuracy = accuracy_score(y_test, predictions)
    assert accuracy > 0.8, f"Model accuracy is too low: {accuracy:.2f}"
