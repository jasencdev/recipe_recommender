import { forwardRef, type ComponentPropsWithoutRef, type ElementRef } from 'react'
import { clsx } from 'clsx'

const Card = forwardRef<ElementRef<'div'>, ComponentPropsWithoutRef<'div'>>(
  ({ className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={clsx(
          'overflow-hidden rounded-lg bg-white shadow-sm dark:bg-gray-800/50 dark:shadow-none dark:outline dark:-outline-offset-1 dark:outline-white/10',
          className
        )}
        {...props}
      />
    )
  }
)

Card.displayName = 'Card'

export default Card
