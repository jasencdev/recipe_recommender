import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Table, TableHead, TableHeader, TableBody, TableRow, TableCell } from '../table';

describe('Table edge cases', () => {
  it('renders dense + grid + striped and row without href', () => {
    render(
      <Table bleed dense grid striped>
        <TableHead>
          <tr>
            <TableHeader>H</TableHeader>
          </tr>
        </TableHead>
        <TableBody>
          <TableRow>
            <TableCell>Cell 1</TableCell>
            <TableCell>Cell 2</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    );
    expect(screen.getByText('H')).toBeInTheDocument();
    expect(screen.getByText('Cell 1')).toBeInTheDocument();
    // No overlay link when row has no href
    expect(screen.queryByRole('link', { name: /row/i })).toBeNull();
  });
});

