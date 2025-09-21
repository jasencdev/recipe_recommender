"""Module Imports"""

import ast
from pathlib import Path
from collections import Counter
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from wordcloud import WordCloud
from .config import RAW_RECIPES_PATH, RAW_INTERACTIONS_PATH


def load_data():
    """Module for loading data"""

    # Build the absolute file path using centralized configuration
    recipes_data_path = RAW_RECIPES_PATH.resolve()
    interactions_data_path = RAW_INTERACTIONS_PATH.resolve()

    # Load the dataset
    recipes = pd.read_csv(recipes_data_path)
    interactions = pd.read_csv(interactions_data_path)

    return recipes, interactions


def summary_data(recipes, interactions):
    """summarize the data for humans"""

    # Summary statistics
    print("\nPrinting the column names for recipes:")
    print(recipes.columns)
    print("\nPrinting the column names for interactions:")
    print(interactions.columns)

    # Display initial rows
    print("\nDisplaying the first few rows of the recipes dataset:")
    print(recipes.head())
    print("\nDisplaying the first few rows of the interactions dataset:")
    print(interactions.head())

    # Check data structure
    print("\nChecking the recipes data structure:")
    print(recipes.info())
    print("\nChecking the interactions data structure:")
    print(interactions.info())

    # Check for null values
    print("\nChecking recipes or missing values:")
    print(recipes.isnull().sum())
    print("\nChecking interactions for missing values:")
    print(interactions.isnull().sum())


def plot_preparation_time(recipes):
    """
    Plots histogram of preparation time
    """

    plt.hist(recipes["minutes"], bins=18, edgecolor="blue")
    plt.title("Distribution of Preparation Time (minutes)")
    plt.xlabel("Preparation Time (minutes)")
    plt.ylabel("Frequency")
    plt.show()


def plot_ratings_distribution(interactions):
    """
    Plots the distribution of ratings for recipes.
    """
    plt.hist(interactions["rating"], bins=5, edgecolor="blue", align="mid")
    plt.title("Distribution of Ratings")
    plt.xlabel("Ratings (1 to 5)")
    plt.ylabel("Frequency")
    plt.xticks(range(1, 6))
    plt.show()


def plot_ingredients_distribution(recipes):
    """
    Plots the histogram of the number of ingredients in recipes.
    """
    plt.hist(recipes["n_ingredients"], bins=20, edgecolor="blue")
    plt.title("Distribution of Number of Ingredients")
    plt.xlabel("Number of Ingredients")
    plt.ylabel("Frequency")
    plt.show()


def plot_correlation_heatmap(recipes):
    """
    Plots a heatmap showing correlations between numeric features.
    """
    numeric_features = ["minutes", "n_steps", "n_ingredients"]
    corr_matrix = recipes[numeric_features].corr()

    plt.figure(figsize=(8, 6))
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("Correlation Heatmap of Recipe Features")
    plt.show()


def plot_review_sentiment(interactions):
    """
    Creates a word cloud from review text in the interactions dataset.
    """
    review_text = " ".join(interactions["review"].dropna())
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(
        review_text
    )

    plt.figure(figsize=(10, 6))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.title("Word Cloud of Recipe Reviews")
    plt.show()


def plot_prep_time_vs_ingredients(recipes):
    """Plot preparation time against number of ingredients"""

    # Assuming 'ingredients' column is a list of ingredients
    recipes["num_ingredients"] = recipes["ingredients"].apply(
        lambda x: len(ast.literal_eval(x))
    )

    plt.figure(figsize=(10, 6))
    plt.scatter(recipes["minutes"], recipes["num_ingredients"], alpha=0.5)
    plt.title("Preparation Time vs Number of Ingredients")
    plt.xlabel("Preparation Time (minutes)")
    plt.ylabel("Number of Ingredients")
    plt.grid(True)
    plt.show()


def plot_most_used_ingredients(recipes, top_n=10):
    """Plot the most used ingredients"""

    # Flatten the list of ingredients and count occurrences
    all_ingredients = [
        ingredient
        for sublist in recipes["ingredients"].apply(eval)
        for ingredient in sublist
    ]
    ingredient_counts = Counter(all_ingredients)
    most_common_ingredients = ingredient_counts.most_common(top_n)

    # Unzip the list of tuples
    ingredients, counts = zip(*most_common_ingredients)

    plt.figure(figsize=(10, 6))
    plt.barh(ingredients, counts, color="skyblue")
    plt.xlabel("Count")
    plt.title(f"Top {top_n} Most Used Ingredients")
    plt.gca().invert_yaxis()  # Invert y-axis to have the most common ingredient at the top
    plt.show()


def preprocess_data(recipes, interactions):
    """Clean up the data for usability"""

    recipes_cleaned = recipes.copy()  # Ensure it's a separate copy
    recipes_cleaned["num_ingredients"] = recipes_cleaned["ingredients"].apply(
        lambda x: len(ast.literal_eval(x))
    )

    # Apply the filtering criteria:
    # - Keep only recipes with <= 20 ingredients
    # - Keep only recipes with preparation time <= 60 minutes
    recipes_filtered = recipes_cleaned.loc[
        (recipes_cleaned["num_ingredients"] <= 20) & (recipes_cleaned["minutes"] <= 60)
    ]

    print(f"Original dataset size: {recipes_cleaned.shape[0]} recipes")
    print(f"Filtered dataset size: {recipes_filtered.shape[0]} recipes")

    # Fill missing values in interactions
    interactions["review"] = interactions["review"].fillna("Unknown")

    return recipes_filtered, interactions
