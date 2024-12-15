"""Module Imports"""

import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from wordcloud import WordCloud


def load_data():
    '''Module for loading data'''

    # Build the absolute file path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    recipes_data_path = os.path.join(base_dir, '../data/RAW_recipes.csv')
    interactions_data_path = os.path.join(base_dir, '../data/RAW_interactions.csv')

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
    '''Clean up the data for useability'''

    # Drop missing values in recipes
    recipes_cleaned_na = recipes.dropna()

    # Drop recipes with preparation times over 180 minutes
    recipes_cleaned = recipes[recipes['minutes'] <= 180]
    print(f"Original dataset size: {recipes_cleaned_na.shape[0]} recipes")
    print(f"Filtered dataset size: {recipes_cleaned.shape[0]} recipes")

    # Fill missing values in interactions
    interactions['review'] = interactions['review'].fillna('Unknown')

    return recipes_cleaned, interactions

def plot_preparation_time(recipes):
    """
    Plots histogram of preparation time
    """

    plt.hist(recipes['minutes'], bins=50, edgecolor='blue')
    plt.title('Distribution of Preparation Time (minutes)')
    plt.xlabel('Preparation Time (minutes)')
    plt.ylabel('Frequency')
    plt.show()

def plot_ratings_distribution(interactions):
    """
    Plots the distribution of ratings for recipes.
    """
    plt.hist(interactions['rating'], bins=5, edgecolor='blue', align='mid')
    plt.title('Distribution of Ratings')
    plt.xlabel('Ratings (1 to 5)')
    plt.ylabel('Frequency')
    plt.xticks(range(1, 6))
    plt.show()

def plot_ingredients_distribution(recipes):
    """
    Plots the histogram of the number of ingredients in recipes.
    """
    plt.hist(recipes['n_ingredients'], bins=20, edgecolor='blue')
    plt.title('Distribution of Number of Ingredients')
    plt.xlabel('Number of Ingredients')
    plt.ylabel('Frequency')
    plt.show()

def plot_correlation_heatmap(recipes):
    """
    Plots a heatmap showing correlations between numeric features.
    """
    numeric_features = ['minutes', 'n_steps', 'n_ingredients']
    corr_matrix = recipes[numeric_features].corr()

    plt.figure(figsize=(8, 6))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('Correlation Heatmap of Recipe Features')
    plt.show()

def plot_review_sentiment(interactions):
    """
    Creates a word cloud from review text in the interactions dataset.
    """
    review_text = ' '.join(interactions['review'].dropna())
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(review_text)

    plt.figure(figsize=(10, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Word Cloud of Recipe Reviews')
    plt.show()
