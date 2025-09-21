# Frontend Documentation

This document provides comprehensive documentation for the Recipe Recommender React frontend application.

## Overview

The frontend is a modern React 19 single-page application (SPA) built with TypeScript, Tailwind CSS, and Vite. It provides a responsive, accessible interface for recipe discovery and management.

## Technology Stack

### Core Technologies
- **React 19**: Modern UI library with hooks and concurrent features
- **TypeScript**: Type-safe JavaScript for better development experience
- **Vite**: Fast build tool and development server
- **React Router**: Client-side routing with React Router v7

### UI Framework
- **Tailwind CSS v4**: Utility-first CSS framework
- **Headless UI**: Accessible, unstyled UI components
- **Heroicons**: SVG icon library
- **Motion**: Animation library for smooth transitions

### Development Tools
- **Vitest**: Fast unit testing framework
- **React Testing Library**: Component testing utilities
- **ESLint**: Code linting and style enforcement
- **TypeScript ESLint**: TypeScript-specific linting rules

## Project Structure

```
src/
├── js/                           # TypeScript/React source files
│   ├── components/               # Reusable UI components
│   │   ├── __tests__/           # Component tests
│   │   ├── auth-layout.tsx      # Authentication page layout
│   │   ├── AuthContext.tsx      # Authentication context provider
│   │   ├── button.tsx           # Button component with variants
│   │   ├── card.tsx             # Card component
│   │   ├── input.tsx            # Form input component
│   │   ├── navbar.tsx           # Navigation bar
│   │   ├── ProtectedRouter.tsx  # Route protection component
│   │   ├── saveButton.tsx       # Recipe save/unsave button
│   │   ├── sidebar.tsx          # Sidebar navigation
│   │   └── [UI components...]   # Other Tailwind UI components
│   ├── pages/                   # Page components
│   │   ├── __tests__/           # Page tests
│   │   ├── collections.tsx      # Recipe collections page
│   │   ├── forgot-password.tsx  # Password reset request
│   │   ├── login.tsx            # User login page
│   │   ├── recipe-detail.tsx    # Individual recipe view
│   │   ├── recommendations.tsx  # Recipe recommendations/results
│   │   ├── registration.tsx     # User registration page
│   │   ├── reset-password.tsx   # Password reset form
│   │   ├── saved-recipes.tsx    # User's saved recipes
│   │   ├── search.tsx           # Recipe search interface
│   │   └── stackedWrapper.tsx   # Layout wrapper component
│   ├── services/                # API and external services
│   │   ├── __tests__/           # Service tests
│   │   ├── api.ts               # Main API client
│   │   ├── ingredients.ts       # Ingredient-related services
│   │   ├── recentlyViewed.ts    # Recently viewed recipes
│   │   └── recipeNotes.ts       # Recipe notes management
│   ├── utils/                   # Utility functions
│   │   ├── __tests__/           # Utility tests
│   │   └── logger.ts            # Logging utilities
│   ├── App.tsx                  # Main application component
│   └── main.tsx                 # Application entry point
├── styles/                      # CSS styles
│   └── App.css                  # Global styles
└── setupTests.ts                # Test configuration
```

## Core Components

### Authentication System

#### AuthContext
**File**: `components/AuthContext.tsx`

Provides global authentication state management using React Context.

```typescript
interface AuthContextType {
    user: any;
    setUser: React.Dispatch<React.SetStateAction<any>>;
    loading: boolean;
    checkAuth: () => Promise<void>;
}
```

**Usage**:
```tsx
import { useAuth } from '../components/AuthContext';

function MyComponent() {
    const { user, loading, checkAuth } = useAuth();
    // ...
}
```

**Features**:
- Automatic authentication check on app load
- Global user state management
- Loading state handling
- Auth status refresh functionality

#### ProtectedRoute
**File**: `components/ProtectedRouter.tsx`

Higher-order component that protects routes requiring authentication.

```tsx
<ProtectedRoute>
    <PrivatePage />
</ProtectedRoute>
```

**Features**:
- Redirects unauthenticated users to login
- Shows loading state during auth check
- Preserves intended destination after login

### UI Components

#### Button Component
**File**: `components/button.tsx`

Flexible button component with multiple variants and sizes.

```tsx
interface ButtonProps {
    variant?: 'solid' | 'outline' | 'plain';
    color?: 'dark' | 'gray' | 'red' | 'orange' | 'amber' | 'yellow' | 'lime' | 'green' | 'emerald' | 'teal' | 'cyan' | 'sky' | 'blue' | 'indigo' | 'violet' | 'purple' | 'fuchsia' | 'pink' | 'rose' | 'white' | 'zinc';
    size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
    disabled?: boolean;
    className?: string;
    children: ReactNode;
}
```

**Usage**:
```tsx
<Button variant="solid" color="blue" size="md" onClick={handleClick}>
    Click me
</Button>
```

#### SaveButton Component
**File**: `components/saveButton.tsx`

Specialized button for saving/unsaving recipes with state management.

```tsx
interface SaveButtonProps {
    recipeId: string;
    size?: 'sm' | 'md' | 'lg';
    color?: 'default' | 'gray' | 'red';
    className?: string;
    onSaveChange?: (isSaved: boolean) => void;
    onClick?: (e: React.MouseEvent) => void;
}
```

**Features**:
- Automatic save state detection
- Optimistic UI updates
- Loading states during API calls
- Heart icon with filled/outline states
- Event propagation control

#### Card Component
**File**: `components/card.tsx`

Container component for content with consistent styling.

```tsx
<Card>
    <CardHeader>
        <CardTitle>Recipe Name</CardTitle>
    </CardHeader>
    <CardContent>
        Recipe details...
    </CardContent>
</Card>
```

### Form Components

#### Input Component
**File**: `components/input.tsx`

Styled input component with error handling and accessibility features.

```tsx
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
    invalid?: boolean;
    className?: string;
}
```

**Features**:
- Consistent styling with Tailwind
- Error state styling
- Accessibility attributes
- TypeScript support for all HTML input props

#### Field Components
**Files**: `components/fieldset.tsx`, `components/textarea.tsx`

Form field containers and specialized inputs with proper labeling and error handling.

### Layout Components

#### StackedWrapper
**File**: `pages/stackedWrapper.tsx`

Main layout wrapper providing consistent page structure with navigation.

**Features**:
- Responsive sidebar navigation
- User profile section
- Logout functionality
- Mobile-friendly hamburger menu

#### Sidebar
**File**: `components/sidebar.tsx`

Navigation sidebar with route highlighting and responsive behavior.

**Features**:
- Active route detection
- Icon and text navigation items
- Responsive design (collapsible on mobile)
- Accessibility features

## Page Components

### Search Page
**File**: `pages/search.tsx`

Main search interface with text and parameter-based search options.

**Features**:
- Text-based recipe search
- Parameter search with sliders:
  - Cook time (5-60 minutes)
  - Complexity score (1-50)
  - Number of ingredients (1-20)
- Form validation and error handling
- Navigation to results page with state

### Recommendations Page
**File**: `pages/recommendations.tsx`

Displays search results and recipe recommendations with pagination.

**Features**:
- Recipe grid layout with cards
- Save/unsave functionality
- Pagination controls
- Recipe detail navigation
- Filter display and modification

### Recipe Detail Page
**File**: `pages/recipe-detail.tsx`

Individual recipe view with full details and save functionality.

**Features**:
- Complete recipe information display
- Ingredient list with quantities
- Step-by-step instructions
- Save/unsave button
- Navigation back to search results

### Saved Recipes Page
**File**: `pages/saved-recipes.tsx`

User's personal recipe collection management.

**Features**:
- Grid view of saved recipes
- Remove from saved functionality
- Search within saved recipes
- Empty state handling

### Authentication Pages

#### Login Page
**File**: `pages/login.tsx`

User authentication interface with form validation.

**Features**:
- Email/password login form
- Form validation and error display
- Navigation to registration and password reset
- Remember user preference

#### Registration Page
**File**: `pages/registration.tsx`

New user account creation with comprehensive form.

**Features**:
- Multi-field registration form
- Form validation
- Newsletter signup option
- Country selection
- Terms acceptance

#### Password Reset Pages
**Files**: `pages/forgot-password.tsx`, `pages/reset-password.tsx`

Password recovery workflow with email verification.

**Features**:
- Email-based password reset request
- Secure token validation
- New password form with confirmation
- Success/error state handling

## Services

### API Service
**File**: `services/api.ts`

Central API client with TypeScript interfaces and error handling.

#### Core Features:
- Axios-based HTTP client with credentials
- Comprehensive error handling
- TypeScript interfaces for all data types
- Response caching for performance

#### Key Functions:

```typescript
// Authentication
getAuthStatus(): Promise<AuthResponse>

// Recipe operations
searchRecipes(filters: SearchFilters, page?: number, limit?: number): Promise<SearchResponse>
getRecipeById(recipeId: string): Promise<Recipe>

// Saved recipes
getSavedRecipes(): Promise<Recipe[]>
saveRecipe(recipeId: string): Promise<void>
removeSavedRecipe(recipeId: string): Promise<void>
isRecipeSaved(recipeId: string): Promise<boolean>
toggleSaveRecipe(recipeId: string): Promise<boolean>
```

#### Data Types:

```typescript
interface Recipe {
    id: string;
    name: string;
    description: string;
    cookTime: number;
    difficulty: string;
    ingredients: string[];
    instructions: string[];
    cuisine?: string;
    dietaryTags?: string[];
    complexityScore?: number;
    imageUrl?: string;
}

interface SearchFilters {
    query?: string;
    complexityScore?: number;
    numberOfIngredients?: number;
    dietaryRestrictions?: string[];
    cuisine?: string;
    cookTime?: number;
}
```

### Local Storage Services

#### Recently Viewed Service
**File**: `services/recentlyViewed.ts`

Manages recently viewed recipes in local storage.

**Features**:
- Automatic recipe view tracking
- Configurable history limit
- Duplicate prevention
- Local storage persistence

#### Recipe Notes Service
**File**: `services/recipeNotes.ts`

User's personal notes for recipes stored locally.

**Features**:
- Note creation and editing
- Local storage persistence
- Recipe association
- CRUD operations

### Ingredient Service
**File**: `services/ingredients.ts`

Ingredient processing and standardization utilities.

**Features**:
- Ingredient parsing and normalization
- Quantity and unit extraction
- Common ingredient recognition
- Shopping list generation

## State Management

### Authentication State
Managed globally through AuthContext:
- User authentication status
- User profile information
- Loading states
- Auth check functionality

### Form State
Local component state using React hooks:
- useState for form inputs
- Form validation state
- Submit loading states
- Error message state

### API State
Request-specific state management:
- Loading indicators
- Error handling
- Data caching (saved recipes)
- Optimistic updates

## Routing

### Route Configuration
**File**: `App.tsx`

```tsx
<Routes>
    <Route path="/" element={<ProtectedRoute><Search /></ProtectedRoute>} />
    <Route path="/search" element={<ProtectedRoute><Search /></ProtectedRoute>} />
    <Route path="/recommendations" element={<ProtectedRoute><Recommendations /></ProtectedRoute>} />
    <Route path="/saved-recipes" element={<ProtectedRoute><SavedRecipes /></ProtectedRoute>} />
    <Route path="/collections" element={<ProtectedRoute><Collections /></ProtectedRoute>} />
    <Route path="/recipe/:id" element={<ProtectedRoute><RecipeDetail /></ProtectedRoute>} />
    <Route path="/login" element={<Login />} />
    <Route path="/forgot-password" element={<ForgotPassword />} />
    <Route path="/reset-password" element={<ResetPassword />} />
    <Route path="/registration" element={<Registration />} />
    <Route path="*" element={<Navigate to="/" />} />
</Routes>
```

### Navigation Flow
1. **Unauthenticated users**: Redirected to `/login`
2. **Authenticated users**: Access to all protected routes
3. **Search flow**: Search → Recommendations → Recipe Detail
4. **Authentication flow**: Login → Dashboard or Registration → Login

## Styling and Design

### Tailwind CSS Configuration
- **Version**: Tailwind CSS v4
- **Configuration**: Tailwind config includes custom color schemes
- **Responsive**: Mobile-first responsive design
- **Dark mode**: Support for dark/light theme switching

### Design System
- **Colors**: Consistent color palette with semantic naming
- **Typography**: Type scale with heading and text components
- **Spacing**: Consistent spacing using Tailwind spacing scale
- **Components**: Reusable component library with design tokens

### Accessibility
- **Keyboard navigation**: Full keyboard accessibility
- **Screen readers**: Proper ARIA labels and semantic HTML
- **Focus management**: Visible focus indicators
- **Color contrast**: WCAG compliant color combinations

## Testing

### Test Framework
- **Vitest**: Fast unit testing with Vite integration
- **React Testing Library**: Component testing utilities
- **jsdom**: DOM environment for testing

### Test Categories

#### Component Tests
```bash
src/js/components/__tests__/
├── button.test.tsx
├── button.variants.test.tsx
├── saveButton.test.tsx
├── authContext.test.tsx
└── [component-tests...]
```

#### Service Tests
```bash
src/js/services/__tests__/
├── api.test.ts
├── recentlyViewed.test.ts
└── recipeNotes.test.ts
```

#### Page Tests
```bash
src/js/pages/__tests__/
└── login_forgot.test.tsx
```

### Testing Commands
```bash
# Run tests in watch mode
npm run test

# Run tests with coverage
npm run test:run

# Generate coverage report
npm run coverage
```

### Test Coverage Goals
- **Components**: >90% coverage
- **Services**: >95% coverage
- **Critical paths**: 100% coverage (auth, API calls)

## Performance Optimization

### Code Splitting
- Route-based code splitting with React.lazy
- Component lazy loading for large components
- Dynamic imports for non-critical features

### Caching Strategies
- **Saved recipes**: Local caching with TTL
- **API responses**: Request deduplication
- **Static assets**: Vite build optimization

### Bundle Optimization
- Tree shaking for unused code elimination
- CSS purging in production builds
- Asset optimization (images, fonts)

## Development Workflow

### Development Server
```bash
# Start development server
npm run dev

# Server runs on http://localhost:5173
# Hot reload enabled for fast development
```

### Build Process
```bash
# Type checking
tsc -b

# Production build
npm run build

# Preview production build
npm run preview
```

### Code Quality
```bash
# Lint code
npm run lint

# Type checking
npx tsc --noEmit

# Run tests
npm run test
```

## Environment Configuration

### Vite Configuration
**File**: `vite.config.ts`

- Proxy configuration for API calls
- Plugin configuration (React, Tailwind)
- Build optimization settings
- Test environment setup

### Environment Variables
The frontend uses environment variables for configuration:

```env
# Development
VITE_API_BASE_URL=http://localhost:8080/api

# Production
VITE_API_BASE_URL=https://yourdomain.com/api
```

## Integration with Backend

### API Integration
- **Base URL**: Configurable via environment
- **Authentication**: Session-based with cookies
- **Error handling**: Consistent error response processing
- **Type safety**: TypeScript interfaces matching backend models

### Development Proxy
Vite development server proxies API calls to the Flask backend:

```javascript
// vite.config.ts
server: {
    proxy: {
        '/api': 'http://localhost:8080'
    }
}
```

## Deployment

### Build Assets
```bash
npm run build
```

Generates optimized production build in `dist/` directory:
- Minified JavaScript/CSS
- Asset optimization
- Source maps for debugging

### Static File Serving
Production build files are served by Flask:
- `dist/` contents copied to Flask `static/` directory
- Index.html served by Flask template
- Client-side routing handled by Flask catch-all route

## Browser Compatibility

### Supported Browsers
- **Chrome**: Latest 2 versions
- **Firefox**: Latest 2 versions
- **Safari**: Latest 2 versions
- **Edge**: Latest 2 versions

### Polyfills
- Modern browser features used (ES2020+)
- Vite handles necessary polyfills
- Progressive enhancement for older browsers

## Security Considerations

### XSS Prevention
- React's built-in XSS protection
- Sanitized user input
- Content Security Policy headers

### CSRF Protection
- Flask-WTF CSRF tokens
- Secure cookie configuration
- Same-site cookie attributes

### Authentication Security
- Secure session management
- Automatic logout on token expiry
- Protected route enforcement

## Contributing to Frontend

### Code Style
- **TypeScript**: Strict mode enabled
- **ESLint**: Enforced code style rules
- **Prettier**: Code formatting (if configured)
- **Conventional commits**: For change tracking

### Component Guidelines
1. **Functional components**: Use hooks instead of classes
2. **TypeScript**: Full type coverage required
3. **Accessibility**: WCAG 2.1 AA compliance
4. **Testing**: Unit tests for all components
5. **Documentation**: JSDoc comments for complex logic

### Best Practices
- Use semantic HTML elements
- Implement proper loading states
- Handle errors gracefully
- Follow React performance patterns
- Maintain consistent naming conventions

## Troubleshooting

### Common Issues

#### Development Server Issues
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf node_modules/.vite
```

#### Build Issues
```bash
# Check TypeScript errors
npx tsc --noEmit

# Verify all dependencies
npm audit

# Clean build
rm -rf dist
npm run build
```

#### API Connection Issues
- Check proxy configuration in `vite.config.ts`
- Verify backend server is running
- Check CORS configuration
- Verify API base URL environment variable

### Debugging
- Browser DevTools for React debugging
- React Developer Tools extension
- Network tab for API request debugging
- Console logging with logger utility

---

For API integration details, see [API.md](API.md).

For backend architecture, see [README.md](../README.md).