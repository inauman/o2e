# Secure Storage and Encryption Test Script

This document provides step-by-step instructions for testing the secure storage and encryption/decryption functionality in the YubiKey Bitcoin Seed Storage application. The test is designed to verify that the seed phrases are properly encrypted, stored, and can be retrieved with the YubiKey.

## Prerequisites

- YubiKey 5 Series device
- Chrome browser (version 70+) or Safari browser (version 13+)
- YubiKey Bitcoin Seed Storage application running with HTTPS
- Browser's developer tools for monitoring network requests and console logs
- Successfully completed registration process with a User ID

## Test Environment Setup

1. Ensure the application is running:
   ```bash
   python app.py
   ```

2. Open your browser and navigate to `https://localhost:5000`

3. Open the browser's developer tools (F12 or right-click and select "Inspect")

4. Ensure you have access to the application's data directory to examine stored files

## Test Case 1: Seed Storage & Encryption Process

### Test Steps

1. Before beginning, locate and open the data files:
   ```
   data/credentials.json     # Contains WebAuthn credentials
   data/encrypted_seeds.json # Contains encrypted seed phrases
   ```

2. Take note of the current contents of these files

3. Navigate to the application homepage and generate a new seed phrase

4. Complete the YubiKey registration process with a username (e.g., "storagetest1")

5. Examine the files again and note the changes:
   - `credentials.json` should have a new entry with the user ID and credential information
   - `encrypted_seeds.json` should have a new entry with the user ID and encrypted seed data

### Expected Results

- New entries should be added to both files
- The seed phrase should be stored in encoded/encrypted form, not plaintext
- The credential ID in `credentials.json` should match what's referenced in `encrypted_seeds.json`
- Metadata such as creation time should be present

## Test Case 2: Seed Retrieval & Decryption Process

### Test Steps

1. Using the User ID from Test Case 1, navigate to the authentication page

2. Authenticate with the YubiKey

3. Observe that the seed phrase is correctly displayed

4. In the browser console, examine the network traffic for:
   - Authentication request/response
   - Seed retrieval request/response

### Expected Results

- The displayed seed phrase should match the original seed phrase
- Network responses should contain encoded/encrypted data, not plaintext seed phrases
- Decryption should happen client-side after authentication

## Test Case 3: Secure Memory Handling

### Test Steps

1. Successfully authenticate and view a seed phrase

2. Open a new browser tab and navigate to another site

3. Return to the application tab

4. Navigate to the seed view page without re-authenticating

5. After the configured timeout period (default 60 seconds):
   - Try to access the seed view page again

### Expected Results

- The seed phrase should be available within the session timeout
- After timeout, the seed phrase should no longer be accessible without re-authentication
- The application should clearly indicate when a seed has been cleared from memory

## Test Case 4: Multiple Seed Storage

### Test Steps

1. Register a new YubiKey with a different username (e.g., "storagetest2")

2. Generate and store a new seed phrase with this registration

3. Authenticate with each User ID in separate sessions and verify:
   - Each User ID retrieves the correct corresponding seed phrase
   - Seeds are not mixed up between users

### Expected Results

- Each User ID should be associated with the correct seed phrase
- Authenticating with one User ID should not give access to another user's seed phrase
- Storage files should maintain separation of user data

## Test Case 5: Data Persistence

### Test Steps

1. After storing at least two different seed phrases:

2. Restart the application:
   ```bash
   # Ctrl+C to stop, then
   python app.py
   ```

3. Authenticate with each User ID and verify that the correct seed phrases are still retrievable

### Expected Results

- Seed phrases should persist across application restarts
- Authentication should still work after application restart
- No data corruption or mixing between users

## Test Case 6: Encryption Verification

### Test Steps

1. Examine the `encrypted_seeds.json` file

2. For a User ID with a known seed phrase:
   - Copy the encrypted seed data
   - In a separate terminal or Python script, attempt to decode it:
     ```python
     import base64
     encoded_data = "PASTE_ENCODED_DATA_HERE"
     decoded = base64.b64decode(encoded_data)
     print(decoded)
     ```

### Expected Results

- Base64 decoding alone should not reveal the seed phrase
- This verifies that additional security measures (beyond simple encoding) are in place
  
## Test Case 7: Storage Format Verification

### Test Steps

1. Examine the structure of both storage files:
   - `credentials.json`
   - `encrypted_seeds.json`

2. Verify that they contain the expected fields:
   - User IDs
   - Credential IDs
   - Public key data
   - Encrypted seed data
   - Metadata (creation time, etc.)

### Expected Results

- Files should have a consistent, well-structured format
- All necessary data for authentication and decryption should be present
- No sensitive data should be stored in plaintext

## Test Results Documentation

For each test case, document the following:

1. Test case ID and description
2. Pass/Fail status
3. Any error messages encountered
4. Before/after snippets of the data files (with sensitive information redacted)
5. Any unexpected behavior

## Troubleshooting Common Issues

### Storage Issues

- If seed phrases can't be retrieved, check file permissions on the data directory
- Verify that the JSON files are properly formatted and not corrupted
- Check for disk space issues if storage operations fail

### Encryption Issues

- If decryption fails, verify that the same YubiKey is being used
- Check for browser compatibility issues with the WebAuthn implementation
- Examine console logs for any cryptographic operation errors

### Memory Management Issues

- If seeds remain accessible after timeout, check the secure memory timeout configuration
- If seeds are cleared too quickly, adjust the timeout settings in the configuration
- Verify that session management is working correctly

## Completion Criteria

The secure storage and encryption test is considered successful if:

1. All test cases pass
2. Seed phrases are properly encrypted at rest
3. Only authenticated users with the correct YubiKey can decrypt their seed phrases
4. Secure memory management properly clears sensitive data
5. Data persistence works across application restarts
6. No security vulnerabilities are identified in the storage mechanism 