import { describe, it, expect, beforeEach } from 'vitest';
import {
  saveRecipeNote,
  getRecipeNote,
  getRecipeNotes,
  deleteRecipeNote,
  enrichRecipeWithUserData,
} from '../recipeNotes';

describe('recipeNotes', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('saves, reads, updates, deletes notes and enriches recipe', () => {
    expect(getRecipeNotes()).toEqual([]);

    saveRecipeNote('r1', 'hello');
    let note = getRecipeNote('r1');
    expect(note?.note).toBe('hello');
    expect(note?.createdAt instanceof Date).toBe(true);
    expect(note?.updatedAt instanceof Date).toBe(true);

    saveRecipeNote('r1', 'updated');
    note = getRecipeNote('r1');
    expect(note?.note).toBe('updated');

    const recipe = { id: 'r1', name: '', description: '', cookTime: 0, difficulty: 'easy', ingredients: [], instructions: [] } as any;
    const enriched = enrichRecipeWithUserData(recipe);
    expect(enriched.userNote?.note).toBe('updated');

    deleteRecipeNote('r1');
    expect(getRecipeNote('r1')).toBeNull();
  });
});

