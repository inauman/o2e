# Tailwind CSS Best Practices

## Overview

This document outlines the standards and best practices for using Tailwind CSS in the O2E project. Tailwind CSS is a utility-first CSS framework that allows for rapid UI development without leaving your HTML/JSX.

## Configuration

### Project Setup

- **TW-CONFIG-1**: Maintain a single source of truth in `tailwind.config.js` for design tokens
- **TW-CONFIG-2**: Extend Tailwind's default theme rather than overriding it completely
- **TW-CONFIG-3**: Define custom colors, spacing, fonts, and other design tokens in the theme configuration
- **TW-CONFIG-4**: Use semantic naming for custom colors (e.g., `primary`, `secondary`, not `blue`, `red`)
- **TW-CONFIG-5**: Configure content paths properly to include all files with Tailwind classes

```js
// Example tailwind.config.js
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
          950: '#052e16',
        },
        secondary: {
          // ... color scale
        },
      },
      fontFamily: {
        sans: ['Inter var', 'sans-serif'],
      },
      // ... other theme extensions
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
```

### Plugins and Extensions

- **TW-PLUGIN-1**: Use official Tailwind plugins for common UI patterns (`@tailwindcss/forms`, `@tailwindcss/typography`)
- **TW-PLUGIN-2**: Document all custom plugins in the project
- **TW-PLUGIN-3**: Create custom plugins for complex, repeated patterns specific to the project
- **TW-PLUGIN-4**: Use the JIT (Just-In-Time) mode for development and production

## Class Usage

### General Principles

- **TW-CLASS-1**: Use utility classes directly in JSX for component styling
- **TW-CLASS-2**: Group related utilities with consistent ordering (layout → sizing → spacing → typography → visual)
- **TW-CLASS-3**: Use the clsx or classnames library for conditional class application
- **TW-CLASS-4**: Avoid using `@apply` except for highly reused component patterns
- **TW-CLASS-5**: Prefer composition with React components over complex class combinations

### Examples

```tsx
// Good: Direct utility classes with consistent ordering
<button className="block w-full py-2 px-4 mt-4 text-sm font-medium text-white bg-primary-600 rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500">
  Submit
</button>

// Good: Using clsx for conditional classes
<div className={clsx(
  "p-4 rounded-lg",
  isActive ? "bg-primary-100 text-primary-900" : "bg-gray-100 text-gray-900"
)}>
  {content}
</div>

// Avoid: Too many unorganized classes
<div className="rounded-lg text-sm bg-white shadow p-4 hover:shadow-md text-gray-800 flex items-center">
  {content}
</div>
```

## Component Patterns

### Atomic Design

- **TW-COMP-1**: Follow atomic design principles (atoms, molecules, organisms)
- **TW-COMP-2**: Create reusable base components with consistent styling
- **TW-COMP-3**: Use composition to build complex components from simpler ones
- **TW-COMP-4**: Allow component customization through props rather than direct class overrides
- **TW-COMP-5**: Implement a consistent component API for styling variations

### Examples

```tsx
// Atom: Button component with variants
function Button({ variant = 'primary', size = 'md', className, children, ...props }) {
  const baseClasses = "inline-flex items-center font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2";
  
  const variants = {
    primary: "bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500",
    secondary: "bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500",
    // ... other variants
  };
  
  const sizes = {
    sm: "py-1 px-2 text-xs",
    md: "py-2 px-4 text-sm",
    lg: "py-3 px-6 text-base",
  };
  
  return (
    <button 
      className={clsx(baseClasses, variants[variant], sizes[size], className)}
      {...props}
    >
      {children}
    </button>
  );
}

// Usage
<Button variant="secondary" size="lg">Click Me</Button>
```

## Custom Component Classes

### Creating Reusable Styles

- **TW-CUSTOM-1**: Use `@layer components` for defining custom component classes
- **TW-CUSTOM-2**: Keep custom component classes focused and composable
- **TW-CUSTOM-3**: Document custom component classes clearly
- **TW-CUSTOM-4**: Name custom classes semantically based on their purpose
- **TW-CUSTOM-5**: Use `@apply` only for styles that are frequently reused

### Example

```css
/* In src/index.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer components {
  .btn {
    @apply inline-flex items-center justify-center px-4 py-2 rounded-md font-medium focus:outline-none focus:ring-2 focus:ring-offset-2;
  }
  
  .btn-primary {
    @apply btn bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500;
  }
  
  .btn-secondary {
    @apply btn bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500;
  }
  
  .card {
    @apply bg-white rounded-lg shadow p-4;
  }
  
  /* ... other common component classes */
}
```

## Responsive Design

### Mobile-First Approach

- **TW-RESP-1**: Design mobile-first, then add responsive variants for larger screens
- **TW-RESP-2**: Use Tailwind's responsive prefixes consistently (`sm:`, `md:`, `lg:`, `xl:`, `2xl:`)
- **TW-RESP-3**: Test thoroughly at different viewport sizes
- **TW-RESP-4**: Limit the number of breakpoints used in a single component
- **TW-RESP-5**: Document complex responsive behaviors

### Example

```tsx
<div className="flex flex-col space-y-4 md:flex-row md:space-y-0 md:space-x-4">
  <div className="w-full md:w-1/3 lg:w-1/4">Sidebar</div>
  <div className="w-full md:w-2/3 lg:w-3/4">Main Content</div>
</div>
```

## Dark Mode

### Implementation

- **TW-DARK-1**: Use Tailwind's dark mode support via the `dark:` prefix
- **TW-DARK-2**: Implement a consistent dark mode color scheme
- **TW-DARK-3**: Test all components in both light and dark modes
- **TW-DARK-4**: Ensure sufficient contrast in both modes
- **TW-DARK-5**: Use CSS variables for complex theming when needed

### Example

```tsx
<div className="bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 p-4 rounded-lg">
  <h2 className="text-xl font-bold text-gray-900 dark:text-white">Card Title</h2>
  <p className="mt-2 text-gray-700 dark:text-gray-300">Card content goes here.</p>
</div>
```

## Accessibility

### Best Practices

- **TW-A11Y-1**: Ensure sufficient color contrast (WCAG AA minimum)
- **TW-A11Y-2**: Use semantic HTML elements with Tailwind classes
- **TW-A11Y-3**: Test focus states and keyboard navigation
- **TW-A11Y-4**: Add appropriate ARIA attributes as needed
- **TW-A11Y-5**: Use Tailwind's focus utilities to enhance keyboard interactions

### Example

```tsx
<button 
  className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
  aria-label="Submit form"
>
  Submit
</button>
```

## Performance

### Optimization

- **TW-PERF-1**: Use Tailwind's JIT mode for smaller CSS builds
- **TW-PERF-2**: Purge unused styles in production
- **TW-PERF-3**: Minimize the use of arbitrary values (`[mask-type:luminance]`)
- **TW-PERF-4**: Consider extracting very complex utility combinations into components
- **TW-PERF-5**: Use prefers-reduced-motion utilities for animations

### Example Configuration

```js
// tailwind.config.js for production
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    // ... theme configuration
  },
  variants: {
    extend: {
      opacity: ['disabled'],
      cursor: ['disabled'],
      backgroundColor: ['active', 'disabled'],
      textColor: ['active', 'disabled'],
    },
  },
}
```

## Integration with React

### Component Structure

- **TW-REACT-1**: Co-locate Tailwind-styled components with related business logic
- **TW-REACT-2**: Create presentational components that accept className props for extensibility
- **TW-REACT-3**: Use React's composition pattern with Tailwind classes
- **TW-REACT-4**: Create a UI component library using Tailwind for consistency
- **TW-REACT-5**: Document component styling patterns in the project

### Example

```tsx
// Button.tsx
import { clsx } from 'clsx';
import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
}

export function Button({
  variant = 'primary',
  size = 'md',
  className,
  children,
  ...props
}: ButtonProps) {
  // Button implementation with Tailwind classes
}

// Usage
import { Button } from './components/Button';

function MyComponent() {
  return (
    <div className="p-4">
      <Button 
        variant="primary" 
        size="lg"
        className="mt-4" // Extended with additional classes
      >
        Submit
      </Button>
    </div>
  );
}
```

## Custom Forms

### Styling Forms

- **TW-FORM-1**: Use `@tailwindcss/forms` plugin for base form styling
- **TW-FORM-2**: Create consistent input, select, and checkbox components
- **TW-FORM-3**: Implement accessible form validation styles
- **TW-FORM-4**: Design clear focus and error states
- **TW-FORM-5**: Ensure form controls have sufficient size for touch targets

### Example

```tsx
<div className="space-y-4">
  <div>
    <label htmlFor="email" className="block text-sm font-medium text-gray-700">
      Email
    </label>
    <input
      type="email"
      id="email"
      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
      placeholder="you@example.com"
    />
  </div>
  
  <div>
    <label htmlFor="password" className="block text-sm font-medium text-gray-700">
      Password
    </label>
    <input
      type="password"
      id="password"
      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
    />
  </div>
  
  <div className="flex items-center">
    <input
      id="remember_me"
      type="checkbox"
      className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
    />
    <label htmlFor="remember_me" className="ml-2 block text-sm text-gray-700">
      Remember me
    </label>
  </div>
</div>
```

## WebAuthn UI Integration

### Tailwind-Styled Components

- **TW-WEBAUTHN-1**: Create consistent UI components for WebAuthn operations
- **TW-WEBAUTHN-2**: Design clear visual feedback for YubiKey interactions
- **TW-WEBAUTHN-3**: Implement loading and success/error states with Tailwind
- **TW-WEBAUTHN-4**: Use animations judiciously for user guidance
- **TW-WEBAUTHN-5**: Ensure responsive design for WebAuthn flows

### Example

```tsx
<div className="p-6 max-w-md mx-auto bg-white rounded-xl shadow-md overflow-hidden">
  <div className="flex items-center space-x-4">
    <div className="flex-shrink-0">
      <svg className="h-12 w-12 text-primary-600" fill="currentColor" viewBox="0 0 24 24">
        {/* YubiKey icon */}
      </svg>
    </div>
    <div>
      <h3 className="text-lg font-medium text-gray-900">Authenticate with YubiKey</h3>
      <p className="text-gray-500">Insert your YubiKey and tap when it flashes</p>
    </div>
  </div>
  
  {isLoading ? (
    <div className="mt-4 flex justify-center">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
    </div>
  ) : (
    <button
      className="mt-4 w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
      onClick={startAuthentication}
    >
      Start Authentication
    </button>
  )}
</div>
```

## Updates
This document should be reviewed and updated regularly as new Tailwind CSS best practices emerge or requirements change. 