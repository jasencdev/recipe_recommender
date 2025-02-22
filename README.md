# Easy & Quick Food Recipe Recommender

Problem: Create a recommendation system that suggests recipes for busy individuals that have
limited time and patience on their hands.

Dataset: Food.com Recipes and Interactions

This was the problem I chose as part of Quantic's Data Science Foundations Capstone.

Live Model: [click here](https://food-recipe-recommender.streamlit.app/)

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
