"""Module Imports"""

import ast
from pathlib import Path
import streamlit as st
import joblib


def load_model():
    """
    Load the machine learning model from the specified directory.

    :param model_name: The name of the joblib file containing the saved model.
    :return: Loaded model object, or None if not found.
    """
    base_dir = Path(__file__).resolve().parent
    model_path = (base_dir / "./models" / "recipe_recommender_model.joblib").resolve()

    try:
        # Attempt to load the model
        loaded_model = joblib.load(model_path)
        return loaded_model

    except FileNotFoundError:
        st.error(
            f"Model file not found: {model_path}. Please ensure it exists in './models'."
        )
        return None

    except (joblib.externals.loky.process_executor.TerminatedWorkerError, IOError) as e:
        st.error(f"An error occurred while loading the model: {e}")
        return None


def main():
    """Main script to execute the recipe recommendation system."""
    loaded_model = load_model()
    st.session_state["recommendations"] = None
    st.session_state["selected_recipe"] = None

    # Sidebar: A place to add user input controls
    with st.sidebar:
        # Creating an input field for the user to enter their name
        user_name = st.text_input("Enter your name:")

        # Creating a text area for the user to enter ingredients
        cook_time = st.slider(
            "Desired cook time (0 - 30 min):", min_value=0, max_value=30
        )

        # Option to choose a number range, demonstrating selection widgets
        complexity = st.slider(
            "Desired complexity (0-50) for your recipe:", min_value=0, max_value=50
        )

        if loaded_model is not None and user_name and cook_time and complexity:
            if st.button("Recommend Recipes"):
                # Get recommendations
                recommendations = loaded_model.recommend_recipes(cook_time, complexity)

                # Store recommendations in session state
                st.session_state["recommendations"] = recommendations
                st.session_state["selected_recipe"] = None

    if (
        "recommendations" in st.session_state
        and st.session_state["recommendations"] is None
    ):
        # Title and a brief description of what our app does
        st.title("Recipe Recommendation App")
        st.write(
            "Welcome! This app will demonstrate recipe recommendations based on desired cooktime and "
            "complexity. We've taken a large dataset from Kaggle and distilled it down to only highly "
            "rated recipes with a limited complexity score, a combination of the number of steps and "
            "ingredients in a recipe."
        )
        st.write("1. First, let's make sure the model loads. We'll do this for you.")
        if loaded_model:
            st.success("Model loaded successfully!")
        st.write(
            "2. Open the slider on the left. Enter your name, desired cook time, and complexity."
        )
        if user_name:
            st.success(f"-- Hello, {user_name}! Nice to meet you.")

        if cook_time:
            st.success(f"-- You have selected {cook_time} completiy for your recipe.")

        if complexity:
            st.success(f"-- You have selected {complexity} completiy for your recipe.")
        st.write(
            "3. Don't click the Recommend Recipes button until you've completed the above steps."
        )
        if user_name and cook_time and complexity and loaded_model is not None:
            st.success("Great! Now we can recommend some recipes for you.")

    # Show all recommendations and their details
    if (
        "recommendations" in st.session_state
        and st.session_state["recommendations"] is not None
    ):
        st.title(f"{user_name}'s Recommended Recipes:")
        for _, row in st.session_state["recommendations"].iterrows():
            st.write("---")
            st.write(f"## {row['name'].title()}")
            st.write(f"**Cook Time:** {row['minutes']} minutes")
            st.write(f"**Complexity:** {row['complexity_score']}")
            st.write("**Ingredients:**")
            st.write(
                ", ".join(
                    [ingredient.title() for ingredient in ast.literal_eval(row["ingredients"])]
                )
            )
            st.write("**Steps:**")
            steps = ast.literal_eval(row["steps"])
            for i, step in enumerate(steps, 1):
                st.write(f"{i}. {step.capitalize()}")


if __name__ == "__main__":
    main()
