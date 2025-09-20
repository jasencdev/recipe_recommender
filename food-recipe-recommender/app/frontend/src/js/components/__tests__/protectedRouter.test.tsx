import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import AuthProvider from '../AuthContext';
import ProtectedRoute from '../ProtectedRouter';

vi.mock('../../services/api', () => ({
  getAuthStatus: vi.fn(),
}));

import { getAuthStatus } from '../../services/api';

describe('ProtectedRoute', () => {
  it('redirects to /login when unauthenticated', async () => {
    (getAuthStatus as unknown as vi.Mock).mockRejectedValue(new Error('unauthorized'));

    render(
      <MemoryRouter initialEntries={["/"]}>
        <AuthProvider>
          <Routes>
            <Route path="/" element={<ProtectedRoute><div>Private</div></ProtectedRoute>} />
            <Route path="/login" element={<div>Login Page</div>} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Login Page')).toBeInTheDocument();
    });
  });

  it('renders children when authenticated', async () => {
    (getAuthStatus as unknown as vi.Mock).mockResolvedValue({
      authenticated: true,
      user: { id: 1, email: 'tester@example.com' },
    });

    render(
      <MemoryRouter initialEntries={["/"]}>
        <AuthProvider>
          <Routes>
            <Route path="/" element={<ProtectedRoute><div>Private</div></ProtectedRoute>} />
            <Route path="/login" element={<div>Login Page</div>} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Private')).toBeInTheDocument();
    });
  });
});

