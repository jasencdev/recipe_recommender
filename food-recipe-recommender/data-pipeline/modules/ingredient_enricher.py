"""
Ingredient Enricher Module
Fetches full ingredient information (with quantities) from Food.com
using recipe IDs from the dataset.
"""

import ast
import json
import re
import time
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup


class IngredientEnricher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )
        self.successful_fetches = 0
        self.failed_fetches = 0
        self.cache = {}  # Cache successful requests

    def clean_recipe_name_for_url(self, name):
        """Convert recipe name to URL-friendly format"""
        # Remove special characters and replace spaces with hyphens
        cleaned = re.sub(r"[^\w\s-]", "", name.lower())
        cleaned = re.sub(r"\s+", "-", cleaned.strip())
        # Remove multiple consecutive hyphens
        cleaned = re.sub(r"-+", "-", cleaned)
        return cleaned.strip("-")

    def fetch_ingredients_from_food_com(self, recipe_id, recipe_name):
        """
        Attempt to fetch ingredients with quantities from Food.com

        Args:
            recipe_id: Food.com recipe ID
            recipe_name: Recipe name for URL construction

        Returns:
            List of ingredients with quantities, or None if failed
        """
        # Check cache first
        cache_key = f"{recipe_id}_{recipe_name}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            # Try different URL formats
            cleaned_name = self.clean_recipe_name_for_url(recipe_name)
            url_formats = [
                f"https://www.food.com/recipe/{cleaned_name}-{recipe_id}",
                f"https://www.food.com/recipe/{recipe_id}",
                f"https://www.food.com/recipe/{recipe_id}/{cleaned_name}",
            ]

            for url in url_formats:
                try:
                    print(f"    Trying: {url}")
                    response = self.session.get(url, timeout=15)
                    if response.status_code == 200:
                        ingredients = self._extract_ingredients_from_html(response.text)
                        if ingredients:
                            # Cache successful result
                            self.cache[cache_key] = ingredients
                            return ingredients
                except requests.RequestException as e:
                    print(f"    Request failed: {e}")
                    continue

            # Cache failed attempt to avoid retrying
            self.cache[cache_key] = None
            return None

        except Exception as e:
            print(f"    Error fetching recipe {recipe_id}: {e}")
            return None

    def _extract_ingredients_from_html(self, html):
        """Extract ingredients from Food.com HTML"""
        try:
            soup = BeautifulSoup(html, "html.parser")

            # Look for JSON-LD structured data first (most reliable)
            json_scripts = soup.find_all("script", type="application/ld+json")
            for script in json_scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, list):
                        data = data[0]

                    if data.get("@type") == "Recipe" and "recipeIngredient" in data:
                        ingredients = data["recipeIngredient"]
                        if ingredients:
                            return ingredients
                except Exception:
                    continue

            # Look for common ingredient selectors on Food.com
            ingredient_selectors = [
                ".recipe-ingredients li",
                ".ingredients li",
                ".recipe-ingredient",
                '[data-testid="recipe-ingredient"]',
                ".ingredient-item",
                ".recipe-summary__item",
                ".ingredients__section li",
            ]

            for selector in ingredient_selectors:
                ingredients = soup.select(selector)
                if ingredients:
                    ingredient_list = []
                    for ing in ingredients:
                        text = ing.get_text(strip=True)
                        if text and len(text) > 2:  # Filter out empty or very short items
                            ingredient_list.append(text)

                    if ingredient_list and len(ingredient_list) > 1:  # Need at least 2 ingredients
                        return ingredient_list

            return None

        except Exception as e:
            print(f"    Error parsing HTML: {e}")
            return None

    def enrich_recipe_dataframe(
        self, df, max_requests=None, delay=2.0, start_from=0, save_progress_every=50
    ):
        """
        Enrich a recipe dataframe with detailed ingredients

        Args:
            df: Recipe dataframe with 'food_recipe_id', 'name', and 'ingredients' columns
            max_requests: Maximum number of web requests to make (None for all)
            delay: Delay between requests in seconds
            start_from: Index to start from (for resuming)
            save_progress_every: Save progress every N recipes

        Returns:
            Enhanced dataframe with 'detailed_ingredients' column
        """
        df = df.copy()

        # Initialize detailed_ingredients column if it doesn't exist
        if "detailed_ingredients" not in df.columns:
            df["detailed_ingredients"] = df["ingredients"]  # Default to original

        total_recipes = len(df) if max_requests is None else min(max_requests, len(df))
        end_index = start_from + total_recipes if max_requests else len(df)

        print("Starting ingredient enrichment...")
        print(
            f"Processing recipes {start_from} to {end_index - 1} (total: {end_index - start_from})"
        )
        print(f"Delay between requests: {delay} seconds")

        progress_file = Path("enrichment_progress.csv")

        for idx in range(start_from, end_index):
            row = df.iloc[idx]
            # Use food_recipe_id if available, fallback to id
            recipe_id = row.get("food_recipe_id", row.get("id", None))
            recipe_name = row["name"]

            print(f"\nProcessing recipe {idx + 1}/{len(df)}: {recipe_name}")
            print(f"  Food.com Recipe ID: {recipe_id}")

            # Skip if already enriched (not just original ingredients)
            current_ingredients = row.get("detailed_ingredients", row["ingredients"])
            original_ingredients = (
                ast.literal_eval(row["ingredients"])
                if isinstance(row["ingredients"], str)
                else row["ingredients"]
            )

            if (
                isinstance(current_ingredients, list)
                and current_ingredients != original_ingredients
                and len(current_ingredients) > 0
            ):
                print("  ↻ Already enriched, skipping")
                self.successful_fetches += 1
                continue

            # Fetch detailed ingredients
            detailed_ingredients = self.fetch_ingredients_from_food_com(recipe_id, recipe_name)

            if detailed_ingredients and len(detailed_ingredients) > 1:
                df.at[idx, "detailed_ingredients"] = detailed_ingredients
                self.successful_fetches += 1
                print(f"  ✓ Found {len(detailed_ingredients)} detailed ingredients")
                print(f"    Sample: {detailed_ingredients[0]}")
            else:
                self.failed_fetches += 1
                print("  ✗ Could not fetch detailed ingredients, keeping original")

            # Save progress periodically
            if (idx - start_from + 1) % save_progress_every == 0:
                print(
                    f"\n📊 Saving progress... ({self.successful_fetches} successful, {self.failed_fetches} failed)"
                )
                df.to_csv(progress_file, index=False)

            # Respectful delay
            if idx < end_index - 1:
                time.sleep(delay)

        print("\n🎉 Enrichment complete!")
        print(f"Successfully enriched: {self.successful_fetches}")
        print(f"Failed to enrich: {self.failed_fetches}")
        print(
            f"Success rate: {self.successful_fetches / (self.successful_fetches + self.failed_fetches) * 100:.1f}%"
        )

        # Save final results
        output_file = Path("enriched_recipes.csv")
        df.to_csv(output_file, index=False)
        print(f"Results saved to: {output_file}")

        return df

    def sample_test(self, df, num_samples=5):
        """Test the enricher with a few sample recipes"""
        print("🧪 Testing ingredient enrichment with sample recipes...\n")

        sample_df = df.head(num_samples).copy()
        enriched_df = self.enrich_recipe_dataframe(sample_df, max_requests=num_samples, delay=1.0)

        print("\n📋 Results Summary:")
        print("-" * 80)

        for _idx, row in enriched_df.iterrows():
            print(f"\nRecipe: {row['name']}")
            print(f"ID: {row['id']}")

            original = (
                ast.literal_eval(row["ingredients"])
                if isinstance(row["ingredients"], str)
                else row["ingredients"]
            )
            detailed = row["detailed_ingredients"]

            print(f"Original ingredients ({len(original)}): {original[:3]}...")
            if isinstance(detailed, list) and detailed != original:
                print(f"Detailed ingredients ({len(detailed)}): {detailed[:3]}...")
                print("✅ ENRICHED")
            else:
                print("❌ NOT ENRICHED")

        return enriched_df


def load_processed_dataset():
    """Load the processed dataset by running the data pipeline"""
    print("📚 Loading processed dataset...")

    # Import pipeline modules
    from features import select_features
    from preprocessing import load_data, preprocess_data

    # Run the data pipeline
    recipes, interactions = load_data()
    recipes_cleaned = recipes.dropna()
    recipes_cleaned = recipes_cleaned[recipes_cleaned["minutes"] <= 180]

    recipes_cleaned, interactions_cleaned = preprocess_data(recipes_cleaned, interactions)
    selected_features = select_features(recipes_cleaned, interactions_cleaned)

    print(f"Processed dataset: {len(selected_features)} recipes")
    print(f"Columns: {list(selected_features.columns)}")

    return selected_features


def main():
    """Main function to run the enrichment"""
    try:
        df = load_processed_dataset()
    except Exception as e:
        print(f"❌ Error loading processed dataset: {e}")
        print("Falling back to loading from saved CSV if available...")

        # Try to load from saved processed data
        processed_path = Path("processed_recipes.csv")
        if processed_path.exists():
            df = pd.read_csv(processed_path)
            print(f"Loaded {len(df)} recipes from saved file")
        else:
            print("❌ No processed data found. Please run the data pipeline first.")
            return

    # Create enricher
    enricher = IngredientEnricher()

    # Ask user what they want to do
    print("\nChoose an option:")
    print("1. Test with 5 sample recipes")
    print("2. Enrich first 100 recipes")
    print("3. Enrich first 1000 recipes")
    print("4. Enrich ALL recipes (this will take a very long time!)")

    choice = input("\nEnter choice (1-4): ").strip()

    if choice == "1":
        enricher.sample_test(df, 5)
    elif choice == "2":
        enricher.enrich_recipe_dataframe(df, max_requests=100, delay=1.5)
    elif choice == "3":
        enricher.enrich_recipe_dataframe(df, max_requests=1000, delay=1.0)
    elif choice == "4":
        confirm = input(
            "This will process ALL 231k+ recipes and take many hours. Continue? (yes/no): "
        )
        if confirm.lower() == "yes":
            enricher.enrich_recipe_dataframe(df, delay=0.5)
        else:
            print("Cancelled.")
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()
