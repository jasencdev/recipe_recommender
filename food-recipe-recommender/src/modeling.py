# models.py

import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)

def create_recommendation_label(recipes, threshold=0.5):
    """
    Create a binary recommendation label based on ingredient_match_score.
    
    Args:
        recipes: DataFrame with engineered features.
        threshold: Minimum match score to consider the recipe recommended.
    
    Returns:
        recipes: DataFrame with an added 'recommended' column.
    """
    recipes['recommended'] = (recipes['ingredient_match_score'] >= threshold).astype(int)
    return recipes

def train_test_split_data(features, target_column='recommended'):
    """
    Splits the data into training and testing sets.
    
    Args:
        features: DataFrame containing the feature set including a target column.
        target_column: Name of the target column (default: 'recommended').
    
    Returns:
        X_train, X_test, y_train, y_test: Split data ready for modeling.
    """
    X = features.drop(target_column, axis=1)
    y = features[target_column]
    return train_test_split(X, y, test_size=0.2, random_state=42)

def train_model(X_train, y_train):
    """
    Trains a Logistic Regression model on the training data.
    
    Args:
        X_train: Training feature set.
        y_train: Training target labels.
    
    Returns:
        model: Trained Logistic Regression model.
    """
    model = LogisticRegression(random_state=42, max_iter=1000)
    model.fit(X_train, y_train)

    # Save the trained model
    try:
        joblib.dump(model, './models/recipe_recommender_model.joblib')
        print("Model saved successfully to 'recipe_recommender_model.joblib'")
    except Exception as e:
        print(f"Error saving model: {e}")

    return model

def evaluate_model(model, X_test, y_test):
    """
    Evaluates the classification model on test data and prints metrics.
    
    Args:
        model: Trained model.
        X_test: Testing feature set.
        y_test: True labels for the test set.
    
    Returns:
        None
    """
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]  # Predicted probabilities for the positive class
    
    # Print evaluation metrics
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("Precision:", precision_score(y_test, y_pred, zero_division=0))
    print("Recall:", recall_score(y_test, y_pred, zero_division=0))
    print("F1 Score:", f1_score(y_test, y_pred, zero_division=0))
    print("ROC-AUC Score:", roc_auc_score(y_test, y_prob))
    
    # Print confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    print("\nConfusion Matrix:")
    print(cm)

def streamlit_evaluate_model(model, X_test, y_test):
    """
    Evaluates the classification model on test data and returns metrics.
    
    Args:
        model: Trained model.
        X_test: Testing feature set.
        y_test: True labels for the test set.
    
    Returns:
        dict: Evaluation metrics and confusion matrix.
    """
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]  # Predicted probabilities for the positive class
    
    # Compute classification metrics
    metrics = {
        "Accuracy": accuracy_score(y_test, y_pred),
        "Precision": precision_score(y_test, y_pred, zero_division=0),
        "Recall": recall_score(y_test, y_pred, zero_division=0),
        "F1 Score": f1_score(y_test, y_pred, zero_division=0),
        "ROC-AUC Score": roc_auc_score(y_test, y_prob),
        "Confusion Matrix": confusion_matrix(y_test, y_pred).tolist(),  # Convert to list for JSON compatibility
        "Classification Report": classification_report(y_test, y_pred, output_dict=True)
    }
    
    return metrics