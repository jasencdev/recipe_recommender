import { describe, it, expect, vi, beforeEach, type Mock } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import LoginPage from '../login';
import ForgotPassword from '../forgot-password';

describe('Login and Forgot Password pages', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn());
  });

  it('submits login form and calls /api/login', async () => {
    (fetch as unknown as Mock).mockResolvedValue({ json: async () => ({ success: true }) });
    const { container } = render(<LoginPage />);

    const form = container.querySelector('form') as HTMLFormElement;
    fireEvent.submit(form);

    expect(fetch).toHaveBeenCalled();
    const [url, opts] = (fetch as unknown as Mock).mock.calls[0] as any[];
    expect(url).toBe('/api/login');
    expect((opts as any).method).toBe('POST');
  });

  it('submits forgot password and shows sent message', async () => {
    (fetch as unknown as Mock).mockResolvedValue({ json: async () => ({ success: true }) });
    const { container } = render(<ForgotPassword />);
    const input = container.querySelector('input[name="email"]') as HTMLInputElement;
    fireEvent.change(input, { target: { value: 'person@example.com' } });

    const form = container.querySelector('form') as HTMLFormElement;
    fireEvent.submit(form);

    // Message should appear indicating link sent
    expect(await screen.findByText(/We’ve sent a reset link/i)).toBeInTheDocument();
    expect(fetch).toHaveBeenCalledWith('/api/forgot-password', expect.anything());
  });
});
