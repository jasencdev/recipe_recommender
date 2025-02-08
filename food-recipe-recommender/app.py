# app.py

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

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

from wordcloud import WordCloud

# Streamlit page configuration
st.set_page_config(page_title="Recipe Data Analysis", page_icon="📊", layout="wide")

st.title("Recipe Data Analysis and Model Training")

# Sidebar progress bar
progress_bar = st.sidebar.progress(0)
status_text = st.sidebar.empty()

# Load and preprocess data
st.sidebar.header("Load and Preprocess Data")
if st.sidebar.button("Load Data"):
    with st.spinner("Loading data..."):
        recipes, interactions = load_data()
        recipes_filtered, interactions = preprocess_data(recipes, interactions)
        st.session_state["recipes_filtered"] = recipes_filtered
        st.session_state["interactions"] = interactions
        st.success(f"Data loaded: {len(recipes_filtered)} recipes")
    progress_bar.progress(20)

# Exploratory Data Analysis
st.sidebar.header("Exploratory Data Analysis")
if st.sidebar.button("Generate Visuals"):
    if "recipes_filtered" in st.session_state and "interactions" in st.session_state:

        # Preparation Time Distribution
        st.subheader("Preparation Time Distribution")

        # Define bins in 15-minute increments from 0 to 180
        bins = np.arange(0, 181, 10)  # Explicitly defining bins up to 180 minutes

        # Compute histogram using these bins
        hist_values, bin_edges = np.histogram(st.session_state["recipes_filtered"]["minutes"], bins=bins)

        # Create bin labels as "start-end" format
        bin_labels = [f"{int(bin_edges[i])}-{int(bin_edges[i+1])}" for i in range(len(bin_edges) - 1)]

        # Ensure all bins are represented (even if some bins have zero frequency)
        hist_df = pd.DataFrame({"Time Interval (min)": bin_labels, "Frequency": hist_values})

        # Convert to categorical to enforce correct order
        hist_df["Time Interval (min)"] = pd.Categorical(hist_df["Time Interval (min)"], categories=bin_labels, ordered=True)

        # Sort DataFrame and plot
        hist_df = hist_df.sort_values("Time Interval (min)")
        st.bar_chart(hist_df.set_index("Time Interval (min)"))

        # Ratings Distribution
        st.subheader("Ratings Distribution")

        # Define rating bins (1 to 5)
        bins = [0.5, 1.5, 2.5, 3.5, 4.5, 5.5]  # Ensures ratings are grouped correctly

        # Compute histogram
        hist_values, bin_edges = np.histogram(st.session_state["interactions"]["rating"], bins=bins)

        # Create bin labels corresponding to ratings (1 to 5)
        bin_labels = [str(int(bin_edges[i])) for i in range(len(bin_edges) - 1)]

        # Ensure all ratings (1-5) are present (even if frequency is 0)
        hist_df = pd.DataFrame({"Rating": bin_labels, "Frequency": hist_values})

        # Convert "Rating" to categorical with an enforced order
        hist_df["Rating"] = pd.Categorical(hist_df["Rating"], categories=bin_labels, ordered=True)

        # Sort and plot
        hist_df = hist_df.sort_values("Rating")
        st.bar_chart(hist_df.set_index("Rating"))

        # Ingredients Distribution (Line Chart)
        st.subheader("Number of Ingredients in Recipes")

        # Count occurrences of each ingredient count (1-30)
        ingredient_counts = st.session_state["recipes_filtered"]["n_ingredients"].value_counts().sort_index()

        # Ensure all ingredient counts (1-30) are represented
        full_range = pd.Series(0, index=range(1, 31))  # Default to zero counts
        ingredient_counts = full_range.add(ingredient_counts, fill_value=0)  # Merge with actual data

        # Convert to DataFrame for Streamlit
        hist_df = pd.DataFrame({"Number of Ingredients": ingredient_counts.index, "Frequency": ingredient_counts.values})

        # Plot as a line chart
        st.line_chart(hist_df.set_index("Number of Ingredients"))

        # Correlation Heatmap
        st.subheader("Correlation Heatmap")
        with st.spinner("Generating heatmap..."):
            numeric_features = ["minutes", "n_steps", "n_ingredients"]
            corr_matrix = st.session_state["recipes_filtered"][numeric_features].corr()
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
            st.pyplot(fig)

        # Sentiment Analysis Word Cloud
        st.subheader("Review Sentiment Analysis")
        with st.spinner("Generating word cloud..."):
            review_text = " ".join(st.session_state["interactions"]["review"].dropna())
            wordcloud = WordCloud(width=800, height=400, background_color="white").generate(review_text)
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.imshow(wordcloud, interpolation="bilinear")
            ax.axis("off")
            st.pyplot(fig)

        st.success("Visuals generated.")
    else:
        st.error("Please load data first.")
    progress_bar.progress(40)

# Feature Engineering and Selection
st.sidebar.header("Feature Engineering and Selection")
if st.sidebar.button("Engineer & Select Features"):
    if "recipes_filtered" in st.session_state and "interactions" in st.session_state:
        recipes, interactions = engineer_features(
            st.session_state["recipes_filtered"], st.session_state["interactions"]
        )
        selected_features = select_features(recipes)
        selected_features.to_csv("selected_features.csv", index=False)
        st.session_state["selected_features"] = selected_features
        st.success("Features engineered and selected.")
    else:
        st.error("Please load data first.")
    progress_bar.progress(60)

# Load Selected Features and Prepare Data
st.sidebar.header("Prepare Data for Modeling")
if st.sidebar.button("Prepare Data"):
    if "selected_features" in st.session_state:
        selected_features = pd.read_csv("selected_features.csv")
        selected_features["rating_binary"] = (selected_features["avg_rating"] >= 4.0).astype(int)
        st.session_state["selected_features"] = selected_features
        st.session_state["target_column"] = "rating_binary"
        st.success("Data prepared for training.")
    else:
        st.error("Please engineer and select features first.")
    progress_bar.progress(70)

# Train and Evaluate Model
st.sidebar.header("Train and Evaluate Model")
if st.sidebar.button("Train & Evaluate Model"):
    if "selected_features" in st.session_state:
        selected_features = st.session_state["selected_features"]
        target_column = st.session_state["target_column"]

        # Split Data
        X_train, X_test, y_train, y_test = train_test_split_data(selected_features, target_column)

        # Train Model
        model = train_model(X_train, y_train)
        st.session_state["model"] = model
        st.success("Model training completed.")

        # Model Evaluation
        st.subheader("Model Evaluation Results")
        evaluation_results = streamlit_evaluate_model(model, X_test, y_test)

        if evaluation_results:
            st.metric(label="Model Accuracy", value=f"{evaluation_results['Accuracy']:.4f}")

            # Classification Report
            report_df = pd.DataFrame(evaluation_results["Classification Report"]).transpose()
            st.subheader("Classification Report")
            st.dataframe(report_df)

            # Confusion Matrix Heatmap
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

import io
import contextlib

# =============================================================================
# Validation Checks
# =============================================================================
st.sidebar.header("Validation Checks")
if st.sidebar.button("Run Validation Checks"):
    if "selected_features" in st.session_state and "target_column" in st.session_state:
        X_train, X_test, y_train, y_test = train_test_split_data(
            st.session_state["selected_features"], st.session_state["target_column"]
        )

        def capture_print(func, *args, **kwargs):
            """Captures print output from a function and returns it as a string."""
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                func(*args, **kwargs)
            return buffer.getvalue()

        st.subheader("Class Distribution Check")
        class_distribution_output = capture_print(check_class_distribution, y_train, y_test)
        st.text(class_distribution_output)

        st.subheader("Data Leakage Check")
        data_leakage_output = capture_print(check_data_leakage, X_train, X_test)
        st.text(data_leakage_output)

        st.subheader("Feature Correlation Inspection")
        correlation_output = capture_print(inspect_feature_correlations, st.session_state["selected_features"], st.session_state["target_column"])
        st.text(correlation_output)

        st.subheader("Cross-Validation")
        model = train_model(X_train, y_train)  # Train model before cross-validation
        cross_validation_output = capture_print(cross_validate_model, model, X_train, y_train)
        st.text(cross_validation_output)

        st.subheader("Manual Prediction Review")
        prediction_review_output = capture_print(manually_review_predictions, model, X_test, y_test)
        st.text(prediction_review_output)

        st.success("Validation checks completed.")
    else:
        st.error("Please prepare data before running validation checks.")

st.button("Rerun App")