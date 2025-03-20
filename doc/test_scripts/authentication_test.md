# WebAuthn Authentication Test Script

This document provides step-by-step instructions for testing the WebAuthn authentication flow in the YubiKey Bitcoin Seed Storage application. The test is designed to verify that the YubiKey authentication process works correctly in different browsers.

## Prerequisites

- YubiKey 5 Series device
- Chrome browser (version 70+) and/or Safari browser (version 13+)
- YubiKey Bitcoin Seed Storage application running with HTTPS
- Chrome DevTools or Safari Web Inspector for monitoring network requests and console logs
- Successfully completed registration process with a User ID

## Test Environment Setup

1. Ensure the application is running:
   ```bash
   python app.py
   ```

2. Open Chrome or Safari and navigate to `https://localhost:5001`

3. Open the browser's developer tools:
   - Chrome: Press F12 or right-click and select "Inspect"
   - Safari: Enable Developer menu in Safari → Preferences → Advanced, then select Develop → Show Web Inspector

4. In Developer Tools, select the following tabs:
   - Network tab (to monitor HTTP requests)
   - Console tab (to view any JavaScript errors)
   - In Chrome, you can also navigate to `chrome://webauthn-internals` in a separate tab to monitor WebAuthn activity

5. Ensure you have a User ID from a previous successful registration. If not, complete the registration process first.

## Test Case 1: Basic Authentication Flow

### Test Steps (Chrome)

1. Click "Retrieve Seed" in the navigation menu or homepage
2. Enter the User ID obtained during registration
3. Click the "Authenticate with YubiKey" button
4. When prompted, ensure your YubiKey is connected
5. Touch your YubiKey when the light flashes
6. Observe the authentication success and subsequent seed phrase display

### Expected Results

- Browser should display a WebAuthn prompt for YubiKey interaction
- After touching the YubiKey, the page should redirect to the seed view page
- The seed phrase should be displayed on the screen
- No JavaScript errors should appear in the console
- Network requests should show:
  - POST request to `/begin-authentication` with 200 status
  - POST request to `/complete-authentication` with 200 status
  - GET request to `/view-seed` with 200 status

### Test Steps (Safari)

Repeat the same steps as for Chrome but in Safari browser.

## Test Case 2: Error Handling - Invalid User ID

### Test Steps

1. Navigate to the authentication page
2. Enter an invalid User ID (e.g., random UUID that doesn't exist in the system)
3. Click the "Authenticate with YubiKey" button

### Expected Results

- Application should display an error message indicating the User ID is invalid
- No WebAuthn prompt should appear
- Error should be logged in the console

## Test Case 3: Error Handling - No YubiKey Connected

### Test Steps

1. Disconnect your YubiKey from the computer
2. Navigate to the authentication page
3. Enter a valid User ID
4. Click the "Authenticate with YubiKey" button

### Expected Results

- Browser should display a WebAuthn error indicating no authenticator is available
- Application should display an appropriate error message
- Error should be logged in the console

## Test Case 4: Error Handling - Authentication Timeout

### Test Steps

1. Navigate to the authentication page
2. Enter a valid User ID
3. Click the "Authenticate with YubiKey" button
4. When prompted, do NOT touch the YubiKey for the duration of the timeout period (typically 60 seconds)

### Expected Results

- After the timeout period, the browser should cancel the WebAuthn operation
- Application should display a timeout error message
- Error should be logged in the console

## Test Case 5: Error Handling - Wrong YubiKey

### Test Steps

1. If available, use a different YubiKey than the one used for registration
2. Navigate to the authentication page
3. Enter a valid User ID
4. Click the "Authenticate with YubiKey" button
5. When prompted, touch the different YubiKey

### Expected Results

- Authentication should fail
- Application should display an error message indicating the YubiKey is not recognized
- Error should be logged in the console

## Test Case 6: Authentication with Browser JavaScript Console Logging

### Test Steps

1. Before starting the authentication process, add the following to the browser console:
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

2. Proceed with a normal authentication using a valid User ID

### Expected Results

- Detailed WebAuthn options and results should be logged to the console
- This information can be used to troubleshoot any issues with the authentication flow

## Test Case 7: Session Management - Seed Viewing

### Test Steps

1. Successfully authenticate with the YubiKey and view the seed phrase
2. Navigate away from the seed view page (e.g., click Home)
3. Attempt to return to the seed view page directly without re-authenticating

### Expected Results

- Session should properly track authentication state
- Application should either require re-authentication or allow seed viewing within the session timeout
- Behavior should be consistent with the application's security model

## Test Results Documentation

For each test case, document the following:

1. Browser version and operating system
2. Test case ID and description
3. Pass/Fail status
4. Any error messages encountered
5. Screenshots of key steps (if available)
6. Any unexpected behavior

## Troubleshooting Common Issues

### Chrome-Specific Issues

- If you see "The operation either timed out or was not allowed" error, ensure the YubiKey is properly connected and not being used by another application
- For "Security key not supported" errors, verify you're using a compatible YubiKey model
- Use `chrome://webauthn-internals` to see detailed diagnostics

### Safari-Specific Issues

- Safari may request permission to use the security key at the OS level
- If WebAuthn doesn't work, verify that you're using macOS 10.15+ and Safari 13+
- Check if Safari extensions or content blockers might be interfering

### General WebAuthn Issues

- WebAuthn requires HTTPS (except on localhost in some browsers)
- Some browsers cache WebAuthn credentials - try clearing browser cache if repeated tests behave unexpectedly
- YubiKey Manager application can be used to verify the YubiKey is functioning properly

## Completion Criteria

The authentication test is considered successful if:

1. All test cases pass in both Chrome and Safari
2. The application correctly handles both successful authentication and error cases
3. The seed phrase is correctly displayed after successful authentication
4. No unexpected errors occur in the JavaScript console
5. All network requests complete with appropriate status codes
6. Session management behaves as expected 