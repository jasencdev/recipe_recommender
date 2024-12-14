import pandas as pd
import os

# Build the absolute file path
base_dir = os.path.dirname(os.path.abspath(__file__))
recipes_data_path = os.path.join(base_dir, '../data/RAW_recipes.csv')
interactions_data_path = os.path.join(base_dir, '../data/RAW_interactions.csv')

# Load the dataset
recipes = pd.read_csv(recipes_data_path)
interactions = pd.read_csv(interactions_data_path)

# Display initial rows
print(recipes.head())
print(interactions.head())

# Check data structure
print(recipes.info())
print(interactions.info())

# Summary statistics
print(recipes.describe())
print(interactions.describe())

# Check for null values
print(recipes.isnull().sum())
print(interactions.isnull().sum())

def preprocess_data(recipes, interactions):
    # Drop missing values in recipes
    recipes_cleaned = recipes.dropna()

    # Fill missing values in interactions
    interactions['review'] = interactions['review'].fillna('Unknown')

    return recipes_cleaned, interactions
