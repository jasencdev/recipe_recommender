import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io
import contextlib
from wordcloud import WordCloud

# Import preprocessing and other necessary modules
from src.preprocessing import (
    load_data,
    preprocess_data,
)
from src.feature_engineering import engineer_features
from src.feature_selection import select_features
from src.modeling import train_test_split_data, train_model, streamlit_evaluate_model
from src.validation_checks import (
    check_class_distribution,
    check_data_leakage,
    inspect_feature_correlations,
    cross_validate_model,
    manually_review_predictions
)

# Streamlit page configuration
st.set_page_config(page_title="Recipe Data Analysis", page_icon="📊", layout="wide")

st.title("Recipe Data Analysis and Model Training")

# Sidebar progress bar
progress_bar = st.sidebar.progress(0)
status_text = st.sidebar.empty()

# =============================================================================
# Load and Preprocess Data (Optimized with st.cache_data)
# =============================================================================
@st.cache_data
def get_data():
    """Loads and preprocesses the dataset using Streamlit caching."""
    recipes, interactions = load_data()  # Uses caching to prevent reloading files
    recipes_filtered, interactions = preprocess_data(recipes, interactions)
    return recipes_filtered, interactions

st.sidebar.header("1. Load and Preprocess Data")
if st.sidebar.button("Load Data"):
    with st.spinner("Loading data..."):
        recipes_filtered, interactions = get_data()  # Uses cached function
        st.session_state["recipes_filtered"] = recipes_filtered
        st.session_state["interactions"] = interactions
        st.success(f"Data loaded: {len(recipes_filtered)} recipes")
    progress_bar.progress(20)

# =============================================================================
# Exploratory Data Analysis
# =============================================================================
@st.cache_data
def generate_preparation_time_chart(recipes):
    """Caches the Preparation Time Distribution plot data."""
    bins = np.arange(0, 181, 10)
    hist_values, bin_edges = np.histogram(recipes["minutes"], bins=bins)
    bin_labels = [f"{int(bin_edges[i])}-{int(bin_edges[i+1])}" for i in range(len(bin_edges) - 1)]
    hist_df = pd.DataFrame({"Time Interval (min)": bin_labels, "Frequency": hist_values})
    hist_df["Time Interval (min)"] = pd.Categorical(hist_df["Time Interval (min)"], categories=bin_labels, ordered=True)
    return hist_df.sort_values("Time Interval (min)")

@st.cache_data
def generate_ratings_distribution_chart(interactions):
    """Caches the Ratings Distribution plot data."""
    bins = [0.5, 1.5, 2.5, 3.5, 4.5, 5.5]
    hist_values, bin_edges = np.histogram(interactions["rating"], bins=bins)
    bin_labels = [str(int(bin_edges[i])) for i in range(len(bin_edges) - 1)]
    hist_df = pd.DataFrame({"Rating": bin_labels, "Frequency": hist_values})
    hist_df["Rating"] = pd.Categorical(hist_df["Rating"], categories=bin_labels, ordered=True)
    return hist_df.sort_values("Rating")

@st.cache_data
def generate_ingredients_distribution_chart(recipes):
    """Caches the Number of Ingredients plot data."""
    ingredient_counts = recipes["n_ingredients"].value_counts().sort_index()
    full_range = pd.Series(0, index=range(1, 31))
    ingredient_counts = full_range.add(ingredient_counts, fill_value=0)
    return pd.DataFrame({"Number of Ingredients": ingredient_counts.index, "Frequency": ingredient_counts.values})

@st.cache_data
def generate_correlation_heatmap(recipes):
    """Caches the correlation heatmap figure."""
    numeric_features = ["minutes", "n_steps", "n_ingredients"]
    corr_matrix = recipes[numeric_features].corr()
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
    return fig

@st.cache_data
def generate_wordcloud(interactions):
    """Caches the word cloud visualization."""
    review_text = " ".join(interactions["review"].dropna())
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(review_text)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    return fig

# Exploratory Data Analysis
st.sidebar.header("Exploratory Data Analysis")
if st.sidebar.button("Generate Visuals"):
    if "recipes_filtered" in st.session_state and "interactions" in st.session_state:
        recipes_filtered = st.session_state["recipes_filtered"]
        interactions = st.session_state["interactions"]

        # Preparation Time Distribution (Cached)
        st.subheader("Preparation Time Distribution")
        prep_time_chart = generate_preparation_time_chart(recipes_filtered)
        st.bar_chart(prep_time_chart.set_index("Time Interval (min)"))

        # Ratings Distribution (Cached)
        st.subheader("Ratings Distribution")
        ratings_chart = generate_ratings_distribution_chart(interactions)
        st.bar_chart(ratings_chart.set_index("Rating"))

        # Ingredients Distribution (Cached)
        st.subheader("Number of Ingredients in Recipes")
        ingredients_chart = generate_ingredients_distribution_chart(recipes_filtered)
        st.line_chart(ingredients_chart.set_index("Number of Ingredients"))

        # Correlation Heatmap (Cached)
        st.subheader("Correlation Heatmap")
        with st.spinner("Generating heatmap..."):
            heatmap_fig = generate_correlation_heatmap(recipes_filtered)
            st.pyplot(heatmap_fig)

        # Sentiment Analysis Word Cloud (Cached)
        st.subheader("Review Sentiment Analysis")
        wordcloud_fig = generate_wordcloud(interactions)
        st.pyplot(wordcloud_fig)

        st.success("Visuals generated.")
    else:
        st.error("Please load data first.")
    progress_bar.progress(40)

# =============================================================================
# Feature Engineering and Selection
# =============================================================================
st.sidebar.header("3. Feature Engineering and Selection")
if st.sidebar.button("Engineer & Select Features"):
    if "recipes_filtered" in st.session_state and "interactions" in st.session_state:
        recipes, interactions = engineer_features(st.session_state["recipes_filtered"], st.session_state["interactions"])
        selected_features = select_features(recipes)
        selected_features.to_csv("selected_features.csv", index=False)
        st.session_state["selected_features"] = selected_features
        st.success("Features engineered and selected.")
    else:
        st.error("Please load data first.")
    progress_bar.progress(60)

# =============================================================================
# Load Selected Features and Prepare Data
# =============================================================================
st.sidebar.header("4. Prepare Data for Modeling")
if st.sidebar.button("Prepare Data"):
    if "selected_features" in st.session_state:
        selected_features = pd.read_csv("selected_features.csv")
        selected_features['rating_binary'] = (selected_features['avg_rating'] >= 4.0).astype(int)
        st.session_state["selected_features"] = selected_features
        st.session_state["target_column"] = "rating_binary"
        st.success("✅ Data Prepared for Training!")
    else:
        st.error("⚠️ Please engineer and select features first.")
    progress_bar.progress(70)

# =============================================================================
# Validation Checks
# =============================================================================
st.sidebar.header("5. Validation Checks")
if st.sidebar.button("Run Validation Checks"):
    if "selected_features" in st.session_state and "target_column" in st.session_state:
        X_train, X_test, y_train, y_test = train_test_split_data(
            st.session_state["selected_features"], st.session_state["target_column"]
        )

        def capture_print(func, *args, **kwargs):
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                func(*args, **kwargs)
            return buffer.getvalue()

        st.subheader("Class Distribution Check")
        st.text(capture_print(check_class_distribution, y_train, y_test))

        st.subheader("Data Leakage Check")
        st.text(capture_print(check_data_leakage, X_train, X_test))

        st.subheader("Feature Correlation Inspection")
        st.text(capture_print(inspect_feature_correlations, st.session_state["selected_features"], st.session_state["target_column"]))

        st.subheader("Cross-Validation")
        model = train_model(X_train, y_train)
        st.text(capture_print(cross_validate_model, model, X_train, y_train))

        st.subheader("Manual Prediction Review")
        st.text(capture_print(manually_review_predictions, model, X_test, y_test))

        st.success("Validation checks completed.")
    else:
        st.error("Please prepare data before running validation checks.")

# =============================================================================
# Train and Evaluate Model
# =============================================================================
st.sidebar.header("6. Train and Evaluate Model")
if st.sidebar.button("Train & Evaluate Model"):
    if "selected_features" in st.session_state:
        selected_features = st.session_state["selected_features"]
        target_column = st.session_state["target_column"]
        X_train, X_test, y_train, y_test = train_test_split_data(selected_features, target_column)
        model = train_model(X_train, y_train)
        st.session_state["model"] = model
        st.success("Model training completed.")
        st.subheader("Model Evaluation Results")
        evaluation_results = streamlit_evaluate_model(model, X_test, y_test)

        if evaluation_results:
            st.metric(label="Model Accuracy", value=f"{evaluation_results['Accuracy']:.4f}")
            report_df = pd.DataFrame(evaluation_results["Classification Report"]).transpose()
            st.subheader("Classification Report")
            st.dataframe(report_df)
            st.subheader("Confusion Matrix")
            fig, ax = plt.subplots()
            sns.heatmap(evaluation_results["Confusion Matrix"], annot=True, fmt="d", cmap="coolwarm", ax=ax)
            st.pyplot(fig)
            st.success("Model evaluation completed.")
        else:
            st.warning("No evaluation results found.")
    else:
        st.error("Please prepare data first.")
    progress_bar.progress(90)

# =============================================================================
# Rerun Button
# =============================================================================
st.button("Rerun App")
