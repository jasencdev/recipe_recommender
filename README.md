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
│   ├── src/
│   │   ├── data/                   # Datasets (not in Git)
│   │   ├── __init__.py             # Python entry point for src module
│   │   ├── preprocessing.py        # Data cleaning
│   │   ├── feature_engineering.py  # Feature engineering file
│   │   ├── feature_selection.py    # Feature selection file
│   │   ├── modeling.py             # File for modeling
│   │   ├── validation_checks.py    # Developed validation checks
│   │── app.py                      # Streamlit application
│   │── main.py                     # Main model pipeline
├── images/                         # Output images
│── .gitignore                      # Git ignore config file
│── LICENSE                         # How the app can be used
│── README.md                       # Instructions for use
│── recipe_recommender_mode.joblib  # Saved model
│── requirements.txt                # Dependencies
│── selected_features.csv           # CSV output from the model
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

## Running the model and all it's outputs

```bash
.venv➜ recipe-recommender (main) ✔ python food-recipe-recommender/main.py
                                         name      id  minutes  ...                                        description                                        ingredients n_ingredients
0  arriba   baked winter squash mexican style  137739       55  ...  autumn is my favorite time of year to cook! th...  ['winter squash', 'mexican seasoning', 'mixed ...             7
1            a bit different  breakfast pizza   31490       30  ...  this recipe calls for the crust to be prebaked...  ['prepared pizza crust', 'sausage patty', 'egg...             6
2                   all in the kitchen  chili  112140      130  ...  this modified version of 'mom's' chili was a h...  ['ground beef', 'yellow onions', 'diced tomato...            13
3                          alouette  potatoes   59389       45  ...  this is a super easy, great tasting, make ahea...  ['spreadable cheese with garlic and herbs', 'n...            11
6                       aww  marinated olives   25274       15  ...  my italian mil was thoroughly impressed by my ...  ['fennel seeds', 'green olives', 'ripe olives'...             9

[5 rows x 12 columns]
   user_id  recipe_id        date  rating                                             review
0    38094      40893  2003-02-17       4  Great with a salad. Cooked on top of stove for...
1  1293707      40893  2011-12-21       5  So simple, so delicious! Great for chilly fall...
2     8937      44394  2002-12-01       4  This worked very well and is EASY.  I used not...
3   126440      85009  2010-02-27       5  I made the Mexican topping and took it to bunk...
4    57222      85009  2011-10-01       5  Made the cheddar bacon topping, adding a sprin...

<class 'pandas.core.frame.DataFrame'>
Index: 209592 entries, 0 to 231636
Data columns (total 12 columns):
 #   Column          Non-Null Count   Dtype 
---  ------          --------------   ----- 
 0   name            209592 non-null  object
 1   id              209592 non-null  int64 
 2   minutes         209592 non-null  int64 
 3   contributor_id  209592 non-null  int64 
 4   submitted       209592 non-null  object
 5   tags            209592 non-null  object
 6   nutrition       209592 non-null  object
 7   n_steps         209592 non-null  int64 
 8   steps           209592 non-null  object
 9   description     209592 non-null  object
 10  ingredients     209592 non-null  object
 11  n_ingredients   209592 non-null  int64 
dtypes: int64(5), object(7)
memory usage: 20.8+ MB
None

<class 'pandas.core.frame.DataFrame'>
RangeIndex: 1132367 entries, 0 to 1132366
Data columns (total 5 columns):
 #   Column     Non-Null Count    Dtype 
---  ------     --------------    ----- 
 0   user_id    1132367 non-null  int64 
 1   recipe_id  1132367 non-null  int64 
 2   date       1132367 non-null  object
 3   rating     1132367 non-null  int64 
 4   review     1132198 non-null  object
dtypes: int64(3), object(2)
memory usage: 43.2+ MB
None
                 id        minutes  contributor_id        n_steps  n_ingredients
count  209592.00000  209592.000000    2.095920e+05  209592.000000  209592.000000
mean   226763.13407      43.145435    5.425096e+06       9.680279       9.002538
std    139744.12128      32.687181    9.855879e+07       5.795727       3.697197
min        40.00000       0.000000    2.700000e+01       0.000000       1.000000
25%    106594.00000      20.000000    5.838200e+04       6.000000       6.000000
50%    213280.50000      35.000000    1.823580e+05       9.000000       9.000000
75%    337619.75000      60.000000    4.121860e+05      12.000000      11.000000
max    537716.00000     180.000000    2.002290e+09      97.000000      43.000000
            user_id     recipe_id        rating
count  1.132367e+06  1.132367e+06  1.132367e+06
mean   1.384291e+08  1.608972e+05  4.411016e+00
std    5.014269e+08  1.303987e+05  1.264752e+00
min    1.533000e+03  3.800000e+01  0.000000e+00
25%    1.354700e+05  5.425700e+04  4.000000e+00
50%    3.309370e+05  1.205470e+05  5.000000e+00
75%    8.045500e+05  2.438520e+05  5.000000e+00
max    2.002373e+09  5.377160e+05  5.000000e+00
name              0
id                0
minutes           0
contributor_id    0
submitted         0
tags              0
nutrition         0
n_steps           0
steps             0
description       0
ingredients       0
n_ingredients     0
dtype: int64
user_id        0
recipe_id      0
date           0
rating         0
review       169
dtype: int64
2025-02-11 16:02:27.883 Python[42930:2511859] +[IMKClient subclass]: chose IMKClient_Modern
2025-02-11 16:02:27.884 Python[42930:2511859] +[IMKInputSession subclass]: chose IMKInputSession_Modern

Original dataset size: 209592 recipes

Filtered dataset size: 164727 recipes

Selected Features Sample:
                                          name  avg_rating  ...                                        ingredients                                              steps
0   arriba   baked winter squash mexican style    5.000000  ...  ['winter squash', 'mexican seasoning', 'mixed ...  ['make a choice and proceed with recipe', 'dep...
16                              chile rellenos    4.045455  ...  ['egg roll wrap', 'whole green chilies', 'chee...  ['drain green chiles', 'sprinkle cornstarch on...
17                              chinese  candy    4.833333  ...  ['butterscotch chips', 'chinese noodles', 'sal...  ['melt butterscotch chips in heavy saucepan ov...
20                      cream  of spinach soup    4.666667  ...  ['water', 'salt', 'boiling potatoes', 'fresh s...  ['bring water and salt to a boil', 'cut the po...
25            emotional balance  spice mixture    5.000000  ...  ['ground black pepper', 'ground ginger', 'grou...  ['mix the spices together and store in an airt...

[5 rows x 6 columns]

--- Class Distribution Check ---
Class Distribution in Training Set:
cluster
2    0.237560
1    0.206770
3    0.158468
0    0.154446
5    0.124902
4    0.117854
Name: proportion, dtype: float64
Class Distribution in Test Set:
cluster
2    0.239052
1    0.208556
0    0.158260
3    0.154141
5    0.124079
4    0.115913
Name: proportion, dtype: float64

--- Data Leakage Check ---
No data leakage detected.
Model and scaler saved successfully

Recommended Recipes:
       minutes  complexity_score  similarity_distance
11732       30                50                  0.0
13588       30                50                  0.0
14131       30                50                  0.0
15390       30                50                  0.0
27262       30                50                  0.0
```

## Author
Jasen Carroll \
08 Feb 2025