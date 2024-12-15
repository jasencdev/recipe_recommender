"""Feature Engineering"""

def engineer_features(recipes, interactions):
    """
    Create new features for the dataset.
    Args:
        recipes: DataFrame containing recipes data.
        interactions: DataFrame containing user interactions data.
    Returns:
        recipes: DataFrame with new features added.
        interactions: DataFrame with any processed features.
    """
    # Example: Average rating per recipe
    recipe_avg_rating = interactions.groupby('recipe_id')['rating'].mean().reset_index()
    recipe_avg_rating.rename(columns={'rating': 'avg_rating'}, inplace=True)
    recipes = recipes.merge(recipe_avg_rating, left_on='id', right_on='recipe_id', how='left')
    
    # Example: Count of user interactions per recipe
    recipe_interaction_count = interactions.groupby('recipe_id').size().reset_index(name='num_interactions')
    recipes = recipes.merge(recipe_interaction_count, left_on='id', right_on='recipe_id', how='left')
    
    # Fill missing values (e.g., recipes with no interactions)
    # Instead of using inplace=True, reassign the column after applying fillna
    recipes['avg_rating'] = recipes['avg_rating'].fillna(0)
    recipes['num_interactions'] = recipes['num_interactions'].fillna(0)

    
    # Example: Complexity score (derived feature)
    recipes['complexity_score'] = recipes['n_steps'] * recipes['n_ingredients']
    
    return recipes, interactions