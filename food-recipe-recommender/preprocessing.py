import pandas as pd

# Load the datasets
recipes = pd.read_csv('RAW_recipes.csv')
interactions = pd.read_csv('RAW_interactions.csv')

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
