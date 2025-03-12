# API Design Rules

## Clean Interface Boundaries

- **IB-1**: Backend code (Flask) must never make assumptions about frontend implementation details.
- **IB-2**: All communication between frontend and backend must occur through well-defined APIs.
- **IB-3**: API contracts must be strictly followed as defined in the API Interface Design Guide.
- **IB-4**: Each API should have a clearly defined responsibility and scope.

## RESTful API Structure

- **RS-1**: Organize APIs around resources following RESTful principles.
- **RS-2**: API versioning must be included in URL structure (e.g., `/api/v1/`).
- **RS-3**: Use appropriate HTTP methods for different operations:
  - `GET`: Retrieve resources (idempotent, safe)
  - `POST`: Create resources or trigger actions
  - `PUT`: Update resources completely (idempotent)
  - `PATCH`: Update resources partially
  - `DELETE`: Remove resources
- **RS-4**: API endpoints should use kebab-case for URLs.

## API Response Formats

- **RF-1**: Use consistent response formats across all endpoints.
- **RF-2**: Success responses should follow the standard format:
  ```json
  {
    "status": "success",
    "data": { ... }
  }
  ```
- **RF-3**: Error responses should follow the standard format:
  ```json
  {
    "status": "error",
    "error": {
      "code": "error_code",
      "message": "Human-readable error message",
      "details": { ... }
    }
  }
  ```
- **RF-4**: Use appropriate HTTP status codes:
  - 200: Success
  - 201: Created
  - 400: Bad Request
  - 401: Unauthorized
  - 403: Forbidden
  - 404: Not Found
  - 500: Internal Server Error

## Error Handling

- **EH-1**: All errors must be caught and translated to appropriate HTTP response codes.
- **EH-2**: Error responses must follow the standardized format defined above.
- **EH-3**: Sensitive error details must not be exposed to the client in production.
- **EH-4**: Common error codes should be used consistently across all endpoints.
- **EH-5**: All expected exceptions should be explicitly handled with appropriate user feedback.

## Security Requirements

- **SR-1**: All API endpoints must implement appropriate authentication and authorization checks.
- **SR-2**: All user inputs must be validated and sanitized before processing.
- **SR-3**: CSRF protection must be implemented for all state-changing operations.
- **SR-4**: Use HTTP-only cookies for session management where appropriate.
- **SR-5**: Authentication tokens must have appropriate expiration.
- **SR-6**: Re-authentication should be required for sensitive operations.

## CSRF Protection

- **CP-1**: Implement Double-Submit Cookie Pattern:
  - CSRF token sent in HTTP-only cookie
  - Same token required in Authorization header or request body
  - Tokens validated on all state-changing operations
- **CP-2**: Use SameSite cookie attributes.
- **CP-3**: Ensure CSRF tokens are rotated regularly.

## API Documentation

- **AD-1**: All APIs must be documented with parameters, response formats, and example usage.
- **AD-2**: Use tools like Swagger/OpenAPI for API documentation.
- **AD-3**: Document authentication requirements for each endpoint.
- **AD-4**: Provide example requests and responses for each endpoint.
- **AD-5**: Document error codes and their meanings.

## Implementation Guidelines

- **IG-1**: Organize API routes in blueprints based on resource type.
- **IG-2**: Business logic should be in service classes, not directly in route handlers.
- **IG-3**: Database models should be separate from API serialization schemas.
- **IG-4**: Implement proper request validation with decorators or middleware.
- **IG-5**: Use dependency injection for service dependencies.

## Testing Requirements

- **TR-1**: All API endpoints must have corresponding tests.
- **TR-2**: Test both successful and error cases for each endpoint.
- **TR-3**: Test authentication and authorization requirements.
- **TR-4**: Use mock data and services for testing.
- **TR-5**: Test edge cases and input validation.

## WebAuthn API Integration

- **WA-1**: Challenges and credentials must be properly validated against stored values.
- **WA-2**: User IDs must be consistent across registration and authentication flows.
- **WA-3**: Proper error handling must be implemented for each WebAuthn operation.
- **WA-4**: Validate origins and relying party IDs in WebAuthn responses.

## Performance Considerations

- **PC-1**: Design APIs to minimize request/response payload size.
- **PC-2**: Consider pagination for large data sets.
- **PC-3**: Document performance expectations for each endpoint.
- **PC-4**: Implement caching where appropriate.
- **PC-5**: Use efficient serialization methods.

## Contract-First Development

- **CD-1**: Define API contracts before implementation begins.
- **CD-2**: Follow a contract-first approach to API development.
- **CD-3**: API contracts should include:
  - Endpoint path and HTTP method
  - Request parameters and body format
  - Response structure and status codes
  - Authentication requirements
  - Error handling and response formats
- **CD-4**: Implement typed interfaces for request/response data.

## Updates
This document should be reviewed and updated regularly as new API design best practices emerge or requirements change. 