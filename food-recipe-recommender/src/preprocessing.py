"""Module Imports"""

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from wordcloud import WordCloud

###########################
# Exploratory Data Analysis
###########################

def load_data():
    '''Module for loading data'''

    # Build the absolute file path
    base_dir = Path.cwd()

    recipes_data_path = (
        base_dir / 'food-recipe-recommender' / 'data' / 'RAW_recipes.csv').resolve()
    interactions_data_path = (
        base_dir / 'food-recipe-recommender' / 'data' / 'RAW_interactions.csv').resolve()

    # Load the dataset
    recipes = pd.read_csv(recipes_data_path)
    interactions = pd.read_csv(interactions_data_path)

    return recipes, interactions

def summary_data(recipes, interactions):
    '''Summarize the data for humans'''

    print(recipes.head())
    print(interactions.head())
    print(recipes.info())
    print(interactions.info())
    print(recipes.describe())
    print(interactions.describe())
    print(recipes.isnull().sum())
    print(interactions.isnull().sum())

def preprocess_data(recipes, interactions):
    '''Clean up the data for usability'''

    # Drop missing values in recipes
    recipes_cleaned_na = recipes.dropna()

    # Clean the ingredients column:
    # Convert to lowercase and trim whitespace for each ingredient
    recipes_cleaned_na.loc[:, 'ingredients'] = recipes_cleaned_na['ingredients'].apply(
        lambda x: ",".join([ing.strip().lower() for ing in x.split(",")])
    )

    # Drop recipes with preparation times over 180 minutes
    recipes_cleaned = recipes_cleaned_na[recipes_cleaned_na['minutes'] <= 180]
    print(f"Original dataset size (after dropping NAs): {recipes_cleaned_na.shape[0]} recipes")
    print(f"Filtered dataset size (minutes <= 180): {recipes_cleaned.shape[0]} recipes")

    # Fill missing values in interactions
    interactions['review'] = interactions['review'].fillna('Unknown')

    return recipes_cleaned, interactions

def plot_preparation_time(recipes):
    """
    Plots histogram of preparation time.
    """
    plt.hist(recipes['minutes'], bins=50, edgecolor='blue')
    plt.title('Distribution of Preparation Time (minutes)')
    plt.xlabel('Preparation Time (minutes)')
    plt.ylabel('Frequency')
    plt.show()

def plot_ratings_distribution(interactions):
    """
    Plots the distribution of ratings for recipes.
    (May be repurposed or removed if ratings are no longer used.)
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
