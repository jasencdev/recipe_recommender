import { describe, it, expect, vi, beforeEach } from 'vitest';

vi.mock('axios', () => {
  const get = vi.fn();
  const post = vi.fn();
  const del = vi.fn();
  const instance = { get, post, delete: del };
  return {
    default: { create: () => instance },
  };
});

import api, { getAuthStatus, searchRecipes, getRecipeById, getSavedRecipes, saveRecipe, removeSavedRecipe, getSavedRecipeIds, isRecipeSaved, toggleSaveRecipe } from '../api';

const axiosInstance = (api as any);

describe('api service', () => {
  beforeEach(() => {
    axiosInstance.get.mockReset();
    axiosInstance.post.mockReset();
    axiosInstance.delete.mockReset();
  });

  it('getAuthStatus returns data on success', async () => {
    axiosInstance.get.mockResolvedValue({ data: { ok: true } });
    const res = await getAuthStatus();
    expect(res).toEqual({ ok: true });
  });

  it('getAuthStatus throws formatted error on failure', async () => {
    axiosInstance.get.mockRejectedValue({ message: 'fail', response: { data: { message: 'nope' } } });
    await expect(getAuthStatus()).rejects.toThrow('nope');
  });

  it('save/remove recipe propagate axios errors as Error', async () => {
    axiosInstance.post.mockRejectedValue({ message: 'fail', response: { data: { message: 'nope' } } });
    await expect(saveRecipe('1')).rejects.toThrow('nope');

    axiosInstance.delete.mockRejectedValue({ message: 'boom', response: { data: { message: 'bad' } } });
    await expect(removeSavedRecipe('1')).rejects.toThrow('bad');
  });

  it('searchRecipes builds query and returns data', async () => {
    axiosInstance.get.mockResolvedValue({ data: { recipes: [], total: 0, page: 1, limit: 20, hasMore: false } });
    await searchRecipes(
      {
        query: 'pasta',
        complexityScore: 10,
        numberOfIngredients: 5,
        dietaryRestrictions: ['vegan', 'gluten-free'],
        cuisine: 'italian',
        cookTime: 30,
      },
      2,
      50
    );
    const called = axiosInstance.get.mock.calls[0][0] as string;
    expect(called).toContain('/search?');
    expect(called).toContain('query=pasta');
    expect(called).toContain('complexity_score=10');
    expect(called).toContain('number_of_ingredients=5');
    expect(called).toContain('dietary_restrictions=vegan%2Cgluten-free');
    expect(called).toContain('cuisine=italian');
    expect(called).toContain('cook_time=30');
    expect(called).toContain('page=2');
    expect(called).toContain('limit=50');
  });

  it('searchRecipes with empty filters only sends page/limit', async () => {
    axiosInstance.get.mockResolvedValue({ data: { recipes: [], total: 0, page: 1, limit: 20, hasMore: false } });
    await searchRecipes({}, 1, 20);
    const called = axiosInstance.get.mock.calls.pop()[0] as string;
    expect(called).toContain('/search?');
    expect(called).toContain('page=1');
    expect(called).toContain('limit=20');
    expect(called).not.toContain('query=');
    expect(called).not.toContain('complexity_score=');
    expect(called).not.toContain('number_of_ingredients=');
    expect(called).not.toContain('dietary_restrictions=');
    expect(called).not.toContain('cuisine=');
    expect(called).not.toContain('cook_time=');
  });

  it('searchRecipes throws formatted error on failure', async () => {
    axiosInstance.get.mockRejectedValue({ message: 'boom', response: { data: { message: 'bad' } } });
    await expect(searchRecipes({})).rejects.toThrow('bad');
  });

  it('getRecipeById success and error', async () => {
    axiosInstance.get.mockResolvedValueOnce({ data: { recipe: { id: '1' } } });
    const r = await getRecipeById('1');
    expect(r).toEqual({ id: '1' });
    axiosInstance.get.mockRejectedValueOnce({ message: 'err', response: { data: { message: 'no' } } });
    await expect(getRecipeById('2')).rejects.toThrow('no');
  });

  it('error paths fall back to err.message when no response', async () => {
    axiosInstance.get.mockRejectedValueOnce({ message: 'auth-err' });
    await expect(getAuthStatus()).rejects.toThrow('auth-err');

    axiosInstance.get.mockRejectedValueOnce({ message: 'search-err' });
    await expect(searchRecipes({})).rejects.toThrow('search-err');

    axiosInstance.get.mockRejectedValueOnce({ message: 'get-recipe-err' });
    await expect(getRecipeById('x')).rejects.toThrow('get-recipe-err');

    axiosInstance.get.mockRejectedValueOnce({ message: 'get-saved-err' });
    await expect(getSavedRecipes()).rejects.toThrow('get-saved-err');

    axiosInstance.post.mockRejectedValueOnce({ message: 'save-err' });
    await expect(saveRecipe('x')).rejects.toThrow('save-err');

    axiosInstance.delete.mockRejectedValueOnce({ message: 'remove-err' });
    await expect(removeSavedRecipe('x')).rejects.toThrow('remove-err');
  });

  it('getSavedRecipes success and error', async () => {
    axiosInstance.get.mockResolvedValueOnce({ data: { recipes: [{ id: 'x' }] } });
    const rr = await getSavedRecipes();
    expect(rr).toEqual([{ id: 'x' }]);
    axiosInstance.get.mockRejectedValueOnce({ message: 'e', response: { data: { message: 'oops' } } });
    await expect(getSavedRecipes()).rejects.toThrow('oops');
  });

  it('getSavedRecipeIds caches and forceRefresh triggers new request', async () => {
    axiosInstance.get
      .mockResolvedValueOnce({ data: { recipes: [{ id: '1' }, { id: '2' }] } })
      .mockResolvedValueOnce({ data: { recipes: [{ id: '2' }, { id: '3' }] } });

    const set1 = await getSavedRecipeIds();
    expect(set1 instanceof Set).toBe(true);
    expect(Array.from(set1)).toEqual(['1', '2']);
    expect(axiosInstance.get).toHaveBeenCalledTimes(1);

    // Cached call should not hit network
    const setCached = await getSavedRecipeIds();
    expect(Array.from(setCached)).toEqual(['1', '2']);
    expect(axiosInstance.get).toHaveBeenCalledTimes(1);

    // Force refresh should call again
    const set2 = await getSavedRecipeIds(true);
    expect(Array.from(set2)).toEqual(['2', '3']);
    expect(axiosInstance.get).toHaveBeenCalledTimes(2);
  });

  it('getSavedRecipeIds returns empty set on error and clears pending', async () => {
    axiosInstance.get.mockRejectedValueOnce({ message: 'net' });
    const set = await getSavedRecipeIds(true);
    expect(set instanceof Set).toBe(true);
    expect(Array.from(set)).toEqual([]);
    // Subsequent call should try again (pending cleared)
    axiosInstance.get.mockResolvedValueOnce({ data: { recipes: [{ id: 'z' }] } });
    const set2 = await getSavedRecipeIds(true);
    expect(Array.from(set2)).toEqual(['z']);
  });

  it('getSavedRecipeIds coalesces concurrent requests', async () => {
    let resolveFn: any;
    const deferred = new Promise((res) => (resolveFn = res));
    axiosInstance.get.mockReturnValueOnce(deferred);

    const p1 = getSavedRecipeIds(true);
    const p2 = getSavedRecipeIds(true);
    expect(axiosInstance.get).toHaveBeenCalledTimes(1);

    resolveFn({ data: { recipes: [{ id: 'a' }] } });
    const [s1, s2] = await Promise.all([p1, p2]);
    expect(Array.from(s1)).toEqual(['a']);
    expect(Array.from(s2)).toEqual(['a']);
  });

  it('isRecipeSaved checks membership', async () => {
    axiosInstance.get.mockResolvedValue({ data: { recipes: [{ id: '9' }] } });
    const saved = await isRecipeSaved('9');
    expect(saved).toBe(true);
  });

  it('toggleSaveRecipe calls delete when already saved, post when not', async () => {
    // Already saved path
    axiosInstance.get.mockResolvedValueOnce({ data: { recipes: [{ id: '5' }] } });
    axiosInstance.delete.mockResolvedValue({});
    let result = await toggleSaveRecipe('5');
    expect(result).toBe(false);
    expect(axiosInstance.delete).toHaveBeenCalled();

    // Not saved path
    axiosInstance.get.mockResolvedValueOnce({ data: { recipes: [] } });
    axiosInstance.post.mockResolvedValue({});
    result = await toggleSaveRecipe('7');
    expect(result).toBe(true);
    expect(axiosInstance.post).toHaveBeenCalled();
  });
});
