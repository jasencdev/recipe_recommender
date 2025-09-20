import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Input, InputGroup } from '../input';
import { Fieldset, Legend, Field, Label, Description, ErrorMessage, FieldGroup } from '../fieldset';
import { Checkbox, CheckboxField, CheckboxGroup } from '../checkbox';
import { Select } from '../select';
import { Textarea } from '../textarea';

describe('Form controls', () => {
  it('renders Input and InputGroup', () => {
    render(
      <InputGroup>
        <Input placeholder="Type here" />
      </InputGroup>
    );
    expect(screen.getByPlaceholderText('Type here')).toBeInTheDocument();
  });

  it('renders Select single and multiple', () => {
    const { rerender } = render(<Select defaultValue="a"><option value="a">A</option></Select>);
    const select = screen.getByDisplayValue('A');
    expect(select).toBeInTheDocument();

    rerender(<Select multiple defaultValue={["a"]}><option value="a">A</option></Select>);
    expect(screen.getByDisplayValue('A')).toBeInTheDocument();
  });

  it('renders Textarea resizable and non-resizable', () => {
    const { rerender } = render(<Textarea placeholder="Note" />);
    expect(screen.getByPlaceholderText('Note')).toBeInTheDocument();
    rerender(<Textarea placeholder="Note" resizable={false} />);
    expect(screen.getByPlaceholderText('Note')).toBeInTheDocument();
  });

  it('renders Fieldset group with label, description, and error', () => {
    render(
      <Fieldset>
        <Legend>Legend</Legend>
        <Field>
          <Label htmlFor="x">Label</Label>
          <Description>Helpful</Description>
          <ErrorMessage>Error</ErrorMessage>
          <FieldGroup>
            <input id="x" />
          </FieldGroup>
        </Field>
      </Fieldset>
    );
    expect(screen.getByText('Legend')).toBeInTheDocument();
    expect(screen.getByText('Label')).toBeInTheDocument();
    expect(screen.getByText('Helpful')).toBeInTheDocument();
    expect(screen.getByText('Error')).toBeInTheDocument();
  });

  it('renders Checkbox, CheckboxField and group', () => {
    render(
      <CheckboxGroup>
        <CheckboxField>
          <Checkbox aria-label="cb" defaultChecked />
        </CheckboxField>
      </CheckboxGroup>
    );
    // The underlying HeadlessUI checkbox is a button role
    const cb = screen.getByRole('checkbox', { hidden: true }) || screen.getByRole('button', { hidden: true });
    expect(cb).toBeTruthy();
  });
});

