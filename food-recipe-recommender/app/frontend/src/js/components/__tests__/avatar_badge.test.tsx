import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Avatar, AvatarButton } from '../avatar';
import { Badge, BadgeButton } from '../badge';

describe('Avatar and Badge', () => {
  it('renders Avatar with initials and img', () => {
    const { rerender } = render(<Avatar initials="AB" alt="Alice" />);
    // The initials SVG has a title when alt provided
    expect(screen.getByTitle('Alice')).toBeInTheDocument();

    rerender(<Avatar src="/img.png" alt="Pic" />);
    const img = screen.getByAltText('Pic') as HTMLImageElement;
    expect(img).toBeInTheDocument();
    expect(img.src).toContain('/img.png');
  });

  it('renders AvatarButton as button and as link', () => {
    render(<AvatarButton aria-label="avatar" initials="CD" />);
    expect(screen.getByRole('button', { name: /avatar/i })).toBeInTheDocument();

    render(<AvatarButton href="/profile" aria-label="avatar-link" initials="EF" />);
    const link = screen.getByRole('link', { name: /avatar-link/i });
    expect(link).toHaveAttribute('href', '/profile');
  });

  it('renders Badge and BadgeButton variations', () => {
    const { rerender } = render(<Badge>New</Badge>);
    expect(screen.getByText('New')).toBeInTheDocument();

    rerender(<BadgeButton aria-label="bbtn">B</BadgeButton>);
    expect(screen.getByRole('button', { name: /bbtn/i })).toBeInTheDocument();

    rerender(
      <BadgeButton href="/go" aria-label="bbtn-link">
        Go
      </BadgeButton>
    );
    const link = screen.getByRole('link', { name: /bbtn-link/i });
    expect(link).toHaveAttribute('href', '/go');
  });
});

