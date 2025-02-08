import streamlit as st
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from src.preprocessing import load_data, preprocess_data
from src.feature_selection import select_features
from src.modeling import RecipeRecommender  # Import the KNN-based recommendation system

def load_model():
    """
    Load the machine learning model from the specified directory.
    
    :param model_name: The name of the joblib file containing the saved model.
    :return: Loaded model object, or None if not found.
    """
    base_dir = Path(__file__).resolve().parent
    model_path = (base_dir / './models' / 'recipe_recommender_model.joblib').resolve()
    
    try:
        # Attempt to load the model
        loaded_model = joblib.load(model_path)
        st.success(f"Model loaded successfully!")
        return loaded_model
    
    except FileNotFoundError:
        st.error(f"Model file not found: {model_path}. Please ensure it exists in '{MODEL_DIR}'.")
        return None
    
    except Exception as e:
        st.error(f"An error occurred while loading the model: {e}")
        return None
    
    return None

def main():
    # Title and a brief description of what our app does
    st.title("Recipe Recommendation App")
    st.write("Welcome! This app will demonstrate recipe recommendations based on your available ingredients.")
    st.write(f"1. First, let's make sure the model loads. Click the button below on the left to load the model.")
    loaded = False
    if st.button('Load Model'):
        # Loading the model from the specified path
        loaded_model = load_model()
        loaded = True

    st.write(f"2. Enter your name, ingredients, and the number of ingredients your desired recipe should have using the side bar on the left.")
        
    # Creating an input field for the user to enter their name
    user_name = st.text_input('Enter your name:')

    # Creating a text area for the user to enter ingredients
    cook_time = st.slider(
        'Desired cook time (0 - 60 min):',
        min_value=0,
        max_value=60
    )

    # Option to choose a number range, demonstrating selection widgets
    complexity = st.slider(
        'Desired complexity (0-100) for your recipe:',
        min_value=0,
        max_value=100
    )

    # Main area of the app: displaying user inputs and some computations
    if user_name:
        st.write(f"-- Hello, {user_name}! Nice to meet you.")
    
    if cook_time:
        st.write(f"-- You have selected {cook_time} completiy for your recipe.")

    if complexity:
        st.write(f"-- You have selected {complexity} completiy for your recipe.")

    if user_name and cook_time and complexity and loaded:
        st.write(f"Great! Now we can recommend some recipes for you.")
        
    if st.button("Recommend Recipes"):
        # Load the dataset
        # Load the dataset
        recipes, interactions = load_data()

        # Preprocess the dataset
        recipes_cleaned, interactions_cleaned = preprocess_data(recipes, interactions)

        # Feature selection
        selected_features = select_features(recipes_cleaned, interactions_cleaned)

        ### 🔹 Integrating KNN-Based Recommendation System ###
        
        # Initialize the Recipe Recommender
        recommender = RecipeRecommender(selected_features, k=5)  # k=5: Number of recommendations to make
        
        # Get recommendations
        recommendations = recommender.recommend_recipes(cook_time, complexity)
        
        # Display recommendations
        st.write("Here are your recommended recipes:")
        st.dataframe(recommendations)

if __name__ == "__main__":
    main()
