import { describe, it, expect, beforeEach } from 'vitest';
import {
  addToRecentlyViewed,
  getRecentlyViewed,
  clearRecentlyViewed,
  removeFromRecentlyViewed,
  getRecentlyViewedByTimeframe,
} from '../recentlyViewed';

const sample = {
  id: 'r1',
  name: 'Recipe 1',
  description: '',
  cookTime: 10,
  difficulty: 'easy',
  ingredients: [],
  instructions: [],
};

describe('recentlyViewed', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('adds, reads, removes, and clears', () => {
    expect(getRecentlyViewed()).toEqual([]);
    addToRecentlyViewed(sample as any);
    const list1 = getRecentlyViewed();
    expect(list1.length).toBe(1);
    expect(list1[0].id).toBe('r1');
    expect(list1[0].viewedAt instanceof Date).toBe(true);

    addToRecentlyViewed({ ...sample, id: 'r2' } as any);
    expect(getRecentlyViewed().length).toBe(2);

    removeFromRecentlyViewed('r1');
    const list2 = getRecentlyViewed();
    expect(list2.map(r => r.id)).toEqual(['r2']);

    clearRecentlyViewed();
    expect(getRecentlyViewed()).toEqual([]);
  });

  it('filters by timeframe', () => {
    addToRecentlyViewed(sample as any);
    const recent = getRecentlyViewedByTimeframe(7);
    expect(recent.length).toBe(1);
  });
});

