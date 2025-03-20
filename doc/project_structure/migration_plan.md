# Migration Plan: Restructuring the YubiKey Bitcoin Seed Storage Project

This document outlines the step-by-step process to migrate from the current project structure to the recommended modular structure with separate frontend and backend components.

## Phase 1: Preparation and Initial Setup (1-2 days)

### 1.1 Create New Directory Structure
```bash
# Create main directories
mkdir -p backend/api
mkdir -p backend/services
mkdir -p backend/models
mkdir -p backend/utils
mkdir -p backend/tests/unit
mkdir -p backend/tests/integration
mkdir -p frontend/src/components/{common,layouts,forms}
mkdir -p frontend/src/pages/{Home,Registration,Authentication,SeedManagement}
mkdir -p frontend/src/{hooks,services/api,services/webauthn,types,utils}
mkdir -p frontend/tests
mkdir -p doc/user_guides
```

### 1.2 Create Package Initialization Files
```bash
# Create __init__.py files for Python packages
touch backend/api/__init__.py
touch backend/services/__init__.py
touch backend/models/__init__.py
touch backend/utils/__init__.py
```

### 1.3 Create Configuration Files
```bash
# Create configuration files
touch backend/pyproject.toml
touch frontend/package.json
touch frontend/tsconfig.json
touch frontend/tailwind.config.js
```

## Phase 2: Backend Restructuring (2-3 days)

### 2.1 Move Backend Files

1. Copy `app.py` to `backend/app.py` and refactor as needed
2. Move utility files:
   ```bash
   cp bitcoin_utils.py backend/utils/bitcoin_utils.py
   cp yubikey_utils.py backend/utils/security.py
   # etc.
   ```
3. Move templates and static directories:
   ```bash
   cp -r templates backend/templates
   cp -r static backend/static
   ```
4. Move data directory (or create symlinks if needed):
   ```bash
   cp -r data data.bak  # Backup
   # Either move or create symlinks depending on your workflow
   ```

### 2.2 Split `app.py` Into Modular Components

1. Create API route files:
   ```bash
   # Extract auth endpoints to auth.py
   # Extract seed management endpoints to seeds.py
   # Extract yubikey endpoints to yubikeys.py
   ```

2. Create service files:
   ```bash
   # Extract Bitcoin operations to bitcoin_service.py
   # Extract WebAuthn operations to webauthn_service.py
   # Extract encryption operations to encryption_service.py
   ```

3. Update imports and references across files

### 2.3 Refactor Main App

Update `backend/app.py` to import from the new modules:

```python
from api.auth import auth_bp
from api.seeds import seeds_bp
from api.yubikeys import yubikeys_bp

app = Flask(__name__)
app.register_blueprint(auth_bp)
app.register_blueprint(seeds_bp)
app.register_blueprint(yubikeys_bp)
```

### 2.4 Migrate Configuration

1. Extract configuration to `config.yaml`
2. Update the code to load configuration from this file

## Phase 3: Frontend Setup (3-4 days)

### 3.1 Initialize React Project

```bash
# Navigate to frontend directory
cd frontend

# Initialize React project with TypeScript
npx create-react-app . --template typescript

# Install additional dependencies
npm install tailwindcss postcss autoprefixer axios
npm install -D @types/webauthn-json
```

### 3.2 Configure Build Tools

1. Set up Tailwind CSS:
   ```bash
   npx tailwindcss init -p
   ```

2. Configure proxy for local development in `package.json`:
   ```json
   "proxy": "http://localhost:5001"
   ```

### 3.3 Create Initial Component Structure

1. Set up base components based on the existing templates
2. Create API service layer for communicating with the backend
3. Implement WebAuthn utilities for client-side WebAuthn operations

## Phase 4: Integration and Testing (3-5 days)

### 4.1 Set Up Development Environment

1. Create development scripts:
   ```bash
   # In project root
   touch dev.sh
   ```

2. Script content:
   ```bash
   #!/bin/bash
   # Start backend
   cd backend && python app.py &
   BACKEND_PID=$!
   
   # Start frontend
   cd ../frontend && npm start &
   FRONTEND_PID=$!
   
   # Handle shutdown
   function cleanup {
     kill $BACKEND_PID
     kill $FRONTEND_PID
     exit 0
   }
   
   trap cleanup SIGINT
   wait
   ```

### 4.2 Update Backend to Serve the React App

Modify `backend/app.py` to serve the React app in production:

```python
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join('static', path)):
        return send_from_directory('static', path)
    return send_from_directory('static', 'index.html')
```

### 4.3 Set Up Tests

1. Migrate existing tests to the new structure
2. Create new tests for the modular components
3. Set up frontend unit tests with Jest

## Phase 5: Documentation Update (1-2 days)

### 5.1 Update READMEs

1. Update the main `README.md` with new setup instructions
2. Create/update component-specific documentation

### 5.2 Move Documentation Files

1. Reorganize documentation:
   ```bash
   # Move files to appropriate locations
   mv doc/test_scripts/* backend/tests/
   ```

### 5.3 Create Development Guides

1. Create a guide for developers on how to work with the new structure
2. Document API interfaces for frontend-backend communication

## Phase 6: Deployment Preparation (1-2 days)

### 6.1 Create Production Build Scripts

```bash
# In project root
touch build.sh
```

Script content:
```bash
#!/bin/bash
# Build frontend
cd frontend && npm run build

# Copy build to backend static directory
rm -rf ../backend/static/*
cp -r build/* ../backend/static/
```

### 6.2 Update Deployment Documentation

1. Update deployment documentation with new build and deployment steps
2. Create Docker configuration if necessary

## Phase 7: Testing and Final Adjustments (2-3 days)

### 7.1 End-to-End Testing

1. Test the complete application flow
2. Ensure all features work with the new structure
3. Validate API interfaces

### 7.2 Performance Optimization

1. Optimize API responses
2. Minimize frontend bundle size
3. Implement caching where appropriate

### 7.3 Final Review and Documentation Update

1. Review the entire codebase
2. Update documentation with any final changes
3. Create a post-migration summary

## Timeline

Total estimated time: **13-21 days**

- Phase 1: 1-2 days
- Phase 2: 2-3 days
- Phase 3: 3-4 days
- Phase 4: 3-5 days
- Phase 5: 1-2 days
- Phase 6: 1-2 days
- Phase 7: 2-3 days

## Mitigation Strategies

- **Backup**: Create full backups before starting migration
- **Parallel Development**: Maintain the old structure until the new one is fully tested
- **Phased Approach**: Roll out changes gradually, starting with backend restructuring
- **Rollback Plan**: Document steps to roll back in case of critical issues 