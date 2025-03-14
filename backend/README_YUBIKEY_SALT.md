# YubiKey Salt API

## Overview

The YubiKey Salt API is a critical component of our Bitcoin seed phrase storage solution. It provides a secure way to generate, store, and manage salts associated with YubiKey credentials, which are used for encrypting and decrypting Bitcoin seed phrases.

## Why YubiKey Salts?

We use a salt-based approach for several important security reasons:

1. **Physical Security**: By requiring the physical YubiKey to be present for both encryption and decryption, we ensure that even if the encrypted data is compromised, it cannot be decrypted without the physical device.

2. **No Key Storage**: The encryption key is never stored anywhere - it's derived on-demand when the YubiKey is present.

3. **Multiple Purposes**: A single YubiKey can have multiple salts for different purposes, allowing for isolation between different security domains.

4. **Revocation**: Individual salts can be revoked without affecting others, providing fine-grained control.

5. **Backup Support**: Multiple YubiKeys can be registered with different salts, allowing for backup devices.

## Architecture

The YubiKey Salt system consists of several components:

1. **YubiKeySalt Model**: Handles database operations for salt management
2. **YubiKey Salt API**: RESTful endpoints for salt management
3. **Client Utilities**: JavaScript utilities for salt management and encryption/decryption
4. **React Components**: UI components for salt management

## Key Concepts

### Salt Generation

Salts are generated using a cryptographically secure random number generator (`os.urandom(32)`). Each salt is 256 bits (32 bytes) in length, providing strong security against brute force attacks.

### Key Derivation

The encryption key is derived as follows:

1. The salt is combined with the credential ID to create a unique input
2. This input is signed by the YubiKey using WebAuthn
3. The resulting signature is used as the encryption key

This approach ensures that:
- The encryption key is never stored anywhere
- The YubiKey must be physically present to decrypt data
- Each YubiKey generates a unique key, even with the same salt

### Encryption

We use AES-256-GCM for authenticated encryption, which provides:
- Strong encryption (256-bit key)
- Authentication (tamper detection)
- Performance (hardware acceleration)

## Getting Started

### Prerequisites

- A registered YubiKey credential
- Authentication token for API access

### Basic Usage

#### 1. Register a Salt

```javascript
import { registerYubiKeySalt } from '../utils/yubikeySaltApi';

// Register a salt for a YubiKey credential
const result = await registerYubiKeySalt(credentialId, 'seed_encryption');
console.log(`Salt ID: ${result.salt_id}`);
console.log(`Salt: ${result.salt}`);
```

#### 2. Encrypt a Seed Phrase

```javascript
import { encryptSeedPhrase } from '../utils/seedEncryption';
import { getYubiKeySalt } from '../utils/yubikeySaltApi';

// Get the salt
const salt = await getYubiKeySalt(saltId);

// Encrypt the seed phrase
const encryptedSeed = await encryptSeedPhrase(
  seedPhrase,
  credentialId,
  salt.salt,
  signCallback // Function to sign data with the YubiKey
);
```

#### 3. Decrypt a Seed Phrase

```javascript
import { decryptSeedPhrase } from '../utils/seedEncryption';
import { getYubiKeySalt } from '../utils/yubikeySaltApi';

// Get the salt
const salt = await getYubiKeySalt(saltId);

// Decrypt the seed phrase
const decryptedSeed = await decryptSeedPhrase(
  encryptedSeed,
  credentialId,
  salt.salt,
  signCallback // Function to sign data with the YubiKey
);
```

## API Reference

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/yubikeys/register` | POST | Register a new YubiKey salt |
| `/api/v1/yubikeys/salts` | GET | Get all salts for a YubiKey credential |
| `/api/v1/yubikeys/salt/<salt_id>` | GET | Get a specific salt by ID |
| `/api/v1/yubikeys/salt/<salt_id>` | DELETE | Delete a specific salt |
| `/api/v1/yubikeys/generate-salt` | POST | Generate a random salt |

For detailed API documentation, see [YubiKey Salt API Documentation](./docs/yubikey_salt_api.md).

## Client Utilities

### yubikeySaltApi.js

Provides functions for interacting with the YubiKey Salt API:

- `registerYubiKeySalt(credentialId, purpose)`: Register a new salt
- `getYubiKeySalts(credentialId, purpose)`: Get all salts for a credential
- `getYubiKeySalt(saltId)`: Get a specific salt
- `deleteYubiKeySalt(saltId)`: Delete a salt
- `generateSalt()`: Generate a random salt
- `deriveEncryptionKey(credentialId, saltHex, signCallback)`: Derive an encryption key

### seedEncryption.js

Provides functions for encrypting and decrypting seed phrases:

- `encryptSeedPhrase(seedPhrase, credentialId, saltHex, signCallback)`: Encrypt a seed phrase
- `decryptSeedPhrase(encryptedHex, credentialId, saltHex, signCallback)`: Decrypt a seed phrase
- `generateRandomSeedPhrase(wordCount)`: Generate a random seed phrase (for testing)

## React Components

### YubiKeySaltManager

A component for managing YubiKey salts:

- Register new salts
- View existing salts
- Delete salts
- Generate random salts

### SeedPhraseEncryption

A component for encrypting and decrypting seed phrases:

- Select a salt
- Encrypt seed phrases
- Decrypt seed phrases
- Generate random seed phrases (for testing)

## Testing

The YubiKey Salt API includes comprehensive test coverage:

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test the API endpoints with a test database
- **End-to-End Tests**: Test the full flow from registration to encryption/decryption

To run the tests:

```bash
# Run unit tests
python -m unittest discover -s backend/tests/unit

# Run integration tests
python -m unittest discover -s backend/tests/integration
```

## Security Considerations

1. **Salt Storage**: Salts are stored in the database, but this is secure because the salt alone is not sufficient to derive the encryption key. The YubiKey's private key is also required, which never leaves the device.

2. **Key Derivation**: The key derivation process is secure because the YubiKey's private key never leaves the device, and WebAuthn includes origin validation to prevent phishing.

3. **Encryption**: AES-256-GCM provides strong encryption and authentication, and a unique IV is used for each encryption operation.

4. **API Security**: All endpoints require authentication, and input validation is performed to prevent injection attacks.

## Best Practices

1. **Multiple YubiKeys**: Register multiple YubiKeys as backups for critical seed phrases.

2. **Purpose Isolation**: Use different salt purposes for different types of data.

3. **Regular Testing**: Regularly test the decryption process to ensure you can recover your seed phrases.

4. **Secure Storage**: Ensure the database storing the salts is properly secured.

5. **Transport Security**: Always use HTTPS for API communication.

## Troubleshooting

### Common Issues

1. **Authentication Errors**: Ensure you have a valid authentication token.

2. **YubiKey Not Recognized**: Make sure the YubiKey is properly inserted and recognized by the browser.

3. **Encryption/Decryption Failures**: Verify that you're using the correct salt and credential ID.

4. **API Connection Issues**: Check your network connection and ensure the API server is running.

## Contributing

When contributing to the YubiKey Salt API, please follow these guidelines:

1. **Test-Driven Development**: Write tests before implementing features.

2. **Security First**: Always prioritize security in your design decisions.

3. **Documentation**: Update documentation when making changes.

4. **Code Style**: Follow the existing code style and conventions.

## Further Reading

- [YubiKey Salt API Documentation](./docs/yubikey_salt_api.md)
- [YubiKey Salt Technical Design](./docs/yubikey_salt_technical_design.md)
- [WebAuthn Specification](https://www.w3.org/TR/webauthn-2/)
- [AES-GCM Specification](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38d.pdf) 