# Easy & Quick Food Recipe Recommender

Problem: Create a recommendation system that suggests recipes for busy individuals that have
limited time and patience on their hands.

Dataset: Food.com Recipes and Interactions

Live Model: [click here](https://recipe-recommender.jasenc.dev/)

```text
recipe-recommender/
│── .venv/                          # Virtual environment (not in Git)
│── food-recipe-recommender/
│   ├── data/                       # Datasets (not in Git)
│   ├── models/                     # Model outputs from running main.py
│   ├── src/
│   │   ├── __init__.py             # Python entry point for src module
│   │   ├── preprocessing.py        # Data cleaning
│   │   ├── feature_engineering.py  # Feature engineering file
│   │   ├── feature_selection.py    # Feature selection file
│   │   ├── modeling.py             # File for modeling
│   │   ├── validation_checks.py    # Developed validation checks
│   │── app.py                      # Streamlit application
│   │── main.py                     # Main model pipeline
│── .gitignore                      # Git ignore config file
│── LICENSE                         # How the app can be used
│── railway.json                    # Necessary file for hosting on Railway
│── README.md                       # Instructions for use
│── requirements.txt                # Dependencies
```

## Installation

This is for windows because Unix operating systems can install virtualenv as a package outside of `pip`.

```bash
pip install virtualenv
python -m venv .venv
```

and since i use Git Bash on Windows we need to activate that correctly.

`source .venv/Scripts/activate`

or if you're using powershell you can

`.venv\Scripts\activate.ps1`

and we can get on with it.

`pip install -r requirements.txt`

## Get the Data

The data can be directly downloaded from the following bash script using your terminal.

```bash
curl -L -o ~/Downloads/recipe-recommender-data.zip\
  https://www.kaggle.com/api/v1/datasets/download/shuyangli94/food-com-recipes-and-user-interactions
```

Unzip the file downloaded to your downloads file and move the extracted `recipe-recommender-data` to `data` folder under `src`. Note: Running this code block will download the zip file.

## Run the model

You can run this locally in two different ways.

1. The model is packaged in this repo. Run an interactive version using Steamlit. This will walk you through the steps of loading and
evaluating the model.
`steamlit run food-recipe-recommender/app.py`

2. You can go over the data science process and rebuild the model by running:
`python food-recipe-recommender/main.py`

## Author

Jasen Carroll \
08 Feb 2025

## Testing & QA

- Backend unit tests:
  - Run: `uv run pytest -q -p no:cacheprovider`
  - With coverage: `uv run pytest -q -p no:cacheprovider --cov=app --cov-report=term-missing`

- Frontend unit tests (Vitest):
  - From `food-recipe-recommender/app/frontend`: `npm run test` (watch) or `npm run test:run` (coverage/CI)

- Live integration tests (hit running backend):
  - Start the Flask server locally
  - Run: `LIVE_API=1 uv run pytest -q -p no:cacheprovider tests/test_integration_live.py`
  - Optional: override base URL, e.g. `API_BASE_URL=http://localhost:5000/api`

- Makefile shortcuts (from repo root):
  - `make test` — backend unit tests
  - `make test-cov` — backend tests with coverage
  - `make test-frontend` — frontend tests (watch)
  - `make test-frontend-cov` — frontend tests with coverage
  - `make test-live` — live integration tests (override API with `make test-live API=http://localhost:5000/api`)

- CI & Coverage:
  - GitHub Actions runs backend and frontend tests on pushes/PRs.
  - Codecov reports coverage with separate flags for backend and frontend (thresholds in `codecov.yml`).
