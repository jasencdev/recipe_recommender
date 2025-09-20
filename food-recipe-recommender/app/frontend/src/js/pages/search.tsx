import { useState } from "react";
import { useNavigate } from "react-router-dom";
import StackedWrapper from "./stackedWrapper";
import { Field, Label } from "../components/fieldset";
import { Button } from "../components/button";
import { Input } from "../components/input";
import { Heading } from "../components/heading";
import { Strong, Text } from "../components/text";
import { Divider } from '../components/divider'
import { searchRecipes, type SearchFilters } from "../services/api";
// Removed recently viewed cards and images

export default function Search() {
    const navigate = useNavigate();
    const [searchQuery, setSearchQuery] = useState("");
    const [complexityScore, setComplexityScore] = useState(24);
    const [numberOfIngredients, setNumberOfIngredients] = useState(10);
    const [cookTime, setCookTime] = useState(30);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Removed recently viewed

    const handleTextSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!searchQuery.trim()) return;

        setIsLoading(true);
        setError(null);

        try {
            const filters: SearchFilters = { query: searchQuery.trim() };
            const response = await searchRecipes(filters);
            // Navigate to recommendations page with results
            navigate('/recommendations', {
                state: {
                    recipes: response.recipes,
                    query: searchQuery.trim(),
                    filters,
                    total: response.total,
                    hasMore: response.hasMore
                }
            });
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to search recipes');
        } finally {
            setIsLoading(false);
        }
    };

    const handleParameterSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);

        try {
            const filters: SearchFilters = {
                complexityScore,
                numberOfIngredients,
                cookTime,
            };
            const response = await searchRecipes(filters);
            // Navigate to recommendations page with results
            navigate('/recommendations', {
                state: {
                    recipes: response.recipes,
                    query: `Cook Time: ${cookTime}min, Complexity: ${complexityScore}, Ingredients: ${numberOfIngredients}`,
                    filters,
                    total: response.total,
                    hasMore: response.hasMore
                }
            });
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to search recipes');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <StackedWrapper>
            <>
                <Heading>Welcome to Recipe Recommender</Heading><br />
                <Strong>Get started by searching for your favorite ingredients or dishes!</Strong>
                <Divider />
                <br />
                <br />
                <Text>
                    Find the best recipes tailored to your needs, you can find recipes via Search
                    below by typing in your ingredients or dish names. Also, you can explore popular
                    recipes and get personalized recommendations based on your preferences.
                </Text>

                <br />
                <Divider />
                <br />

                {/* Recently Viewed removed */}

                {/* Advanced filters removed */}

                {/* Text Search Form */}
                <form onSubmit={handleTextSearch}>
                    <Field>
                        <Label htmlFor="search-query">Search</Label>
                        <Input
                            id="search-query"
                            type="text"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            placeholder="Enter ingredients or dish name..."
                        />
                        <br />
                    </Field>
                    <Button type="submit" disabled={isLoading || !searchQuery.trim()}>
                        {isLoading ? 'Searching...' : 'Search Recipes'}
                    </Button>
                </form>

                <br />
                <br />
                <Divider />
                <br />

                {/* Parameter Search Form */}
                <form onSubmit={handleParameterSearch}>
                    <Field>
                        <Strong>Parameter Search</Strong>
                        <br />
                        <br />
                        <div className="space-y-6">
                            <div>
                                <label htmlFor="cook_time" className="block mb-2 text-sm font-medium">
                                    Target Cook Time: {cookTime} minutes
                                </label>
                                <input
                                    id="cook_time"
                                    type="range"
                                    min="5"
                                    max="60"
                                    value={cookTime}
                                    onChange={(e) => setCookTime(Number(e.target.value))}
                                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-gray-900 dark:bg-gray-700 dark:accent-white"
                                />
                            </div>
                            <div>
                                <label htmlFor="complexity_score" className="block mb-2 text-sm font-medium">
                                    Target Complexity Score: {complexityScore}
                                </label>
                                <input
                                    id="complexity_score"
                                    type="range"
                                    min="1"
                                    max="50"
                                    value={complexityScore}
                                    onChange={(e) => setComplexityScore(Number(e.target.value))}
                                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-gray-900 dark:bg-gray-700 dark:accent-white"
                                />
                            </div>
                            <div>
                                <label htmlFor="number_of_ingredients" className="block mb-2 text-sm font-medium">
                                    Target Number of Ingredients: {numberOfIngredients}
                                </label>
                                <input
                                    id="number_of_ingredients"
                                    type="range"
                                    min="1"
                                    max="20"
                                    value={numberOfIngredients}
                                    onChange={(e) => setNumberOfIngredients(Number(e.target.value))}
                                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-gray-900 dark:bg-gray-700 dark:accent-white"
                                />
                            </div>
                        </div>
                    </Field>
                    <br />
                    <Button type="submit" disabled={isLoading}>
                        {isLoading ? 'Searching...' : 'Search by Parameters'}
                    </Button>
                </form>

                {error && (
                    <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                        <Text className="text-red-700">{error}</Text>
                    </div>
                )}

                <br />
                <br />
                <Divider />
                <br />
                <Text>
                    Enter your search criteria above and click submit to find recipes that match your preferences.
                    The parameter search uses machine learning to find recipes that best match your target complexity and ingredient preferences.
                </Text>
                <br />
                <br />
                <Text>
                    Enjoy your cooking journey with Recipe Recommender!
                </Text>
            </>
        </StackedWrapper>
    )
}
