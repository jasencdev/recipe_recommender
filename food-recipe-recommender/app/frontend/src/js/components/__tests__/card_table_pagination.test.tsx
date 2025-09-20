import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import Card from '../card';
import { Table, TableHead, TableHeader, TableBody, TableRow, TableCell } from '../table';
import { Pagination, PaginationPrevious, PaginationNext, PaginationList, PaginationPage, PaginationGap } from '../pagination';

describe('Card, Table, and Pagination', () => {
  it('renders Card content', () => {
    render(<Card>Content</Card>);
    expect(screen.getByText('Content')).toBeInTheDocument();
  });

  it('renders Table with header and link row', () => {
    render(
      <Table>
        <TableHead>
          <tr>
            <TableHeader>Col</TableHeader>
          </tr>
        </TableHead>
        <TableBody>
          <TableRow href="/row/1" title="Row 1">
            <TableCell>Cell</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    );
    expect(screen.getByText('Col')).toBeInTheDocument();
    expect(screen.getByText('Cell')).toBeInTheDocument();
    // Overlay link exists with aria-label from title
    const rowLink = screen.getByRole('link', { name: 'Row 1' });
    expect(rowLink).toHaveAttribute('href', '/row/1');
  });

  it('renders Pagination controls with states', () => {
    render(
      <Pagination>
        <PaginationPrevious />
        <PaginationList>
          <PaginationPage href="/p/1" current>
            1
          </PaginationPage>
          <PaginationGap />
          <PaginationPage href="/p/3">3</PaginationPage>
        </PaginationList>
        <PaginationNext href="/next" />
      </Pagination>
    );

    // Previous should be disabled button
    const prev = screen.getByRole('button', { name: /previous page/i });
    expect(prev).toBeDisabled();

    // Current page has aria-current
    const page1 = screen.getByRole('link', { name: /page 1/i });
    expect(page1).toHaveAttribute('aria-current', 'page');

    // Has gap and next link
    expect(screen.getByText('…')).toBeInTheDocument();
    const next = screen.getByRole('link', { name: /next page/i });
    expect(next).toHaveAttribute('href', '/next');
  });
});

