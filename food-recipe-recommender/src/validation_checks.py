"""
validation_checks.py
Module for input validation and data quality checks in the Recipe Recommender System.
"""

import ast
from pathlib import Path
import numpy as np


def validate_input_data(recipes_df, required_columns=None):
    """
    Validate input DataFrame for required columns and data types.
    
    Args:
        recipes_df (pd.DataFrame): Input recipes DataFrame
        required_columns (list): List of required column names
        
    Returns:
        bool: True if valid, False otherwise
        
    Raises:
        ValueError: If data validation fails
    """
    if required_columns is None:
        required_columns = ['name', 'minutes', 'ingredients', 'steps']

    # Check if DataFrame is empty
    if recipes_df.empty:
        raise ValueError("Input DataFrame is empty")

    # Check for required columns
    missing_cols = set(required_columns) - set(recipes_df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # Check for null values in required columns
    null_counts = recipes_df[required_columns].isnull().sum()
    if null_counts.any():
        raise ValueError(f"Null values found in columns: {null_counts[null_counts > 0]}")

    return True

def validate_numeric_range(value, min_val, max_val, param_name):
    """
    Validate that a numeric value falls within an acceptable range.
    
    Args:
        value (float): Value to validate
        min_val (float): Minimum acceptable value
        max_val (float): Maximum acceptable value
        param_name (str): Name of parameter being validated
        
    Returns:
        float: Validated value
        
    Raises:
        ValueError: If value is outside acceptable range
    """
    if not isinstance(value, (int, float)):
        raise ValueError(f"{param_name} must be a number")

    if value < min_val or value > max_val:
        raise ValueError(
            f"{param_name} must be between {min_val} and {max_val}, got {value}"
        )

    return value

def validate_ingredients_format(ingredients_str):
    """
    Validate that ingredients string can be safely parsed and is properly formatted.
    
    Args:
        ingredients_str (str): String representation of ingredients list
        
    Returns:
        list: Parsed ingredients list
        
    Raises:
        ValueError: If ingredients string is invalid
    """
    try:
        ingredients = ast.literal_eval(ingredients_str)
        if not isinstance(ingredients, list):
            raise ValueError("Ingredients must be a list")

        # Check that all ingredients are strings
        if not all(isinstance(i, str) for i in ingredients):
            raise ValueError("All ingredients must be strings")

        return ingredients

    except (ValueError, SyntaxError) as e:
        raise ValueError(f"Invalid ingredients format: {e}") from e

def validate_model_files(base_path):
    """
    Validate that required model files exist and are accessible.
    
    Args:
        base_path (str or Path): Base directory path
        
    Returns:
        bool: True if all files exist and are accessible
        
    Raises:
        FileNotFoundError: If required files are missing
    """
    base_path = Path(base_path)
    required_files = [
        'recipe_recommender_model.joblib',
    ]

    for file in required_files:
        file_path = base_path / 'models' / file
        if not file_path.exists():
            raise FileNotFoundError(f"Required model file not found: {file}")
        if not file_path.is_file():
            raise ValueError(f"Path exists but is not a file: {file}")

    return True

def validate_clustering_inputs(n_clusters, data_size):
    """
    Validate inputs for k-means clustering.
    
    Args:
        n_clusters (int): Number of clusters
        data_size (int): Number of data points
        
    Returns:
        bool: True if inputs are valid
        
    Raises:
        ValueError: If clustering parameters are invalid
    """
    if not isinstance(n_clusters, int):
        raise ValueError("Number of clusters must be an integer")

    if n_clusters < 2:
        raise ValueError("Must have at least 2 clusters")

    if n_clusters > data_size:
        raise ValueError(
            f"Number of clusters ({n_clusters}) cannot exceed number of data points ({data_size})"
        )

    return True

def validate_recipe_df_schema(df):
    """
    Validate the schema of a recipe DataFrame.
    
    Args:
        df (pd.DataFrame): Recipe DataFrame to validate
        
    Returns:
        bool: True if schema is valid
        
    Raises:
        ValueError: If schema validation fails
    """
    expected_dtypes = {
        'name': 'object',
        'minutes': 'number',
        'ingredients': 'object',
        'steps': 'object'
    }

    for col, expected_type in expected_dtypes.items():
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

        if expected_type == 'number':
            if not np.issubdtype(df[col].dtype, np.number):
                raise ValueError(f"Column {col} must be numeric")
        elif df[col].dtype != 'object':
            raise ValueError(f"Column {col} must be of type object")

    return True
