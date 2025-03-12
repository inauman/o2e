# YubiKey Bitcoin Seed Storage: MVP2 Technical Design

## Overview

MVP2 enhances the YubiKey Bitcoin Seed Storage application with several key security and usability improvements:

1. **Multi-YubiKey Support**: Allow registration of multiple YubiKeys (up to 5) per user for redundancy
2. **AES-GCM Encryption**: Replace basic encoding with strong authenticated encryption
3. **SQLite Database**: Switch from file-based storage to a more robust database system
4. **Wizard-style Interface**: Guided user experience to reduce cognitive load

This document provides a detailed technical design for these enhancements.

## Database Design

### SQLite Schema

```sql
-- Users table
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    username TEXT,
    creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    max_yubikeys INTEGER DEFAULT 5
);

-- YubiKeys table
CREATE TABLE yubikeys (
    credential_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    public_key BLOB NOT NULL,
    aaguid TEXT,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    nickname TEXT,
    sign_count INTEGER DEFAULT 0,
    is_primary BOOLEAN DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Seeds table
CREATE TABLE seeds (
    seed_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    encrypted_seed BLOB NOT NULL,
    creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP,
    metadata TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Wrapped keys table
CREATE TABLE wrapped_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    credential_id TEXT NOT NULL,
    seed_id TEXT NOT NULL,
    wrapped_key BLOB NOT NULL,
    salt BLOB NOT NULL,
    key_wrapping_algorithm TEXT DEFAULT 'HKDF-SHA256+AES-256-GCM',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (credential_id) REFERENCES yubikeys(credential_id) ON DELETE CASCADE,
    FOREIGN KEY (seed_id) REFERENCES seeds(seed_id) ON DELETE CASCADE
);

-- Challenges table
CREATE TABLE challenges (
    user_id TEXT NOT NULL,
    challenge BLOB NOT NULL,
    creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expiry_date TIMESTAMP,
    PRIMARY KEY (user_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
```

### Connection Management

- Connection pooling to prevent database locking issues
- Transaction support for atomic operations
- Thread safety for concurrent access
- Auto-reconnection on failure

## Cryptographic Design

### Key Hierarchy

1. **Data Key (DK)**
   - 256-bit random key generated during seed creation
   - Used to encrypt seed with AES-256-GCM
   - Never stored directly, only in wrapped form

2. **Wrapping Key (WK)**
   - Derived per YubiKey using HKDF-SHA256
   - Input material: WebAuthn signature + hmac-secret output + salt
   - Used to encrypt (wrap) the Data Key

3. **Salt**
   - Unique 256-bit random value per YubiKey
   - Stored alongside wrapped key
   - Used as input to HKDF for wrapping key derivation

### Envelope Encryption Process

1. **Seed Encryption**:
   ```
   DK = random_bytes(32)  # Generate 256-bit Data Key
   nonce = random_bytes(12)  # Generate AES-GCM nonce
   ciphertext, tag = AES_GCM_Encrypt(key=DK, plaintext=seed, nonce=nonce)
   encrypted_seed = nonce || ciphertext || tag
   ```

2. **Key Wrapping** (for each YubiKey):
   ```
   salt = random_bytes(32)  # Unique per YubiKey
   
   # During WebAuthn authentication with hmac-secret extension
   signature = result of WebAuthn authentication
   device_secret = result of hmac-secret extension
   
   # Derive wrapping key
   WK = HKDF-SHA256(input_key_material=signature||device_secret, salt=salt, info="YubiKey Seed Storage Wrapping Key", length=32)
   
   # Wrap data key
   wrapped_key_nonce = random_bytes(12)
   wrapped_key, wrapped_key_tag = AES_GCM_Encrypt(key=WK, plaintext=DK, nonce=wrapped_key_nonce)
   wrapped_key_complete = wrapped_key_nonce || wrapped_key || wrapped_key_tag
   ```

3. **Seed Decryption**:
   ```
   # Authenticate with any registered YubiKey
   signature = result of WebAuthn authentication
   device_secret = result of hmac-secret extension
   
   # Retrieve salt and wrapped key for this YubiKey
   salt, wrapped_key_complete = retrieve_from_database()
   
   # Extract components
   wrapped_key_nonce = wrapped_key_complete[0:12]
   wrapped_key = wrapped_key_complete[12:-16]
   wrapped_key_tag = wrapped_key_complete[-16:]
   
   # Derive wrapping key
   WK = HKDF-SHA256(input_key_material=signature||device_secret, salt=salt, info="YubiKey Seed Storage Wrapping Key", length=32)
   
   # Unwrap data key
   DK = AES_GCM_Decrypt(key=WK, ciphertext=wrapped_key, nonce=wrapped_key_nonce, tag=wrapped_key_tag)
   
   # Decrypt seed
   encrypted_seed = retrieve_from_database()
   nonce = encrypted_seed[0:12]
   ciphertext = encrypted_seed[12:-16]
   tag = encrypted_seed[-16:]
   
   seed = AES_GCM_Decrypt(key=DK, ciphertext=ciphertext, nonce=nonce, tag=tag)
   ```

## FIDO2 hmac-secret Extension

### Extension Usage

The FIDO2 `hmac-secret` extension provides a way to derive deterministic secrets from a YubiKey:

1. **During Registration**:
   - Enable the `hmac-secret` extension in registration options
   ```javascript
   credentialCreationOptions.extensions = {
     hmacCreateSecret: true
   };
   ```

2. **During Authentication**:
   - Provide a salt value to get deterministic output
   ```javascript
   credentialRequestOptions.extensions = {
     hmacGetSecret: {
       salt1: new Uint8Array(32) // 32 bytes of salt
     }
   };
   ```

3. **Processing Result**:
   - Extract the secret from the authentication response
   ```javascript
   const secret = authenticationResponse.getClientExtensionResults().hmacGetSecret.output1;
   ```

### Security Properties

- Deterministic: Same salt will produce the same output for a given credential
- Device-bound: Secret is derived using device-specific keys
- No extraction: Secret derivation happens inside YubiKey's secure element
- Touch required: User must physically touch the YubiKey

## User Flow Design

### Wizard-style Interface with React & Tailwind

The wizard-style interface will be implemented using React for components and state management, with Tailwind CSS for styling. This allows for a modern, responsive, and maintainable UI.

1. **Initial Registration Flow**:
   - Welcome screen with explanation
   - Insert YubiKey prompt
   - Registration in progress indicator
   - Success confirmation
   - "Add backup YubiKey?" prompt

2. **Backup YubiKey Registration Flow**:
   - "Register backup YubiKey" screen (shows count: X/5)
   - Insert backup YubiKey prompt
   - Registration in progress indicator
   - Success confirmation
   - "Add another backup?" or "Continue" options

3. **Seed Management Flow**:
   - Create new seed or import existing
   - View registered YubiKeys
   - Success confirmation with recovery instructions
   - Secure display of seed with timeout

4. **Authentication Flow**:
   - "Insert any registered YubiKey" prompt
   - Authentication in progress indicator
   - Success confirmation
   - Secure access to seed or other protected resources

### Progressive Disclosure

- Information revealed gradually as needed
- Contextual help available throughout
- Clear visual indication of progress (e.g., "Step 2 of 4")
- Confirmation before critical operations

## Frontend Architecture

### React Component Hierarchy

```
App
├── WizardContainer
│   ├── WizardProgress
│   ├── WizardStep
│   │   ├── StepContent (varies by step)
│   │   ├── NavigationButtons
│   │   └── ContextualHelp
│   └── WizardFooter
├── YubiKeyRegistration
│   ├── RegistrationIntro
│   ├── YubiKeyPrompt
│   ├── RegistrationStatus
│   └── RegistrationSuccess
├── BackupRegistration
│   ├── BackupIntro
│   ├── YubiKeyList
│   ├── BackupPrompt
│   └── BackupSummary
├── SeedManagement
│   ├── SeedOptions
│   ├── YubiKeySelector
│   ├── SeedDisplay
│   └── RecoveryInstructions
└── Authentication
    ├── AuthPrompt
    ├── AuthStatus
    └── AuthSuccess
```

### State Management

React's built-in state management (useState, useContext) will be used for most state. For more complex state, we'll implement custom hooks:

1. **Wizard State Hook**:
   ```javascript
   const useWizardState = (steps) => {
     const [currentStep, setCurrentStep] = useState(0);
     const [stepData, setStepData] = useState({});
     
     // Navigation functions
     const nextStep = () => setCurrentStep(prev => Math.min(prev + 1, steps.length - 1));
     const prevStep = () => setCurrentStep(prev => Math.max(prev - 1, 0));
     const goToStep = (step) => setCurrentStep(step);
     
     // Data functions
     const updateStepData = (data) => setStepData(prev => ({...prev, ...data}));
     
     return {
       currentStep,
       stepData,
       nextStep,
       prevStep,
       goToStep,
       updateStepData,
       isFirstStep: currentStep === 0,
       isLastStep: currentStep === steps.length - 1
     };
   };
   ```

2. **YubiKey Management Hook**:
   ```javascript
   const useYubiKeyManager = () => {
     const [yubiKeys, setYubiKeys] = useState([]);
     const [registrationStatus, setRegistrationStatus] = useState('idle');
     
     // Functions for YubiKey operations
     const registerYubiKey = async () => {/* ... */};
     const listYubiKeys = async () => {/* ... */};
     const removeYubiKey = async (credentialId) => {/* ... */};
     
     return {
       yubiKeys,
       registrationStatus,
       registerYubiKey,
       listYubiKeys,
       removeYubiKey
     };
   };
   ```

### Styling with Tailwind CSS

All components will use Tailwind CSS for styling, with custom components created for consistent UI elements:

```javascript
// Button component example
const Button = ({ primary, children, onClick, disabled }) => (
  <button
    onClick={onClick}
    disabled={disabled}
    className={`px-4 py-2 rounded-md font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 ${
      primary
        ? 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500'
        : 'bg-gray-200 text-gray-800 hover:bg-gray-300 focus:ring-gray-500'
    } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
  >
    {children}
  </button>
);
```

## Flask and React Integration

### Backend API Structure

The Flask backend will expose RESTful APIs for the React frontend to consume:

1. **Authentication APIs**:
   - `/api/auth/begin-registration` - Start YubiKey registration
   - `/api/auth/complete-registration` - Complete YubiKey registration
   - `/api/auth/begin-authentication` - Start YubiKey authentication
   - `/api/auth/complete-authentication` - Complete YubiKey authentication

2. **YubiKey Management APIs**:
   - `/api/yubikeys` - CRUD operations for YubiKeys
   - `/api/yubikeys/:credentialId` - Operations on specific YubiKeys

3. **Seed Management APIs**:
   - `/api/seeds` - Operations for seed generation/retrieval
   - `/api/seeds/:seedId` - Operations on specific seeds

### Integration Strategy

1. **Flask as API Backend**:
   - Flask will serve the initial HTML page that loads the React application
   - All subsequent communication will be via JSON APIs
   - Authentication will be managed via secure HTTP-only cookies

2. **Proxy Configuration**:
   - During development, the React dev server will proxy API requests to Flask
   - In production, Flask will serve the compiled React build

3. **WebAuthn Integration**:
   - React will use the WebAuthn browser API directly
   - Challenge generation and verification will happen on the Flask backend
   - React will handle UI states (prompting, success, error)

## Implementation Plan

### Phase 1: Database Implementation
1. Design SQLite database schema 
2. Write comprehensive tests for database operations
3. Implement database connection manager class
4. Create schema initialization script (fresh start, no migration)
5. Implement CRUD operations with test validation
6. Add transaction support and error handling

### Phase 2: Encryption Implementation
1. Write tests for key derivation and AES-GCM operations
2. Create key derivation functions
3. Implement AES-256-GCM encryption/decryption
4. Create envelope encryption utilities
5. Add integrity verification for encrypted data
6. Implement secure key handling in memory

### Phase 3: Multi-YubiKey Support
1. Update WebAuthn registration flow
2. Implement hmac-secret extension handling
3. Create YubiKey management interface
4. Add credential listing and selection
5. Implement credential revocation

### Phase 4: React UI Implementation
1. Set up React development environment with Tailwind CSS
2. Create reusable component library for wizard interface
3. Implement core wizard container and navigation
4. Develop individual wizard steps for each flow
5. Add form validation and state management
6. Integrate with Flask backend APIs
7. Implement responsive design for all screens

### Phase 5: App Modernization & Modularization
1. Refactor Flask backend into modular components
2. Create clean API layer for frontend communication
3. Implement service layer for database and business logic
4. Apply domain-driven design for cryptographic operations
5. Standardize error handling across frontend and backend

## Security Considerations

### Key Protection
- Data Key (DK) only exists in memory during encryption/decryption
- Wrapping Keys (WK) derived on-demand and never stored
- AES-GCM provides authentication and encryption

### Database Security
- Connection string and credentials protected
- Prepared statements to prevent SQL injection
- Input validation for all database operations

### User Experience Considerations
- Clear error messages without exposing sensitive details
- No timeout bypass possibilities
- Confirmation for destructive operations

## Testing Strategy

1. **Unit Testing**:
   - Test each cryptographic function
   - Validate database operations
   - Test UI component behavior

2. **Integration Testing**:
   - End-to-end encryption/decryption tests
   - Multi-YubiKey registration and authentication
   - Database migration testing

3. **Security Testing**:
   - Attempt key recovery without YubiKey
   - Test against known cryptographic vulnerabilities
   - Database security verification

4. **Usability Testing**:
   - Test with users of varying technical expertise
   - Validate wizard flow understanding
   - Verify error message clarity

## Development Approach

### Test-Driven Development (TDD)

MVP2 will employ Test-Driven Development to ensure robust implementation:

1. **AES-GCM Testing Priority**:
   - Begin with tests for AES-GCM encryption/decryption
   - Test vectors will include NIST-approved test cases
   - Tests will cover: key generation, encryption, decryption, authentication failures

2. **TDD Workflow**:
   - Write failing tests that define expected behavior
   - Implement minimal code to make tests pass
   - Refactor for clarity and optimization
   - Repeat for each feature

3. **Test Coverage Goals**:
   - Cryptographic operations: 100% coverage
   - Database operations: 90%+ coverage
   - UI components: 80%+ coverage
   - End-to-end flows: Cover all critical paths

### Modular Architecture

The MVP2 implementation will follow these architectural principles:

1. **Package Structure**:
   ```
   /app
     /crypto - Cryptographic operations
       /tests
     /data - Database and storage
       /tests
     /auth - WebAuthn and YubiKey operations
       /tests
     /ui - User interface components
       /tests
     /utils - Shared utilities
       /tests
   ```

2. **Dependency Management**:
   - Clear separation between layers
   - Dependency injection for testability
   - Interface-based design

3. **Refactoring Guidelines**:
   - Classes should not exceed 300-400 lines
   - Methods should not exceed 50 lines
   - Extract utility functions for reusable operations
   - Use design patterns where appropriate (Factory, Strategy, etc.)

By following these development practices, MVP2 will maintain high code quality while efficiently implementing the planned features.

### React and Tailwind Development Workflow

1. **Component-First Development**:
   - Design and implement reusable components first
   - Create a storybook-like environment for component testing
   - Build pages by composing these components

2. **Responsive Design Strategy**:
   - Mobile-first approach using Tailwind breakpoints
   - Testing on multiple device sizes during development
   - Accessibility considerations built in from the start

3. **API Integration**:
   - Mock APIs during initial frontend development
   - Gradual replacement with real backend endpoints
   - End-to-end testing of complete flows

4. **State Management Evolution**:
   - Start with React's built-in state management
   - Evaluate complexity thresholds for introducing additional state management
   - Use custom hooks to encapsulate complex logic

## Conclusion

The MVP2 technical design enhances the security and usability of the YubiKey Bitcoin Seed Storage application through proper encryption, multiple YubiKey support, and improved user experience. The wizard-style interface guides users through complex security operations while maintaining strong cryptographic guarantees through envelope encryption and the use of the FIDO2 hmac-secret extension. 