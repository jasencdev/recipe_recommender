import pandas as pd
import pytest

@pytest.fixture
def load_data():
    """Fixture to load dataset."""
    recipes = pd.read_csv('food-recipe-recommender/data/RAW_recipes.csv')
    interactions = pd.read_csv('food-recipe-recommender/data/RAW_interactions.csv')
    return recipes, interactions

def test_no_missing_values(load_data):
    recipes, interactions = load_data

    # Drop missing values in recipes
    recipes = recipes.dropna()

    # Fill missing values in 'review' for interactions
    interactions['review'] = interactions['review'].fillna('Unknown')

    # Assert that there are no remaining missing values
    assert recipes.isnull().sum().sum() == 0, "Recipes dataset contains missing values."
    assert interactions.isnull().sum().sum() == 0, "Interactions dataset contains missing values."





def test_no_duplicates(load_data):
    recipes, interactions = load_data
    assert recipes.duplicated().sum() == 0, "Recipes dataset contains duplicates."
    assert interactions.duplicated().sum() == 0, "Interactions dataset contains duplicates."

def test_column_types(load_data):
    recipes, _ = load_data
    expected_columns = ['minutes', 'n_steps', 'n_ingredients']
    for col in expected_columns:
        assert col in recipes.columns, f"Column {col} is missing from the recipes dataset."

