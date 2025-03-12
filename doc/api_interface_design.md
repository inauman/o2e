# API Interface Design Guide

This document outlines the principles, patterns, and specifications for designing and implementing the API interfaces between the Flask backend and React frontend in the YubiKey Bitcoin Seed Storage application.

## Core Principles

### 1. Clean Interface Boundaries

Each API should have a clearly defined responsibility and scope. The interfaces should establish a strong boundary between the backend and frontend, with each side only knowing what it needs to know about the other.

- **Backend**: Responsible for data processing, business logic, security operations, and persistence
- **Frontend**: Responsible for user interface, state management, and user interactions

### 2. Contract-First Development

All APIs should be defined with a clear contract before implementation begins. This contract includes:

- Endpoint path and HTTP method
- Request parameters and body format
- Response structure and status codes
- Authentication requirements
- Error handling and response formats

### 3. Security as Non-Negotiable

Security is not an add-on but a fundamental part of every API design decision:

- All endpoints must authenticate and authorize access appropriately
- Sensitive operations must include additional verification
- All inputs must be validated and sanitized
- Data must be protected both in transit and at rest

## API Structure

### RESTful Resource Organization

APIs should be organized around resources following RESTful principles:

```
/api/v1/                           # API root with version
  /auth/                           # Authentication operations
    /begin-registration            # Start YubiKey registration
    /complete-registration         # Complete YubiKey registration
    /begin-authentication          # Start YubiKey authentication
    /complete-authentication       # Complete YubiKey authentication
  /yubikeys/                       # YubiKey management
    /{credential_id}               # Operations on a specific YubiKey
  /seeds/                          # Seed management
    /{seed_id}                     # Operations on a specific seed
  /user/                           # User operations
    /profile                       # User profile operations
```

### HTTP Methods

Use appropriate HTTP methods for different operations:

- `GET`: Retrieve resources (idempotent, safe)
- `POST`: Create resources or trigger actions
- `PUT`: Update resources completely (idempotent)
- `PATCH`: Update resources partially
- `DELETE`: Remove resources

## API Contracts

### Authentication APIs

#### Begin Registration

**Endpoint**: `POST /api/v1/auth/begin-registration`

**Request**:
```json
{
  "username": "string",
  "displayName": "string"
}
```

**Response (200 OK)**:
```json
{
  "status": "success",
  "data": {
    "publicKey": {
      "challenge": "base64url-encoded-string",
      "rp": {
        "name": "YubiKey Bitcoin Seed Storage",
        "id": "localhost"
      },
      "user": {
        "id": "base64url-encoded-string",
        "name": "string",
        "displayName": "string"
      },
      "pubKeyCredParams": [
        {
          "type": "public-key",
          "alg": -7
        }
      ],
      "timeout": 60000,
      "attestation": "direct",
      "authenticatorSelection": {
        "authenticatorAttachment": "cross-platform",
        "userVerification": "preferred",
        "requireResidentKey": false
      },
      "extensions": {
        "hmacCreateSecret": true
      }
    }
  }
}
```

**Response (400 Bad Request)**:
```json
{
  "status": "error",
  "error": {
    "code": "invalid_request",
    "message": "Username is required"
  }
}
```

#### Complete Registration

**Endpoint**: `POST /api/v1/auth/complete-registration`

**Request**:
```json
{
  "id": "base64url-encoded-string",
  "rawId": "base64url-encoded-string",
  "response": {
    "clientDataJSON": "base64url-encoded-string",
    "attestationObject": "base64url-encoded-string",
    "transports": ["usb", "nfc"]
  },
  "type": "public-key",
  "clientExtensionResults": {
    "hmacCreateSecret": true
  }
}
```

**Response (200 OK)**:
```json
{
  "status": "success",
  "data": {
    "credentialId": "base64url-encoded-string",
    "userId": "string",
    "created": "ISO-8601-date-string"
  }
}
```

**Response (400 Bad Request)**:
```json
{
  "status": "error",
  "error": {
    "code": "registration_failed",
    "message": "YubiKey registration failed"
  }
}
```

### YubiKey Management APIs

#### List YubiKeys

**Endpoint**: `GET /api/v1/yubikeys`

**Response (200 OK)**:
```json
{
  "status": "success",
  "data": {
    "yubikeys": [
      {
        "credentialId": "base64url-encoded-string",
        "nickname": "string",
        "registered": "ISO-8601-date-string",
        "isPrimary": true,
        "lastUsed": "ISO-8601-date-string"
      }
    ]
  }
}
```

### Seed Management APIs

#### Generate New Seed

**Endpoint**: `POST /api/v1/seeds`

**Request**:
```json
{
  "strength": 256,
  "yubikeys": [
    "credentialId1",
    "credentialId2"
  ]
}
```

**Response (200 OK)**:
```json
{
  "status": "success",
  "data": {
    "seedId": "string",
    "created": "ISO-8601-date-string",
    "associatedYubiKeys": [
      {
        "credentialId": "base64url-encoded-string",
        "nickname": "string"
      }
    ]
  }
}
```

## Error Handling

### Standardized Error Response

All error responses should follow a consistent format:

```json
{
  "status": "error",
  "error": {
    "code": "error_code",
    "message": "Human-readable error message",
    "details": {} // Optional additional error details
  }
}
```

### Common Error Codes

- `invalid_request`: Malformed request or missing required fields
- `authentication_required`: User not authenticated
- `permission_denied`: User not authorized for this operation
- `resource_not_found`: Requested resource doesn't exist
- `validation_error`: Input validation failed
- `webauthn_error`: WebAuthn operation failed
- `internal_error`: Server-side error

## Security Implementation

### Authentication Flow

1. **Session-Based Authentication**:
   - Sessions maintained via HTTP-only cookies
   - Session tokens should have appropriate expiration
   - Re-authentication required for sensitive operations

2. **WebAuthn Integration**:
   - Backend generates challenges and validates responses
   - Credentials stored securely in the database
   - Proper validation of all WebAuthn parameters

### CSRF Protection

1. **Double-Submit Cookie Pattern**:
   - CSRF token sent in HTTP-only cookie
   - Same token required in Authorization header or request body
   - Tokens validated on all state-changing operations

2. **Implementation**:
   ```python
   # On session creation
   csrf_token = generate_secure_random_token()
   response.set_cookie('csrf_token', csrf_token, httponly=True, secure=True, samesite='Lax')
   
   # On API request validation
   def validate_csrf(request):
       cookie_token = request.cookies.get('csrf_token')
       header_token = request.headers.get('X-CSRF-Token')
       if not cookie_token or not header_token or cookie_token != header_token:
           raise CSRFValidationError()
   ```

## Implementation Guidelines

### Flask Backend

1. **API Structure**:
   ```python
   # app/api/__init__.py
   from flask import Blueprint
   
   api = Blueprint('api', __name__, url_prefix='/api/v1')
   
   # Import and register blueprints
   from .auth import auth_bp
   from .yubikeys import yubikeys_bp
   from .seeds import seeds_bp
   
   api.register_blueprint(auth_bp, url_prefix='/auth')
   api.register_blueprint(yubikeys_bp, url_prefix='/yubikeys')
   api.register_blueprint(seeds_bp, url_prefix='/seeds')
   ```

2. **Route Implementation**:
   ```python
   # app/api/auth.py
   from flask import Blueprint, request, jsonify
   from app.services import webauthn_service
   from app.utils.validators import validate_request
   from app.utils.security import validate_csrf
   
   auth_bp = Blueprint('auth', __name__)
   
   @auth_bp.route('/begin-registration', methods=['POST'])
   @validate_csrf
   @validate_request(['username'])
   def begin_registration():
       data = request.json
       username = data.get('username')
       display_name = data.get('displayName', username)
       
       try:
           reg_options = webauthn_service.generate_registration_options(username, display_name)
           return jsonify({
               'status': 'success',
               'data': {
                   'publicKey': reg_options
               }
           })
       except Exception as e:
           return jsonify({
               'status': 'error',
               'error': {
                   'code': 'registration_error',
                   'message': str(e)
               }
           }), 400
   ```

### React Frontend

1. **API Service**:
   ```typescript
   // src/services/api/authService.ts
   import { ApiResponse } from '../types';
   import { httpClient } from './httpClient';
   
   export const authService = {
     async beginRegistration(username: string, displayName?: string): Promise<ApiResponse> {
       return httpClient.post('/api/v1/auth/begin-registration', {
         username,
         displayName: displayName || username
       });
     },
     
     async completeRegistration(credential: PublicKeyCredential): Promise<ApiResponse> {
       // Convert credential to JSON-serializable format
       const response = {
         id: credential.id,
         rawId: btoa(String.fromCharCode(...new Uint8Array(credential.rawId))),
         response: {
           clientDataJSON: btoa(String.fromCharCode(
             ...new Uint8Array(credential.response.clientDataJSON)
           )),
           attestationObject: btoa(String.fromCharCode(
             ...new Uint8Array(credential.response.attestationObject)
           )),
           // Add other properties as needed
         },
         type: credential.type,
         clientExtensionResults: credential.getClientExtensionResults()
       };
       
       return httpClient.post('/api/v1/auth/complete-registration', response);
     }
   };
   ```

2. **HTTP Client with CSRF Handling**:
   ```typescript
   // src/services/api/httpClient.ts
   import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
   
   // Create base axios instance
   const axiosInstance: AxiosInstance = axios.create({
     baseURL: process.env.REACT_APP_API_URL || '',
     headers: {
       'Content-Type': 'application/json',
     },
     withCredentials: true, // Important for cookies
   });
   
   // Add interceptor to include CSRF token
   axiosInstance.interceptors.request.use((config: AxiosRequestConfig) => {
     // Get CSRF token from cookie
     const csrfToken = getCookie('csrf_token');
     if (csrfToken) {
       config.headers = {
         ...config.headers,
         'X-CSRF-Token': csrfToken,
       };
     }
     return config;
   });
   
   // Helper to get cookies by name
   function getCookie(name: string): string | null {
     const match = document.cookie.match(new RegExp(`(^| )${name}=([^;]+)`));
     return match ? match[2] : null;
   }
   
   export const httpClient = {
     async get(url: string, config?: AxiosRequestConfig) {
       try {
         const response = await axiosInstance.get(url, config);
         return response.data;
       } catch (error) {
         return handleApiError(error);
       }
     },
     
     async post(url: string, data?: any, config?: AxiosRequestConfig) {
       try {
         const response = await axiosInstance.post(url, data, config);
         return response.data;
       } catch (error) {
         return handleApiError(error);
       }
     },
     
     // Add other methods as needed
   };
   
   function handleApiError(error: any) {
     // Standardize error handling
     if (error.response) {
       // The request was made and the server responded with a non-2xx status
       return error.response.data;
     } else if (error.request) {
       // The request was made but no response was received
       return {
         status: 'error',
         error: {
           code: 'network_error',
           message: 'No response received from server',
         }
       };
     } else {
       // Something happened in setting up the request
       return {
         status: 'error',
         error: {
           code: 'request_error',
           message: error.message,
         }
       };
     }
   }
   ```

## Testing API Interfaces

### Automated Testing

1. **Unit Testing API Handlers**:
   ```python
   # app/tests/api/test_auth.py
   def test_begin_registration_success(client, mocker):
       # Arrange
       mock_options = {...}  # Mock registration options
       mocker.patch('app.services.webauthn_service.generate_registration_options', 
                   return_value=mock_options)
       
       # Act
       response = client.post('/api/v1/auth/begin-registration', 
                             json={'username': 'testuser'})
       
       # Assert
       assert response.status_code == 200
       assert response.json['status'] == 'success'
       assert 'publicKey' in response.json['data']
   
   def test_begin_registration_missing_username(client):
       # Act
       response = client.post('/api/v1/auth/begin-registration', json={})
       
       # Assert
       assert response.status_code == 400
       assert response.json['status'] == 'error'
       assert response.json['error']['code'] == 'invalid_request'
   ```

2. **Integration Testing**:
   ```python
   # app/tests/integration/test_auth_flow.py
   def test_registration_authentication_flow(client, mock_webauthn):
       # Arrange
       username = "testuser"
       mock_webauthn.setup_mock_registration()
       
       # Act - Step 1: Begin Registration
       begin_reg_response = client.post('/api/v1/auth/begin-registration', 
                                       json={'username': username})
       
       # Assert Step 1
       assert begin_reg_response.status_code == 200
       
       # Act - Step 2: Complete Registration with mock credential
       mock_credential = mock_webauthn.generate_credential()
       complete_reg_response = client.post('/api/v1/auth/complete-registration',
                                         json=mock_credential)
       
       # Assert Step 2
       assert complete_reg_response.status_code == 200
       
       # Continue with authentication flow...
   ```

## API Documentation

### API Documentation Generation

Use OpenAPI/Swagger to document all APIs:

```python
# app/__init__.py
from flask import Flask
from flask_swagger_ui import get_swaggerui_blueprint

def create_app():
    app = Flask(__name__)
    
    # Register API blueprint
    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint)
    
    # Set up Swagger UI
    SWAGGER_URL = '/api/docs'
    API_URL = '/static/swagger.json'
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={'app_name': "YubiKey Bitcoin Seed Storage API"}
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    
    return app
```

## Conclusion

Following these guidelines will ensure clean, secure interfaces between the Flask backend and React frontend. The clear API contracts enable independent development while maintaining strong boundaries between application layers. The focus on security-by-design ensures that all communications between components are properly secured and validated. 