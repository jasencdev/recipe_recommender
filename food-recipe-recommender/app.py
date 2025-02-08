import streamlit as st
import joblib
import numpy as np
from pathlib import Path

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
    st.write(f"2. Enter your name, ingredients, and the number of ingredients your desired recipe should have using the side bar on the left.")

    # Sidebar: A place to add user input controls
    with st.sidebar:
        if st.button('Load Model'):
            # Loading the model from the specified path
            loaded_model = load_model()

        
        # Creating an input field for the user to enter their name
        user_name = st.text_input('Enter your name:')

        # Creating a text area for the user to enter ingredients
        ingredients = st.text_area('Enter your ingredients, separated by commas:')

        # Option to choose a number range, demonstrating selection widgets
        num_range = st.slider(
            'Select a number of ingredients for your recipe:',
            min_value=0,
            max_value=50
        )

        

    # Main area of the app: displaying user inputs and some computations
    if user_name:
        st.write(f"-- Hello, {user_name}! Nice to meet you. The ingredients you entered are: ")
    
    if ingredients:
        # Displaying the cleaned list back to the user
        for ingredient in ingredients.split(","):
            st.write(f"-- -- {ingredient}")

    if num_range:
        st.write(f"-- You have selected {num_range} ingredients for your recipe.")

if __name__ == "__main__":
    main()
