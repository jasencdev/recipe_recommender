# Copilot Instructions for Recipe Recommender

## Project Overview

This is a **Recipe Recommendation System** that suggests recipes for busy individuals with limited time and patience. The system uses machine learning (K-means clustering) to recommend recipes based on cooking time and complexity preferences.

**Live Application**: [recipe-recommender.jasenc.dev](https://recipe-recommender.jasenc.dev/)  
**Dataset**: Food.com Recipes and Interactions from Kaggle  
**Author**: Jasen Carroll (Data Science Foundations Capstone)

## Architecture & Components

### Core Application Structure
```
recipe-recommender/
├── food-recipe-recommender/           # Main application directory
│   ├── app.py                        # Streamlit web application (main entry point)
│   ├── main.py                       # ML pipeline & model training script
│   ├── models/                       # Trained ML models (joblib files)
│   ├── data/                         # Dataset files (not in git)
│   └── src/                          # Core modules
│       ├── preprocessing.py          # Data loading, cleaning, EDA
│       ├── features.py               # Feature engineering & selection
│       ├── modeling.py               # ML model training & optimization
│       ├── recommender.py            # Recipe recommendation engine
│       └── validation_checks.py      # Data validation & model checks
├── requirements.txt                  # Python dependencies
├── railway.json                      # Deployment configuration
└── .gitignore                        # Git ignore (excludes data/, models/, .venv/)
```

### Key Technologies
- **Web Framework**: Streamlit (interactive web app)
- **ML/Data**: scikit-learn, pandas, numpy (K-means clustering)
- **Visualization**: matplotlib, seaborn, altair
- **Deployment**: Railway platform
- **Code Formatting**: Black formatter (configured)

## Development Guidelines

### Code Style & Formatting
- **ALWAYS** use Black formatter for code formatting
- Run `python -m black .` before committing
- Follow PEP 8 conventions for naming and structure
- Use docstrings for all functions and classes
- Keep imports organized (stdlib, third-party, local)

### Project Conventions
- Use relative imports within the `src/` module
- Store ML models in `models/` directory as `.joblib` files
- Data files go in `data/` directory (excluded from git)
- Use `Path` objects for file paths, not string concatenation
- Validate inputs using functions from `validation_checks.py`

### Common Development Tasks

#### Running the Application
```bash
# Install dependencies
pip install -r requirements.txt

# Run Streamlit web app
cd food-recipe-recommender
streamlit run app.py

# Run ML pipeline (model training)
python main.py
```

#### Data Setup
```bash
# Download dataset (manual step required)
curl -L -o ~/Downloads/recipe-recommender-data.zip \
  https://www.kaggle.com/api/v1/datasets/download/shuyangli94/food-com-recipes-and-user-interactions

# Extract to food-recipe-recommender/data/
```

#### Code Quality
```bash
# Format code
python -m black .

# Check formatting
python -m black --check .
```

## Module Descriptions

### `app.py` - Streamlit Web Application
- **Purpose**: User-facing web interface for recipe recommendations
- **Key Functions**:
  - `load_model()`: Loads trained ML model from models/ directory
  - `main()`: Main Streamlit app with sidebar controls and recipe display
- **Features**: Search recipes, get recommendations based on cook time/complexity
- **User Flow**: Name input → preferences → search/recommend → detailed recipe view

### `main.py` - ML Pipeline
- **Purpose**: Complete data science pipeline from raw data to trained model
- **Workflow**: Load data → clean → EDA → preprocess → feature engineering → model training → validation
- **Model**: K-means clustering with 6 clusters for recipe grouping
- **Output**: Saves trained model as `recipe_recommender_model.joblib`

### `src/preprocessing.py` - Data Processing
- **Functions**:
  - `load_data()`: Load raw CSV files from data/ directory
  - `summary_data()`: Data exploration and statistics
  - `preprocess_data()`: Data cleaning and preparation
  - Plotting functions for EDA visualizations

### `src/features.py` - Feature Engineering
- **Key Function**: `select_features()`: Creates model-ready feature set
- **Features Created**:
  - `avg_rating`: Average user rating per recipe
  - `num_interactions`: Recipe popularity metric
  - `complexity_score`: Combines steps and ingredients count
- **Filtering**: Only recipes with rating ≥4, interactions ≥3, complexity ≤100

### `src/modeling.py` - Machine Learning
- **Functions**:
  - `optimal_number_of_clusters()`: Elbow method for K-means
  - `optimal_silhouette_score()`: Silhouette analysis
  - `train_test_split_data()`: Data splitting utilities

### `src/recommender.py` - Recommendation Engine
- **Class**: `RecipeRecommender` - KMeans-based recommendation system
- **Features**: Cook time and complexity-based clustering
- **Methods**: Model training, prediction, recipe recommendation
- **Validation**: Input validation using `validation_checks.py`

### `src/validation_checks.py` - Data Validation
- **Purpose**: Comprehensive input validation and data quality checks
- **Functions**: Schema validation, numeric range checks, data leakage detection
- **Usage**: Called throughout the pipeline to ensure data integrity

## Business Logic & Domain Knowledge

### Recipe Complexity Scoring
- **Formula**: `complexity_score = n_steps × n_ingredients`
- **Filtering**: Recipes with complexity ≤ 100 (for busy users)
- **Purpose**: Helps users find quick, simple recipes

### Quality Filters
- **Minimum Rating**: ≥ 4.0 (only highly-rated recipes)
- **Minimum Interactions**: ≥ 3 (ensures recipe popularity)
- **Maximum Cook Time**: ≤ 180 minutes (reasonable time limit)

### Recommendation Algorithm
1. **Clustering**: K-means with 6 clusters based on cook time and complexity
2. **User Input**: Desired cook time and complexity level
3. **Matching**: Find recipes in appropriate cluster
4. **Ranking**: By similarity to user preferences

## Important Implementation Notes

### Error Handling
- Model loading includes comprehensive error handling in `app.py`
- Validation functions raise specific exceptions with clear messages
- Streamlit displays user-friendly error messages for missing models/data

### Data Dependencies
- **Critical**: Raw data files must be in `food-recipe-recommender/data/`
- **Files**: `RAW_recipes.csv`, `RAW_interactions.csv`
- **Source**: Kaggle Food.com dataset (manual download required)

### Model Persistence
- Models saved as `.joblib` files in `models/` directory
- Model loading handles missing files gracefully
- App continues to function even without trained model (shows error)

### Deployment
- **Platform**: Railway (configured via `railway.json`)
- **Command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
- **Environment**: Requires all dependencies from `requirements.txt`

## Code Examples

### Adding New Features
```python
# In src/features.py
def select_features(recipes, interactions):
    # Add new feature
    recipes["new_feature"] = recipes["column1"] * recipes["column2"]
    
    # Update feature list
    selected_features = recipes[["minutes", "complexity_score", "new_feature"]]
    return selected_features
```

### Model Validation
```python
# Always validate inputs
from src.validation_checks import validate_numeric_range, validate_input_data

validate_numeric_range(cook_time, 1, 180, "cook_time")
validate_input_data(recipes_df, required_columns=["minutes", "complexity_score"])
```

### Streamlit Components
```python
# Standard pattern for Streamlit controls
user_input = st.sidebar.text_input("Enter name:")
cook_time = st.sidebar.slider("Cook Time (minutes)", 1, 180, 30)

if st.button("Get Recommendations"):
    recommendations = recommender.recommend(cook_time, complexity)
    for _, recipe in recommendations.iterrows():
        st.write(f"## {recipe['name'].title()}")
```

This is a production-ready ML application with a focus on user experience and code quality. When making changes, prioritize data validation, error handling, and maintaining the existing user interface patterns.