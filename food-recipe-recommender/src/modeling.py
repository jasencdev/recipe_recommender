from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix


def train_test_split_data(features, target_column):
    """
    Splits the data into training and testing sets.
    Args:
        features: DataFrame containing the feature set.
        target_column: Name of the target column.
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
