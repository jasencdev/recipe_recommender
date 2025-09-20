import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Link } from '../link';

describe('Link', () => {
  it('renders anchor with href', () => {
    render(<Link href="/test">Go</Link>);
    const a = screen.getByRole('link', { name: /go/i });
    expect(a).toBeInTheDocument();
    expect(a).toHaveAttribute('href', '/test');
  });
});

