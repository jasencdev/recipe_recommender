from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt


def optimal_number_of_clusters(recipes_df):
    """
    Find the optimal number of clusters using the elbow method.

    Args:
        recipes_df (DataFrame): Data to cluster.

    Returns:
        int: Optimal number of clusters.
    """
    X = recipes_df[['minutes', 'complexity_score']]

    # Create a range of clusters
    clusters = range(2, 20)

    # Create a list to store the inertia values
    inertia_values = []

    # Create a KMeans instance for each value of k
    for k in clusters:
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(X)
        inertia_values.append(kmeans.inertia_)

    # Plot WCSS to find the "elbow"
    plt.figure(figsize=(8, 5))
    plt.plot(clusters, inertia_values, marker='o', linestyle='--')
    plt.xlabel("Number of Clusters (k)")
    plt.ylabel("WCSS (Inertia)")
    plt.title("Elbow Method to Determine Optimal k")
    plt.show()

    return clusters, inertia_values

def optimal_silhouette_score(recipes_df):
    """
    Find the optimal number of clusters using the silhouette score.

    Args:
        recipes_df (DataFrame): Data to cluster.

    Returns:
        int: Optimal number of clusters.
    """

    X = recipes_df[['minutes', 'complexity_score']]

    # Create a range of clusters
    clusters = range(4, 10)

    # Create a list to store the silhouette scores
    silhouette_scores = []

    # Create a KMeans instance for each value of k
    for k in clusters:
        kmeans = KMeans(n_clusters=k, random_state=42)
        cluster_labels = kmeans.fit_predict(X)
        silhouette_scores.append(silhouette_score(X, cluster_labels))

    # Plot silhouette scores
    plt.figure(figsize=(8, 5))
    plt.plot(clusters, silhouette_scores, marker='o', linestyle='--')
    plt.xlabel("Number of Clusters (k)")
    plt.ylabel("Silhouette Score")
    plt.title("Silhouette Score to Determine Optimal k")
    plt.show()

def train_test_split_data(recipes_df):
    """
    Split the data into training and testing sets.

    Args:
        recipes_df (DataFrame): Preprocessed recipes DataFrame.

    Returns:
        X_train (DataFrame): Training features.
        X_test (DataFrame): Testing features.
        y_train (Series): Training target.
        y_test (Series): Testing target.
    """
    # Select features for clustering
    X = recipes_df[['minutes', 'complexity_score']]

    # Train K-Means
    kmeans = KMeans(n_clusters=6, random_state=42)
    recipes_df['cluster'] = kmeans.fit_predict(X)

    # Define feature columns (X) and target (y)
    X = recipes_df[['minutes', 'complexity_score']]  # Features: Cooking time and complexity
    y = recipes_df['cluster']  # Target: Cluster labels

    # Split into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.33,  # 33% of the data will be for testing
        random_state=42  # Ensures reproducibility

    )

    return X_train, X_test, y_train, y_test
