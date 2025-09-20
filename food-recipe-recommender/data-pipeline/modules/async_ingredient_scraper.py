"""
Async Ingredient Scraper
Continuously scrapes Food.com for detailed ingredient information with quantities.
Stores results in SQLite database with connection pooling and retry logic.
"""

import asyncio
import aiohttp
import sqlite3
import json
import time
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from bs4 import BeautifulSoup
import pandas as pd
import ast
from datetime import datetime
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class ScrapingResult:
    food_recipe_id: int
    success: bool
    detailed_ingredients: Optional[List[str]]
    error_message: Optional[str]
    scraped_at: datetime


class AsyncIngredientScraper:
    def __init__(self, db_path: str = "enriched_ingredients.db", max_concurrent: int = 10):
        self.db_path = Path(db_path)
        self.max_concurrent = max_concurrent
        self.session = None
        self.successful_scrapes = 0
        self.failed_scrapes = 0
        self.setup_database()

    def setup_database(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS enriched_ingredients (
                food_recipe_id INTEGER PRIMARY KEY,
                recipe_name TEXT,
                original_ingredients TEXT,
                detailed_ingredients TEXT,
                success BOOLEAN,
                error_message TEXT,
                scraped_at TIMESTAMP,
                attempts INTEGER DEFAULT 1
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraping_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                total_recipes INTEGER,
                completed_recipes INTEGER,
                successful_scrapes INTEGER,
                failed_scrapes INTEGER,
                last_updated TIMESTAMP
            )
        ''')

        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_food_recipe_id ON enriched_ingredients(food_recipe_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_success ON enriched_ingredients(success)')

        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")

    def get_completed_recipe_ids(self) -> set:
        """Get set of recipe IDs that have already been processed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT food_recipe_id FROM enriched_ingredients')
        completed_ids = {row[0] for row in cursor.fetchall()}
        conn.close()
        return completed_ids

    def save_result(self, recipe_id: int, recipe_name: str, original_ingredients: List[str], result: ScrapingResult):
        """Save scraping result to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if recipe already exists
        cursor.execute('SELECT attempts FROM enriched_ingredients WHERE food_recipe_id = ?', (recipe_id,))
        existing = cursor.fetchone()

        detailed_ingredients_json = json.dumps(result.detailed_ingredients) if result.detailed_ingredients else None
        original_ingredients_json = json.dumps(original_ingredients)

        if existing:
            # Update existing record
            cursor.execute('''
                UPDATE enriched_ingredients
                SET detailed_ingredients = ?, success = ?, error_message = ?,
                    scraped_at = ?, attempts = attempts + 1
                WHERE food_recipe_id = ?
            ''', (detailed_ingredients_json, result.success, result.error_message,
                  result.scraped_at, recipe_id))
        else:
            # Insert new record
            cursor.execute('''
                INSERT INTO enriched_ingredients
                (food_recipe_id, recipe_name, original_ingredients, detailed_ingredients,
                 success, error_message, scraped_at, attempts)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            ''', (recipe_id, recipe_name, original_ingredients_json, detailed_ingredients_json,
                  result.success, result.error_message, result.scraped_at))

        conn.commit()
        conn.close()

    def update_progress(self, total: int, completed: int, successful: int, failed: int):
        """Update scraping progress in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('DELETE FROM scraping_progress')  # Keep only latest progress
        cursor.execute('''
            INSERT INTO scraping_progress
            (total_recipes, completed_recipes, successful_scrapes, failed_scrapes, last_updated)
            VALUES (?, ?, ?, ?, ?)
        ''', (total, completed, successful, failed, datetime.now()))

        conn.commit()
        conn.close()

    def clean_recipe_name_for_url(self, name: str) -> str:
        """Convert recipe name to URL-friendly format"""
        cleaned = re.sub(r'[^\w\s-]', '', name.lower())
        cleaned = re.sub(r'\s+', '-', cleaned.strip())
        cleaned = re.sub(r'-+', '-', cleaned)
        return cleaned.strip('-')

    async def create_session(self):
        """Create aiohttp session with proper configuration"""
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        connector = aiohttp.TCPConnector(
            limit=self.max_concurrent,
            limit_per_host=5,
            ttl_dns_cache=300,
            use_dns_cache=True,
        )

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers=headers
        )

    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()

    async def scrape_single_recipe(self, recipe_id: int, recipe_name: str, max_retries: int = 3) -> ScrapingResult:
        """Scrape a single recipe with retry logic"""
        cleaned_name = self.clean_recipe_name_for_url(recipe_name)

        url_formats = [
            f"https://www.food.com/recipe/{cleaned_name}-{recipe_id}",
            f"https://www.food.com/recipe/{recipe_id}",
            f"https://www.food.com/recipe/{recipe_id}/{cleaned_name}"
        ]

        for attempt in range(max_retries):
            for url in url_formats:
                try:
                    async with self.session.get(url) as response:
                        if response.status == 200:
                            html = await response.text()
                            ingredients = self._extract_ingredients_from_html(html)

                            if ingredients and len(ingredients) > 1:
                                return ScrapingResult(
                                    food_recipe_id=recipe_id,
                                    success=True,
                                    detailed_ingredients=ingredients,
                                    error_message=None,
                                    scraped_at=datetime.now()
                                )

                        elif response.status == 429:  # Rate limited
                            await asyncio.sleep(5 * (attempt + 1))  # Exponential backoff

                except asyncio.TimeoutError:
                    logger.warning(f"Timeout for recipe {recipe_id}, attempt {attempt + 1}")
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff

                except Exception as e:
                    logger.warning(f"Error scraping recipe {recipe_id}: {e}")

        return ScrapingResult(
            food_recipe_id=recipe_id,
            success=False,
            detailed_ingredients=None,
            error_message="Failed after all retry attempts",
            scraped_at=datetime.now()
        )

    def _extract_ingredients_from_html(self, html: str) -> Optional[List[str]]:
        """Extract ingredients from Food.com HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')

            # Look for JSON-LD structured data first (most reliable)
            json_scripts = soup.find_all('script', type='application/ld+json')
            for script in json_scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, list):
                        data = data[0]

                    if data.get('@type') == 'Recipe' and 'recipeIngredient' in data:
                        ingredients = data['recipeIngredient']
                        if ingredients and len(ingredients) > 1:
                            return ingredients
                except:
                    continue

            # Fallback to HTML selectors
            ingredient_selectors = [
                '.recipe-ingredients li',
                '.ingredients li',
                '.recipe-ingredient',
                '[data-testid="recipe-ingredient"]',
                '.ingredient-item',
                '.recipe-summary__item',
                '.ingredients__section li'
            ]

            for selector in ingredient_selectors:
                ingredients = soup.select(selector)
                if ingredients:
                    ingredient_list = []
                    for ing in ingredients:
                        text = ing.get_text(strip=True)
                        if text and len(text) > 2:
                            ingredient_list.append(text)

                    if ingredient_list and len(ingredient_list) > 1:
                        return ingredient_list

            return None

        except Exception as e:
            logger.warning(f"Error parsing HTML: {e}")
            return None

    async def scrape_batch(self, recipes_batch: List[Dict], delay_between_batches: float = 1.0):
        """Scrape a batch of recipes concurrently"""
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def scrape_with_semaphore(recipe_data):
            async with semaphore:
                recipe_id = recipe_data['food_recipe_id']
                recipe_name = recipe_data['name']
                original_ingredients = recipe_data['ingredients']

                result = await self.scrape_single_recipe(recipe_id, recipe_name)
                self.save_result(recipe_id, recipe_name, original_ingredients, result)

                if result.success:
                    self.successful_scrapes += 1
                    logger.info(f"✓ Recipe {recipe_id}: {recipe_name} - {len(result.detailed_ingredients)} ingredients")
                else:
                    self.failed_scrapes += 1
                    logger.warning(f"✗ Recipe {recipe_id}: {recipe_name} - {result.error_message}")

                return result

        # Process batch concurrently
        tasks = [scrape_with_semaphore(recipe) for recipe in recipes_batch]
        await asyncio.gather(*tasks, return_exceptions=True)

        # Delay between batches to be respectful
        if delay_between_batches > 0:
            await asyncio.sleep(delay_between_batches)

    async def scrape_dataset(self, df: pd.DataFrame, batch_size: int = 50, delay_between_batches: float = 2.0,
                           resume: bool = True):
        """
        Scrape entire dataset with batching and progress tracking

        Args:
            df: DataFrame with recipes to scrape
            batch_size: Number of recipes to process concurrently
            delay_between_batches: Delay between batches in seconds
            resume: Whether to resume from previous progress
        """
        logger.info(f"Starting async ingredient scraping for {len(df)} recipes")

        # Filter out already completed recipes if resuming
        if resume:
            completed_ids = self.get_completed_recipe_ids()
            if completed_ids:
                df = df[~df['food_recipe_id'].isin(completed_ids)]
                logger.info(f"Resuming: {len(completed_ids)} recipes already completed, {len(df)} remaining")

        if len(df) == 0:
            logger.info("All recipes already processed!")
            return

        await self.create_session()

        try:
            total_recipes = len(df)

            # Process in batches
            for i in range(0, len(df), batch_size):
                batch_df = df.iloc[i:i + batch_size]
                batch_recipes = []

                for _, row in batch_df.iterrows():
                    # Parse ingredients if they're stored as string
                    ingredients = row['ingredients']
                    if isinstance(ingredients, str):
                        try:
                            ingredients = ast.literal_eval(ingredients)
                        except:
                            ingredients = ingredients.split(',')

                    batch_recipes.append({
                        'food_recipe_id': row['food_recipe_id'],
                        'name': row['name'],
                        'ingredients': ingredients
                    })

                batch_num = i // batch_size + 1
                total_batches = (len(df) + batch_size - 1) // batch_size

                logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch_recipes)} recipes)")

                await self.scrape_batch(batch_recipes, delay_between_batches)

                # Update progress
                completed = min(i + batch_size, len(df))
                self.update_progress(total_recipes, completed, self.successful_scrapes, self.failed_scrapes)

                logger.info(f"Progress: {completed}/{total_recipes} ({completed/total_recipes*100:.1f}%) - "
                           f"Success: {self.successful_scrapes}, Failed: {self.failed_scrapes}")

        finally:
            await self.close_session()

        logger.info(f"Scraping complete! Success: {self.successful_scrapes}, Failed: {self.failed_scrapes}")

    def export_to_csv(self, output_path: str = "enriched_recipes.csv"):
        """Export enriched data to CSV"""
        conn = sqlite3.connect(self.db_path)

        query = '''
            SELECT food_recipe_id, recipe_name, original_ingredients,
                   detailed_ingredients, success, scraped_at
            FROM enriched_ingredients
            ORDER BY food_recipe_id
        '''

        df = pd.read_sql_query(query, conn)
        conn.close()

        # Parse JSON columns back to lists
        df['original_ingredients'] = df['original_ingredients'].apply(json.loads)
        df['detailed_ingredients'] = df['detailed_ingredients'].apply(
            lambda x: json.loads(x) if x else None
        )

        df.to_csv(output_path, index=False)
        logger.info(f"Exported {len(df)} recipes to {output_path}")

        return df

    def get_progress_stats(self) -> Dict[str, Any]:
        """Get current scraping progress statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get latest progress
        cursor.execute('SELECT * FROM scraping_progress ORDER BY last_updated DESC LIMIT 1')
        progress = cursor.fetchone()

        # Get success/failure counts
        cursor.execute('SELECT success, COUNT(*) FROM enriched_ingredients GROUP BY success')
        counts = dict(cursor.fetchall())

        conn.close()

        return {
            'total_recipes': progress[1] if progress else 0,
            'completed_recipes': progress[2] if progress else 0,
            'successful_scrapes': counts.get(True, 0),
            'failed_scrapes': counts.get(False, 0),
            'last_updated': progress[5] if progress else None
        }


def main():
    """CLI interface for the scraper"""
    print("🕷️  Async Food.com Ingredient Scraper")
    print("=====================================")

    # Load processed dataset
    try:
        from preprocessing import load_data, preprocess_data
        from features import select_features

        print("📚 Loading processed dataset...")
        recipes, interactions = load_data()
        recipes_cleaned = recipes.dropna()
        recipes_cleaned = recipes_cleaned[recipes_cleaned["minutes"] <= 180]
        recipes_cleaned, interactions_cleaned = preprocess_data(recipes_cleaned, interactions)
        df = select_features(recipes_cleaned, interactions_cleaned)

        print(f"Loaded {len(df)} recipes for scraping")

    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        return

    # Initialize scraper
    scraper = AsyncIngredientScraper(max_concurrent=10)

    # Show current progress
    stats = scraper.get_progress_stats()
    if stats['completed_recipes'] > 0:
        print(f"\nCurrent Progress:")
        print(f"  Completed: {stats['completed_recipes']}/{stats['total_recipes']}")
        print(f"  Successful: {stats['successful_scrapes']}")
        print(f"  Failed: {stats['failed_scrapes']}")
        print(f"  Last updated: {stats['last_updated']}")

    # Ask user what to do
    print("\nOptions:")
    print("1. Start/Resume scraping (batch size: 50)")
    print("2. Start/Resume scraping (batch size: 20, slower)")
    print("3. Export current results to CSV")
    print("4. Show progress statistics")

    choice = input("\nEnter choice (1-4): ").strip()

    if choice == "1":
        asyncio.run(scraper.scrape_dataset(df, batch_size=50, delay_between_batches=1.0))
    elif choice == "2":
        asyncio.run(scraper.scrape_dataset(df, batch_size=20, delay_between_batches=2.0))
    elif choice == "3":
        scraper.export_to_csv()
    elif choice == "4":
        stats = scraper.get_progress_stats()
        print(f"\nProgress Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()