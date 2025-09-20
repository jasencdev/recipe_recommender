import type { Recipe } from './api';

const RECIPE_NOTES_KEY = 'recipe-notes';

export interface RecipeNote {
    id: string;
    recipeId: string;
    note: string;
    createdAt: Date;
    updatedAt: Date;
}

export interface RecipeWithUserData extends Recipe {
    userNote?: RecipeNote;
}

export const saveRecipeNote = (recipeId: string, noteText: string): void => {
    try {
        const notes = getRecipeNotes();
        const existingNote = notes.find(note => note.recipeId === recipeId);

        if (existingNote) {
            // Update existing note
            existingNote.note = noteText;
            existingNote.updatedAt = new Date();
        } else {
            // Create new note
            const newNote: RecipeNote = {
                id: `note_${recipeId}_${Date.now()}`,
                recipeId,
                note: noteText,
                createdAt: new Date(),
                updatedAt: new Date()
            };
            notes.push(newNote);
        }

        localStorage.setItem(RECIPE_NOTES_KEY, JSON.stringify(notes));
    } catch (error) {
        console.error('Failed to save recipe note:', error);
    }
};

export const getRecipeNote = (recipeId: string): RecipeNote | null => {
    try {
        const notes = getRecipeNotes();
        return notes.find(note => note.recipeId === recipeId) || null;
    } catch (error) {
        console.error('Failed to get recipe note:', error);
        return null;
    }
};

export const getRecipeNotes = (): RecipeNote[] => {
    try {
        const stored = localStorage.getItem(RECIPE_NOTES_KEY);
        if (!stored) return [];

        const notes = JSON.parse(stored);
        return notes.map((note: any) => ({
            ...note,
            createdAt: new Date(note.createdAt),
            updatedAt: new Date(note.updatedAt)
        }));
    } catch (error) {
        console.error('Failed to get recipe notes:', error);
        return [];
    }
};

export const deleteRecipeNote = (recipeId: string): void => {
    try {
        const notes = getRecipeNotes();
        const filteredNotes = notes.filter(note => note.recipeId !== recipeId);
        localStorage.setItem(RECIPE_NOTES_KEY, JSON.stringify(filteredNotes));
    } catch (error) {
        console.error('Failed to delete recipe note:', error);
    }
};

export const enrichRecipeWithUserData = (recipe: Recipe): RecipeWithUserData => {
    const userNote = getRecipeNote(recipe.id);

    return {
        ...recipe,
        userNote: userNote || undefined
    };
};