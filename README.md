# recipe-recommender

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

Unzip the file downloaded to your downloads file and move the extracted `recipe-recommender-data` to `data` folder under `src`. Note: Running the next code block will download the zip file.

## Then let's import the data

Note: You should check `food-recipe-recommender/src/preprocessing.py` to make sure the right file paths are set based on your system.

```bash
def load_data():
    '''Module for loading data'''

    # Build the absolute file path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # For Unix
    # recipes_data_path = os.path.join(base_dir, '../data/RAW_recipes.csv')
    # interactions_data_path = os.path.join(base_dir, '../data/RAW_interactions.csv')
    
    # For Windows
    recipes_data_path = os.path.join(base_dir, 'data\RAW_recipes.csv')
    interactions_data_path = os.path.join(base_dir, 'data\RAW_interactions.csv')

    # Load the dataset
    recipes = pd.read_csv(recipes_data_path)
    interactions = pd.read_csv(interactions_data_path)

    return recipes, interactions
```

## Run the model

`python food-recipe-recommender/main.py`

## Get the outputs/see the images

```bash
Original dataset size: 231637 recipes
Original dataset size: 226657 recipes
Filtered dataset size: 214249 recipes
Filtered dataset size: 214249 recipes
```

![prep_time](images/prep_time.png)
![ratings](images/ratings.png)
![num_ingredients](images/num_ingredients.png)
![heat_map](images/heat_map.png)
![review_sentiment](images/review_sentiment.png)

```bash
Selected features saved to 'selected_features.csv'.
Model training completed.
Accuracy: 0.9978296382730455
Precision: 0.9974639578796483
Recall: 0.9999723650030399
F1 Score: 0.9987165863958158
ROC-AUC Score: 0.9999993655230289

Confusion Matrix:
[[ 6572    92]
 [    1 36185]]
```
