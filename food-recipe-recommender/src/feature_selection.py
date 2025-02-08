"""Feature Selection"""
def select_features(recipes):
    """
    Select the most important features for modeling.
    Args:
        recipes: DataFrame containing recipes data with engineered features.
    Returns:
        selected_features: DataFrame containing only selected features.
    """
    # Define features to keep, adding the new ingredient_match_score
    selected_columns = [
        'minutes', 
        'n_steps', 
        'n_ingredients', 
        'avg_rating', 
        'num_interactions', 
        'complexity_score',
        'ingredient_match_score'  # integrated new feature
    ]
    
    # Select these features
    selected_features = recipes[selected_columns]
    return selected_features