# Cursor Rules

This directory contains modular rule files for the YubiKey Bitcoin Seed Storage application. These rules should be followed by all contributors and enforced by Cursor.

## Rule Files Structure

The rules are organized into modular files, each focused on a specific aspect of development:

- **api_design.md**: Guidelines for designing and implementing clean API interfaces between components
- **backend_rules.md**: Rules specific to Flask backend development and architecture
- **bitcoin_security.md**: Security guidelines specific to Bitcoin/cryptocurrency operations
- **code_review_checklist.md**: Comprehensive checklist for code reviews
- **coding.md**: General coding standards and best practices
- **deployment.md**: Guidelines for deployment processes and environments
- **development_setup.md**: Instructions for setting up the development environment (Python/Flask backend and React/Tailwind frontend)
- **frontend_rules.md**: Rules specific to React frontend development and Tailwind CSS styling
- **modular_design_principles.md**: Principles for creating modular, maintainable architecture
- **python_best_practices.md**: Best practices specific to Python development
- **security.md**: Security guidelines for all aspects of the application
- **tailwind_css_best_practices.md**: Detailed guidelines for using Tailwind CSS in the project
- **testing.md**: Standards and practices for testing all components

## Using These Rules

1. **Development**: Refer to these rules during development to ensure code quality and consistency
2. **Code Review**: Use these rules as a reference during code reviews
3. **Cursor Integration**: Cursor will enforce these rules during development
4. **Onboarding**: New team members should review these rules to understand the project's standards

## Tech Stack Documentation

The rules provide comprehensive guidance for all aspects of our tech stack:

1. **Backend**: Python 3.14+, Flask, SQLAlchemy
2. **Frontend**: React 18+, TypeScript, Tailwind CSS
3. **Authentication**: WebAuthn, YubiKey integration
4. **Testing**: Pytest, React Testing Library, Cypress

## Rule Enforcement

These rules are enforced by:

1. Linting and static analysis tools
2. Code review procedures
3. Automated testing
4. Cursor's automated validation

## Maintenance

These rules should be reviewed and updated regularly as new best practices emerge or requirements change. Updates should be made through pull requests with appropriate approvals.

## Exceptions

Exceptions to these rules must be explicitly justified and documented in the code. If an exception pattern emerges frequently, consider updating the rules to accommodate it.

## Key Principles

All rules are guided by these core principles:

1. **Security**: The application deals with sensitive cryptocurrency operations and must be secure by design
2. **Modularity**: Clean interfaces between components enable independent development and testing
3. **Testability**: All code must be testable and have appropriate test coverage
4. **Maintainability**: Code should be easy to understand, modify, and extend
5. **Performance**: The application should be efficient and responsive 