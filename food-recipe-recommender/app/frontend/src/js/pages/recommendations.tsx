import { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import StackedWrapper from "./stackedWrapper";
import { Button } from "../components/button";
import { Heading } from "../components/heading";
import { Strong, Text } from "../components/text";
import { Divider } from '../components/divider'
import Card from '../components/card'
import { Field, Label } from "../components/fieldset";
import { type Recipe, searchRecipes, type SearchFilters } from "../services/api";
import SaveButton from "../components/saveButton";
import { useToast } from "../components/toast";

type SortOption = 'relevance' | 'cookTime' | 'difficulty' | 'name';

export default function Recommendations() {
    const location = useLocation();
    const navigate = useNavigate();
    const [recipes, setRecipes] = useState<Recipe[]>([]);
    const [displayedRecipes, setDisplayedRecipes] = useState<Recipe[]>([]);
    const [searchQuery, setSearchQuery] = useState<string>("");
    const [searchFilters, setSearchFilters] = useState<SearchFilters>({});
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [sortBy, setSortBy] = useState<SortOption>('relevance');
    const [currentPage, setCurrentPage] = useState(1);
    const [recipesPerPage] = useState(12);
    const [totalRecipes, setTotalRecipes] = useState(0);
    const [hasMore, setHasMore] = useState(false);
    const toast = useToast();

    useEffect(() => {
        // Try to get search results from location state first (fresh search)
        if (location.state?.recipes) {
            const searchData = {
                recipes: location.state.recipes,
                query: location.state.query || "",
                filters: location.state.filters || {},
                total: location.state.total || location.state.recipes.length,
                hasMore: location.state.hasMore || false
            };

            // Save to localStorage for persistence
            localStorage.setItem('search-results', JSON.stringify(searchData));

            // Set state
            setRecipes(searchData.recipes);
            setSearchQuery(searchData.query);
            setSearchFilters(searchData.filters);
            setTotalRecipes(searchData.total);
            setHasMore(searchData.hasMore);
            setCurrentPage(1);
        } else {
            // Try to restore from localStorage
            const savedResults = localStorage.getItem('search-results');
            if (savedResults) {
                try {
                    const searchData = JSON.parse(savedResults);
                    setRecipes(searchData.recipes);
                    setSearchQuery(searchData.query);
                    setSearchFilters(searchData.filters);
                    setTotalRecipes(searchData.total);
                    setHasMore(searchData.hasMore);
                    setCurrentPage(1);
                } catch (e) {
                    console.error('Error restoring search results:', e);
                    navigate("/search");
                }
            } else {
                // If no saved results, redirect back to search
                navigate("/search");
            }
        }
    }, [location.state, navigate]);

    useEffect(() => {
        // Apply sorting and pagination when recipes or sort option changes
        applyFiltering();
    }, [recipes, sortBy, currentPage]);

    const applyFiltering = () => {
        let sortedRecipes = [...recipes];

        // Apply sorting
        switch (sortBy) {
            case 'cookTime':
                sortedRecipes.sort((a, b) => a.cookTime - b.cookTime);
                break;
            case 'difficulty':
                const difficultyOrder = { 'easy': 1, 'medium': 2, 'hard': 3 };
                sortedRecipes.sort((a, b) =>
                    (difficultyOrder[a.difficulty as keyof typeof difficultyOrder] || 2) -
                    (difficultyOrder[b.difficulty as keyof typeof difficultyOrder] || 2)
                );
                break;
            case 'name':
                sortedRecipes.sort((a, b) => a.name.localeCompare(b.name));
                break;
            default: // relevance
                // Keep original order (already sorted by relevance from API)
                break;
        }

        // Apply pagination
        const startIndex = (currentPage - 1) * recipesPerPage;
        const endIndex = startIndex + recipesPerPage;
        setDisplayedRecipes(sortedRecipes.slice(startIndex, endIndex));
    };

    const loadMoreResults = async () => {
        if (!hasMore || isLoading) return;

        try {
            setIsLoading(true);
            const nextPage = Math.floor(recipes.length / 20) + 1; // Assuming API uses 20 per page
            const response = await searchRecipes(searchFilters, nextPage, 20);

            const updatedRecipes = [...recipes, ...response.recipes];
            setRecipes(updatedRecipes);
            setTotalRecipes(response.total);
            setHasMore(response.hasMore);

            // Update localStorage with new results
            const savedResults = localStorage.getItem('search-results');
            if (savedResults) {
                try {
                    const searchData = JSON.parse(savedResults);
                    searchData.recipes = updatedRecipes;
                    searchData.total = response.total;
                    searchData.hasMore = response.hasMore;
                    localStorage.setItem('search-results', JSON.stringify(searchData));
                } catch (e) {
                    console.error('Error updating saved results:', e);
                }
            }
        } catch (err) {
            const msg = err instanceof Error ? err.message : 'Failed to load more results';
            setError(msg);
            toast.error(msg);
        } finally {
            setIsLoading(false);
        }
    };


    const handleViewRecipe = (recipeId: string) => {
        navigate(`/recipe/${recipeId}`);
    };

    const handleNewSearch = () => {
        navigate("/search");
    };

    const totalPages = Math.ceil(recipes.length / recipesPerPage);

    if (recipes.length === 0 && !location.state?.recipes) {
        return (
            <StackedWrapper>
                <div className="text-center py-12">
                    <Heading>No Search Results</Heading>
                    <br />
                    <Text className="text-gray-500 dark:text-zinc-400 mb-4">Start by searching for recipes.</Text>
                    <Button onClick={handleNewSearch}>Go to Search</Button>
                </div>
            </StackedWrapper>
        );
    }

    return (
        <StackedWrapper>
            <>
                <div className="flex justify-between items-start mb-4">
                    <div>
                        <Heading>Search Results</Heading>
                        <br />
                        {searchQuery && (
                            <Strong>Results for: "{searchQuery}"</Strong>
                        )}
                    </div>
                    <Button onClick={handleNewSearch} color="gray">
                        New Search
                    </Button>
                </div>

                <Divider />
                <br />

                {error && (
                    <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                        <Text className="text-red-700">{error}</Text>
                    </div>
                )}

                {/* Results Controls */}
                <div className="flex justify-between items-center mb-6">
                    <Strong>Found {recipes.length} recipes</Strong>
                    <div className="flex gap-4 items-center">
                        <Field>
                            <Label htmlFor="sort-by">Sort by:</Label>
                            <select
                                id="sort-by"
                                value={sortBy}
                                onChange={(e) => setSortBy(e.target.value as SortOption)}
                                className="p-2 border rounded"
                            >
                                <option value="relevance">Relevance</option>
                                <option value="cookTime">Cook Time</option>
                                <option value="difficulty">Difficulty</option>
                                <option value="name">Name</option>
                            </select>
                        </Field>
                    </div>
                </div>

                {recipes.length === 0 ? (
                    <div className="text-center py-12">
                        <Text className="text-gray-500 dark:text-zinc-400 mb-4">No recipes found matching your search.</Text>
                        <Button onClick={handleNewSearch}>Try a Different Search</Button>
                    </div>
                ) : (
                    <>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {displayedRecipes.map((recipe) => (
                            <Card
                                key={recipe.id}
                                className="overflow-hidden hover:shadow-lg transition-shadow duration-200 cursor-pointer"
                                onClick={() => handleViewRecipe(recipe.id)}
                            >
                                <div className="p-4">
                                    <div className="flex justify-between items-start mb-2">
                                        <Heading level={3} className="text-lg line-clamp-1 flex-1">{recipe.name}</Heading>
                                        <div className="flex gap-2 ml-2">
                                            {/* Difficulty Badge */}
                                            <span className={`px-2 py-1 text-xs font-medium rounded-full text-white ${
                                                recipe.difficulty === 'easy' ? 'bg-green-500' :
                                                recipe.difficulty === 'medium' ? 'bg-yellow-500' :
                                                'bg-red-500'
                                            }`}>
                                                {recipe.difficulty}
                                            </span>
                                            {/* Cook Time Badge */}
                                            <span className="px-2 py-1 text-xs font-medium rounded-full bg-gray-600 text-white">
                                                {recipe.cookTime} min
                                            </span>
                                        </div>
                                    </div>

                                    <Text className="text-sm text-gray-600 dark:text-zinc-400 line-clamp-2 mb-4">
                                        {recipe.description}
                                    </Text>

                                    {/* Recipe Stats */}
                                    <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-zinc-400 mb-4">
                                        <div className="flex items-center gap-1">
                                            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                            </svg>
                                            <span>{recipe.ingredients.length} ingredients</span>
                                        </div>
                                        {recipe.cuisine && (
                                            <div className="flex items-center gap-1">
                                                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                                    <path fillRule="evenodd" d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" clipRule="evenodd" />
                                                </svg>
                                                <span className="capitalize">{recipe.cuisine}</span>
                                            </div>
                                        )}
                                    </div>

                                    {/* Dietary Tags */}
                                    {recipe.dietaryTags && recipe.dietaryTags.length > 0 && (
                                        <div className="flex flex-wrap gap-1 mb-4">
                                            {recipe.dietaryTags.slice(0, 3).map((tag) => (
                                                <span
                                                    key={tag}
                                                    className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full capitalize"
                                                >
                                                    {tag}
                                                </span>
                                            ))}
                                            {recipe.dietaryTags.length > 3 && (
                                                <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">
                                                    +{recipe.dietaryTags.length - 3}
                                                </span>
                                            )}
                                        </div>
                                    )}

                                    <div className="flex gap-2 items-center">
                                        <Text className="text-sm text-gray-500 dark:text-zinc-400 flex-1">Click to view recipe</Text>
                                        <SaveButton
                                            recipeId={recipe.id}
                                            size="sm"
                                        />
                                    </div>
                                </div>
                            </Card>
                        ))}
                        </div>

                        {/* Pagination Controls */}
                        {totalPages > 1 && (
                            <div className="flex justify-center items-center gap-4 mt-8">
                                <Button
                                    color="gray"
                                    disabled={currentPage === 1}
                                    onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                                >
                                    Previous
                                </Button>

                                <div className="flex gap-2">
                                    {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                                        let pageNum;
                                        if (totalPages <= 5) {
                                            pageNum = i + 1;
                                        } else if (currentPage <= 3) {
                                            pageNum = i + 1;
                                        } else if (currentPage >= totalPages - 2) {
                                            pageNum = totalPages - 4 + i;
                                        } else {
                                            pageNum = currentPage - 2 + i;
                                        }

                                        return (
                                            <Button
                                                key={pageNum}
                                                size="sm"
                                                color={currentPage === pageNum ? "default" : "gray"}
                                                onClick={() => setCurrentPage(pageNum)}
                                            >
                                                {pageNum}
                                            </Button>
                                        );
                                    })}
                                </div>

                                <Button
                                    color="gray"
                                    disabled={currentPage === totalPages}
                                    onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                                >
                                    Next
                                </Button>
                            </div>
                        )}

                        {/* Load More from API */}
                        {hasMore && (
                            <div className="text-center mt-8">
                                <Button
                                    onClick={loadMoreResults}
                                    disabled={isLoading}
                                    color="gray"
                                >
                                    {isLoading ? 'Loading...' : 'Load More Results from Server'}
                                </Button>
                            </div>
                        )}

                        {/* Results Summary */}
                        <div className="text-center mt-6">
                            <Text className="text-sm text-gray-600 dark:text-zinc-400">
                                Showing {(currentPage - 1) * recipesPerPage + 1}-{Math.min(currentPage * recipesPerPage, recipes.length)} of {recipes.length} recipes
                                {totalRecipes > recipes.length && ` (${totalRecipes} total available)`}
                            </Text>
                        </div>
                    </>
                )}

                <br />
                <br />
                <Divider />

                <div className="text-center">
                    <Text>
                        Want to refine your search? Try different ingredients or adjust the parameters.
                    </Text>
                    <br />
                    <Button onClick={handleNewSearch}>Search Again</Button>
                </div>
            </>
        </StackedWrapper>
    )
}
