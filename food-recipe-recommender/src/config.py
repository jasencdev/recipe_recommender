"""
Configuration file for the Recipe Recommender System.
Contains centralized constants for file paths and filenames to maintain consistency.
"""

from pathlib import Path

# Base directories - use current working directory as project root
BASE_DIR = Path.cwd()

# Check if we're already in the food-recipe-recommender directory
if BASE_DIR.name == "food-recipe-recommender":
    PROJECT_DIR = BASE_DIR
else:
    PROJECT_DIR = BASE_DIR / "food-recipe-recommender"

DATA_DIR = PROJECT_DIR / "data"
MODELS_DIR = PROJECT_DIR / "models"

# Data filenames
RAW_RECIPES_FILENAME = "RAW_recipes.csv"
RAW_INTERACTIONS_FILENAME = "RAW_interactions.csv"

# Model filenames
RECIPE_RECOMMENDER_MODEL_FILENAME = "recipe_recommender_model.joblib"
SCALER_MODEL_FILENAME = "scaler.joblib"

# Full data file paths
RAW_RECIPES_PATH = DATA_DIR / RAW_RECIPES_FILENAME
RAW_INTERACTIONS_PATH = DATA_DIR / RAW_INTERACTIONS_FILENAME

# Full model file paths
RECIPE_RECOMMENDER_MODEL_PATH = MODELS_DIR / RECIPE_RECOMMENDER_MODEL_FILENAME
SCALER_MODEL_PATH = MODELS_DIR / SCALER_MODEL_FILENAME

# Relative paths for app.py context (when running from food-recipe-recommender directory)
MODELS_RELATIVE_DIR = "./models"
MODELS_RELATIVE_MODEL_PATH = (
    Path(MODELS_RELATIVE_DIR) / RECIPE_RECOMMENDER_MODEL_FILENAME
)
MODELS_RELATIVE_SCALER_PATH = Path(MODELS_RELATIVE_DIR) / SCALER_MODEL_FILENAME
