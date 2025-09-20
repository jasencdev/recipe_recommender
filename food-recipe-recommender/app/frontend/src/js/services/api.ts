import axios, { AxiosError } from 'axios';
import logger from '../utils/logger';

const api = axios.create({
  baseURL: '/api', // Vite proxy will handle this
  withCredentials: true, // Send cookies with requests
});

export default api;

// Function to get authentication status
export const getAuthStatus = async () => {
  try {
    const response = await api.get('/auth/me');
    return response.data;
  } catch (error) {
    const err = error as AxiosError;
    console.error("API error fetching auth status:", err.message);
    throw new Error((err.response?.data as any)?.message || err.message);
  }
};

// Types for search functionality
export interface SearchFilters {
  query?: string;
  complexityScore?: number;
  numberOfIngredients?: number;
  dietaryRestrictions?: string[];
  cuisine?: string;
  cookTime?: number;
}

export interface Recipe {
  id: string;
  name: string;
  description: string;
  cookTime: number;
  difficulty: string;
  ingredients: string[];
  instructions: string[];
  cuisine?: string;
  dietaryTags?: string[];
  complexityScore?: number;
  imageUrl?: string;
}

export interface SearchResponse {
  recipes: Recipe[];
  total: number;
  page: number;
  limit: number;
  hasMore: boolean;
}

// Search recipes with text query and/or filters
export const searchRecipes = async (filters: SearchFilters, page: number = 1, limit: number = 20): Promise<SearchResponse> => {
  try {
    const params = new URLSearchParams();

    if (filters.query) params.append('query', filters.query);
    if (filters.complexityScore !== undefined) params.append('complexity_score', filters.complexityScore.toString());
    if (filters.numberOfIngredients !== undefined) params.append('number_of_ingredients', filters.numberOfIngredients.toString());
    if (filters.dietaryRestrictions?.length) params.append('dietary_restrictions', filters.dietaryRestrictions.join(','));
    if (filters.cuisine) params.append('cuisine', filters.cuisine);
    if (filters.cookTime !== undefined) params.append('cook_time', filters.cookTime.toString());

    params.append('page', page.toString());
    params.append('limit', limit.toString());

    const response = await api.get(`/search?${params.toString()}`);
    return response.data;
  } catch (error) {
    const err = error as AxiosError;
    console.error("API error searching recipes:", err.message);
    throw new Error((err.response?.data as any)?.message || err.message);
  }
};

// Get recipe by ID
export const getRecipeById = async (recipeId: string): Promise<Recipe> => {
  try {
    const response = await api.get(`/recipes/${recipeId}`);
    return response.data.recipe;
  } catch (error) {
    const err = error as AxiosError;
    console.error("API error fetching recipe:", err.message);
    throw new Error((err.response?.data as any)?.message || err.message);
  }
};


// Get saved recipes
export const getSavedRecipes = async (): Promise<Recipe[]> => {
  try {
    const response = await api.get('/saved-recipes');
    return response.data.recipes;
  } catch (error) {
    const err = error as AxiosError;
    console.error("API error fetching saved recipes:", err.message);
    throw new Error((err.response?.data as any)?.message || err.message);
  }
};

// Save a recipe
export const saveRecipe = async (recipeId: string): Promise<void> => {
  try {
    await api.post('/saved-recipes', { recipe_id: recipeId });
  } catch (error) {
    const err = error as AxiosError;
    console.error("API error saving recipe:", err.message);
    throw new Error((err.response?.data as any)?.message || err.message);
  }
};

// Remove a saved recipe
export const removeSavedRecipe = async (recipeId: string): Promise<void> => {
  try {
    await api.delete(`/saved-recipes/${recipeId}`);
  } catch (error) {
    const err = error as AxiosError;
    console.error("API error removing saved recipe:", err.message);
    throw new Error((err.response?.data as any)?.message || err.message);
  }
};

// Local cache for saved recipe IDs to improve performance
// Invalidate any existing cache since we fixed the ID format issues
let savedRecipeCache: Set<string> | null = null;
let cacheLastUpdated: number = 0;
let pendingRequest: Promise<Set<string>> | null = null;
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

// Get list of saved recipe IDs
export const getSavedRecipeIds = async (forceRefresh = false): Promise<Set<string>> => {
  const now = Date.now();

  if (!forceRefresh && savedRecipeCache && (now - cacheLastUpdated) < CACHE_DURATION) {
    return savedRecipeCache;
  }

  // If there's already a request in progress, wait for it
  if (pendingRequest) {
    return pendingRequest;
  }

  // Start new request and cache the promise
  pendingRequest = (async (): Promise<Set<string>> => {
    try {
      const response = await api.get('/saved-recipes');
      // Updated to handle the new simplified response format that just returns recipe IDs
      const recipeIds = new Set<string>(response.data.recipes.map((recipe: {id: string}) => recipe.id as string));

      savedRecipeCache = recipeIds;
      cacheLastUpdated = Date.now();

      logger.debug(`[SAVED DEBUG] Fetched saved recipe IDs from server: [${Array.from(recipeIds).join(', ')}]`);
      return recipeIds;
    } catch (error) {
      const err = error as AxiosError;
      console.error("API error fetching saved recipe IDs:", err.message);
      // Return empty set if error, don't throw to avoid breaking UI
      return new Set<string>();
    } finally {
      // Clear pending request when done
      pendingRequest = null;
    }
  })();

  return pendingRequest;
};

// Check if a recipe is saved
export const isRecipeSaved = async (recipeId: string): Promise<boolean> => {
  // Force fresh cache since we changed ID format
  const savedIds = await getSavedRecipeIds(true);
  const isSaved = savedIds.has(recipeId);
  const idsArray = Array.from(savedIds);
  logger.debug(`[SAVED DEBUG] Recipe ${recipeId} saved status: ${isSaved}`);
  logger.debug(`[SAVED DEBUG] Fresh saved IDs: [${idsArray.join(', ')}]`);
  return isSaved;
};

// Toggle save/unsave recipe
export const toggleSaveRecipe = async (recipeId: string): Promise<boolean> => {
  logger.debug(`[TOGGLE DEBUG] Toggling recipe ${recipeId}`);
  const isSaved = await isRecipeSaved(recipeId);
  logger.debug(`[TOGGLE DEBUG] Recipe ${recipeId} is currently saved: ${isSaved}`);

  if (isSaved) {
    logger.debug(`[TOGGLE DEBUG] Removing recipe ${recipeId}`);
    await removeSavedRecipe(recipeId);
    savedRecipeCache?.delete(recipeId);
    return false;
  } else {
    logger.debug(`[TOGGLE DEBUG] Saving recipe ${recipeId}`);
    await saveRecipe(recipeId);
    savedRecipeCache?.add(recipeId);
    return true;
  }
};
