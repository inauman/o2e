# Recommended Project Structure

Based on the current codebase and planned React/Flask integration, here's the recommended project structure:

```
o2e/
├── README.md                              # Project overview, setup instructions
├── .cursor/                               # Cursor configuration
│   └── rules/                             # Modular cursor rules
├── backend/                               # Backend Python code
│   ├── app.py                             # Main Flask application
│   ├── config.yaml                        # Configuration file
│   ├── pyproject.toml                     # Python dependencies and project metadata
│   ├── api/                               # API endpoints
│   │   ├── __init__.py                    # API package initialization
│   │   ├── auth.py                        # Authentication endpoints
│   │   ├── seeds.py                       # Seed management endpoints
│   │   └── yubikeys.py                    # YubiKey management endpoints
│   ├── services/                          # Business logic services
│   │   ├── __init__.py                    # Services package initialization
│   │   ├── bitcoin_service.py             # Bitcoin-related operations
│   │   ├── webauthn_service.py            # WebAuthn operations
│   │   └── encryption_service.py          # Encryption/decryption operations
│   ├── models/                            # Data models
│   │   ├── __init__.py                    # Models package initialization
│   │   └── schemas.py                     # Data validation schemas
│   ├── utils/                             # Utility functions
│   │   ├── __init__.py                    # Utils package initialization
│   │   ├── bitcoin_utils.py               # Bitcoin utilities
│   │   ├── security.py                    # Security utilities
│   │   └── validation.py                  # Input validation
│   ├── templates/                         # Flask templates (legacy, to be replaced by React)
│   │   └── ...                            # Various template files
│   ├── static/                            # Static assets (legacy, to be replaced by React)
│   │   └── ...                            # CSS, JS, images
│   └── tests/                             # Backend tests
│       ├── unit/                          # Unit tests
│       │   └── ...                        # Test files for each module
│       └── integration/                   # Integration tests
│           └── ...                        # End-to-end tests
├── frontend/                              # React frontend
│   ├── package.json                       # NPM dependencies and scripts
│   ├── tsconfig.json                      # TypeScript configuration
│   ├── tailwind.config.js                 # Tailwind CSS configuration
│   ├── public/                            # Public assets
│   │   └── ...                            # Favicon, index.html, etc.
│   ├── src/                               # React source code
│   │   ├── components/                    # Reusable UI components
│   │   │   ├── common/                    # Common UI elements
│   │   │   ├── layouts/                   # Layout components
│   │   │   └── forms/                     # Form components
│   │   ├── pages/                         # Page components
│   │   │   ├── Home/
│   │   │   ├── Registration/
│   │   │   ├── Authentication/
│   │   │   └── SeedManagement/
│   │   ├── hooks/                         # Custom React hooks
│   │   ├── services/                      # API services
│   │   │   ├── api/                       # API communication
│   │   │   └── webauthn/                  # WebAuthn integration
│   │   ├── types/                         # TypeScript type definitions
│   │   └── utils/                         # Utility functions
│   └── tests/                             # Frontend tests
│       └── ...                            # Jest test files
├── data/                                  # Application data storage
│   ├── .gitignore                         # Ignore sensitive data
│   ├── credentials.json                   # YubiKey credentials storage
│   └── encrypted_seeds.json               # Encrypted seed phrases
└── doc/                                   # Project documentation
    ├── api_interface_design.md            # API interface design
    ├── architecture.md                    # System architecture
    ├── mvp2_technical_design.md           # Technical design for MVP2
    ├── project_plan.md                    # Project plan and roadmap
    ├── react_integration_guide.md         # Guide for React integration
    ├── security.md                        # Security documentation
    └── user_guides/                       # User documentation
        └── usage.md                       # Usage guide
```

## Implementation Plan for Structure Refactoring

1. **Create the Basic Directory Structure**:
   - Create `backend` and `frontend` directories
   - Move Python files to appropriate locations in `backend`
   - Set up empty structure for `frontend`

2. **Modularize the Backend**:
   - Split `app.py` into modular components
   - Organize code into appropriate packages (api, services, utils)
   - Move templates and static files to backend directory initially

3. **Set Up the Frontend**:
   - Create React application structure
   - Set up TypeScript and Tailwind CSS configuration
   - Implement the recommended directory structure for React

4. **Configure Build and Development Environment**:
   - Update scripts for development and production
   - Configure proxy for local development
   - Set up Flask to serve the React build in production

5. **Migrate Documentation**:
   - Organize documentation into appropriate categories
   - Move test scripts documentation to a more appropriate location
   - Update READMEs to reflect new structure

## Benefits of This Structure

1. **Clear Separation of Concerns**:
   - Frontend and backend code are clearly separated
   - Each component has a defined responsibility

2. **Modular Architecture**:
   - Backend functionality is organized by domain (auth, seeds, yubikeys)
   - Frontend is organized by feature and component type

3. **Improved Maintainability**:
   - Smaller, focused files are easier to maintain
   - Clear imports and dependencies make code easier to understand

4. **Better Testing Capabilities**:
   - Dedicated test directories for both frontend and backend
   - Organized structure makes unit testing easier

5. **Aligned with Project Evolution**:
   - Structure supports the planned migration to React frontend
   - Maintains backward compatibility during transition 