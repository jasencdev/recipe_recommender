import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import AuthProvider, { useAuth } from '../AuthContext';

vi.mock('../../services/api', () => ({
  getAuthStatus: vi.fn(),
}));

import { getAuthStatus } from '../../services/api';

function Probe() {
  const { user, loading } = useAuth();
  return (
    <div>
      <div data-testid="loading">{String(loading)}</div>
      <div data-testid="email">{user?.email ?? ''}</div>
    </div>
  );
}

describe('AuthProvider', () => {
  it('sets user on successful auth status', async () => {
    (getAuthStatus as unknown as vi.Mock).mockResolvedValue({
      authenticated: true,
      user: { id: 1, email: 'tester@example.com' },
    });

    render(
      <AuthProvider>
        <Probe />
      </AuthProvider>
    );

    // loading initially true, eventually false and email filled
    await waitFor(() => {
      expect(screen.getByTestId('loading').textContent).toBe('false');
      expect(screen.getByTestId('email').textContent).toBe('tester@example.com');
    });
  });

  it('clears user on failed auth status', async () => {
    (getAuthStatus as unknown as vi.Mock).mockRejectedValue(new Error('unauthorized'));

    render(
      <AuthProvider>
        <Probe />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('loading').textContent).toBe('false');
      expect(screen.getByTestId('email').textContent).toBe('');
    });
  });
});

