import pandas as pd
import pytest

@pytest.fixture
def load_recipes():
    """Fixture to load the recipes dataset."""
    return pd.read_csv('food-recipe-recommender/data/RAW_recipes.csv')

def test_ingredient_count(load_recipes):
    recipes = load_recipes
    # Example: Check if the number of ingredients is non-negative
    assert (recipes['n_ingredients'] >= 0).all(), "Some recipes have negative ingredient counts."

def test_feature_creation(load_recipes):
    recipes = load_recipes
    recipes['complexity_score'] = recipes['n_ingredients'] * recipes['n_steps']

    # Ensure the feature is correctly calculated
    assert (recipes['complexity_score'] == recipes['n_ingredients'] * recipes['n_steps']).all(), \
        "Complexity score calculation is incorrect."
