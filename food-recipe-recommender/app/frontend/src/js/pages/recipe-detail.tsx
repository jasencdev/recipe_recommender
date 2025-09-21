import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import StackedWrapper from "./stackedWrapper";
import { Button } from "../components/button";
import { Heading } from "../components/heading";
import { Strong, Text } from "../components/text";
import { Divider } from '../components/divider'
import Card from '../components/card'
import { getRecipeById, type Recipe } from "../services/api";
import SaveButton from "../components/saveButton";
import { addToRecentlyViewed } from "../services/recentlyViewed";
import {
    saveRecipeNote,
    getRecipeNote,
    deleteRecipeNote,
    type RecipeNote
} from "../services/recipeNotes";
import {
    getEnrichedIngredients,
    scaleRecipeIngredients,
    formatIngredient,
    type EnrichedIngredients,
    type ParsedIngredient
} from "../services/ingredients";
import { useToast } from "../components/toast";

export default function RecipeDetail() {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const [recipe, setRecipe] = useState<Recipe | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [servings, setServings] = useState(1);
    const [userNote, setUserNote] = useState<RecipeNote | null>(null);
    const [noteText, setNoteText] = useState("");
    const [isEditingNote, setIsEditingNote] = useState(false);
    const [enrichedIngredients, setEnrichedIngredients] = useState<EnrichedIngredients | null>(null);
    const [scaledIngredients, setScaledIngredients] = useState<ParsedIngredient[]>([]);
    const toast = useToast();

    useEffect(() => {
        if (id) {
            loadRecipe(id);
        }
    }, [id]);

    const loadRecipe = async (recipeId: string) => {
        try {
            setIsLoading(true);
            setError(null);
            const recipeData = await getRecipeById(recipeId);
            setRecipe(recipeData);
            setServings(1); // Default serving size

            // Track this recipe as recently viewed
            addToRecentlyViewed(recipeData);

            // Load user's note for this recipe
            const note = getRecipeNote(recipeId);
            setUserNote(note);
            setNoteText(note?.note || "");

            // Load enriched ingredients
            loadEnrichedIngredients(recipeId);
        } catch (err) {
            const msg = err instanceof Error ? err.message : 'Failed to load recipe';
            setError(msg);
            toast.error(msg);
        } finally {
            setIsLoading(false);
        }
    };

    const loadEnrichedIngredients = async (recipeId: string) => {
        try {
            const enriched = await getEnrichedIngredients(recipeId);
            if (enriched) {
                setEnrichedIngredients(enriched);
                // Initialize with 1x serving
                const scaled = scaleRecipeIngredients(enriched, 1);
                setScaledIngredients(scaled);
            }
        } catch (err) {
            console.error('Failed to load enriched ingredients:', err);
            toast.info('Showing basic ingredients');
            // Continue without enriched ingredients - fallback to basic ingredients
        }
    };

    const handleBack = () => {
        navigate(-1); // Go back to previous page
    };

    const setServingSize = (newServings: number) => {
        // Limit serving sizes to reasonable range
        const clampedServings = Math.max(0.5, Math.min(4, newServings));
        setServings(clampedServings);

        // Update scaled ingredients if enriched data is available
        if (enrichedIngredients) {
            const scaled = scaleRecipeIngredients(enrichedIngredients, clampedServings);
            setScaledIngredients(scaled);
        }
    };

    const getScaledQuantity = (ingredient: string) => {
        // Simple scaling - in a real app, you'd parse ingredient quantities more sophisticatedly
        if (servings === 1) return ingredient;
        return ingredient.replace(/(\d+(?:\.\d+)?)/g, (match) => {
            const num = parseFloat(match);
            return (num * servings).toString();
        });
    };

    const handleSaveNote = () => {
        if (!recipe || !noteText.trim()) return;

        try {
            saveRecipeNote(recipe.id, noteText.trim());
            const updatedNote = getRecipeNote(recipe.id);
            setUserNote(updatedNote);
            setIsEditingNote(false);
            toast.success('Note saved');
        } catch (err) {
            setError('Failed to save note');
            toast.error('Failed to save note');
        }
    };

    const handleDeleteNote = () => {
        if (!recipe) return;

        try {
            deleteRecipeNote(recipe.id);
            setUserNote(null);
            setNoteText("");
            setIsEditingNote(false);
            toast.info('Note deleted');
        } catch (err) {
            setError('Failed to delete note');
            toast.error('Failed to delete note');
        }
    };


    const handleEditNote = () => {
        setIsEditingNote(true);
        setNoteText(userNote?.note || "");
    };

    const handleCancelEdit = () => {
        setIsEditingNote(false);
        setNoteText(userNote?.note || "");
    };

    if (isLoading) {
        return (
            <StackedWrapper>
                <div className="flex justify-center items-center min-h-64">
                    <Text>Loading recipe...</Text>
                </div>
            </StackedWrapper>
        );
    }

    if (error || !recipe) {
        return (
            <StackedWrapper>
                <div className="text-center py-12">
                    <Heading>Recipe Not Found</Heading>
                    <br />
                    <Text className="text-gray-500 dark:text-zinc-400 mb-4">
                        {error || 'The recipe you\'re looking for could not be found.'}
                    </Text>
                    <Button onClick={handleBack}>Go Back</Button>
                </div>
            </StackedWrapper>
        );
    }

    return (
        <StackedWrapper>
            <>
                <div className="flex justify-between items-start mb-6">
                    <div className="flex-1">
                        <Heading>{recipe.name}</Heading>
                        <br />
                        <Text className="text-gray-600 dark:text-zinc-400">{recipe.description}</Text>
                    </div>
                    <div className="flex gap-2 ml-4">
                        <Button onClick={handleBack} color="gray">
                            Back
                        </Button>
                        <SaveButton
                            recipeId={recipe.id}
                            size="md"
                        />
                    </div>
                </div>

                {recipe.imageUrl && (
                    <div className="mb-6">
                        <img
                            src={recipe.imageUrl}
                            alt={recipe.name}
                            className="w-full h-64 object-cover rounded-lg"
                        />
                    </div>
                )}

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Recipe Info */}
                    <div className="lg:col-span-1">
                        <Card className="p-6">
                            <Strong>Recipe Info</Strong>
                            <br />
                            <br />
                            <div className="space-y-3">
                                <div className="flex justify-between">
                                    <span>Cook Time:</span>
                                    <span>{recipe.cookTime} min</span>
                                </div>
                                <div className="flex justify-between">
                                    <span>Difficulty:</span>
                                    <span className="capitalize">{recipe.difficulty}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span>Ingredients:</span>
                                    <span>{recipe.ingredients.length}</span>
                                </div>
                                {recipe.cuisine && (
                                    <div className="flex justify-between">
                                        <span>Cuisine:</span>
                                        <span className="capitalize">{recipe.cuisine}</span>
                                    </div>
                                )}
                                {recipe.complexityScore && (
                                    <div className="flex justify-between">
                                        <span>Complexity:</span>
                                        <span>{recipe.complexityScore}/50</span>
                                    </div>
                                )}
                            </div>

                            {recipe.dietaryTags && recipe.dietaryTags.length > 0 && (
                                <>
                                    <br />
                                    <Divider />
                                    <br />
                                    <Strong>Dietary Tags</Strong>
                                    <br />
                                    <br />
                                    <div className="flex flex-wrap gap-2">
                                        {recipe.dietaryTags.map((tag) => (
                                            <span
                                                key={tag}
                                                className="px-2 py-1 bg-gray-100 text-gray-800 text-sm rounded-full capitalize"
                                            >
                                                {tag}
                                            </span>
                                        ))}
                                    </div>
                                </>
                            )}
                        </Card>

                        {/* Serving Size Adjuster */}
                        <Card className="p-6 mt-6">
                            <Strong>Serving Size</Strong>
                            <br />
                            <br />
                            <div className="text-center">
                                <div className="text-lg font-semibold mb-4">
                                    {servings === 1 ? '1 serving' : `${servings}x servings`}
                                </div>
                                <div className="grid grid-cols-3 gap-2">
                                    <Button
                                        size="sm"
                                        color={servings === 0.5 ? "default" : "gray"}
                                        onClick={() => setServingSize(0.5)}
                                    >
                                        0.5x
                                    </Button>
                                    <Button
                                        size="sm"
                                        color={servings === 1 ? "default" : "gray"}
                                        onClick={() => setServingSize(1)}
                                    >
                                        1x
                                    </Button>
                                    <Button
                                        size="sm"
                                        color={servings === 1.5 ? "default" : "gray"}
                                        onClick={() => setServingSize(1.5)}
                                    >
                                        1.5x
                                    </Button>
                                    <Button
                                        size="sm"
                                        color={servings === 2 ? "default" : "gray"}
                                        onClick={() => setServingSize(2)}
                                    >
                                        2x
                                    </Button>
                                    <Button
                                        size="sm"
                                        color={servings === 3 ? "default" : "gray"}
                                        onClick={() => setServingSize(3)}
                                    >
                                        3x
                                    </Button>
                                    <Button
                                        size="sm"
                                        color={servings === 4 ? "default" : "gray"}
                                        onClick={() => setServingSize(4)}
                                    >
                                        4x
                                    </Button>
                                </div>
                            </div>
                        </Card>

                        {/* Recipe Notes */}
                        <Card className="p-6 mt-6">
                            <div className="flex justify-between items-center mb-4">
                                <Strong>My Notes</Strong>
                                {!isEditingNote && userNote && (
                                    <div className="flex gap-2">
                                        <Button size="sm" color="gray" onClick={handleEditNote}>
                                            Edit
                                        </Button>
                                        <Button size="sm" color="red" onClick={handleDeleteNote}>
                                            Delete
                                        </Button>
                                    </div>
                                )}
                            </div>

                            {isEditingNote ? (
                                <div className="space-y-4">
                                    <textarea
                                        value={noteText}
                                        onChange={(e) => setNoteText(e.target.value)}
                                        placeholder="Add your notes about this recipe..."
                                        className="w-full p-3 border rounded-lg resize-none focus:ring-2 focus:ring-gray-200 focus:border-gray-400"
                                        rows={4}
                                    />
                                    <div className="flex gap-2">
                                        <Button size="sm" onClick={handleSaveNote} disabled={!noteText.trim()}>
                                            Save Note
                                        </Button>
                                        <Button size="sm" color="gray" onClick={handleCancelEdit}>
                                            Cancel
                                        </Button>
                                    </div>
                                </div>
                            ) : userNote ? (
                                <div className="bg-gray-50 p-3 rounded-lg">
                                    <Text className="whitespace-pre-wrap">{userNote.note}</Text>
                                    <Text className="text-xs text-gray-500 dark:text-zinc-400 mt-2">
                                        Updated {userNote.updatedAt.toLocaleDateString()}
                                    </Text>
                                </div>
                            ) : (
                                <div className="text-center py-4">
                                    <Text className="text-gray-500 dark:text-zinc-400 mb-2">No notes yet</Text>
                                    <Button size="sm" color="gray" onClick={() => setIsEditingNote(true)}>
                                        Add Note
                                    </Button>
                                </div>
                            )}
                        </Card>
                    </div>

                    {/* Ingredients and Instructions */}
                    <div className="lg:col-span-2 space-y-8">
                        {/* Ingredients */}
                        <Card className="p-6">
                            <div className="flex justify-between items-center mb-4">
                                <Strong>Ingredients</Strong>
                                {scaledIngredients.length > 0 && (
                                    <Text className="text-sm text-green-600">
                                        ✓ Enhanced with quantities
                                    </Text>
                                )}
                            </div>
                            <ul className="space-y-3">
                                {scaledIngredients.length > 0 ? (
                                    // Use enriched ingredients with proper scaling
                                    scaledIngredients.map((ingredient, index) => (
                                        <li key={index} className="flex items-start">
                                            <span className="text-gray-400 mr-3 mt-1">•</span>
                                            <div className="flex-1">
                                                <span className="font-medium">
                                                    {formatIngredient(ingredient)}
                                                </span>
                                                {ingredient.preparation && (
                                                    <div className="text-sm text-gray-600 dark:text-zinc-400 mt-1">
                                                        Preparation: {ingredient.preparation}
                                                    </div>
                                                )}
                                            </div>
                                        </li>
                                    ))
                                ) : (
                                    // Fallback to basic ingredients with simple scaling
                                    recipe.ingredients.map((ingredient, index) => (
                                        <li key={index} className="flex items-start">
                                            <span className="text-gray-400 mr-3 mt-1">•</span>
                                            <span>{getScaledQuantity(ingredient)}</span>
                                        </li>
                                    ))
                                )}
                            </ul>

                        </Card>

                        {/* Instructions */}
                        <Card className="p-6">
                            <Strong>Instructions</Strong>
                            <br />
                            <br />
                            <ol className="space-y-4">
                                {recipe.instructions.map((instruction, index) => (
                                    <li key={index} className="flex items-start">
                                        <span className="flex-shrink-0 w-6 h-6 bg-gray-900 text-white text-sm rounded-full flex items-center justify-center mr-4 mt-1">
                                            {index + 1}
                                        </span>
                                        <span className="flex-1">{instruction}</span>
                                    </li>
                                ))}
                            </ol>
                        </Card>
                    </div>
                </div>

                <br />
                <br />
                <Divider />
                <br />

                <div className="text-center">
                    <Text>
                        Enjoy cooking! Don't forget to save this recipe if you liked it.
                    </Text>
                    <br />
                    <div className="flex justify-center gap-4">
                        <Button onClick={handleBack} color="gray">
                            Back to Results
                        </Button>
                        <Button onClick={() => navigate('/search')}>
                            Find More Recipes
                        </Button>
                    </div>
                </div>
            </>
        </StackedWrapper>
    )
}
