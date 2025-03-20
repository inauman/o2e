# React Integration Guide

This guide outlines the implementation details, setup instructions, and best practices for integrating React and Tailwind CSS with the Flask application for the YubiKey Bitcoin Seed Storage project.

## Architecture Overview

The MVP2 architecture follows a clean separation of concerns:

- **Frontend**: React application with Tailwind CSS
  - **Responsibility**: User interface, state management, and user interactions
  - **Key Components**: Wizard flows, YubiKey interaction UI, seed management screens
  
- **Backend**: Flask API with SQLite database
  - **Responsibility**: Business logic, authentication, data storage, WebAuthn operations
  - **Key Components**: WebAuthn services, encryption, credential management

The key principle is maintaining **clean interface boundaries** between frontend and backend through well-defined API contracts.

## Clean Interface Architecture

```
┌────────────────────┐                  ┌────────────────────┐
│                    │                  │                    │
│   React Frontend   │                  │   Flask Backend    │
│                    │                  │                    │
└───────┬────────────┘                  └────────┬───────────┘
        │                                        │
        │                                        │
        ▼                                        ▼
┌────────────────────┐                  ┌────────────────────┐
│                    │                  │                    │
│  Frontend Services │ ───REST APIs───> │   API Endpoints    │
│                    │ <───JSON Data──  │                    │
└────────────────────┘                  └────────┬───────────┘
                                                 │
                                                 │
                                                 ▼
                                        ┌────────────────────┐
                                        │                    │
                                        │  Business Services │
                                        │                    │
                                        └────────┬───────────┘
                                                 │
                                                 │
                                                 ▼
                                        ┌────────────────────┐
                                        │                    │
                                        │ Data Access Layer  │
                                        │                    │
                                        └────────────────────┘
```

## Setup Instructions

### 1. Setting Up the Development Environment

#### Install Node.js and npm

For macOS:
```bash
brew install node
```

Verify installation:
```bash
node --version
npm --version
```

#### Create React Application

Create a new React application in a `frontend` directory inside your project:

```bash
mkdir -p frontend
cd frontend
npx create-react-app . --template typescript
```

#### Install and Configure Tailwind CSS

Install Tailwind CSS and its dependencies:

```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

Update the `tailwind.config.js` file to include the paths to your template files:

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          light: '#4da6ff',
          DEFAULT: '#0077cc',
          dark: '#004c8c',
        },
        secondary: {
          light: '#8c9eff',
          DEFAULT: '#536dfe',
          dark: '#0043ca',
        },
      },
    },
  },
  plugins: [],
}
```

Add Tailwind directives to your `src/index.css` file:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Custom base styles */
@layer base {
  body {
    @apply bg-gray-50;
  }
  h1 {
    @apply text-2xl font-bold text-gray-900;
  }
  h2 {
    @apply text-xl font-semibold text-gray-800;
  }
}

/* Custom component styles */
@layer components {
  .btn-primary {
    @apply bg-primary text-white font-bold py-2 px-4 rounded shadow hover:bg-primary-dark transition-colors;
  }
  .card {
    @apply bg-white p-6 rounded-lg shadow-md;
  }
}
```

#### Configure Proxy for Development

To allow the React development server to communicate with the Flask backend, add a proxy configuration in `frontend/package.json`:

```json
{
  "name": "yubikey-seed-storage-frontend",
  "version": "0.1.0",
  "private": true,
  "proxy": "http://localhost:5001",
  "dependencies": {
    // ... other dependencies
  }
}
```

### 2. Setting Up the Component Structure

Create the following directory structure in the `src` folder:

```
src/
├── components/           # Reusable UI components
│   ├── common/           # Commonly used UI elements (buttons, cards, etc.)
│   ├── layouts/          # Layout components (main layout, wizard layout)
│   └── forms/            # Form components and input elements
├── pages/                # Page-level components for each screen
│   ├── Home/
│   ├── Registration/
│   ├── Authentication/
│   └── SeedManagement/
├── hooks/                # Custom React hooks
│   ├── useApi.ts         # Hook for API communication
│   ├── useAuth.ts        # Authentication state and logic
│   └── useWizard.ts      # Wizard state management
├── services/             # API services and other external services
│   ├── api/              # API communication layer
│   │   ├── client.ts     # API client setup with axios
│   │   ├── auth.ts       # Authentication API methods
│   │   ├── yubikeys.ts   # YubiKey management API methods
│   │   └── seeds.ts      # Seed management API methods
│   └── webauthn/         # WebAuthn service
│       └── webauthnService.ts  # WebAuthn browser API integration
├── types/                # TypeScript type definitions
│   ├── api.ts            # API response and request types
│   └── models.ts         # Domain model types
└── utils/                # Utility functions
    ├── validation.ts     # Form validation
    └── security.ts       # Security related utilities
```

## Clean API Interface Implementation

### 1. API Client Setup

Create a base API client in `src/services/api/client.ts`:

```typescript
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

// Standard API response format
export interface ApiResponse<T = any> {
  status: 'success' | 'error';
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
}

// Create axios instance with default configuration
const apiClient: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Required for cookies (including CSRF)
});

// Add request interceptor for CSRF token
apiClient.interceptors.request.use((config: AxiosRequestConfig) => {
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

// Response interceptor for standardized error handling
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response.data,
  (error) => {
    // Standardized error handling
    if (error.response) {
      // The server responded with an error status
      return Promise.reject(error.response.data || {
        status: 'error',
        error: {
          code: `http_${error.response.status}`,
          message: error.response.statusText || 'An error occurred',
        },
      });
    } else if (error.request) {
      // No response received
      return Promise.reject({
        status: 'error',
        error: {
          code: 'network_error',
          message: 'No response received from server',
        },
      });
    } else {
      // Something else happened
      return Promise.reject({
        status: 'error',
        error: {
          code: 'unknown_error',
          message: error.message || 'An unknown error occurred',
        },
      });
    }
  }
);

// Helper to get cookie by name
function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp(`(^|;\\s*)(${name})=([^;]*)`));
  return match ? match[3] : null;
}

// Export typed request methods
export const apiService = {
  get: <T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> =>
    apiClient.get(url, config),
  
  post: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> =>
    apiClient.post(url, data, config),
  
  put: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> =>
    apiClient.put(url, data, config),
  
  delete: <T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> =>
    apiClient.delete(url, config),
};
```

### 2. Service Implementation Example

Create an authentication service in `src/services/api/auth.ts`:

```typescript
import { apiService, ApiResponse } from './client';

// Types for authentication API
export interface RegistrationOptions {
  publicKey: PublicKeyCredentialCreationOptions;
}

export interface RegistrationResult {
  credentialId: string;
  userId: string;
  created: string;
}

// Authentication service
export const authService = {
  // Begin registration process
  beginRegistration: async (username: string, displayName?: string): Promise<ApiResponse<RegistrationOptions>> => {
    return apiService.post<RegistrationOptions>('/auth/begin-registration', {
      username,
      displayName: displayName || username,
    });
  },
  
  // Complete registration with WebAuthn credential
  completeRegistration: async (credential: PublicKeyCredential): Promise<ApiResponse<RegistrationResult>> => {
    // Convert credential to JSON-serializable format
    const credentialJSON = {
      id: credential.id,
      rawId: bufferToBase64URLString(credential.rawId),
      type: credential.type,
      response: {
        clientDataJSON: bufferToBase64URLString(
          (credential.response as AuthenticatorAttestationResponse).clientDataJSON
        ),
        attestationObject: bufferToBase64URLString(
          (credential.response as AuthenticatorAttestationResponse).attestationObject
        ),
        transports: (credential.response as AuthenticatorAttestationResponse).getTransports?.() || [],
      },
      clientExtensionResults: credential.getClientExtensionResults(),
    };
    
    return apiService.post<RegistrationResult>('/auth/complete-registration', credentialJSON);
  },
  
  // Add other authentication methods here
};

// Helper to convert ArrayBuffer to Base64URL string
function bufferToBase64URLString(buffer: ArrayBuffer): string {
  const bytes = new Uint8Array(buffer);
  let str = '';
  for (const byte of bytes) {
    str += String.fromCharCode(byte);
  }
  // Standard base64 encoder
  let base64 = btoa(str);
  // Convert to base64URL
  return base64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
}
```

### 3. React Hook for API Integration

Create a custom hook for authentication in `src/hooks/useAuth.ts`:

```typescript
import { useState, useCallback, useEffect } from 'react';
import { authService, RegistrationOptions, RegistrationResult } from '../services/api/auth';
import { ApiResponse } from '../services/api/client';

interface UseAuthState {
  isLoading: boolean;
  error: string | null;
  user: {
    userId: string;
    username: string;
  } | null;
  registrationOptions: RegistrationOptions | null;
}

export function useAuth() {
  const [state, setState] = useState<UseAuthState>({
    isLoading: false,
    error: null,
    user: null,
    registrationOptions: null,
  });
  
  // Begin YubiKey registration process
  const beginRegistration = useCallback(async (username: string, displayName?: string) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      const response = await authService.beginRegistration(username, displayName);
      
      if (response.status === 'success' && response.data) {
        setState(prev => ({
          ...prev,
          isLoading: false,
          registrationOptions: response.data,
        }));
        return response.data;
      } else {
        throw new Error(response.error?.message || 'Failed to start registration');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred';
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));
      throw error;
    }
  }, []);
  
  // Complete YubiKey registration with credential
  const completeRegistration = useCallback(async (credential: PublicKeyCredential) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      const response = await authService.completeRegistration(credential);
      
      if (response.status === 'success' && response.data) {
        setState(prev => ({
          ...prev,
          isLoading: false,
          user: {
            userId: response.data.userId,
            username: response.data.userId, // Normally we'd have a display name too
          },
          registrationOptions: null,
        }));
        return response.data;
      } else {
        throw new Error(response.error?.message || 'Failed to complete registration');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred';
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));
      throw error;
    }
  }, []);
  
  // Check if user is already authenticated
  useEffect(() => {
    // Code to check current authentication status
    // This would call an endpoint like /api/v1/auth/status
  }, []);
  
  return {
    isLoading: state.isLoading,
    error: state.error,
    user: state.user,
    registrationOptions: state.registrationOptions,
    beginRegistration,
    completeRegistration,
    // Add other auth methods
  };
}
```

## Flask Backend API Implementation

### 1. API Blueprint Structure

Organize the Flask API with clear blueprints for different resources:

```python
# app/api/__init__.py
from flask import Blueprint

# Create main API blueprint with versioning
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# Import and register resource blueprints
from .auth import auth_bp
from .yubikeys import yubikeys_bp
from .seeds import seeds_bp
from .user import user_bp

api_v1.register_blueprint(auth_bp, url_prefix='/auth')
api_v1.register_blueprint(yubikeys_bp, url_prefix='/yubikeys')
api_v1.register_blueprint(seeds_bp, url_prefix='/seeds')
api_v1.register_blueprint(user_bp, url_prefix='/user')

# Register the API blueprint with the app
def init_app(app):
    from .error_handlers import register_error_handlers
    register_error_handlers(api_v1)
    app.register_blueprint(api_v1)
```

### 2. Authentication API Example

```python
# app/api/auth.py
from flask import Blueprint, request, jsonify, session
from app.services.webauthn_service import WebAuthnService
from app.services.user_service import UserService
from app.utils.security import generate_csrf_token, validate_csrf
from app.utils.validators import validate_request_json
from app.utils.responses import success_response, error_response

auth_bp = Blueprint('auth', __name__)
webauthn_service = WebAuthnService()
user_service = UserService()

@auth_bp.route('/begin-registration', methods=['POST'])
@validate_csrf
@validate_request_json(['username'])
def begin_registration():
    """
    Begin WebAuthn registration process
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - username
          properties:
            username:
              type: string
              description: Username for registration
            displayName:
              type: string
              description: Display name (defaults to username)
    responses:
      200:
        description: Registration options for WebAuthn
        schema:
          type: object
          properties:
            status:
              type: string
              enum: [success]
            data:
              type: object
              properties:
                publicKey:
                  type: object
                  description: WebAuthn credential creation options
      400:
        description: Invalid request
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    data = request.json
    username = data.get('username')
    display_name = data.get('displayName', username)
    
    try:
        registration_options = webauthn_service.generate_registration_options(username, display_name)
        # Store challenge in session for verification later
        session['current_registration_challenge'] = registration_options['challenge']
        session['registering_username'] = username
        session['registering_display_name'] = display_name
        
        return success_response({'publicKey': registration_options})
    except Exception as e:
        return error_response('registration_error', str(e), 400)

@auth_bp.route('/complete-registration', methods=['POST'])
@validate_csrf
def complete_registration():
    """
    Complete WebAuthn registration with credential from client
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - id
            - rawId
            - response
            - type
          properties:
            id:
              type: string
            rawId:
              type: string
            response:
              type: object
              properties:
                clientDataJSON:
                  type: string
                attestationObject:
                  type: string
                transports:
                  type: array
                  items:
                    type: string
            type:
              type: string
              enum: [public-key]
            clientExtensionResults:
              type: object
    responses:
      200:
        description: Successful registration
        schema:
          type: object
          properties:
            status:
              type: string
              enum: [success]
            data:
              type: object
              properties:
                credentialId:
                  type: string
                userId:
                  type: string
                created:
                  type: string
                  format: date-time
      400:
        description: Registration failed
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    if 'current_registration_challenge' not in session:
        return error_response('registration_error', 'No active registration session', 400)
    
    try:
        username = session.get('registering_username')
        display_name = session.get('registering_display_name')
        expected_challenge = session.get('current_registration_challenge')
        
        # Verify and register the credential
        credential_id, user_id = webauthn_service.verify_registration_response(
            request.json,
            expected_challenge,
            username,
            display_name
        )
        
        # Clean up session
        session.pop('current_registration_challenge')
        session.pop('registering_username')
        session.pop('registering_display_name')
        
        # Success! Create the user account and store credential
        user_service.create_user(user_id, username, credential_id)
        
        # Generate new CSRF token
        csrf_token = generate_csrf_token()
        response = success_response({
            'credentialId': credential_id,
            'userId': user_id,
            'created': datetime.utcnow().isoformat() + 'Z'
        })
        
        # Set CSRF token cookie
        response.set_cookie(
            'csrf_token',
            csrf_token,
            httponly=True,
            secure=True,
            samesite='Lax'
        )
        
        return response
    except Exception as e:
        return error_response('registration_failed', str(e), 400)
```

### 3. Response Utility Functions

Create standardized API response helpers:

```python
# app/utils/responses.py
from flask import jsonify

def success_response(data=None):
    """
    Create a standardized success response
    """
    response = {
        'status': 'success',
    }
    
    if data is not None:
        response['data'] = data
        
    return jsonify(response)

def error_response(code, message, status_code=400, details=None):
    """
    Create a standardized error response
    """
    response = {
        'status': 'error',
        'error': {
            'code': code,
            'message': message
        }
    }
    
    if details is not None:
        response['error']['details'] = details
        
    return jsonify(response), status_code
```

## CORS Configuration

For development, configure CORS to allow the React development server to communicate with the Flask backend:

```python
# app/__init__.py
from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    
    # Configure CORS for development
    if app.config['ENV'] == 'development':
        CORS(app, resources={
            r"/api/*": {
                "origins": "http://localhost:3000",
                "supports_credentials": True  # Important for cookies
            }
        })
    
    # Register blueprints
    from .api import init_app as init_api
    init_api(app)
    
    return app
```

## Deployment Strategy

### Development Workflow

During development, you'll run both the Flask backend and React frontend separately:

1. **Flask backend**: `python app.py` (runs on port 5001)
2. **React frontend**: `cd frontend && npm start` (runs on port 3000)

The React development server will proxy API requests to the Flask backend.

### Production Deployment

For production, build the React application and have Flask serve it:

1. Build the React application:
   ```bash
   cd frontend
   npm run build
   ```

2. Configure Flask to serve the built React app:
   ```python
   # app/__init__.py
   from flask import Flask, send_from_directory
   import os
   
   def create_app():
       app = Flask(__name__, static_folder='../frontend/build')
       
       # API routes
       from .api import init_app as init_api
       init_api(app)
       
       # Serve React app
       @app.route('/', defaults={'path': ''})
       @app.route('/<path:path>')
       def serve(path):
           if path != "" and os.path.exists(app.static_folder + '/' + path):
               return send_from_directory(app.static_folder, path)
           else:
               return send_from_directory(app.static_folder, 'index.html')
       
       return app
   ```

## Security Best Practices

### Secure API Communication

1. **Use HTTPS**: Always use HTTPS in production to encrypt data in transit.

2. **CSRF Protection**: Implement CSRF protection as shown in the examples:
   - Send CSRF tokens in HTTP-only cookies
   - Require the same token in request headers
   - Validate tokens on state-changing operations

3. **Input Validation**: Validate all inputs on both client and server sides:
   ```typescript
   // Client-side validation example
   function validateUsername(username: string): string | null {
     if (!username) return 'Username is required';
     if (username.length < 3) return 'Username must be at least 3 characters';
     if (!/^[a-zA-Z0-9_-]+$/.test(username)) return 'Username contains invalid characters';
     return null;
   }
   ```

4. **Authentication**: Ensure proper authentication for all protected routes:
   - Use session cookies for maintaining authentication state
   - Implement proper session expiration and renewal
   - Require re-authentication for sensitive operations

### WebAuthn Security

1. **Challenge Verification**: Always verify that the challenge in the WebAuthn response matches the challenge you generated.

2. **Origin Validation**: Verify that the origin in the client data matches your expected origin.

3. **User Verification**: Consider requiring user verification for sensitive operations.

4. **Resident Keys**: Follow best practices for working with resident keys, as they store user data on the YubiKey.

## Common Issues and Troubleshooting

### WebAuthn API Issues

1. **Cross-Origin Errors**: WebAuthn requires a secure context (HTTPS or localhost). If you're getting errors, make sure:
   - You're using localhost or HTTPS
   - The registered RP ID (relying party ID) is valid for your origin

2. **Browser Support**: Different browsers have varying levels of WebAuthn support. Always include feature detection:
   ```typescript
   if (!window.PublicKeyCredential) {
     // WebAuthn not supported
     showUnsupportedBrowserMessage();
     return;
   }
   ```

### CORS Errors

If you're getting CORS errors during development:

1. Check that your CORS configuration on the Flask side includes the correct origin
2. Ensure `credentials: 'include'` is set for fetch requests or `withCredentials: true` for axios
3. Verify that the proxy configuration in your React app is correct

### Build Issues

1. **Static File Paths**: In production, make sure file paths in your built React app are correct:
   - Use relative paths in imports
   - Set the `homepage` field in `package.json` if not serving from root

2. **404 Errors**: Configure your server to redirect non-file routes to `index.html` for React routing to work

## Resources

- [React Documentation](https://reactjs.org/docs/getting-started.html)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [WebAuthn API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Authentication_API)
- [Flask-CORS](https://flask-cors.readthedocs.io/) 