# YubiKey Bitcoin Seed Storage POC: Architecture

## System Overview

This proof-of-concept demonstrates the use of YubiKeys for Bitcoin seed phrase storage through WebAuthn. The system allows users to generate or import Bitcoin seed phrases, register YubiKeys for authentication, and encrypt/decrypt the seed phrases using YubiKey-backed credentials.

## Core Components

### 1. Bitcoin Seed Management (`bitcoin_utils.py`)

The Bitcoin seed management component handles:
- Generation of BIP39 seed phrases with configurable entropy
- Validation of seed phrases against BIP39 standards
- Conversion between mnemonic phrases and binary seeds
- Secure memory handling for sensitive seed data

**Key Classes & Functions:**
- `BitcoinSeedManager`: Main class for handling seed operations
  - `generate_seed()`: Creates a cryptographically secure random seed
  - `validate_mnemonic()`: Verifies a seed phrase against BIP39 standards
  - `mnemonic_to_seed()`: Converts a mnemonic to a binary seed
  - `secure_erase()`: Securely clears sensitive data from memory

### 2. YubiKey WebAuthn Integration (`yubikey_utils.py`)

The WebAuthn component handles:
- Registration of YubiKeys as WebAuthn authenticators
- Authentication using registered YubiKeys
- Storage and retrieval of WebAuthn credentials
- Challenge-response verification

**Key Classes & Functions:**
- `WebAuthnManager`: Manages WebAuthn operations
  - `generate_registration_options_for_user()`: Creates options for registering a new YubiKey
  - `verify_registration_response()`: Validates registration responses
  - `generate_authentication_options()`: Creates options for authenticating with a YubiKey
  - `verify_authentication_response()`: Validates authentication responses

### 3. Web Application (`app.py`)

The Flask web application ties everything together:
- Provides HTTP endpoints for WebAuthn operations
- Handles seed generation, storage, and retrieval
- Manages secure storage of encrypted seeds
- Provides user interface for all operations

**Key Components:**
- `SecureMemoryManager`: Handles secure storage with automatic clearing
- Flask routes for various operations:
  - `/generate-seed`: Generates a new seed phrase
  - `/register`: YubiKey registration
  - `/authenticate`: YubiKey authentication
  - `/view-seed`: Displays the seed after authentication

### 4. User Interface (`templates/`)

The user interface consists of HTML templates with embedded JavaScript for:
- WebAuthn credential creation and verification
- Seed phrase display and management
- YubiKey interaction guidance
- Error handling and feedback

## Data Flow

### Registration Flow

1. User generates a new seed phrase or imports an existing one
2. System temporarily stores the seed in the secure memory manager
3. User initiates YubiKey registration
4. Browser calls `navigator.credentials.create()` to register the YubiKey
5. Server verifies the registration response
6. If valid, the seed is encrypted and stored with the YubiKey's credential ID
7. A User ID is provided to the user for later authentication

```
┌──────┐   1. Generate/Import Seed   ┌──────────────────┐
│ User ├─────────────────────────────► Bitcoin Utilities │
└──┬───┘                             └──────────┬───────┘
   │                                            │
   │                                            ▼
   │                                  ┌──────────────────┐
   │ 2. Initiate Registration         │ Secure Memory    │
   ├─────────────────────────────────► Manager           │
   │                                  └──────────┬───────┘
   │                                            │
   │                                            ▼
   │                                  ┌──────────────────┐
   │ 3. Register YubiKey             │ WebAuthn Manager  │
   ├─────────────────────────────────► (Registration)    │
   │                                  └──────────┬───────┘
   │                                            │
   │                                            ▼
   │ 4. Store Encrypted Seed          ┌──────────────────┐
   └─────────────────────────────────►│ Storage System   │
                                      └──────────────────┘
```

### Authentication Flow

1. User provides their User ID
2. Server generates authentication options for the YubiKey
3. Browser calls `navigator.credentials.get()` to authenticate with the YubiKey
4. Server verifies the authentication response
5. If valid, the encrypted seed is retrieved and decrypted
6. The seed is temporarily stored in secure memory and displayed to the user
7. Seed is automatically cleared from memory after a timeout

```
┌──────┐   1. Submit User ID         ┌──────────────────┐
│ User ├─────────────────────────────► WebAuthn Manager  │
└──┬───┘                             │ (Authentication) │
   │                                  └──────────┬───────┘
   │                                            │
   │                                            ▼
   │ 2. Authenticate with YubiKey    ┌──────────────────┐
   ├─────────────────────────────────► Storage System   │
   │                                  └──────────┬───────┘
   │                                            │
   │                                            ▼
   │ 3. View Seed Phrase             ┌──────────────────┐
   └─────────────────────────────────► Secure Memory    │
                                      │ Manager         │
                                      └──────────────────┘
```

## Security Model

### Threat Model

The system protects against:
1. **Unauthorized access to seed phrases**: Only someone with the registered YubiKey can access the stored seed
2. **Seed phrase exposure**: Minimized through secure memory handling and timeouts
3. **Brute force attacks**: WebAuthn's cryptographic security prevents credential forging

### Security Layers

1. **WebAuthn Security**:
   - Requires physical possession of the registered YubiKey
   - Uses public key cryptography for authentication
   - Requires user verification (touch) on the YubiKey
   - Based on origin-bound credentials (phishing resistant)

2. **Seed Protection**:
   - Seed phrases are encrypted at rest (albeit with simple encoding in this POC)
   - In memory, seeds are cleared automatically after a timeout
   - Secure memory manager prevents long-term exposure of sensitive data

3. **Transport Security**:
   - All WebAuthn operations require HTTPS
   - Challenges and responses use cryptographic verification

## Storage Architecture

### Database Schema

The application uses a SQLite database with the following tables:

- **users**: Stores user information
  - `user_id`: Unique identifier (TEXT PRIMARY KEY)
  - `email`: User's email (TEXT UNIQUE NOT NULL)
  - `created_at`: Timestamp of user creation (TIMESTAMP)
  - `last_login`: Timestamp of last login (TIMESTAMP)
  - `max_yubikeys`: Maximum number of YubiKeys allowed for this user (INTEGER DEFAULT 5)

- **yubikeys**: Stores WebAuthn credentials
  - `credential_id`: Base64-encoded credential ID (TEXT PRIMARY KEY)
  - `user_id`: Foreign key to users table (TEXT NOT NULL)
  - `public_key`: Public key blob (BLOB NOT NULL)
  - `sign_count`: Current signature counter (INTEGER DEFAULT 0)
  - `aaguid`: Authenticator attestation GUID (TEXT)
  - `nickname`: User-assigned nickname for the YubiKey (TEXT NOT NULL)
  - `is_primary`: Whether this is the primary YubiKey (BOOLEAN DEFAULT 0)
  - `created_at`: Timestamp of credential creation (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
  - `last_used`: Timestamp of last use (TIMESTAMP)

- **yubikey_salts**: Stores salt values for key derivation
  - `salt_id`: Unique identifier (TEXT PRIMARY KEY)
  - `credential_id`: Associated credential ID (TEXT NOT NULL)
  - `salt`: Random salt value (BLOB NOT NULL)
  - `purpose`: Purpose of this salt (TEXT NOT NULL DEFAULT 'seed_encryption')
  - `creation_date`: Timestamp of salt creation (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
  - `last_used`: Timestamp of last use (TIMESTAMP)
  - Foreign key relationship to yubikeys.credential_id

- **seeds**: Stores encrypted seed phrases
  - `seed_id`: Unique identifier (TEXT PRIMARY KEY)
  - `user_id`: Foreign key to users table (TEXT NOT NULL)
  - `wrapped_seed`: Encrypted seed phrase (BLOB NOT NULL)
  - `created_at`: Timestamp of seed creation (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
  - `last_used`: Timestamp of last access (TIMESTAMP)

- **wrapped_keys**: Stores wrapped encryption keys
  - `key_id`: Unique identifier (TEXT PRIMARY KEY)
  - `user_id`: Foreign key to users table (TEXT NOT NULL)
  - `yubikey_id`: Foreign key to yubikeys table (TEXT NOT NULL)
  - `wrapped_key`: Encrypted key material (BLOB NOT NULL)
  - `created_at`: Timestamp of key creation (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
  - `last_used`: Timestamp of last use (TIMESTAMP)
  - Foreign key relationships to users.user_id and yubikeys.credential_id

### Security Considerations

- Database file permissions are restricted
- All sensitive data is encrypted at rest
- Foreign key constraints ensure data integrity
- Automatic cleanup of expired/revoked data
- Regular database backups recommended

## Deployment Model

For this proof-of-concept:
- Single-server deployment
- SQLite database for all data storage
- Self-signed HTTPS certificate
- Local browser-based interaction

In a production environment, additional considerations would include:
- Scalable database system (e.g., PostgreSQL)
- Hardware security modules for key management
- Properly signed TLS certificates
- Backup and disaster recovery mechanisms

## Limitations and Future Enhancements

1. **Current Limitations**:
   - Simple encoding instead of proper encryption
   - File-based storage not suitable for production
   - No backup or recovery mechanism
   - Limited error handling

2. **Potential Enhancements**:
   - Proper key derivation from WebAuthn attestation
   - Strong encryption using AES-GCM or similar
   - Database storage with proper security measures
   - Multiple YubiKey registration (backup keys)
   - Multi-signature support for enhanced security
   - Integration with actual Bitcoin wallet software 