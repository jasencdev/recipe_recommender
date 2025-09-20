import type { Recipe } from './api';

const RECENTLY_VIEWED_KEY = 'recently-viewed-recipes';
const MAX_RECENT_RECIPES = 20;

export interface RecentlyViewedRecipe extends Recipe {
    viewedAt: Date;
}

export const addToRecentlyViewed = (recipe: Recipe): void => {
    try {
        const recentRecipes = getRecentlyViewed();

        // Remove if already exists
        const filteredRecipes = recentRecipes.filter(r => r.id !== recipe.id);

        // Add to beginning
        const updatedRecipes: RecentlyViewedRecipe[] = [
            { ...recipe, viewedAt: new Date() },
            ...filteredRecipes
        ].slice(0, MAX_RECENT_RECIPES);

        localStorage.setItem(RECENTLY_VIEWED_KEY, JSON.stringify(updatedRecipes));
    } catch (error) {
        console.error('Failed to add recipe to recently viewed:', error);
    }
};

export const getRecentlyViewed = (): RecentlyViewedRecipe[] => {
    try {
        const stored = localStorage.getItem(RECENTLY_VIEWED_KEY);
        if (!stored) return [];

        const recipes = JSON.parse(stored);
        // Convert date strings back to Date objects
        return recipes.map((recipe: any) => ({
            ...recipe,
            viewedAt: new Date(recipe.viewedAt)
        }));
    } catch (error) {
        console.error('Failed to get recently viewed recipes:', error);
        return [];
    }
};

export const clearRecentlyViewed = (): void => {
    try {
        localStorage.removeItem(RECENTLY_VIEWED_KEY);
    } catch (error) {
        console.error('Failed to clear recently viewed recipes:', error);
    }
};

export const removeFromRecentlyViewed = (recipeId: string): void => {
    try {
        const recentRecipes = getRecentlyViewed();
        const filteredRecipes = recentRecipes.filter(r => r.id !== recipeId);
        localStorage.setItem(RECENTLY_VIEWED_KEY, JSON.stringify(filteredRecipes));
    } catch (error) {
        console.error('Failed to remove recipe from recently viewed:', error);
    }
};

export const getRecentlyViewedByTimeframe = (days: number): RecentlyViewedRecipe[] => {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - days);

    return getRecentlyViewed().filter(recipe => recipe.viewedAt >= cutoffDate);
};