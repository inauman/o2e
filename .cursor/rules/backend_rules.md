# Backend Development Rules

## Flask Architecture

- **BA-1**: All API routes should be organized in blueprints based on resource type.
- **BA-2**: API versioning must be included in URL structure (e.g., `/api/v1/`).
- **BA-3**: Business logic should be in service classes, not directly in route handlers.
- **BA-4**: Database models should be separate from API serialization schemas.
- **BA-5**: Use dependency injection for service dependencies.
- **BA-6**: Implement proper request validation with decorators or middleware.

## Error Handling

- **EH-1**: All errors must be caught and translated to appropriate HTTP response codes.
- **EH-2**: Error responses must follow the standardized format defined in the API Interface Design.
- **EH-3**: Sensitive error details must not be exposed to the client in production.
- **EH-4**: All expected exceptions should be explicitly handled with appropriate user feedback.
- **EH-5**: Use custom exceptions for domain-specific errors.
- **EH-6**: Log exceptions with appropriate context and severity.

## Service Layer

- **SL-1**: Implement service classes for business logic.
- **SL-2**: Services should be stateless when possible.
- **SL-3**: Service methods should have clear contracts (inputs, outputs, exceptions).
- **SL-4**: Service dependencies should be injected rather than created.
- **SL-5**: Services should be testable in isolation.
- **SL-6**: Transactions should be managed at the service layer.

## Data Access

- **DA-1**: Use Data Access Objects (DAOs) or repositories for database operations.
- **DA-2**: Database operations must be wrapped in appropriate transaction handling.
- **DA-3**: Use SQLAlchemy for ORM functionality.
- **DA-4**: Implement proper connection pooling.
- **DA-5**: Use migration tools for schema changes.
- **DA-6**: Implement proper error handling for database operations.

## Authentication & Authorization

- **AA-1**: Implement proper authentication middleware.
- **AA-2**: Authorization checks should be explicit and centralized.
- **AA-3**: Use role-based or attribute-based access control.
- **AA-4**: Session management should be secure.
- **AA-5**: Implement proper password hashing.
- **AA-6**: Enforce strong password policies.

## WebAuthn Implementation

- **WI-1**: Challenges and credentials must be properly validated against stored values.
- **WI-2**: User IDs must be consistent across registration and authentication flows.
- **WI-3**: Proper error handling must be implemented for each WebAuthn operation.
- **WI-4**: Store WebAuthn credentials securely.
- **WI-5**: Implement credential management functionalities.
- **WI-6**: Validate all WebAuthn response parameters.

## Response Formatting

- **RF-1**: Use consistent response formats across all endpoints.
- **RF-2**: Success responses should include appropriate HTTP status codes.
- **RF-3**: Include metadata in responses where appropriate (pagination, etc.).
- **RF-4**: Use appropriate content types for responses.
- **RF-5**: Implement proper serialization/deserialization.
- **RF-6**: Handle empty or null values consistently.

## Security Implementation

- **SI-1**: Implement CSRF protection for all state-changing operations.
- **SI-2**: All user inputs must be validated and sanitized before processing.
- **SI-3**: Use HTTP-only cookies for session management where appropriate.
- **SI-4**: Implement rate limiting for sensitive operations.
- **SI-5**: Use secure headers (HSTS, Content-Security-Policy, etc.).
- **SI-6**: Protect against common web vulnerabilities (OWASP Top 10).

## Logging and Monitoring

- **LM-1**: Implement structured logging.
- **LM-2**: Log appropriate context with each log entry.
- **LM-3**: Use appropriate log levels.
- **LM-4**: Never log sensitive information.
- **LM-5**: Implement request tracing for complex operations.
- **LM-6**: Log security-relevant events.

## API Documentation

- **AD-1**: Use OpenAPI/Swagger for API documentation.
- **AD-2**: Document all API endpoints with parameters, responses, and examples.
- **AD-3**: Keep documentation in sync with implementation.
- **AD-4**: Include authentication requirements in documentation.
- **AD-5**: Document error responses and codes.
- **AD-6**: Provide example requests and responses.

## Testing Requirements

- **TR-1**: All API endpoints must have corresponding tests.
- **TR-2**: All business logic functions must have unit tests.
- **TR-3**: Use mock objects for external dependencies.
- **TR-4**: Test both success and error paths.
- **TR-5**: Use fixtures for test setup.
- **TR-6**: Test database interactions with a test database.

## Performance Considerations

- **PC-1**: Use appropriate caching strategies.
- **PC-2**: Optimize database queries.
- **PC-3**: Implement pagination for large result sets.
- **PC-4**: Profile endpoints for performance bottlenecks.
- **PC-5**: Optimize response payload size.
- **PC-6**: Use asynchronous processing for long-running tasks.

## Updates
This document should be reviewed and updated regularly as new backend development best practices emerge or requirements change. 