from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import CountVectorizer
import matplotlib.pyplot as plt
import seaborn as sns

def encode_ingredients(recipes):
    """
    Convert the ingredients column into a binary matrix using CountVectorizer.
    
    Args:
        recipes: DataFrame containing a column 'ingredients'.
    
    Returns:
        ingredient_matrix: Sparse matrix (binary encoded ingredients).
        vectorizer: Fitted CountVectorizer object for future transformations.
    """

    # Convert the 'ingredients' column from list format (string) into a space-separated string
    recipes['ingredients_str'] = recipes['ingredients'].apply(lambda x: " ".join(eval(x)))

    # Use CountVectorizer to get a binary representation of ingredients
    vectorizer = CountVectorizer(binary=True)
    ingredient_matrix = vectorizer.fit_transform(recipes['ingredients_str'])

    return ingredient_matrix, vectorizer

def normalize_numerical_features(recipes):
    """
    Standardize numerical features for better clustering performance.
    
    Args:
        recipes: DataFrame containing numerical features.
    
    Returns:
        normalized_features: Scaled numerical feature matrix.
        scaler: Fitted StandardScaler object.
    """

    # Select numerical features to scale
    numerical_columns = ['minutes', 'n_steps', 'n_ingredients', 'avg_rating', 'num_interactions', 'complexity_score']

    # Standardize using StandardScaler
    scaler = StandardScaler()
    normalized_features = scaler.fit_transform(recipes[numerical_columns])

    return normalized_features, scaler

def sanity_check(recipes, ingredient_matrix, normalized_features):
    """
    Perform sanity checks on preprocessed and engineered features.
    
    Args:
        recipes: DataFrame with engineered features.
        ingredient_matrix: Sparse matrix representing ingredient presence.
        normalized_features: Scaled numerical features.
    
    Returns:
        None. Prints summary statistics and visualizations.
    """

    print("\nSanity Check Started\n")

    # Check for missing values
    print("Missing Values Per Column:\n", recipes.isnull().sum())

    # Summary statistics for numerical features
    print("\nNumerical Features Summary:\n", recipes.describe())

    # Confirm ingredient encoding (Sparse matrix shape)
    print(f"\nIngredient Matrix Shape: {ingredient_matrix.shape}")
    print(f"Non-zero values: {ingredient_matrix.nnz} out of {ingredient_matrix.shape[0] * ingredient_matrix.shape[1]}")

    # Verify normalized numerical features
    print("\nSample of Normalized Features:")
    print(normalized_features[:5])

    # Plot feature distributions
    numerical_columns = ['minutes', 'n_steps', 'n_ingredients', 'avg_rating', 'num_interactions', 'complexity_score']

    plt.figure(figsize=(12, 6))
    for i, col in enumerate(numerical_columns):
        plt.subplot(2, 3, i + 1)
        sns.histplot(recipes[col], kde=True)
        plt.title(col)

    plt.tight_layout()
    plt.show()

    # Correlation heatmap
    plt.figure(figsize=(8, 6))
    sns.heatmap(recipes[numerical_columns].corr(), annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
    plt.title("Feature Correlation Matrix")
    plt.show()

    print("\nSanity Check Completed\n")

    return recipes, ingredient_matrix, normalized_features
