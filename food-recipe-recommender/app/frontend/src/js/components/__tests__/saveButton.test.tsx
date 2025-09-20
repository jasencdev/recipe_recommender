import { describe, it, expect, vi, type Mock } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import SaveButton from '../saveButton';

vi.mock('../../services/api', () => ({
  isRecipeSaved: vi.fn(),
  toggleSaveRecipe: vi.fn(),
}));

import { isRecipeSaved, toggleSaveRecipe } from '../../services/api';

describe('SaveButton', () => {
  it('shows initial saved state and toggles on click', async () => {
    (isRecipeSaved as unknown as Mock).mockResolvedValue(false);
    (toggleSaveRecipe as unknown as Mock).mockResolvedValue(true);

    const onSaveChange = vi.fn();
    render(<SaveButton recipeId="123" onSaveChange={onSaveChange} />);

    // Initially shows loading state
    expect(await screen.findByRole('button')).toBeInTheDocument();

    // After load, should show Save
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /save/i })).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('button'));

    await waitFor(() => {
      expect(toggleSaveRecipe).toHaveBeenCalledWith('123');
      expect(screen.getByRole('button', { name: /saved/i })).toBeInTheDocument();
      expect(onSaveChange).toHaveBeenCalledWith(true);
    });
  });
});
