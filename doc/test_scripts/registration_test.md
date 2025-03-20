# WebAuthn Registration Test Script

This document provides step-by-step instructions for testing the WebAuthn registration flow in the YubiKey Bitcoin Seed Storage application. The test is designed to verify that the YubiKey registration process works correctly in different browsers.

## Prerequisites

- YubiKey 5 Series device
- Chrome browser (version 70+) and/or Safari browser (version 13+)
- YubiKey Bitcoin Seed Storage application running with HTTPS
- Chrome DevTools or Safari Web Inspector for monitoring network requests and console logs

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

## Test Case 1: Basic Registration Flow

### Test Steps (Chrome)

1. Click "Register" in the navigation menu or homepage
2. Enter a username (e.g., "testuser1")
3. Click the "Register YubiKey" button
4. When prompted, ensure your YubiKey is connected
5. Touch your YubiKey when the light flashes
6. Observe the registration success message and note the User ID

### Expected Results

- Browser should display a WebAuthn prompt for YubiKey interaction
- After touching the YubiKey, the page should display a success message
- A User ID should be generated and displayed
- No JavaScript errors should appear in the console
- Network requests should show:
  - POST request to `/begin-registration` with 200 status
  - POST request to `/complete-registration` with 200 status

### Test Steps (Safari)

Repeat the same steps as for Chrome but in Safari browser.

## Test Case 2: Error Handling - No YubiKey Connected

### Test Steps

1. Disconnect your YubiKey from the computer
2. Navigate to the registration page
3. Enter a username (e.g., "testuser2")
4. Click the "Register YubiKey" button

### Expected Results

- Browser should display a WebAuthn error indicating no authenticator is available
- Application should display an appropriate error message
- Error should be logged in the console

## Test Case 3: Error Handling - Registration Timeout

### Test Steps

1. Navigate to the registration page
2. Enter a username (e.g., "testuser3")
3. Click the "Register YubiKey" button
4. When prompted, do NOT touch the YubiKey for the duration of the timeout period (typically 60 seconds)

### Expected Results

- After the timeout period, the browser should cancel the WebAuthn operation
- Application should display a timeout error message
- Error should be logged in the console

## Test Case 4: Username Validation

### Test Steps

1. Navigate to the registration page
2. Try registering with:
   - Empty username
   - Very long username (100+ characters)
   - Username with special characters

### Expected Results

- Application should enforce username validation rules
- Appropriate error messages should be displayed for invalid usernames
- No JavaScript errors should occur

## Test Case 5: Registration with Browser JavaScript Console Logging

### Test Steps

1. Before starting the registration process, add the following to the browser console:
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

2. Proceed with a normal registration (username "testuser5")

### Expected Results

- Detailed WebAuthn options and results should be logged to the console
- This information can be used to troubleshoot any issues with the registration flow

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

The registration test is considered successful if:

1. All test cases pass in both Chrome and Safari
2. The application correctly handles both successful registration and error cases
3. The User ID is correctly generated and can be used for subsequent authentication
4. No unexpected errors occur in the JavaScript console
5. All network requests complete with appropriate status codes 