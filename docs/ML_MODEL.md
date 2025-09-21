# Machine Learning Model and Data Pipeline Documentation

This document provides comprehensive documentation for the Recipe Recommender's machine learning model, data pipeline, and recommendation system.

## Overview

The Recipe Recommender uses a K-Means clustering-based recommendation system combined with similarity scoring to provide personalized recipe recommendations. The system processes recipe data, enriches it with detailed ingredient information, and trains a model to cluster similar recipes based on cooking time, complexity, and ingredient count.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Data Pipeline](#data-pipeline)
- [Feature Engineering](#feature-engineering)
- [Model Architecture](#model-architecture)
- [Training Process](#training-process)
- [Recommendation Algorithm](#recommendation-algorithm)
- [Model Deployment](#model-deployment)
- [Performance Optimization](#performance-optimization)
- [Maintenance and Updates](#maintenance-and-updates)

## Architecture Overview

### System Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Raw Data      │    │  Data Pipeline  │    │  ML Model       │
│                 │    │                 │    │                 │
│ • RAW_recipes   │───►│ • Preprocessing │───►│ • K-Means       │
│ • Interactions  │    │ • Feature Eng.  │    │ • Scaler        │
│ • Ingredients   │    │ • Validation    │    │ • Clustering    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Web Scraping    │    │ Data Storage    │    │ Recommendation  │
│                 │    │                 │    │ Service         │
│ • Async scraper │    │ • SQLite DB     │    │                 │
│ • Ingredient    │    │ • Joblib files  │    │ • Recipe search │
│   enrichment    │    │ • CSV exports   │    │ • Similarity    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Data Flow

1. **Data Ingestion**: Load raw recipe and interaction data
2. **Preprocessing**: Clean, filter, and normalize data
3. **Feature Engineering**: Create derived features and complexity scores
4. **Ingredient Enrichment**: Scrape detailed ingredients from Food.com
5. **Model Training**: Fit K-Means clustering and scaler
6. **Model Persistence**: Save trained models to disk
7. **Inference**: Load models and provide recommendations

## Data Pipeline

### Data Sources

#### Primary Datasets

**RAW_recipes.csv**
- Recipe metadata from Food.com
- Contains recipe names, ingredients, steps, timing, and nutritional info
- Approximately 230,000+ recipes

**RAW_interactions.csv**
- User interaction data (ratings, reviews)
- Links users to recipes with feedback
- Used for popularity and quality scoring

#### Enriched Data

**Ingredient Scraping**
- Detailed ingredient information scraped from Food.com
- Enhanced with quantities, units, and preparation methods
- Stored in SQLite database for persistence

### Data Loading and Validation

**File**: `modules/preprocessing.py`

```python
def load_data():
    """Load recipe and interaction datasets from CSV files."""
    base_dir = Path.cwd()
    recipes_path = base_dir / "../data/RAW_recipes.csv"
    interactions_path = base_dir / "../data/RAW_interactions.csv"

    recipes = pd.read_csv(recipes_path)
    interactions = pd.read_csv(interactions_path)

    return recipes, interactions
```

**Key Validation Steps:**
- File existence checking
- Schema validation
- Missing value detection
- Data type verification

### Data Preprocessing

#### Data Cleaning

```python
def preprocess_data(recipes, interactions):
    """Clean and filter recipe data for model training."""

    # Remove recipes with extreme values
    recipes_filtered = recipes[
        (recipes["num_ingredients"] <= 20) &
        (recipes["minutes"] <= 60)
    ]

    # Handle missing values
    interactions["review"] = interactions["review"].fillna("Unknown")

    return recipes_filtered, interactions
```

**Filtering Criteria:**
- Maximum 20 ingredients per recipe
- Maximum 60 minutes preparation time
- Recipes with preparation time ≤ 180 minutes (later filter)
- Non-null essential fields

#### Data Sanitization

**Quality Filters:**
- Remove recipes with complexity score > 100
- Keep only recipes with average rating ≥ 4.0
- Require minimum 3 user interactions
- Remove recipes with missing critical fields

## Feature Engineering

### Core Features

**File**: `modules/features.py`

#### Primary Features

1. **Cooking Time (`minutes`)**
   - Direct from recipe data
   - Filtered to reasonable ranges (≤ 180 minutes)

2. **Complexity Score (`complexity_score`)**
   ```python
   recipes["complexity_score"] = recipes["n_steps"] * recipes["n_ingredients"]
   ```
   - Combination of recipe steps and ingredient count
   - Higher values indicate more complex recipes

3. **Ingredient Count (`ingredient_count`)**
   - Derived from ingredients list
   - Used for clustering and similarity scoring

#### Derived Features

1. **Average Rating (`avg_rating`)**
   ```python
   avg_rating_per_recipe = interactions.groupby("recipe_id")["rating"].mean()
   ```
   - Computed from user interactions
   - Quality indicator for recipes

2. **Popularity Score (`num_interactions`)**
   ```python
   num_interactions_per_recipe = interactions.groupby("recipe_id").size()
   ```
   - Number of user interactions per recipe
   - Proxy for recipe popularity

#### Feature Selection

**Selected Columns:**
```python
selected_columns = [
    "id",              # Original Food.com recipe ID
    "name",            # Recipe name
    "avg_rating",      # Computed average rating
    "minutes",         # Cooking time
    "complexity_score", # Derived complexity
    "ingredients",     # Ingredient list
    "steps",          # Cooking steps
]
```

### Feature Scaling

**Normalization Process:**
```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
features_scaled = scaler.fit_transform(features)
```

**Scaled Features:**
- `minutes`: Cooking time (standardized)
- `complexity_score`: Recipe complexity (standardized)
- `ingredient_count`: Number of ingredients (standardized)

## Model Architecture

### K-Means Clustering

**File**: `modules/recommender.py`

#### Model Configuration

```python
class RecipeRecommender:
    def __init__(self, recipes_df, n_clusters=6):
        self.n_clusters = n_clusters
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        self.scaler = StandardScaler()
        self.feature_names = ["minutes", "complexity_score", "ingredient_count"]
```

**Key Parameters:**
- **n_clusters**: 6 (optimized through silhouette analysis)
- **random_state**: 42 (for reproducibility)
- **init**: 'k-means++' (default, better initialization)

#### Cluster Optimization

**Evaluation Methods:**

1. **Elbow Method**: Analyze within-cluster sum of squares
2. **Silhouette Score**: Measure cluster cohesion and separation

```python
def optimal_silhouette_score(selected_features):
    """Find optimal number of clusters using silhouette score."""
    silhouette_scores = []
    K_range = range(2, 11)

    for k in K_range:
        kmeans = KMeans(n_clusters=k, random_state=42)
        cluster_labels = kmeans.fit_predict(features_scaled)
        silhouette_avg = silhouette_score(features_scaled, cluster_labels)
        silhouette_scores.append(silhouette_avg)
```

**Optimal Configuration:**
- **6 clusters** determined through silhouette analysis
- Balances cluster cohesion and computational efficiency

### Model Training Pipeline

#### Training Process

```python
def _train_kmeans(self):
    """Train the K-Means clustering model."""

    # 1. Feature scaling
    self.features_scaled = pd.DataFrame(
        self.scaler.fit_transform(self.features),
        columns=self.feature_names
    )

    # 2. Cluster training
    self.kmeans = KMeans(n_clusters=self.n_clusters, random_state=42)
    self.kmeans.fit(self.features_scaled)

    # 3. Assign clusters to recipes
    self.data["cluster"] = self.kmeans.labels_

    # 4. Model persistence
    joblib.dump(self, "recipe_recommender_model.joblib")
    joblib.dump(self.scaler, "scaler.joblib")
```

#### Model Persistence

**Saved Artifacts:**
- `recipe_recommender_model.joblib`: Complete trained model
- `scaler.joblib`: Feature scaler for consistent preprocessing

**Storage Location:**
```
food-recipe-recommender/models/
├── recipe_recommender_model.joblib  (38MB)
└── scaler.joblib                    (1KB)
```

## Recommendation Algorithm

### Core Recommendation Logic

#### 1. Cluster Assignment

```python
def recommend_recipes(self, desired_time, desired_complexity, desired_ingredients):
    # Create user preference vector
    user_input = pd.DataFrame([
        [desired_time, desired_complexity, desired_ingredients]
    ], columns=self.feature_names)

    # Scale user input
    user_input_scaled = self.scaler.transform(user_input)

    # Find nearest cluster
    cluster = self.kmeans.predict(user_input_scaled)[0]
```

#### 2. Similarity Scoring

```python
def calculate_similarity_distance(x):
    return np.sqrt(
        (x["minutes"] - desired_time) ** 2 +
        (x["complexity_score"] - desired_complexity) ** 2 +
        (x["ingredient_count"] - desired_ingredients) ** 2
    )

cluster_recipes["similarity_distance"] = cluster_recipes.apply(
    calculate_similarity_distance, axis=1
)
```

#### 3. Recipe Ranking

```python
# Sort by similarity and return top N
recommendations = cluster_recipes.nsmallest(
    n_recommendations, "similarity_distance"
)
```

### Search Functionality

#### Text-Based Search

```python
def search_recipes(self, search_query, n_results=20):
    """Search recipes by name or ingredients."""

    # Search in recipe names and ingredients
    matches = self.data[
        self.data["name"].str.contains(search_query, case=False) |
        self.data["ingredients"].str.contains(search_query, case=False)
    ]

    # Relevance scoring
    matches["relevance_score"] = 0
    name_matches = matches["name"].str.contains(search_query, case=False)
    matches.loc[name_matches, "relevance_score"] += 2

    ingredient_matches = matches["ingredients"].str.contains(search_query, case=False)
    matches.loc[ingredient_matches, "relevance_score"] += 1

    return matches.nlargest(n_results, "relevance_score")
```

**Relevance Scoring:**
- Name matches: +2 points
- Ingredient matches: +1 point
- Results sorted by total relevance score

## Ingredient Enrichment Pipeline

### Async Web Scraping

**File**: `modules/async_ingredient_scraper.py`

#### Scraping Architecture

```python
class AsyncIngredientScraper:
    def __init__(self, max_concurrent=10):
        self.max_concurrent = max_concurrent
        self.session = None
        self.db_path = "enriched_ingredients.db"
```

**Key Features:**
- Asynchronous scraping for performance
- Rate limiting to respect Food.com servers
- SQLite database for persistent storage
- Progress tracking and resumption
- Error handling and retry logic

#### Scraping Process

```python
async def scrape_dataset(self, recipes_df, batch_size=50, delay_between_batches=1.0):
    """Scrape ingredients for recipes in batches."""

    async with aiohttp.ClientSession() as session:
        self.session = session

        for batch_start in range(0, len(recipes_df), batch_size):
            batch = recipes_df.iloc[batch_start:batch_start + batch_size]

            # Process batch concurrently
            tasks = [
                self.scrape_recipe_ingredients(recipe_id, recipe_name)
                for recipe_id, recipe_name in batch[['food_recipe_id', 'name']].values
            ]

            await asyncio.gather(*tasks, return_exceptions=True)
            await asyncio.sleep(delay_between_batches)
```

#### Data Storage

**SQLite Schema:**
```sql
CREATE TABLE enriched_ingredients (
    food_recipe_id INTEGER PRIMARY KEY,
    recipe_name TEXT,
    detailed_ingredients TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN DEFAULT FALSE
);
```

### Ingredient Processing

#### Ingredient Parsing

```python
def parse_detailed_ingredient(ingredient_str):
    """Parse ingredient string into structured data."""

    patterns = [
        r'^(\d+(?:\s+\d+/\d+)?)\s+(\w+)\s+(.+)$',  # "2 1/2 cups flour"
        r'^(\d+/\d+)\s+(\w+)\s+(.+)$',             # "1/2 cup sugar"
        r'^(\d+(?:\.\d+)?)\s+(\w+)\s+(.+)$',       # "1.5 cups milk"
        r'^(\d+)\s+(.+)$',                         # "2 eggs"
    ]

    for pattern in patterns:
        match = re.match(pattern, ingredient_str)
        if match:
            # Extract quantity, unit, name, preparation
            return parse_match_groups(match)
```

**Parsed Structure:**
```python
{
    'original': '2 cups all-purpose flour (sifted)',
    'quantity': 2.0,
    'unit': 'cups',
    'name': 'all-purpose flour',
    'preparation': 'sifted'
}
```

## Model Deployment

### Flask Integration

**File**: `food-recipe-recommender/app/__init__.py`

#### Model Loading

```python
def create_app():
    app = Flask(__name__)

    # Load ML model
    model_path = os.getenv('MODEL_PATH', '../models/recipe_recommender_model.joblib')
    try:
        recommender = joblib.load(model_path)
        app.config['RECOMMENDER'] = recommender
        print(f"Successfully loaded model from {model_path}")
    except Exception as e:
        print(f"Warning: Could not load model from {model_path}: {e}")
        app.config['RECOMMENDER'] = None
```

#### API Integration

**File**: `food-recipe-recommender/app/blueprints/recipes.py`

```python
def _resolve_recommender():
    """Get the loaded recommender instance."""
    try:
        import app as app_module
        if hasattr(app_module, 'recipe_recommender'):
            return getattr(app_module, 'recipe_recommender')
    except Exception:
        pass
    return current_app.config.get('RECOMMENDER')
```

### Docker Deployment

**Model Requirements:**
```dockerfile
# Ensure model file exists in container
COPY food-recipe-recommender/models/recipe_recommender_model.joblib /app/food-recipe-recommender/models/

# Set model path environment variable
ENV MODEL_PATH=/app/food-recipe-recommender/models/recipe_recommender_model.joblib
```

## Performance Optimization

### Model Performance

#### Memory Optimization

**Model Size Management:**
- Model file: ~38MB (compressed with joblib)
- In-memory footprint: ~100MB (including data)
- Lazy loading: Model loaded once at startup

#### Inference Speed

**Recommendation Performance:**
- Cluster prediction: O(1) after training
- Similarity calculation: O(n) where n = cluster size
- Typical response time: <100ms for 20 recommendations

#### Caching Strategy

```python
# API-level caching for saved recipes
saved_recipe_cache: Set[str] | None = None
cache_last_updated: number = 0
CACHE_DURATION = 5 * 60 * 1000  # 5 minutes
```

### Data Pipeline Optimization

#### Async Processing

**Concurrent Scraping:**
- Max 10 concurrent requests
- Batch processing (20-50 recipes per batch)
- Configurable delays between batches
- Progress persistence for resumption

#### Database Optimization

**SQLite Performance:**
```sql
-- Index for fast lookups
CREATE INDEX idx_food_recipe_id ON enriched_ingredients (food_recipe_id);
CREATE INDEX idx_success ON enriched_ingredients (success);
```

## Validation and Testing

### Model Validation

**File**: `modules/validation_checks.py`

#### Data Validation

```python
def validate_input_data(df):
    """Validate input DataFrame for model training."""
    if df.empty:
        raise ValueError("Input DataFrame is empty")

    required_columns = ["minutes", "complexity_score", "ingredients"]
    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
```

#### Class Distribution Check

```python
def check_class_distribution(y_train, y_test):
    """Check if class distribution is balanced across train/test sets."""
    train_dist = y_train.value_counts(normalize=True)
    test_dist = y_test.value_counts(normalize=True)

    print("Training set distribution:")
    print(train_dist)
    print("\nTest set distribution:")
    print(test_dist)
```

#### Data Leakage Detection

```python
def check_data_leakage(X_train, X_test):
    """Check for potential data leakage between train and test sets."""
    # Compare feature distributions
    # Check for identical rows
    # Validate temporal consistency
```

### Integration Testing

**Live API Testing:**
```bash
# Test recommendation endpoint
LIVE_API=1 uv run pytest tests/test_integration_live.py

# Test with custom API endpoint
API_BASE_URL=http://localhost:8080/api LIVE_API=1 uv run pytest
```

## Maintenance and Updates

### Model Retraining

#### Training Pipeline

```bash
cd food-recipe-recommender/data-pipeline
python main.py
```

**Retraining Steps:**
1. Data validation and preprocessing
2. Feature engineering and selection
3. Ingredient enrichment (optional)
4. Model training with optimal parameters
5. Validation and testing
6. Model persistence and deployment

#### Model Versioning

**Version Control:**
- Models stored with timestamps
- Previous versions archived
- Rollback capability for production

### Data Updates

#### Adding New Recipes

```python
# Update dataset with new recipes
new_recipes = load_new_recipe_data()
combined_data = pd.concat([existing_data, new_recipes])

# Retrain model with updated data
recommender = RecipeRecommender(combined_data)
```

#### Ingredient Database Maintenance

```python
# Resume incomplete scraping
scraper = AsyncIngredientScraper()
asyncio.run(scraper.scrape_dataset(recipes_df))

# Export enriched data
enriched_df = scraper.export_to_csv("enriched_recipes.csv")
```

### Performance Monitoring

#### Model Metrics

**Recommendation Quality:**
- User engagement metrics
- Recipe save/unsave ratios
- Search result relevance

**System Performance:**
- Response time monitoring
- Memory usage tracking
- Error rate analysis

#### Health Checks

```python
# Model availability check
if not current_app.config.get('RECOMMENDER'):
    return jsonify({'error': 'Recipe recommendation service unavailable'}), 500

# Data integrity check
def validate_model_data():
    recommender = current_app.config['RECOMMENDER']
    if recommender.data.empty:
        raise ValueError("Model data is empty")
```

### Troubleshooting

#### Common Issues

**Model Loading Failures:**
- Check model file existence
- Verify file permissions
- Validate joblib version compatibility

**Poor Recommendation Quality:**
- Review cluster assignments
- Check feature scaling consistency
- Validate input parameter ranges

**Performance Issues:**
- Monitor memory usage
- Check database query performance
- Analyze recommendation latency

#### Debug Commands

```bash
# Check model file
ls -la food-recipe-recommender/models/

# Validate model loading
python -c "import joblib; joblib.load('recipe_recommender_model.joblib')"

# Test recommendation pipeline
cd food-recipe-recommender/data-pipeline
python -c "from modules.recommender import RecipeRecommender; print('Import successful')"
```

---

For API integration details, see [API.md](API.md).

For deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

For database schema, see [DATABASE.md](DATABASE.md).