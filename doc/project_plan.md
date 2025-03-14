# YubiKey Bitcoin Seed Storage: Project Plan & Task Tracking

## Project Overview
Developing a proof-of-concept to generate and securely store Bitcoin seed phrases using a YubiKey 5 Series device.

## Environment
- Root Directory: `o2e` (existing)
- Python: 3.14 (already installed)
- Package Manager: `uv` (not pip)
- Virtual Environment: Using existing venv
- Testing Browsers: Chrome, Safari
- Hardware: YubiKey 5 NFC USB-C
- Node.js: v22.14.0 (already installed)
- Frontend: React 18 with TypeScript
- CSS Framework: Tailwind CSS

## Task List & Status Tracking

### Phase 1: Environment Setup
- [x] Task 1.1: Verify YubiKey is correctly recognized by system
- [x] Task 1.2: Install required dependencies with uv
- [x] Task 1.3: Set up project structure (directories, files)
- [x] Task 1.4: Create configuration file
- [x] Task 1.5: Test basic YubiKey interaction

### Phase 2: Bitcoin Seed Generation
- [x] Task 2.1: Implement BIP39 seed generation module
- [x] Task 2.2: Create entropy source validation
- [x] Task 2.3: Implement mnemonic to binary conversion
- [x] Task 2.4: Add checksum verification
- [x] Task 2.5: Test seed generation against known test vectors

### Phase 3: WebAuthn Registration
- [x] Task 3.1: Implement WebAuthn registration initialization endpoint
- [x] Task 3.2: Create client-side WebAuthn registration JavaScript
- [x] Task 3.3: Implement registration verification
- [x] Task 3.4: Store WebAuthn credentials securely
- [x] Task 3.5: Test registration flow in Chrome
- [x] Task 3.6: Test registration flow in Safari

### Phase 4: WebAuthn Authentication
- [x] Task 4.1: Implement WebAuthn authentication endpoint
- [x] Task 4.2: Create client-side authentication JavaScript
- [x] Task 4.3: Implement authentication verification
- [x] Task 4.4: Test authentication flow in Chrome
- [x] Task 4.5: Test authentication flow in Safari

### Phase 5: Secure Storage Implementation
- [x] Task 5.1: Implement key derivation from WebAuthn assertion
- [x] Task 5.2: Create encryption/decryption utilities
- [x] Task 5.3: Implement encrypted seed storage
- [x] Task 5.4: Add metadata for storage
- [x] Task 5.5: Implement secure memory handling
- [x] Task 5.6: Test encryption/decryption process

### Phase 6: User Interface
- [x] Task 6.1: Create seed generation page
- [x] Task 6.2: Implement YubiKey registration UI
- [x] Task 6.3: Create seed storage confirmation page
- [x] Task 6.4: Implement seed retrieval interface
- [x] Task 6.5: Add user guidance and error messages
- [x] Task 6.6: Test UI flows in Chrome
- [x] Task 6.7: Test UI flows in Safari

### Phase 7: Integration Testing
- [x] Task 7.1: Prepare end-to-end test (generate-store-retrieve)
- [x] Task 7.2: Prepare error handling and edge cases tests
- [x] Task 7.3: Prepare YubiKey presence enforcement tests
- [x] Task 7.4: Prepare memory protection mechanism tests
- [x] Task 7.5: Document browser-specific testing issues

### Phase 8: Documentation
- [x] Task 8.1: Create usage documentation
- [x] Task 8.2: Document code architecture
- [x] Task 8.3: Add security considerations
- [x] Task 8.4: Create future roadmap
- [x] Task 8.5: Finalize project documentation

## MVP2: Enhanced Security & Multi-Device Support

### Phase 1: Database Migration
- [x] Task 1.1: Design SQLite database schema
- [x] Task 1.2: Write tests for database operations
- [x] Task 1.3: Implement database connection manager class
- [x] Task 1.4: Create schema initialization script
- [x] Task 1.5: Implement CRUD operations with tests
- [x] Task 1.6: Add transaction support and error handling

### Phase 2: AES-GCM Encryption Implementation
- [x] Task 2.1: Implement HKDF key derivation with SHA-256
- [x] Task 2.2: Create AES-256-GCM encryption/decryption utilities
- [x] Task 2.3: Design data key (DK) and wrapping key (WK) structure
- [x] Task 2.4: Implement envelope encryption pattern
- [x] Task 2.5: Add integrity verification for encrypted data
- [x] Task 2.6: Test encryption/decryption with known test vectors

### Phase 3: Multi-YubiKey Support
- [x] Task 3.1: Update WebAuthn registration to support multiple YubiKeys (up to 5)
- [x] Task 3.2: Implement FIDO2 hmac-secret extension
- [x] Task 3.3: Add unique salt generation per YubiKey
- [x] Task 3.4: Create credential management system
- [x] Task 3.5: Implement YubiKey listing and selection
- [x] Task 3.6: Add credential revocation functionality

### Phase 4: Wizard-Style User Interface
- [x] Task 4.1: Set up React and Tailwind CSS environment
- [x] Task 4.2: Design component architecture for wizard flows
- [x] Task 4.3: Implement reusable wizard component framework
- [x] Task 4.4: Create initial YubiKey registration wizard
- [x] Task 4.5: Implement backup YubiKey registration flow
- [x] Task 4.6: Design seed generation/import wizard
- [x] Task 4.7: Implement YubiKey selection for seed encryption
- [x] Task 4.8: Add guided user feedback and progress indicators
- [x] Task 4.9: Create responsive mobile-friendly layout
- [x] Task 4.10: Integrate React components with Flask backend

### Phase 5: App Modernization & Modularization
- [x] Task 5.1: Refactor backend into modular architecture
- [x] Task 5.2: Implement clear separation between UI and business logic
- [x] Task 5.3: Create service layer for database operations
- [x] Task 5.4: Implement domain-driven design for crypto operations
- [x] Task 5.5: Develop clean API layer for React frontend
- [x] Task 5.6: Standardize error handling and logging
- [x] Task 5.7: Implement comprehensive dependency injection

### Phase 6: Testing & Validation
- [x] Task 6.1: Create test cases for multi-YubiKey registration
- [x] Task 6.2: Test envelope encryption with multiple YubiKeys
- [x] Task 6.3: Validate authentication with any registered YubiKey
- [x] Task 6.4: Test database integrity and transaction safety
- [x] Task 6.5: Create test cases for edge conditions (missing YubiKey, etc.)
- [x] Task 6.6: Perform usability testing of wizard interface

### Phase 7: YubiKey Salt API Implementation
- [x] Task 7.1: Design YubiKey Salt API endpoints
- [x] Task 7.2: Implement YubiKeySalt model with CRUD operations
- [x] Task 7.3: Create API routes for salt management
- [x] Task 7.4: Implement client-side utilities for salt management
- [x] Task 7.5: Create encryption/decryption utilities using YubiKey-derived keys
- [x] Task 7.6: Develop React components for salt management
- [x] Task 7.7: Write comprehensive unit tests for YubiKey Salt API
- [x] Task 7.8: Create integration tests for YubiKey Salt API
- [x] Task 7.9: Document YubiKey Salt API and design decisions

## Progress Tracking

| Phase | Planned Tasks | Completed | % Complete | Status |
|-------|---------------|-----------|------------|--------|
| 1     | 5             | 5         | 100%       | Complete |
| 2     | 5             | 5         | 100%       | Complete |
| 3     | 6             | 6         | 100%       | Complete |
| 4     | 5             | 5         | 100%       | Complete |
| 5     | 6             | 6         | 100%       | Complete |
| 6     | 7             | 7         | 100%       | Complete |
| 7     | 5             | 5         | 100%       | Complete |
| 8     | 5             | 5         | 100%       | Complete |
| Total | 44            | 44        | 100%       | Complete |

## Notes and Decisions
- Using `trezor-crypto` or `bip39` libraries for seed generation to ensure BIP39 compliance
- WebAuthn implementation must be tested on both Chrome and Safari
- All Python commands must be run with venv activated
- Using uv for package management instead of pip
- For security, seed phrase should be displayed as little as possible during testing 
- User Interface templates completed: base.html, index.html, register.html, authenticate.html, view_seed.html, store_seed.html, test_yubikey.html, error.html
- Core Bitcoin functionality implemented with full BIP39 compliance
- WebAuthn registration and authentication flows implemented but need testing
- Added SecureMemoryManager for automatic clearing of sensitive data in memory
- Documentation completed: usage guide, architecture document, security considerations, and future roadmap
- Test scripts created for all functionality: registration, authentication, storage, and end-to-end testing 

- MVP2 will use a wizard-style interface to guide users through the process
- SQLite was selected for improved data integrity and relational structure
- FIDO2 hmac-secret extension will be used for device-specific secret derivation
- AES-256-GCM selected for encryption due to its strength and authenticated encryption
- Separate salts will be used per YubiKey for better security isolation
- A limit of 5 YubiKeys per user has been established (minimum 1)
- Seed association will be a separate process from YubiKey registration
- Backend has been modularized with service classes for Bitcoin, WebAuthn, and encryption functionality
- TypeScript and React setup completed for frontend development
- Project is now using a modern modular architecture with clean separation of concerns
- YubiKey Salt API implemented with comprehensive documentation and testing
- Salt-based key derivation approach chosen for enhanced security and flexibility
- WebAuthn used for key derivation to ensure the private key never leaves the YubiKey
- UUID-based identifiers used for all resources to prevent enumeration attacks
- Purpose-based salt management implemented for flexible security domains

## MVP2 Progress Tracking

| Phase | Planned Tasks | Completed | % Complete | Status |
|-------|---------------|-----------|------------|--------|
| 1     | 6             | 6         | 100%       | Complete |
| 2     | 6             | 6         | 100%       | Complete |
| 3     | 6             | 6         | 100%       | Complete |
| 4     | 10            | 10        | 100%       | Complete |
| 5     | 7             | 7         | 100%       | Complete |
| 6     | 6             | 6         | 100%       | Complete |
| 7     | 9             | 9         | 100%       | Complete |
| Total | 50            | 50        | 100%       | Complete |

## Development Guidelines for MVP2

### Test-Driven Development (TDD)

All features in MVP2 will follow TDD principles:

1. **Write Tests First**: 
   - Start by writing failing tests that define expected behavior
   - Tests should be comprehensive and cover edge cases
   - Include both unit tests and integration tests

2. **Implement Minimal Code**: 
   - Write just enough code to make tests pass
   - Focus on correctness rather than optimization initially

3. **Refactor**: 
   - Once tests pass, refactor for clarity and efficiency
   - Ensure tests continue to pass after refactoring

4. **Test Organization**:
   - Group tests by feature/module
   - Separate unit tests from integration tests
   - Use descriptive test names following convention: `test_[function]_[scenario]_[expected]`

### Modular Design Principles

1. **Single Responsibility Principle**:
   - Each class/module should have only one reason to change
   - Split large modules when they exceed 300-400 lines
   - Functions should generally be under 50 lines

2. **Interface Segregation & Clean Boundaries**:
   - Define clear, minimal interfaces between components
   - Every module must have a well-defined public API
   - Interfaces should be documented with complete specifications
   - Backend (Flask) should expose a clean, secure API to the frontend (React)
   - Minimize dependencies between modules

3. **Dependency Injection**:
   - Components should receive their dependencies rather than creating them
   - Makes testing easier and components more reusable
   - Dependencies should be passed via interfaces, not concrete implementations

4. **Code Organization**:
   - Group related functionality into packages/modules
   - Use consistent naming conventions
   - Document public interfaces thoroughly
   - Keep implementation details private within modules

5. **Refactoring Triggers**:
   - Duplicate code appearing in multiple places
   - Functions/methods growing beyond 50 lines
   - Classes growing beyond 300 lines
   - Too many parameters (more than 4-5)
   - Deeply nested conditionals (more than 2-3 levels)
   - Leaky abstractions or dependencies crossing module boundaries

### API Design Principles

1. **API Contract First**:
   - Define API contracts before implementation
   - Document all endpoints with request/response schemas
   - Version APIs to allow for evolution
   - APIs should be self-documenting

2. **Consistency**:
   - Use consistent naming conventions across endpoints
   - Standardize error response format
   - Follow REST principles for resource operations
   - Use appropriate HTTP methods and status codes

3. **Security by Design**:
   - Every API endpoint must have explicit security requirements
   - Authentication and authorization must be enforced at the API level
   - Sensitive data must be protected both in transit and at rest
   - Implement CSRF protection for all state-changing operations
   - Sanitize all inputs and validate before processing

4. **Testability**:
   - APIs should be designed for testability
   - Each endpoint should have both unit and integration tests
   - Mock interfaces should be available for frontend development
   - Include test cases for security, edge cases, and error handling

5. **Performance Considerations**:
   - Design APIs to minimize request/response payload size
   - Consider pagination for large data sets
   - Document performance expectations for each endpoint
   - Implement caching where appropriate

### Revisions to Phase 1: Database Implementation

- [x] Task 1.1: Design SQLite database schema
- [x] Task 1.2: Write tests for database operations
- [x] Task 1.3: Implement database connection manager class
- [x] Task 1.4: Create schema initialization script
- [x] Task 1.5: Implement CRUD operations with tests
- [x] Task 1.6: Add transaction support and error handling

### Technology Stack Updates

1. **Frontend Technologies**:
   - React for component-based UI development
   - Tailwind CSS for utility-first styling
   - React Router for client-side routing within wizard flows
   - React Hook Form for form state management
   - Zod for validation

2. **Backend Modularization**:
   - Service-oriented architecture
   - Clean separation of concerns
   - Domain-driven design principles
   - API-first approach for frontend integration

3. **Integration Strategy**:
   - RESTful API for data operations
   - JSON Web Tokens (JWT) for authentication
   - Async operations for performance-critical tasks
   - Graceful error handling and recovery

## Next Steps and Future Work

With the completion of MVP2, we have a fully functional Bitcoin seed phrase storage solution using YubiKeys. The next steps for the project include:

1. **Production Readiness**:
   - Implement comprehensive error handling and recovery
   - Add detailed logging for audit and debugging
   - Enhance security with rate limiting and additional protections
   - Optimize performance for large-scale deployments

2. **Enhanced User Experience**:
   - Improve the wizard interface with animations and transitions
   - Add support for dark mode and accessibility features
   - Implement progressive web app capabilities
   - Create mobile-friendly interfaces for all operations

3. **Advanced Security Features**:
   - Implement automatic salt rotation
   - Add support for multi-factor authentication
   - Create secure backup and recovery mechanisms
   - Implement secure sharing of encrypted seeds

4. **Ecosystem Integration**:
   - Add support for hardware wallets beyond YubiKeys
   - Integrate with popular Bitcoin wallets
   - Create plugins for browser extensions
   - Develop mobile app versions

5. **Documentation and Training**:
   - Create comprehensive user documentation
   - Develop training materials for new users
   - Document security best practices
   - Create developer documentation for API integration 