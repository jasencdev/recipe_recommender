import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import StackedWrapper from "./stackedWrapper";
import { Button } from "../components/button";
import { Heading } from "../components/heading";
import { Strong, Text } from "../components/text";
import { Divider } from '../components/divider'
import Card from '../components/card'
import { Input } from "../components/input";
import { Field, Label } from "../components/fieldset";
import { Dialog } from "../components/dialog";
import { getSavedRecipes, getRecipeById, type Recipe } from "../services/api";

interface Collection {
    id: string;
    name: string;
    description: string;
    recipes: Recipe[];
    createdAt: Date;
}

export default function Collections() {
    const navigate = useNavigate();
    const [collections, setCollections] = useState<Collection[]>([]);
    const [savedRecipes, setSavedRecipes] = useState<Recipe[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showCreateDialog, setShowCreateDialog] = useState(false);
    const [showEditDialog, setShowEditDialog] = useState(false);
    const [editingCollection, setEditingCollection] = useState<Collection | null>(null);
    const [newCollectionName, setNewCollectionName] = useState("");
    const [newCollectionDescription, setNewCollectionDescription] = useState("");

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            setIsLoading(true);

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

            // Load collections from localStorage (in real app, would be from API)
            const savedCollections = localStorage.getItem('recipe-collections');
            if (savedCollections) {
                const parsedCollections = JSON.parse(savedCollections);
                // Update collections with current recipe data
                const updatedCollections = parsedCollections.map((collection: Collection) => ({
                    ...collection,
                    recipes: collection.recipes.map(recipe =>
                        validRecipes.find(r => r.id === recipe.id) || recipe
                    ).filter(Boolean)
                }));
                setCollections(updatedCollections);
            } else {
                // Create default collections based on recipe tags
                createDefaultCollections(validRecipes);
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load data');
        } finally {
            setIsLoading(false);
        }
    };

    const createDefaultCollections = (recipes: Recipe[]) => {
        const defaultCollections: Collection[] = [
            {
                id: 'quick-dinners',
                name: 'Quick Dinners',
                description: 'Fast meals for busy weeknights',
                recipes: recipes.filter(r => r.cookTime <= 30),
                createdAt: new Date()
            },
            {
                id: 'healthy-options',
                name: 'Healthy Options',
                description: 'Nutritious and wholesome recipes',
                recipes: recipes.filter(r => r.dietaryTags?.includes('healthy')),
                createdAt: new Date()
            },
            {
                id: 'desserts',
                name: 'Desserts',
                description: 'Sweet treats and desserts',
                recipes: recipes.filter(r => r.dietaryTags?.includes('dessert')),
                createdAt: new Date()
            }
        ];

        setCollections(defaultCollections);
        localStorage.setItem('recipe-collections', JSON.stringify(defaultCollections));
    };

    const saveCollections = (updatedCollections: Collection[]) => {
        setCollections(updatedCollections);
        localStorage.setItem('recipe-collections', JSON.stringify(updatedCollections));
    };

    const createCollection = () => {
        if (!newCollectionName.trim()) return;

        const newCollection: Collection = {
            id: Date.now().toString(),
            name: newCollectionName.trim(),
            description: newCollectionDescription.trim(),
            recipes: [],
            createdAt: new Date()
        };

        saveCollections([...collections, newCollection]);
        setNewCollectionName("");
        setNewCollectionDescription("");
        setShowCreateDialog(false);
    };

    const updateCollection = () => {
        if (!editingCollection || !newCollectionName.trim()) return;

        const updatedCollections = collections.map(collection =>
            collection.id === editingCollection.id
                ? { ...collection, name: newCollectionName.trim(), description: newCollectionDescription.trim() }
                : collection
        );

        saveCollections(updatedCollections);
        setEditingCollection(null);
        setNewCollectionName("");
        setNewCollectionDescription("");
        setShowEditDialog(false);
    };

    const deleteCollection = (collectionId: string) => {
        if (confirm('Are you sure you want to delete this collection?')) {
            const updatedCollections = collections.filter(c => c.id !== collectionId);
            saveCollections(updatedCollections);
        }
    };

    const addRecipeToCollection = (collectionId: string, recipe: Recipe) => {
        const updatedCollections = collections.map(collection => {
            if (collection.id === collectionId) {
                const recipeExists = collection.recipes.some(r => r.id === recipe.id);
                if (!recipeExists) {
                    return { ...collection, recipes: [...collection.recipes, recipe] };
                }
            }
            return collection;
        });
        saveCollections(updatedCollections);
    };

    const removeRecipeFromCollection = (collectionId: string, recipeId: string) => {
        const updatedCollections = collections.map(collection => {
            if (collection.id === collectionId) {
                return {
                    ...collection,
                    recipes: collection.recipes.filter(r => r.id !== recipeId)
                };
            }
            return collection;
        });
        saveCollections(updatedCollections);
    };

    const openEditDialog = (collection: Collection) => {
        setEditingCollection(collection);
        setNewCollectionName(collection.name);
        setNewCollectionDescription(collection.description);
        setShowEditDialog(true);
    };

    if (isLoading) {
        return (
            <StackedWrapper>
                <div className="flex justify-center items-center min-h-64">
                    <Text>Loading collections...</Text>
                </div>
            </StackedWrapper>
        );
    }

    return (
        <StackedWrapper>
            <>
                <div className="flex justify-between items-start mb-6">
                    <div>
                        <Heading>Recipe Collections</Heading>
                        <br />
                        <Strong>Organize your saved recipes</Strong>
                    </div>
                    <div className="flex gap-2">
                        <Button onClick={() => navigate('/saved-recipes')} color="gray">
                            Back to Saved Recipes
                        </Button>
                        <Button onClick={() => setShowCreateDialog(true)}>
                            New Collection
                        </Button>
                    </div>
                </div>

                {error && (
                    <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                        <Text className="text-red-700">{error}</Text>
                    </div>
                )}

                {/* Collections Overview */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    <Card className="p-4">
                        <Strong>Total Collections</Strong>
                        <div className="text-2xl font-bold mt-2">{collections.length}</div>
                        <Text className="text-sm text-gray-600">Recipe groups</Text>
                    </Card>

                    <Card className="p-4">
                        <Strong>Total Recipes</Strong>
                        <div className="text-2xl font-bold mt-2">{savedRecipes.length}</div>
                        <Text className="text-sm text-gray-600">Available to organize</Text>
                    </Card>

                    <Card className="p-4">
                        <Strong>Organized Recipes</Strong>
                        <div className="text-2xl font-bold mt-2">
                            {new Set(collections.flatMap(c => c.recipes.map(r => r.id))).size}
                        </div>
                        <Text className="text-sm text-gray-600">In collections</Text>
                    </Card>
                </div>

                <Divider />
                <br />

                {/* Collections Grid */}
                {collections.length === 0 ? (
                    <div className="text-center py-12">
                        <Text className="text-gray-500 mb-4">No collections yet.</Text>
                        <Button onClick={() => setShowCreateDialog(true)}>
                            Create Your First Collection
                        </Button>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {collections.map((collection) => (
                            <Card key={collection.id} className="p-6">
                                <div className="flex justify-between items-start mb-4">
                                    <div>
                                        <Strong>{collection.name}</Strong>
                                        <br />
                                        {collection.description && (
                                            <Text className="text-sm text-gray-600 mt-1">
                                                {collection.description}
                                            </Text>
                                        )}
                                    </div>
                                    <div className="flex gap-1">
                                        <Button
                                            size="sm"
                                            color="gray"
                                            onClick={() => openEditDialog(collection)}
                                        >
                                            Edit
                                        </Button>
                                        <Button
                                            size="sm"
                                            color="red"
                                            onClick={() => deleteCollection(collection.id)}
                                        >
                                            ×
                                        </Button>
                                    </div>
                                </div>

                                <div className="text-center mb-4">
                                    <div className="text-2xl font-bold">{collection.recipes.length}</div>
                                    <Text className="text-sm text-gray-600">recipes</Text>
                                </div>

                                {collection.recipes.length > 0 && (
                                    <div className="space-y-2 mb-4 max-h-32 overflow-y-auto">
                                        {collection.recipes.slice(0, 3).map((recipe) => (
                                            <div key={recipe.id} className="flex justify-between items-center text-sm">
                                                <span className="truncate">{recipe.name}</span>
                                                <Button
                                                    size="sm"
                                                    color="red"
                                                    className="text-xs ml-2"
                                                    onClick={() => removeRecipeFromCollection(collection.id, recipe.id)}
                                                >
                                                    ×
                                                </Button>
                                            </div>
                                        ))}
                                        {collection.recipes.length > 3 && (
                                            <Text className="text-xs text-gray-500">
                                                +{collection.recipes.length - 3} more recipes
                                            </Text>
                                        )}
                                    </div>
                                )}

                                <div className="space-y-2">
                                    <select
                                        className="w-full p-2 border rounded text-sm"
                                        onChange={(e) => {
                                            if (e.target.value) {
                                                const recipe = savedRecipes.find(r => r.id === e.target.value);
                                                if (recipe) {
                                                    addRecipeToCollection(collection.id, recipe);
                                                    e.target.value = "";
                                                }
                                            }
                                        }}
                                    >
                                        <option value="">Add recipe...</option>
                                        {savedRecipes
                                            .filter(recipe => !collection.recipes.some(r => r.id === recipe.id))
                                            .map(recipe => (
                                                <option key={recipe.id} value={recipe.id}>
                                                    {recipe.name}
                                                </option>
                                            ))}
                                    </select>
                                </div>
                            </Card>
                        ))}
                    </div>
                )}

                {/* Create Collection Dialog */}
                <Dialog open={showCreateDialog} onClose={() => setShowCreateDialog(false)}>
                    <div className="p-6">
                        <Heading level={3}>Create New Collection</Heading>
                        <br />
                        <div className="space-y-4">
                            <Field>
                                <Label htmlFor="collection-name">Collection Name</Label>
                                <Input
                                    id="collection-name"
                                    value={newCollectionName}
                                    onChange={(e) => setNewCollectionName(e.target.value)}
                                    placeholder="e.g., Sunday Dinners"
                                />
                            </Field>
                            <Field>
                                <Label htmlFor="collection-description">Description (optional)</Label>
                                <Input
                                    id="collection-description"
                                    value={newCollectionDescription}
                                    onChange={(e) => setNewCollectionDescription(e.target.value)}
                                    placeholder="Brief description of this collection"
                                />
                            </Field>
                        </div>
                        <br />
                        <div className="flex gap-2 justify-end">
                            <Button color="gray" onClick={() => setShowCreateDialog(false)}>
                                Cancel
                            </Button>
                            <Button onClick={createCollection} disabled={!newCollectionName.trim()}>
                                Create Collection
                            </Button>
                        </div>
                    </div>
                </Dialog>

                {/* Edit Collection Dialog */}
                <Dialog open={showEditDialog} onClose={() => setShowEditDialog(false)}>
                    <div className="p-6">
                        <Heading level={3}>Edit Collection</Heading>
                        <br />
                        <div className="space-y-4">
                            <Field>
                                <Label htmlFor="edit-collection-name">Collection Name</Label>
                                <Input
                                    id="edit-collection-name"
                                    value={newCollectionName}
                                    onChange={(e) => setNewCollectionName(e.target.value)}
                                />
                            </Field>
                            <Field>
                                <Label htmlFor="edit-collection-description">Description</Label>
                                <Input
                                    id="edit-collection-description"
                                    value={newCollectionDescription}
                                    onChange={(e) => setNewCollectionDescription(e.target.value)}
                                />
                            </Field>
                        </div>
                        <br />
                        <div className="flex gap-2 justify-end">
                            <Button color="gray" onClick={() => setShowEditDialog(false)}>
                                Cancel
                            </Button>
                            <Button onClick={updateCollection} disabled={!newCollectionName.trim()}>
                                Update Collection
                            </Button>
                        </div>
                    </div>
                </Dialog>
            </>
        </StackedWrapper>
    )
}