import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Button } from '../button';

describe('Button variants', () => {
  it('renders as anchor when href is provided', () => {
    render(<Button href="/path">Go</Button>);
    const link = screen.getByRole('link', { name: /go/i });
    expect(link).toBeInTheDocument();
    expect(link).toHaveAttribute('href', '/path');
  });

  it('supports outline and plain variants', () => {
    render(<Button outline>Outline</Button>);
    expect(screen.getByRole('button', { name: /outline/i })).toBeInTheDocument();

    render(<Button plain>Plain</Button>);
    expect(screen.getByRole('button', { name: /plain/i })).toBeInTheDocument();
  });

  it('respects disabled attribute', () => {
    render(<Button disabled>Disabled</Button>);
    const btn = screen.getByRole('button', { name: /disabled/i });
    expect(btn).toBeDisabled();
  });
});

