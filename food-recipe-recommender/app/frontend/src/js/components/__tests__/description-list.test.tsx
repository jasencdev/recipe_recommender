/**
 * Tests for DescriptionList component
 */

import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { DescriptionList, DescriptionTerm, DescriptionDetails } from '../description-list'

describe('DescriptionList', () => {
  it('should render description list with terms and details', () => {
    render(
      <DescriptionList>
        <DescriptionTerm>Name</DescriptionTerm>
        <DescriptionDetails>John Doe</DescriptionDetails>
        <DescriptionTerm>Email</DescriptionTerm>
        <DescriptionDetails>john@example.com</DescriptionDetails>
      </DescriptionList>
    )

    expect(screen.getByText('Name')).toBeInTheDocument()
    expect(screen.getByText('John Doe')).toBeInTheDocument()
    expect(screen.getByText('Email')).toBeInTheDocument()
    expect(screen.getByText('john@example.com')).toBeInTheDocument()
  })

  it('should render with custom className', () => {
    render(
      <DescriptionList className="custom-list">
        <DescriptionTerm>Term</DescriptionTerm>
        <DescriptionDetails>Details</DescriptionDetails>
      </DescriptionList>
    )

    const list = screen.getByText('Term').closest('dl')
    expect(list).toHaveClass('custom-list')
  })

  it('should handle multiple details for one term', () => {
    render(
      <DescriptionList>
        <DescriptionTerm>Skills</DescriptionTerm>
        <DescriptionDetails>JavaScript</DescriptionDetails>
        <DescriptionDetails>TypeScript</DescriptionDetails>
        <DescriptionDetails>React</DescriptionDetails>
      </DescriptionList>
    )

    expect(screen.getByText('Skills')).toBeInTheDocument()
    expect(screen.getByText('JavaScript')).toBeInTheDocument()
    expect(screen.getByText('TypeScript')).toBeInTheDocument()
    expect(screen.getByText('React')).toBeInTheDocument()
  })
})

describe('DescriptionTerm', () => {
  it('should render term with correct tag', () => {
    render(<DescriptionTerm>Test Term</DescriptionTerm>)

    const term = screen.getByText('Test Term')
    expect(term.tagName).toBe('DT')
  })

  it('should accept custom props', () => {
    render(
      <DescriptionTerm className="term-class" data-testid="custom-term">
        Custom Term
      </DescriptionTerm>
    )

    const term = screen.getByTestId('custom-term')
    expect(term).toHaveClass('term-class')
    expect(term).toHaveTextContent('Custom Term')
  })
})

describe('DescriptionDetails', () => {
  it('should render details with correct tag', () => {
    render(<DescriptionDetails>Test Details</DescriptionDetails>)

    const details = screen.getByText('Test Details')
    expect(details.tagName).toBe('DD')
  })

  it('should accept custom props', () => {
    render(
      <DescriptionDetails className="details-class" data-testid="custom-details">
        Custom Details
      </DescriptionDetails>
    )

    const details = screen.getByTestId('custom-details')
    expect(details).toHaveClass('details-class')
    expect(details).toHaveTextContent('Custom Details')
  })

  it('should render complex content', () => {
    render(
      <DescriptionDetails>
        <strong>Bold text</strong> and <em>italic text</em>
      </DescriptionDetails>
    )

    expect(screen.getByText('Bold text')).toBeInTheDocument()
    expect(screen.getByText('italic text')).toBeInTheDocument()
  })
})