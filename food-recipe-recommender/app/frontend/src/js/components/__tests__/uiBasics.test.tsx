import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Divider } from '../divider';
import { Heading, Subheading } from '../heading';
import { Text, TextLink, Strong, Code } from '../text';

describe('UI basics', () => {
  it('renders Divider soft and regular', () => {
    const { rerender } = render(<Divider soft />);
    const hr = screen.getByRole('presentation');
    expect(hr.tagName.toLowerCase()).toBe('hr');
    rerender(<Divider />);
    expect(screen.getByRole('presentation')).toBeInTheDocument();
  });

  it('renders Heading and Subheading at various levels', () => {
    render(
      <>
        <Heading level={1}>H1</Heading>
        <Subheading level={3}>H3</Subheading>
      </>
    );
    expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
    expect(screen.getByRole('heading', { level: 3 })).toBeInTheDocument();
  });

  it('renders text variants', () => {
    render(
      <>
        <Text>Paragraph</Text>
        <TextLink href="/to"><Strong>Go</Strong></TextLink>
        <Code>{'const a = 1'}</Code>
      </>
    );
    expect(screen.getByText('Paragraph')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /go/i })).toHaveAttribute('href', '/to');
    expect(screen.getByText('const a = 1')).toBeInTheDocument();
  });
});

