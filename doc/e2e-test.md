# YubiKey Bitcoin Seed Storage Testing Guide

Great! I'm glad you have Chrome installed and your YubiKey 5 NFC C plugged in. Let's go through the testing process step by step, following our test scripts in the recommended order.

## Prerequisites

- YubiKey device plugged in
- Chrome browser with Developer Tools
- Backend server running
- Node.js installed (for running example scripts)

## Test Data Setup

Directly inspecting or modifying the database is not recommended as it could compromise security. Instead, use the application APIs for all interactions. For testing, you can:

1. Reset the application state by deleting the database file and restarting the application
2. Use the API endpoints to register YubiKeys and generate seeds

## SQLite Database

The application uses a SQLite database for storage. The database file is located at:

- `yubikey_storage.db` 

## Test Sequence

All the functional tests will primarily involve the browser interacting with the application through the UI. However, for debugging and testing purposes, we might need to monitor the requests and responses at the network level.

## Preparation Steps

1. First, make sure the application is running:
   ```bash
   python app.py
   ```

2. Open Chrome and navigate to `https://localhost:5001`

3. Open Chrome DevTools by pressing F12 or right-clicking and selecting "Inspect"

4. For enhanced WebAuthn debugging, open a separate Chrome tab and navigate to:
   ```
   chrome://webauthn-internals/
   ```
   This special page will show all WebAuthn operations in detail.

## Test 1: WebAuthn Registration Testing

Let's start with testing the registration flow:

1. **Basic Registration Flow**:
   - Click "Register" in the navigation menu or homepage
   - Enter a username (e.g., "testuser1")
   - Click the "Register YubiKey" button
   - When prompted, ensure your YubiKey is connected
   - Touch your YubiKey when the light flashes
   - Verify you see a success message and note the User ID (you'll need this later)

2. **Error Handling Tests**:
   - Try registering with an empty username - verify you get validation error
   - Disconnect your YubiKey, try to register a new user "testuser2", and observe the error
   - Reconnect your YubiKey and start registration but don't touch it for 60 seconds - verify timeout behavior

3. **Debug Logging**:
   - In Chrome DevTools Console, paste this code to enable detailed WebAuthn logging:
   ```javascript
   navigator.credentials.create = new Proxy(navigator.credentials.create, {
     apply: function(target, thisArg, args) {
       console.log('WebAuthn create() called with options:', JSON.stringify(args[0], null, 2));
       return Reflect.apply(target, thisArg, args).then(credential => {
         console.log('WebAuthn create() result:', credential);
         return credential;
       }).catch(error => {
         console.error('WebAuthn create() error:', error);
         throw error;
       });
     }
   });
   ```
   - Register one more user (e.g., "testuser3") and observe the detailed WebAuthn logs

## Test 2: WebAuthn Authentication Testing

Now that you have registered at least one user ID, let's test authentication:

1. **Basic Authentication Flow**:
   - Click "Retrieve Seed" in the navigation
   - Enter the User ID you noted from the registration step
   - Click "Authenticate with YubiKey"
   - Touch your YubiKey when prompted
   - Verify you can see the seed phrase

2. **Error Handling Tests**:
   - Try authenticating with an invalid User ID
   - Disconnect your YubiKey and try authenticating with a valid User ID
   - Try authenticating but don't touch the YubiKey for 60 seconds

3. **Debug Logging**:
   - In Chrome DevTools Console, paste this code to enable authentication logging:
   ```javascript
   navigator.credentials.get = new Proxy(navigator.credentials.get, {
     apply: function(target, thisArg, args) {
       console.log('WebAuthn get() called with options:', JSON.stringify(args[0], null, 2));
       return Reflect.apply(target, thisArg, args).then(credential => {
         console.log('WebAuthn get() result:', credential);
         return credential;
       }).catch(error => {
         console.error('WebAuthn get() error:', error);
         throw error;
       });
     }
   });
   ```
   - Authenticate again and observe the detailed logs

4. **Session Management**:
   - Successfully authenticate and view the seed phrase
   - Navigate away to the home page
   - Try to return to the seed view page directly without re-authenticating
   - Wait for the timeout period (60 seconds) and try again

## Test 3: Secure Storage and Encryption Testing

Let's verify the secure storage functionality:

1. **Examine Storage Files**:
   - Look at the contents of these files before proceeding:
     - `data/credentials.json`
     - `data/encrypted_seeds.json`
   - Take note of the current entries

2. **Generate and Store a New Seed**:
   - Navigate to the home page and generate a new seed
   - Register a new YubiKey with username "storagetest1"
   - Store the seed
   - Check the files again and observe the new entries

3. **Verify Data Protection**:
   - Copy the encrypted seed data from `encrypted_seeds.json`
   - Try to decode it with base64 to verify protection:
   ```python
   import base64
   encoded_data = "PASTE_ENCODED_DATA_HERE"
   decoded = base64.b64decode(encoded_data)
   print(decoded)
   ```
   - Verify that the plaintext seed is not visible

4. **Test Data Persistence**:
   - Restart the application (Ctrl+C then run again)
   - Authenticate with your User ID
   - Verify you can still retrieve the seed

## Test 4: End-to-End Testing

Now let's run through complete workflows:

1. **Complete Workflow Test**:
   - Generate a new seed
   - Note the displayed preview (first few and last few words)
   - Register with username "e2etest1"
   - Store the seed
   - Log out
   - Authenticate with the User ID
   - Verify the seed matches what you noted earlier

2. **Import Workflow Test**:
   - Navigate to the home page
   - Choose to import an existing seed
   - Use this test seed phrase: "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
   - Register with username "e2etest2"
   - Store the seed
   - Log out
   - Authenticate and verify the imported seed is displayed correctly

3. **Error Recovery Tests**:
   - Try importing an invalid seed phrase (e.g., random words)
   - Start a registration but reload the page mid-process
   - Verify the application recovers gracefully

## Recording Test Results

For each test case, document:
1. Whether it passed or failed
2. Any error messages encountered
3. Screenshots of key steps if possible
4. Any unexpected behavior

## Troubleshooting Tips

If you encounter issues:
- Check if the YubiKey is properly connected
- Look at the chrome://webauthn-internals/ page for detailed diagnostics
- Review browser console for JavaScript errors
- Verify the application is running with HTTPS
- Try clearing your browser cache if you see unexpected behaviors

When you complete all tests, you'll have validated the entire functionality of the YubiKey Bitcoin Seed Storage application. Would you like to start with a specific test, or do you need more details on any particular testing area?
