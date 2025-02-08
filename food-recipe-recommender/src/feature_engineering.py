"""Feature Engineering"""

def engineer_features(recipes, interactions, user_ingredients=None):
    """
    Create new features for the dataset based on user's ingredients.
    
    Args:
        recipes: DataFrame containing recipes data.
                 Assumes a column 'ingredients' with comma-separated ingredient names.
        interactions: DataFrame containing user interactions data. (Not used in the new logic)
        user_ingredients: A set (or list) of ingredients provided by the user.
    
    Returns:
        recipes: DataFrame with new features added, including the ingredient match score.
        interactions: Unchanged DataFrame with interactions.
    """
    if user_ingredients is not None:
        # Convert user ingredients to a set for faster lookup.
        user_set = set([ing.strip().lower() for ing in user_ingredients])
        
        def compute_match(recipe_ingredients):
            # Assume each recipe's ingredients are comma-separated
            recipe_set = set([ing.strip().lower() for ing in recipe_ingredients.split(",")])
            common = recipe_set.intersection(user_set)
            return len(common) / len(user_set) if user_set else 0
        
        recipes['ingredient_match_score'] = recipes['ingredients'].apply(compute_match)
    
    # Remove features not used anymore (e.g. rating-based features) or keep them if needed.
    # For example, you can drop the columns added previously:
    # recipes.drop(columns=['avg_rating', 'num_interactions', 'complexity_score'], errors='ignore', inplace=True)
    
    return recipes, interactions