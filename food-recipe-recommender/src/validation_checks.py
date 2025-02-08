import numpy as np
from sklearn.model_selection import cross_val_score

def check_class_distribution(y_train, y_test):
    """
    Checks the distribution of classes in the training and testing sets.
    Args:
        y_train: Target labels for training data.
        y_test: Target labels for testing data.
    Returns:
        None
    """
    print("Class Distribution in Training Set:")
    print(y_train.value_counts(normalize=True))

    print("Class Distribution in Test Set:")
    print(y_test.value_counts(normalize=True))

def check_data_leakage(X_train, X_test):
    """
    Checks for overlap between training and testing datasets to ensure no data leakage.
    Args:
        X_train: Training feature set.
        X_test: Testing feature set.
    Returns:
        None
    """
    overlap = set(X_train.index).intersection(set(X_test.index))
    if overlap:
        print(f"Data leakage detected! {len(overlap)} overlapping rows.")
    else:
        print("No data leakage detected.")

def inspect_feature_correlations(selected_features, target_column):
    """
    Prints the correlation of features with the target variable.
    Args:
        selected_features: DataFrame containing features and the target column.
        target_column: Name of the target column.
    Returns:
        None
    """
    correlations = selected_features.corr()
    print("Feature Correlations with Target:")
    print(correlations[target_column].sort_values(ascending=False))

def cross_validate_model(model, X_train, y_train):
    """
    Performs k-fold cross-validation and prints F1 scores.
    Args:
        model: The model to evaluate.
        X_train: Training feature set.
        y_train: Training target labels.
    Returns:
        None
    """
    print("Performing cross-validation...")
    scores = cross_val_score(model, X_train, y_train, cv=5, scoring='f1')
    print("Cross-Validation F1 Scores:", scores)
    print("Mean F1 Score:", scores.mean())

def manually_review_predictions(model, X_test, y_test, sample_size=10):
    """
    Manually reviews a random sample of predictions compared to true labels.
    Args:
        model: Trained model.
        X_test: Testing feature set.
        y_test: True labels for the test set.
        sample_size: Number of samples to review.
    Returns:
        None
    """
    sample_indices = np.random.choice(len(y_test), sample_size, replace=False)
    sample_predictions = model.predict(X_test.iloc[sample_indices])
    sample_true = y_test.iloc[sample_indices]

    print("Sample Predictions:", sample_predictions)
    print("Sample True Labels:", sample_true.values)
