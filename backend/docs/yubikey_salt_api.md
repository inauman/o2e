# YubiKey Salt API Documentation

This document describes the API endpoints for managing YubiKey salts, which are used for encrypting Bitcoin seed phrases.

## Overview and Design Decisions

The YubiKey Salt API is designed to support secure encryption of Bitcoin seed phrases using YubiKeys. The implementation follows these key design principles:

1. **Salt-based Key Derivation**: Each YubiKey credential can have multiple salts associated with it. These salts are used to derive unique encryption keys for different purposes, enhancing security through isolation.

2. **Separation of Concerns**: The salt management is separate from the actual encryption/decryption process, allowing for flexible key management.

3. **Stateless Design**: The API is designed to be stateless, with all necessary information passed in requests or stored in the database.

4. **Security First**: All endpoints require authentication, and sensitive data (like salts) are stored securely in the database.

5. **Flexible Purpose Support**: Salts can be created for different purposes (e.g., seed encryption, metadata encryption), allowing for fine-grained access control.

## Implementation Details

### Salt Generation and Storage

- Salts are generated using a cryptographically secure random number generator (`os.urandom(32)`)
- Each salt is 256 bits (32 bytes) in length, providing strong security
- Salts are stored in the database in binary format but returned to clients in hexadecimal format
- Each salt has a unique UUID identifier

### Key Derivation Process

The encryption key derivation process works as follows:

1. A salt is retrieved from the database for a specific YubiKey credential
2. The salt is combined with the credential ID to create a unique input
3. This input is signed by the YubiKey using WebAuthn
4. The resulting signature is used as the encryption key
5. AES-256-GCM is used for authenticated encryption

This approach ensures that:
- The encryption key is never stored anywhere
- The YubiKey must be physically present to decrypt data
- Each YubiKey generates a unique key, even with the same salt
- The encryption is resistant to tampering (authenticated encryption)

## Authentication

All endpoints require authentication using a Bearer token:

```
Authorization: Bearer <token>
```

## Endpoints

### Register a YubiKey Salt

Register a new YubiKey by storing a salt associated with its credential ID.

**URL**: `/api/v1/yubikeys/register`

**Method**: `POST`

**Request Body**:
```json
{
    "credential_id": "string",  // The credential ID of the YubiKey
    "purpose": "string"         // Optional: The purpose of the salt (default: "seed_encryption")
}
```

**Response**:
```json
{
    "success": true,
    "salt_id": "string",
    "salt": "hex_string"        // The salt in hexadecimal format
}
```

**Status Codes**:
- `201 Created`: Salt successfully created
- `400 Bad Request`: Missing or invalid parameters
- `401 Unauthorized`: Authentication required
- `500 Internal Server Error`: Server error

### Get YubiKey Salts

Get all salts associated with a YubiKey credential ID.

**URL**: `/api/v1/yubikeys/salts`

**Method**: `GET`

**Query Parameters**:
- `credential_id`: The credential ID of the YubiKey
- `purpose`: Optional filter by purpose

**Response**:
```json
{
    "success": true,
    "salts": [
        {
            "salt_id": "string",
            "credential_id": "string",
            "salt": "hex_string",
            "creation_date": "ISO date string",
            "last_used": "ISO date string or null",
            "purpose": "string"
        },
        ...
    ]
}
```

**Status Codes**:
- `200 OK`: Salts retrieved successfully
- `400 Bad Request`: Missing credential ID
- `401 Unauthorized`: Authentication required
- `500 Internal Server Error`: Server error

### Get a Specific YubiKey Salt

Get a specific salt by its ID.

**URL**: `/api/v1/yubikeys/salt/<salt_id>`

**Method**: `GET`

**Path Parameters**:
- `salt_id`: The ID of the salt to retrieve

**Response**:
```json
{
    "success": true,
    "salt": {
        "salt_id": "string",
        "credential_id": "string",
        "salt": "hex_string",
        "creation_date": "ISO date string",
        "last_used": "ISO date string or null",
        "purpose": "string"
    }
}
```

**Status Codes**:
- `200 OK`: Salt retrieved successfully
- `401 Unauthorized`: Authentication required
- `404 Not Found`: Salt not found
- `500 Internal Server Error`: Server error

### Delete a YubiKey Salt

Delete a specific salt by its ID.

**URL**: `/api/v1/yubikeys/salt/<salt_id>`

**Method**: `DELETE`

**Path Parameters**:
- `salt_id`: The ID of the salt to delete

**Response**:
```json
{
    "success": true
}
```

**Status Codes**:
- `200 OK`: Salt deleted successfully
- `401 Unauthorized`: Authentication required
- `404 Not Found`: Salt not found
- `500 Internal Server Error`: Server error

### Generate a Random Salt

Generate a new random salt without associating it with a YubiKey.

**URL**: `/api/v1/yubikeys/generate-salt`

**Method**: `POST`

**Response**:
```json
{
    "success": true,
    "salt": "hex_string"
}
```

**Status Codes**:
- `200 OK`: Salt generated successfully
- `401 Unauthorized`: Authentication required
- `500 Internal Server Error`: Server error

## Client-Side Integration

The API is designed to be used with the provided client-side utilities:

1. `yubikeySaltApi.js`: Provides functions for interacting with the YubiKey Salt API
2. `seedEncryption.js`: Provides functions for encrypting and decrypting seed phrases using YubiKey-derived keys

These utilities handle:
- API communication
- Salt management
- Key derivation
- Encryption/decryption using the Web Crypto API

## Security Considerations

1. **Salt Rotation**: Consider implementing salt rotation policies for long-term security
2. **Multiple YubiKeys**: Register multiple YubiKeys as backups for critical seed phrases
3. **Purpose Isolation**: Use different salt purposes for different types of data
4. **Secure Storage**: Ensure the database storing the salts is properly secured
5. **Transport Security**: Always use HTTPS for API communication

## Usage Examples

### Register a YubiKey Salt

```bash
curl -X POST \
  https://example.com/api/v1/yubikeys/register \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "credential_id": "abcdef1234567890",
    "purpose": "seed_encryption"
}'
```

### Get YubiKey Salts

```bash
curl -X GET \
  'https://example.com/api/v1/yubikeys/salts?credential_id=abcdef1234567890' \
  -H 'Authorization: Bearer <token>'
```

### Get a Specific YubiKey Salt

```bash
curl -X GET \
  https://example.com/api/v1/yubikeys/salt/12345678-1234-1234-1234-123456789012 \
  -H 'Authorization: Bearer <token>'
```

### Delete a YubiKey Salt

```bash
curl -X DELETE \
  https://example.com/api/v1/yubikeys/salt/12345678-1234-1234-1234-123456789012 \
  -H 'Authorization: Bearer <token>'
```

### Generate a Random Salt

```bash
curl -X POST \
  https://example.com/api/v1/yubikeys/generate-salt \
  -H 'Authorization: Bearer <token>'
```

## Testing

The API includes comprehensive test coverage:

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test the API endpoints with a test database
3. **End-to-End Tests**: Test the full flow from registration to encryption/decryption

## Future Enhancements

1. **Salt Rotation API**: Add endpoints for rotating salts while preserving access to encrypted data
2. **Batch Operations**: Support for batch registration and management of salts
3. **Enhanced Metadata**: Add support for additional metadata on salts
4. **Audit Logging**: Implement detailed audit logging for salt operations 