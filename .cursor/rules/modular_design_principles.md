# Modular Design Principles

## Core Principles

### 1. Single Responsibility Principle

- **SRP-1**: Each module must have a clearly defined responsibility and should not have knowledge of the internals of other modules.
- **SRP-2**: Classes should have only one reason to change.
- **SRP-3**: Functions should do one thing and do it well.
- **SRP-4**: Split large modules when they exceed 300-400 lines.
- **SRP-5**: Functions should generally be under 30 lines of code.
- **SRP-6**: Frontend React components should follow the single responsibility principle.

### 2. Interface Segregation & Clean Boundaries

- **ISB-1**: Define clear, minimal interfaces between components.
- **ISB-2**: Every module must have a well-defined public API.
- **ISB-3**: Interfaces should be documented with complete specifications.
- **ISB-4**: Backend (Flask) should expose a clean, secure API to the frontend (React).
- **ISB-5**: Minimize dependencies between modules.
- **ISB-6**: Frontend code must never directly access backend internals.
- **ISB-7**: Backend code must never make assumptions about frontend implementation details.
- **ISB-8**: All communication between frontend and backend must occur through well-defined APIs.
- **ISB-9**: API contracts must be strictly followed as defined in the API Interface Design Guide.

### 3. Dependency Injection

- **DI-1**: Components should receive their dependencies rather than creating them.
- **DI-2**: Dependencies should be passed via interfaces, not concrete implementations.
- **DI-3**: Use constructor injection for required dependencies.
- **DI-4**: Use setter injection for optional dependencies.
- **DI-5**: Configuration should be injected, not hardcoded.
- **DI-6**: Makes testing easier and components more reusable.

### 4. Separation of Concerns

- **SOC-1**: Business logic must be separate from data access and presentation code.
- **SOC-2**: UI state and API communication concerns should be separated.
- **SOC-3**: Configuration should be separate from application code.
- **SOC-4**: Authentication and authorization logic should be separate from business logic.
- **SOC-5**: Error handling should be consistent across modules.
- **SOC-6**: Logging should be separate from business logic.

## Code Organization

### 1. File and Module Structure

- **FMS-1**: Files should not exceed 300 lines of code (excluding comments and imports).
- **FMS-2**: One class per file (with rare exceptions).
- **FMS-3**: Group related functionality into packages/modules.
- **FMS-4**: Use consistent naming conventions.
- **FMS-5**: Document public interfaces thoroughly.
- **FMS-6**: Keep implementation details private within modules.

### 2. API Design

- **API-1**: Define API contracts before implementation.
- **API-2**: Document all endpoints with request/response schemas.
- **API-3**: Version APIs to allow for evolution.
- **API-4**: APIs should be self-documenting.
- **API-5**: Follow RESTful principles for resource operations.
- **API-6**: Use appropriate HTTP methods and status codes.

### 3. Database Access

- **DB-1**: Data access should be abstracted behind repositories or DAOs.
- **DB-2**: Business logic should never directly interact with the database.
- **DB-3**: Use transactions appropriately.
- **DB-4**: Database models should be separate from API serialization schemas.
- **DB-5**: Implement proper error handling for database operations.
- **DB-6**: Use migrations for schema changes.

### 4. Frontend Organization

- **FO-1**: Components should be organized by feature in a modular structure.
- **FO-2**: Use custom hooks for reusable logic.
- **FO-3**: Separate presentation components from container components.
- **FO-4**: Reusable components should be in a shared directory.
- **FO-5**: Global state should be minimized.
- **FO-6**: All API calls must be centralized in service modules.

## Design Patterns

### 1. Service Layer Pattern

- **SLP-1**: Implement service classes for business logic.
- **SLP-2**: Services should be stateless when possible.
- **SLP-3**: Service methods should have clear contracts.
- **SLP-4**: Services should encapsulate business rules.
- **SLP-5**: Services should be testable in isolation.
- **SLP-6**: Services should not directly interact with the UI.

### 2. Repository Pattern

- **RP-1**: Use repositories to abstract data access.
- **RP-2**: Repositories should provide a collection-like interface.
- **RP-3**: Repositories should hide the details of data storage.
- **RP-4**: Repositories should handle data mapping.
- **RP-5**: Repositories should encapsulate query logic.
- **RP-6**: Repositories should be testable with mocks.

### 3. Factory Pattern

- **FP-1**: Use factories to create complex objects.
- **FP-2**: Factories should hide creation details.
- **FP-3**: Factories should provide a simple interface.
- **FP-4**: Factories should handle dependencies.
- **FP-5**: Factories should be testable.
- **FP-6**: Factories should be used for objects with complex setup.

### 4. Strategy Pattern

- **SP-1**: Use strategies for interchangeable algorithms.
- **SP-2**: Strategies should share a common interface.
- **SP-3**: Strategies should be testable in isolation.
- **SP-4**: Strategies should be configurable.
- **SP-5**: Strategies should be swappable at runtime.
- **SP-6**: Use strategies for variation in behavior.

## Refactoring Triggers

- **RT-1**: Duplicate code appearing in multiple places.
- **RT-2**: Functions/methods growing beyond 50 lines.
- **RT-3**: Classes growing beyond 300 lines.
- **RT-4**: Too many parameters (more than 4-5).
- **RT-5**: Deeply nested conditionals (more than 2-3 levels).
- **RT-6**: Leaky abstractions or dependencies crossing module boundaries.
- **RT-7**: High coupling between modules.
- **RT-8**: Unclear responsibilities.
- **RT-9**: Difficulty writing tests.
- **RT-10**: Frequent changes affecting multiple modules.

## Testing Modular Systems

- **TMS-1**: Unit tests should focus on a single module.
- **TMS-2**: Use mock objects for dependencies.
- **TMS-3**: Integration tests should verify interactions between modules.
- **TMS-4**: Test public interfaces, not implementation details.
- **TMS-5**: Use test doubles (mocks, stubs, fakes) appropriately.
- **TMS-6**: Tests should be independent of each other.
- **TMS-7**: Tests should run quickly.
- **TMS-8**: Tests should be deterministic.
- **TMS-9**: Test both success and error paths.
- **TMS-10**: Verify boundary conditions.

## Implementation Guidelines

### 1. For Backend (Flask)

- **BIG-1**: Organize API routes in blueprints based on resource type.
- **BIG-2**: Business logic should be in service classes, not directly in route handlers.
- **BIG-3**: Use dependency injection for service dependencies.
- **BIG-4**: Implement proper request validation with decorators or middleware.
- **BIG-5**: Follow data access object (DAO) pattern for database operations.
- **BIG-6**: Use SQLAlchemy for ORM functionality.

### 2. For Frontend (React)

- **FIG-1**: Components should be organized by feature in a modular structure.
- **FIG-2**: Use custom hooks for reusable logic.
- **FIG-3**: UI state and API communication concerns should be separated.
- **FIG-4**: Global state should be minimized and managed with appropriate patterns.
- **FIG-5**: All API calls must be centralized in service modules.
- **FIG-6**: Use TypeScript for type safety.

## Updates
This document should be reviewed and updated regularly as new modular design best practices emerge or requirements change. 