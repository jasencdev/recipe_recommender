"""Module Imports"""

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import ast
from collections import Counter

###########################
# Exploratory Data Analysis
###########################

def load_data():
    '''Module for loading data'''

    # Build the absolute file path
    base_dir = Path.cwd()

    # recipes_data_path = os.path.join(base_dir, '../data/RAW_recipes.csv')
    # interactions_data_path = os.path.join(base_dir, '../data/RAW_interactions.csv')
    recipes_data_path = (
        base_dir / 'food-recipe-recommender' / 'data' / 'RAW_recipes.csv').resolve()
    interactions_data_path = (
        base_dir / 'food-recipe-recommender' / 'data' / 'RAW_interactions.csv').resolve()

    # Load the dataset
    recipes = pd.read_csv(recipes_data_path)
    interactions = pd.read_csv(interactions_data_path)

    return recipes, interactions

def summary_data(recipes, interactions):
    '''summarize the data for humans'''

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
    '''Clean up the data for usability'''

    # Drop missing values in recipes
    recipes_cleaned = recipes.dropna()

    recipes_cleaned = recipes_cleaned.copy()  # Ensure it's a separate copy
    recipes_cleaned['num_ingredients'] = recipes_cleaned['ingredients'].apply(lambda x: len(ast.literal_eval(x)))

    # Apply the filtering criteria:
    # - Keep only recipes with average rating >= 4
    # - Keep only recipes with <= 20 ingredients
    # - Keep only recipes with preparation time <= 60 minutes
    recipes_filtered = recipes_cleaned.loc[
        (recipes_cleaned['num_ingredients'] <= 20) & 
        (recipes_cleaned['minutes'] <= 60) 
    ]

    print(f"Original dataset size: {recipes_cleaned.shape[0]} recipes")
    print(f"Filtered dataset size: {recipes_filtered.shape[0]} recipes")

    # Fill missing values in interactions
    interactions['review'] = interactions['review'].fillna('Unknown')

    return recipes_filtered, interactions

def plot_prep_time_vs_ingredients(recipes):
    '''Plot preparation time against number of ingredients'''

    # Assuming 'ingredients' column is a list of ingredients
    recipes['num_ingredients'] = recipes['ingredients'].apply(lambda x: len(eval(x)))

    plt.figure(figsize=(10, 6))
    plt.scatter(recipes['minutes'], recipes['num_ingredients'], alpha=0.5)
    plt.title('Preparation Time vs Number of Ingredients')
    plt.xlabel('Preparation Time (minutes)')
    plt.ylabel('Number of Ingredients')
    plt.grid(True)
    plt.show()

def plot_most_used_ingredients(recipes, top_n=10):
    '''Plot the most used ingredients'''

    # Flatten the list of ingredients and count occurrences
    all_ingredients = [ingredient for sublist in recipes['ingredients'].apply(eval) for ingredient in sublist]
    ingredient_counts = Counter(all_ingredients)
    most_common_ingredients = ingredient_counts.most_common(top_n)

    # Unzip the list of tuples
    ingredients, counts = zip(*most_common_ingredients)

    plt.figure(figsize=(10, 6))
    plt.barh(ingredients, counts, color='skyblue')
    plt.xlabel('Count')
    plt.title(f'Top {top_n} Most Used Ingredients')
    plt.gca().invert_yaxis()  # Invert y-axis to have the most common ingredient at the top
    plt.show()