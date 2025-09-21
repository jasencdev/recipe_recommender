/**
 * Tests for Dialog component
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { Dialog, DialogActions, DialogBody, DialogDescription, DialogTitle } from '../dialog'

describe('Dialog component', () => {
  it('should render open dialog with title and content', () => {
    render(
      <Dialog open={true} onClose={() => {}}>
        <DialogTitle>Test Dialog</DialogTitle>
        <DialogDescription>
          This is a test dialog description.
        </DialogDescription>
        <DialogBody>
          <p>Dialog body content</p>
        </DialogBody>
        <DialogActions>
          <button type="button">Cancel</button>
          <button type="button">OK</button>
        </DialogActions>
      </Dialog>
    )

    expect(screen.getByText('Test Dialog')).toBeInTheDocument()
    expect(screen.getByText('This is a test dialog description.')).toBeInTheDocument()
    expect(screen.getByText('Dialog body content')).toBeInTheDocument()
    expect(screen.getByText('Cancel')).toBeInTheDocument()
    expect(screen.getByText('OK')).toBeInTheDocument()
  })

  it('should not render when closed', () => {
    render(
      <Dialog open={false} onClose={() => {}}>
        <DialogTitle>Test Dialog</DialogTitle>
        <DialogBody>
          <p>Dialog body content</p>
        </DialogBody>
      </Dialog>
    )

    expect(screen.queryByText('Test Dialog')).not.toBeInTheDocument()
    expect(screen.queryByText('Dialog body content')).not.toBeInTheDocument()
  })


  it('should call onClose when escape key is pressed', () => {
    const onClose = vi.fn()
    render(
      <Dialog open={true} onClose={onClose}>
        <DialogTitle>Test Dialog</DialogTitle>
        <DialogBody>
          <p>Dialog body content</p>
        </DialogBody>
      </Dialog>
    )

    fireEvent.keyDown(document, { key: 'Escape' })
    expect(onClose).toHaveBeenCalled()
  })


  it('should handle complex dialog content', () => {
    render(
      <Dialog open={true} onClose={() => {}}>
        <DialogTitle>Complex Dialog</DialogTitle>
        <DialogDescription>
          This dialog contains multiple elements.
        </DialogDescription>
        <DialogBody className="space-y-4">
          <div>
            <label htmlFor="name">Name:</label>
            <input id="name" type="text" placeholder="Enter your name" />
          </div>
          <div>
            <label htmlFor="email">Email:</label>
            <input id="email" type="email" placeholder="Enter your email" />
          </div>
        </DialogBody>
        <DialogActions>
          <button type="button">Cancel</button>
          <button type="button">Submit</button>
        </DialogActions>
      </Dialog>
    )

    expect(screen.getByText('Complex Dialog')).toBeInTheDocument()
    expect(screen.getByLabelText('Name:')).toBeInTheDocument()
    expect(screen.getByLabelText('Email:')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Enter your name')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Enter your email')).toBeInTheDocument()
  })
})

describe('DialogTitle', () => {
  it('should render title within dialog context', () => {
    render(
      <Dialog open={true} onClose={() => {}}>
        <DialogTitle>Test Title</DialogTitle>
      </Dialog>
    )

    const title = screen.getByText('Test Title')
    expect(title).toBeInTheDocument()
  })
})

describe('DialogDescription', () => {
  it('should render description within dialog context', () => {
    render(
      <Dialog open={true} onClose={() => {}}>
        <DialogDescription>This is a description</DialogDescription>
      </Dialog>
    )

    expect(screen.getByText('This is a description')).toBeInTheDocument()
  })
})

describe('DialogBody', () => {
  it('should render body content', () => {
    render(
      <DialogBody>
        <p>Body content</p>
        <div>Additional content</div>
      </DialogBody>
    )

    expect(screen.getByText('Body content')).toBeInTheDocument()
    expect(screen.getByText('Additional content')).toBeInTheDocument()
  })
})

describe('DialogActions', () => {
  it('should render action buttons in correct layout', () => {
    render(
      <DialogActions>
        <button type="button">Cancel</button>
        <button type="button">Save</button>
      </DialogActions>
    )

    expect(screen.getByText('Cancel')).toBeInTheDocument()
    expect(screen.getByText('Save')).toBeInTheDocument()
  })

  it('should handle single action', () => {
    render(
      <DialogActions>
        <button type="button">OK</button>
      </DialogActions>
    )

    expect(screen.getByText('OK')).toBeInTheDocument()
  })
})