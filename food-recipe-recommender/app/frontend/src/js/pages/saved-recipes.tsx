import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import StackedWrapper from "./stackedWrapper";
import { Button } from "../components/button";
import { Heading } from "../components/heading";
import { Strong, Text } from "../components/text";
import { Divider } from '../components/divider'
import Card from '../components/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/table'
import { getSavedRecipes, removeSavedRecipe, getRecipeById, type Recipe } from "../services/api";
import logger from "../utils/logger";

export default function SavedRecipes() {
    const navigate = useNavigate();
    const [savedRecipes, setSavedRecipes] = useState<Recipe[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [removingRecipeId, setRemovingRecipeId] = useState<string | null>(null);

    useEffect(() => {
        loadSavedRecipes();
    }, []);

    const loadSavedRecipes = async () => {
        try {
            setIsLoading(true);
            setError(null);

            // Get saved recipe IDs from the simplified endpoint
            const savedRecipeData = await getSavedRecipes();

            // Fetch full recipe details for each saved recipe ID
            const recipePromises = savedRecipeData.map(async (savedRecipe: {id: string}) => {
                try {
                    return await getRecipeById(savedRecipe.id);
                } catch (err) {
                    console.warn(`Failed to load recipe ${savedRecipe.id}:`, err);
                    return null;
                }
            });

            const recipes = await Promise.all(recipePromises);
            // Filter out any null results from failed fetches
            const validRecipes = recipes.filter((recipe): recipe is Recipe => recipe !== null);

            setSavedRecipes(validRecipes);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load saved recipes');
        } finally {
            setIsLoading(false);
        }
    };

    const handleRemoveRecipe = async (recipeId: string) => {
        try {
            setRemovingRecipeId(recipeId);
            await removeSavedRecipe(recipeId);
            setSavedRecipes(prev => prev.filter(recipe => recipe.id !== recipeId));
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to remove recipe');
        } finally {
            setRemovingRecipeId(null);
        }
    };

    const handleViewRecipe = (recipeId: string) => {
        navigate(`/recipe/${recipeId}`);
    };

    const handleViewAllRecipes = () => {
        // Navigate to all saved recipes page (to be implemented)
        logger.info('View all saved recipes');
    };

    const handleAddNewRecipe = () => {
        // Navigate to search page or add recipe form
        window.location.href = '/search';
    };


    const displayedRecipes = savedRecipes.slice(0, 10);
    const totalRecipes = savedRecipes.length;

    // Group recipes by collection (mock collections for now)
    const collections = [
        { name: 'Quick Dinners', count: savedRecipes.filter(r => r.cookTime <= 30).length },
        { name: 'Healthy Options', count: savedRecipes.filter(r => r.dietaryTags?.includes('healthy')).length },
        { name: 'Desserts', count: savedRecipes.filter(r => r.dietaryTags?.includes('dessert')).length },
        { name: 'Meal Prep', count: savedRecipes.filter(r => r.dietaryTags?.includes('meal-prep')).length },
    ];
    if (isLoading) {
        return (
            <StackedWrapper>
                <div className="flex justify-center items-center min-h-64">
                    <Text>Loading saved recipes...</Text>
                </div>
            </StackedWrapper>
        );
    }

    return (
        <StackedWrapper>
            <>
                <Heading>Saved Recipes</Heading>
                <br />
                <Strong>Your personal collection of favorite recipes</Strong>
                <Divider />
                <br />

                {error && (
                    <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                        <Text className="text-red-700">{error}</Text>
                    </div>
                )}

                <div className="flex justify-between items-center mb-6">
                    <Text>
                        Manage your saved recipes, organize them into collections, and plan your meals.
                    </Text>
                    <Button onClick={handleAddNewRecipe}>Add New Recipe</Button>
                </div>

                <br />
                <Divider />
                <br />

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    <Card className="p-4">
                        <Strong>Total Saved</Strong>
                        <div className="text-2xl font-bold mt-2">{totalRecipes}</div>
                        <Text className="text-sm text-gray-600 dark:text-zinc-400">Recipes in your collection</Text>
                    </Card>

                    <Card className="p-4">
                        <Strong>Collections</Strong>
                        <div className="text-2xl font-bold mt-2">{collections.filter(c => c.count > 0).length}</div>
                        <Text className="text-sm text-gray-600 dark:text-zinc-400">Organized groups</Text>
                    </Card>

                    <Card className="p-4">
                        <Strong>Showing</Strong>
                        <div className="text-2xl font-bold mt-2">{Math.min(10, totalRecipes)}</div>
                        <Text className="text-sm text-gray-600 dark:text-zinc-400">Recipes displayed</Text>
                    </Card>
                </div>

                {collections.some(c => c.count > 0) && (
                    <div className="mb-6">
                        <div className="flex justify-between items-center mb-4">
                            <Strong>Recipe Collections</Strong>
                            <Button onClick={() => navigate('/collections')} size="sm">
                                Manage Collections
                            </Button>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                            {collections.map((collection) => (
                                collection.count > 0 && (
                                    <Card
                                        key={collection.name}
                                        className="p-4 cursor-pointer hover:shadow-lg transition-shadow"
                                        onClick={() => navigate('/collections')}
                                    >
                                        <Strong>{collection.name}</Strong>
                                        <Text className="text-sm mt-1">{collection.count} recipes</Text>
                                    </Card>
                                )
                            ))}
                        </div>
                    </div>
                )}

                <br />
                <Divider />
                <br />

                <Strong>Saved Recipes</Strong>
                <br />
                <br />

                {savedRecipes.length === 0 ? (
                    <div className="text-center py-12">
                        <Text className="text-gray-500 dark:text-zinc-400 mb-4">You haven't saved any recipes yet.</Text>
                        <Button onClick={handleAddNewRecipe}>Find Recipes to Save</Button>
                    </div>
                ) : (
                    <>
                        <div className="overflow-x-auto">
                            <Table>
                                <TableHead>
                                    <TableRow>
                                        <TableHeader className="min-w-[200px]">Recipe Name</TableHeader>
                                        <TableHeader className="min-w-[100px]">Cook Time</TableHeader>
                                        <TableHeader className="min-w-[100px]">Difficulty</TableHeader>
                                        <TableHeader className="min-w-[100px]">Ingredients</TableHeader>
                                        <TableHeader className="min-w-[150px] text-right">Actions</TableHeader>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {displayedRecipes.map((recipe) => (
                                        <TableRow key={recipe.id}>
                                            <TableCell className="max-w-[250px]">
                                                <div>
                                                    <Strong className="block truncate">{recipe.name}</Strong>
                                                    <Text className="text-sm text-gray-600 dark:text-zinc-400 line-clamp-2">{recipe.description}</Text>
                                                </div>
                                            </TableCell>
                                            <TableCell className="whitespace-nowrap">{recipe.cookTime} min</TableCell>
                                            <TableCell className="capitalize whitespace-nowrap">{recipe.difficulty}</TableCell>
                                            <TableCell className="whitespace-nowrap">{recipe.ingredients.length}</TableCell>
                                            <TableCell>
                                                <div className="flex gap-2 justify-end">
                                                    <Button
                                                        size="sm"
                                                        onClick={() => handleViewRecipe(recipe.id)}
                                                    >
                                                        View
                                                    </Button>
                                                    <Button
                                                        size="sm"
                                                        color="red"
                                                        onClick={() => handleRemoveRecipe(recipe.id)}
                                                        disabled={removingRecipeId === recipe.id}
                                                    >
                                                        {removingRecipeId === recipe.id ? 'Removing...' : 'Remove'}
                                                    </Button>
                                                </div>
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </div>

                        <br />
                        <div className="flex justify-between items-center">
                            <Text>Showing {displayedRecipes.length} of {totalRecipes} recipes</Text>
                            {totalRecipes > 10 && (
                                <Button onClick={handleViewAllRecipes}>View All Saved Recipes</Button>
                            )}
                        </div>
                    </>
                )}

                <br />
                <br />
                <Divider />

            </>
        </StackedWrapper>
    )
}
