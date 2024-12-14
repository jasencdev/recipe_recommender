import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import os

# Build the absolute file path
base_dir = os.path.dirname(os.path.abspath(__file__))
recipes_data_path = os.path.join(base_dir, '../data/RAW_recipes.csv')
interactions_data_path = os.path.join(base_dir, '../data/RAW_interactions.csv')

# Load the dataset
recipes = pd.read_csv(recipes_data_path)
interactions = pd.read_csv(interactions_data_path)

# Apply log transformation
recipes['log_minutes'] = np.log1p(recipes['minutes'])

# Define a threshold to exclude outliers
threshold = np.percentile(recipes['minutes'], 99)  # 99th percentile
recipes_filtered = recipes[recipes['minutes'] <= threshold]

# Plot histogram of preparation time
plt.hist(recipes_filtered['minutes'], bins=50, edgecolor='blue')
plt.title('Distribution of Preparation Time (minutes)')
plt.xlabel('Preparation Time (minutes)')
plt.ylabel('Frequency')
plt.show()