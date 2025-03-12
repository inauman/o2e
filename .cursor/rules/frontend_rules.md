# Frontend Development Rules

## Clean Interface Boundaries

- **FR-1**: Frontend code (React) must never directly access backend internals.
- **FR-2**: All communication between frontend and backend must occur through well-defined API endpoints.
- **FR-3**: API contracts must be strictly followed as defined in the API Interface Design Guide.
- **FR-4**: Frontend code should be agnostic to backend implementation details.

## React Structure

- **RS-1**: Components should be organized by feature in a modular structure.
- **RS-2**: Use custom hooks for reusable logic.
- **RS-3**: UI state and API communication concerns should be separated.
- **RS-4**: Global state should be minimized and managed with appropriate patterns (Context, Redux, etc.).
- **RS-5**: Components should follow the single responsibility principle.
- **RS-6**: Files should not exceed 300 lines of code (excluding comments and imports).
- **RS-7**: Functions should not exceed 30 lines of code.
- **RS-8**: Implement React Router for navigation with proper route organization.
- **RS-9**: Use React Suspense and Error Boundaries for loading states and error handling.
- **RS-10**: Implement React.lazy for code splitting of large component trees.

## Tailwind CSS Implementation

- **TW-1**: Use Tailwind utility classes directly in JSX for component styling.
- **TW-2**: Create custom component classes using @apply for frequently reused styles.
- **TW-3**: Maintain a consistent design system using Tailwind's theme configuration.
- **TW-4**: Extend Tailwind's default configuration in `tailwind.config.js` rather than using inline arbitrary values.
- **TW-5**: Use Tailwind's variants (hover, focus, etc.) consistently across similar components.
- **TW-6**: Implement dark mode support with Tailwind's dark variant.
- **TW-7**: Organize utility classes in a consistent order (layout, spacing, typography, etc.).
- **TW-8**: Use the clsx or classnames library for conditional class application.

## API Communication

- **AC-1**: All API calls must be centralized in service modules.
- **AC-2**: API calls must include appropriate error handling.
- **AC-3**: User feedback must be provided during API operations (loading, success, error states).
- **AC-4**: Authentication tokens must be managed securely.
- **AC-5**: API requests should include necessary security headers (CSRF tokens, etc.).
- **AC-6**: Standardized error handling for API responses.
- **AC-7**: Use React Query or SWR for data fetching, caching, and state management.
- **AC-8**: Implement retry logic for failed API requests where appropriate.

## UI/UX Standards

- **UX-1**: All user interfaces must be responsive and mobile-friendly.
- **UX-2**: Form validation must provide immediate feedback to users.
- **UX-3**: All actions with security implications must have confirmation steps.
- **UX-4**: Loading states must be visually indicated to users.
- **UX-5**: Error messages should be user-friendly and actionable.
- **UX-6**: UI components should follow a consistent design system.
- **UX-7**: Implement skeleton loaders for content that requires API data.
- **UX-8**: Use motion and transitions sparingly and purposefully.
- **UX-9**: Design for both light and dark mode.

## TypeScript Usage

- **TS-1**: Use TypeScript for all frontend code.
- **TS-2**: Avoid using `any` type unless absolutely necessary.
- **TS-3**: Define interfaces for all component props.
- **TS-4**: Define types for API request/response data.
- **TS-5**: Use generics where appropriate for reusable components and functions.
- **TS-6**: Add JSDoc comments for public functions and components.
- **TS-7**: Use TypeScript's strict mode.
- **TS-8**: Create barrel exports (index.ts) for cleaner imports.
- **TS-9**: Use type guards for runtime type checking when necessary.

## WebAuthn UI Integration

- **WA-1**: WebAuthn UI must provide clear guidance to users about physical key interactions.
- **WA-2**: Handle WebAuthn browser compatibility issues gracefully.
- **WA-3**: Provide appropriate fallbacks for unsupported browsers.
- **WA-4**: Error messages for WebAuthn operations should be clear and actionable.
- **WA-5**: Use feature detection for WebAuthn capabilities.
- **WA-6**: Implement animated guidance for YubiKey interactions.
- **WA-7**: Provide visual feedback during WebAuthn operations.

## Testing

- **TF-1**: Component tests should focus on behavior, not implementation details.
- **TF-2**: Use React Testing Library for component tests.
- **TF-3**: Test user interactions thoroughly.
- **TF-4**: Mock API calls in component tests.
- **TF-5**: Test error states and loading states.
- **TF-6**: Test responsive behavior where critical.
- **TF-7**: Implement E2E tests for critical user flows using Cypress.
- **TF-8**: Use testing-library/user-event for realistic user interaction testing.
- **TF-9**: Implement snapshot testing sparingly and purposefully.

## Security Considerations

- **SF-1**: No credentials or sensitive data should be stored in client-side code.
- **SF-2**: Use HTTP-only cookies for authentication tokens where possible.
- **SF-3**: Implement CSRF protection for all state-changing operations.
- **SF-4**: Sanitize all user-generated content before rendering.
- **SF-5**: Implement appropriate Content Security Policy.
- **SF-6**: Avoid using dangerouslySetInnerHTML unless absolutely necessary.
- **SF-7**: Use React's built-in XSS protection by avoiding string interpolation in JSX.
- **SF-8**: Implement proper auth state management with secure token refresh.

## Code Organization

- **CO-1**: Group related components in feature directories.
- **CO-2**: Separate presentation components from container components.
- **CO-3**: Follow consistent file naming conventions.
- **CO-4**: Reusable components should be in a shared directory.
- **CO-5**: Import order should be consistent (React, third-party, internal).
- **CO-6**: Export components and functions explicitly.
- **CO-7**: Implement a component library pattern for reusable UI elements.
- **CO-8**: Use an atomic design methodology (atoms, molecules, organisms, templates, pages).

## Performance

- **PF-1**: Use React.memo for pure components when appropriate.
- **PF-2**: Implement virtualization for long lists.
- **PF-3**: Optimize component re-renders.
- **PF-4**: Lazy load components that aren't immediately needed.
- **PF-5**: Optimize bundle size with code splitting.
- **PF-6**: Measure and monitor performance metrics.
- **PF-7**: Use Lighthouse or Web Vitals for performance monitoring.
- **PF-8**: Implement image optimization for all assets.
- **PF-9**: Optimize Tailwind CSS configuration for production.

## Accessibility

- **AF-1**: All interactive elements must be keyboard accessible.
- **AF-2**: Use appropriate ARIA attributes.
- **AF-3**: Ensure sufficient color contrast.
- **AF-4**: Provide alternative text for images.
- **AF-5**: Support screen readers.
- **AF-6**: Test with accessibility tools.
- **AF-7**: Implement focus management for modals and dialogs.
- **AF-8**: Use semantic HTML elements.
- **AF-9**: Ensure all form elements have associated labels.

## Build and Deployment

- **BD-1**: Use proper environment variables for configuration.
- **BD-2**: Implement optimization for production builds (code splitting, tree shaking).
- **BD-3**: Set up continuous integration for frontend builds.
- **BD-4**: Configure proper caching strategies for static assets.
- **BD-5**: Implement build-time type checking and linting.
- **BD-6**: Version static assets for cache busting.

## Updates
This document should be reviewed and updated regularly as new frontend best practices emerge or requirements change. 