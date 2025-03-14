# YubiKey Salt System: Technical Design Document

## Overview

The YubiKey Salt System is a critical component of our Bitcoin seed phrase storage solution. It enables secure encryption and decryption of seed phrases using YubiKeys, ensuring that the seed phrases can only be accessed when the physical YubiKey is present.

## Architecture

The system follows a layered architecture:

1. **Database Layer**: Stores YubiKey credentials and associated salts
2. **Model Layer**: Provides object-oriented access to the database
3. **API Layer**: Exposes RESTful endpoints for salt management
4. **Client Utilities Layer**: Provides JavaScript utilities for encryption/decryption

### Component Diagram

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  React Frontend │────▶│  YubiKey Salt   │────▶│  SQLite         │
│  Components     │◀────│  API            │◀────│  Database       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Client         │     │  YubiKeySalt    │     │  Database       │
│  Utilities      │     │  Model          │     │  Manager        │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Key Design Decisions

### 1. Salt-Based Key Derivation

We chose to use a salt-based key derivation approach for several reasons:

- **No Key Storage**: The encryption key is never stored anywhere, not even in memory for longer than necessary
- **Physical Security**: The YubiKey must be physically present to derive the key
- **Multiple Keys**: Different salts can be used for different purposes with the same YubiKey
- **Key Isolation**: Each YubiKey generates a unique key, even with the same salt

### 2. WebAuthn for Key Derivation

We leverage the WebAuthn standard for key derivation because:

- **Industry Standard**: WebAuthn is a W3C standard supported by all major browsers
- **Hardware Binding**: The private key never leaves the YubiKey
- **Anti-Phishing**: WebAuthn includes origin validation
- **User Verification**: Can require user presence or verification (PIN/biometric)

### 3. AES-256-GCM for Encryption

We selected AES-256-GCM for encryption because:

- **Strong Security**: AES-256 provides strong security against brute force attacks
- **Authenticated Encryption**: GCM mode provides authentication, preventing tampering
- **Performance**: AES is hardware-accelerated on most platforms
- **Web Crypto API**: Supported by the Web Crypto API in all modern browsers

### 4. UUID-Based Identifiers

We use UUIDs for all identifiers (salt_id, credential_id) because:

- **No Collisions**: Virtually eliminates the risk of ID collisions
- **No Sequential IDs**: Prevents enumeration attacks
- **Globally Unique**: Works across distributed systems

### 5. Purpose-Based Salt Management

We support multiple salts per YubiKey with different purposes:

- **Isolation**: Different encryption domains can use different salts
- **Granular Control**: Salts can be revoked individually without affecting others
- **Flexible Usage**: Supports different security requirements for different data

## Database Schema

The YubiKey salts are stored in the `yubikey_salts` table:

```sql
CREATE TABLE yubikey_salts (
    salt_id TEXT PRIMARY KEY,
    credential_id TEXT NOT NULL,
    salt BLOB NOT NULL,
    creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP,
    purpose TEXT DEFAULT 'seed_encryption',
    FOREIGN KEY (credential_id) REFERENCES yubikeys(credential_id) ON DELETE CASCADE
)
```

Key aspects of this schema:

- **salt_id**: UUID primary key
- **credential_id**: Foreign key to the YubiKey credentials table
- **salt**: Binary blob containing the random salt (32 bytes)
- **creation_date**: When the salt was created
- **last_used**: When the salt was last used (for auditing)
- **purpose**: The intended purpose of the salt

## Key Derivation Process

The key derivation process works as follows:

1. **Salt Retrieval**: The salt is retrieved from the database
2. **Data Preparation**: The salt is combined with the credential ID
3. **WebAuthn Signing**: The combined data is signed by the YubiKey
4. **Key Extraction**: The signature is used directly as the encryption key

```javascript
// Pseudocode for key derivation
async function deriveKey(credentialId, salt, yubikey) {
  const dataToSign = concatenate(credentialId, salt);
  const signature = await yubikey.sign(dataToSign);
  return signature; // Used as encryption key
}
```

## Encryption Process

The encryption process uses the Web Crypto API:

1. **Key Derivation**: Derive the key as described above
2. **IV Generation**: Generate a random initialization vector
3. **Encryption**: Encrypt the data using AES-256-GCM
4. **Combination**: Combine the IV and ciphertext for storage

```javascript
// Pseudocode for encryption
async function encrypt(data, key) {
  const iv = randomBytes(12);
  const cryptoKey = await importKey(key);
  const ciphertext = await crypto.subtle.encrypt(
    { name: 'AES-GCM', iv, tagLength: 128 },
    cryptoKey,
    data
  );
  return concatenate(iv, ciphertext);
}
```

## Decryption Process

The decryption process is the reverse of encryption:

1. **Key Derivation**: Derive the key as described above
2. **IV Extraction**: Extract the IV from the stored data
3. **Decryption**: Decrypt the data using AES-256-GCM

```javascript
// Pseudocode for decryption
async function decrypt(encryptedData, key) {
  const iv = encryptedData.slice(0, 12);
  const ciphertext = encryptedData.slice(12);
  const cryptoKey = await importKey(key);
  const plaintext = await crypto.subtle.decrypt(
    { name: 'AES-GCM', iv, tagLength: 128 },
    cryptoKey,
    ciphertext
  );
  return plaintext;
}
```

## API Design

The API follows RESTful principles:

- **Resource-Based**: Each endpoint represents a resource (salt, salts)
- **Standard Methods**: Uses standard HTTP methods (GET, POST, DELETE)
- **JSON Responses**: All responses are in JSON format
- **Status Codes**: Uses appropriate HTTP status codes
- **Error Handling**: Consistent error response format

## Security Considerations

### 1. Salt Storage

Salts are stored in the database, but this is secure because:

- The salt alone is not sufficient to derive the encryption key
- The YubiKey's private key is also required, which never leaves the device
- The database should be properly secured with access controls

### 2. Key Derivation

The key derivation process is secure because:

- The YubiKey's private key never leaves the device
- WebAuthn includes origin validation to prevent phishing
- The derived key is never stored persistently

### 3. Encryption

The encryption process is secure because:

- AES-256-GCM provides strong encryption and authentication
- A unique IV is used for each encryption operation
- The authentication tag prevents tampering

### 4. API Security

The API is secured through:

- Authentication required for all endpoints
- HTTPS for all communications
- Input validation to prevent injection attacks
- Rate limiting to prevent brute force attacks

## Testing Strategy

The system includes comprehensive testing:

1. **Unit Tests**: Test individual components in isolation
   - YubiKeySalt model
   - API endpoints
   - Client utilities

2. **Integration Tests**: Test the interaction between components
   - API endpoints with database
   - Client utilities with API

3. **End-to-End Tests**: Test the complete flow
   - Registration to encryption to decryption

## Performance Considerations

The system is designed for good performance:

- **Database Indexing**: Indexes on credential_id and salt_id
- **Connection Pooling**: Database connection pooling
- **Caching**: No sensitive data is cached
- **Asynchronous Operations**: Client-side operations are asynchronous

## Future Enhancements

1. **Salt Rotation**: Implement automatic salt rotation for long-term security
2. **Multi-Device Support**: Enhance support for multiple YubiKeys per user
3. **Recovery Mechanisms**: Add secure recovery options
4. **Audit Logging**: Add detailed audit logging for security events
5. **Performance Optimizations**: Further optimize for large-scale deployments

## Conclusion

The YubiKey Salt System provides a secure and flexible foundation for encrypting Bitcoin seed phrases. By leveraging the security of YubiKeys and the WebAuthn standard, combined with strong encryption and careful system design, we've created a solution that ensures seed phrases can only be accessed when the physical YubiKey is present. 