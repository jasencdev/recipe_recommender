import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { AuthLayout } from '../auth-layout';
import { Alert, AlertTitle, AlertDescription, AlertBody, AlertActions } from '../alert';
import { Navbar, NavbarItem, NavbarSection, NavbarDivider, NavbarSpacer, NavbarLabel } from '../navbar';
import {
  Sidebar,
  SidebarHeader,
  SidebarBody,
  SidebarFooter,
  SidebarSection,
  SidebarItem,
  SidebarHeading,
  SidebarDivider,
  SidebarSpacer,
  SidebarLabel,
} from '../sidebar';
import { StackedLayout } from '../stacked-layout';
import { Switch } from '../switch';
import { Radio, RadioGroup, RadioField } from '../radio';

describe('AuthLayout and Alert', () => {
  it('renders AuthLayout children', () => {
    render(
      <AuthLayout>
        <div>Child</div>
      </AuthLayout>
    );
    expect(screen.getByText('Child')).toBeInTheDocument();
  });

  it('renders Alert with title, description, body, and actions', () => {
    const onClose = vi.fn();
    render(
      <Alert open onClose={onClose}>
        <AlertTitle>Title</AlertTitle>
        <AlertDescription>Description</AlertDescription>
        <AlertBody>Body</AlertBody>
        <AlertActions>
          <button>Ok</button>
        </AlertActions>
      </Alert>
    );
    expect(screen.getByText('Title')).toBeInTheDocument();
    expect(screen.getByText('Description')).toBeInTheDocument();
    expect(screen.getByText('Body')).toBeInTheDocument();
    expect(screen.getByText('Ok')).toBeInTheDocument();
  });
});

describe('Navbar and Sidebar', () => {
  it('renders Navbar with items and sections', () => {
    render(
      <Navbar>
        <NavbarSection>
          <NavbarItem href="/home">
            <NavbarLabel>Home</NavbarLabel>
          </NavbarItem>
          <NavbarDivider />
          <NavbarItem current>
            <NavbarLabel>Current</NavbarLabel>
          </NavbarItem>
        </NavbarSection>
        <NavbarSpacer />
      </Navbar>
    );
    expect(screen.getByRole('link', { name: /home/i })).toHaveAttribute('href', '/home');
    expect(screen.getByText('Current')).toBeInTheDocument();
  });

  it('renders Sidebar with items and sections', () => {
    render(
      <Sidebar>
        <SidebarHeader>
          <SidebarSection>
            <SidebarHeading>Head</SidebarHeading>
            <SidebarItem href="/a">
              <SidebarLabel>A</SidebarLabel>
            </SidebarItem>
          </SidebarSection>
        </SidebarHeader>
        <SidebarBody>
          <SidebarSection>
            <SidebarItem current>
              <SidebarLabel>Current</SidebarLabel>
            </SidebarItem>
            <SidebarDivider />
          </SidebarSection>
          <SidebarSpacer />
        </SidebarBody>
        <SidebarFooter>
          <SidebarSection>
            <SidebarItem href="/b">
              <SidebarLabel>B</SidebarLabel>
            </SidebarItem>
          </SidebarSection>
        </SidebarFooter>
      </Sidebar>
    );
    expect(screen.getByRole('link', { name: 'A' })).toHaveAttribute('href', '/a');
    expect(screen.getByText('Current')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'B' })).toHaveAttribute('href', '/b');
  });
});

describe('StackedLayout', () => {
  it('opens mobile sidebar on menu click', () => {
    render(
      <StackedLayout navbar={<div>NB</div>} sidebar={<div>SB</div>}>
        <div>Content</div>
      </StackedLayout>
    );
    const openBtn = screen.getByRole('button', { name: /open navigation/i });
    fireEvent.click(openBtn);
    expect(screen.getByRole('button', { name: /close navigation/i })).toBeInTheDocument();
  });
});

describe('Switch and Radio', () => {
  it('renders Switch in checked state', () => {
    render(<Switch defaultChecked aria-label="toggle" />);
    const sw = screen.getByRole('switch', { name: /toggle/i });
    expect(sw).toHaveAttribute('aria-checked', 'true');
  });

  it('renders Radio items in a group', () => {
    render(
      <RadioGroup defaultValue="x">
        <RadioField>
          <Radio value="x" aria-label="X" />
          <Radio value="y" aria-label="Y" />
        </RadioField>
      </RadioGroup>
    );
    expect(screen.getByRole('radio', { name: 'X' })).toBeInTheDocument();
    expect(screen.getByRole('radio', { name: 'Y' })).toBeInTheDocument();
  });
});

