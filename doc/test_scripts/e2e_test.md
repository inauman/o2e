# End-to-End Test Script

This document provides step-by-step instructions for conducting end-to-end testing of the YubiKey Bitcoin Seed Storage application. The test covers the entire workflow from seed generation to storage and retrieval.

## Prerequisites

- YubiKey 5 Series device
- Chrome browser (version 70+) or Safari browser (version 13+)
- YubiKey Bitcoin Seed Storage application running with HTTPS
- Browser's developer tools for monitoring network requests and console logs

## Test Environment Setup

1. Ensure the application is running:
   ```bash
   python app.py
   ```

2. Open your browser and navigate to `https://localhost:5000`

3. Open the browser's developer tools (F12 or right-click and select "Inspect")

4. If testing for the first time, ensure the data files are in a clean state:
   ```bash
   # Optional: Backup existing data files
   mkdir -p data/backup
   cp data/credentials.json data/backup/ 2>/dev/null || echo "No credentials file to backup"
   cp data/encrypted_seeds.json data/backup/ 2>/dev/null || echo "No encrypted seeds file to backup"
   
   # Create empty files
   echo "{}" > data/credentials.json
   echo "{}" > data/encrypted_seeds.json
   ```

## Test Scenario 1: Complete Workflow - Generate, Store, Retrieve

### Test Steps

1. **Generate Seed**
   - Navigate to the application homepage
   - Click "Generate New Seed"
   - Verify a seed preview is displayed (first and last few words)
   - Take note of the visible portions of the seed phrase for later verification

2. **Register YubiKey**
   - Click "Register YubiKey to Store This Seed"
   - Enter a username (e.g., "e2etest1")
   - Click "Register YubiKey"
   - When prompted, insert and touch your YubiKey
   - Once registration is complete, note the User ID provided

3. **Store Seed**
   - After successful registration, confirm that you want to store the seed
   - Click "Encrypt and Store with YubiKey"
   - Verify that a success message is displayed

4. **Log Out**
   - Click "Log Out" or "End Session"
   - Verify you're redirected to the homepage

5. **Retrieve Seed**
   - Click "Retrieve Seed" in the navigation
   - Enter the User ID from step 2
   - Click "Authenticate with YubiKey"
   - When prompted, insert and touch your YubiKey
   - Verify the seed phrase is displayed

6. **Verify Seed Matches**
   - Confirm that the displayed seed phrase matches what was generated in step 1

### Expected Results

- All steps should complete without errors
- The retrieved seed phrase should exactly match the originally generated seed phrase
- The application should provide clear feedback at each step

## Test Scenario 2: Import, Store, Retrieve

### Test Steps

1. **Start with Import**
   - Navigate to the application homepage
   - Click "Import Existing Seed"
   - Enter a valid BIP39 seed phrase (12, 15, 18, 21, or 24 words)
   - Example: "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
   - Click "Validate & Import"
   - Verify the seed is accepted and a preview is displayed

2. **Register New YubiKey**
   - Click "Register YubiKey to Store This Seed"
   - Enter a username (e.g., "e2etest2")
   - Click "Register YubiKey"
   - When prompted, insert and touch your YubiKey
   - Once registration is complete, note the User ID provided

3. **Store Imported Seed**
   - After successful registration, confirm that you want to store the seed
   - Click "Encrypt and Store with YubiKey"
   - Verify that a success message is displayed

4. **Log Out**
   - Click "Log Out" or "End Session"
   - Verify you're redirected to the homepage

5. **Retrieve Imported Seed**
   - Click "Retrieve Seed" in the navigation
   - Enter the User ID from step 2
   - Click "Authenticate with YubiKey"
   - When prompted, insert and touch your YubiKey
   - Verify the seed phrase is displayed

6. **Verify Imported Seed Matches**
   - Confirm that the displayed seed phrase matches what was imported in step 1

### Expected Results

- All steps should complete without errors
- The retrieved seed phrase should exactly match the originally imported seed phrase
- The application should provide clear feedback at each step

## Test Scenario 3: Error Recovery and Edge Cases

### Test Steps

1. **Invalid Seed Import**
   - Navigate to the application homepage
   - Click "Import Existing Seed"
   - Enter an invalid seed phrase (e.g., random words or incorrect checksum)
   - Click "Validate & Import"
   - Verify that an appropriate error message is displayed
   - Verify the application recovers gracefully

2. **Authentication with Wrong YubiKey**
   - If available, use a different YubiKey than the one used for registration
   - Attempt to authenticate with a valid User ID but the wrong YubiKey
   - Verify that authentication fails with an appropriate error message
   - Verify the application recovers gracefully

3. **Session Timeout**
   - Successfully authenticate and view a seed phrase
   - Wait for the session timeout period (default: 60 seconds)
   - Try to access the seed view page again
   - Verify that re-authentication is required
   - Verify the application handles the timeout gracefully

4. **Page Reload During Process**
   - Start the registration process
   - Before completing, reload the page
   - Verify the application handles the interruption gracefully
   - Verify you can restart the process without issues

### Expected Results

- All error cases should be handled gracefully
- The application should display appropriate error messages
- It should be possible to recover from errors and continue using the application

## Test Scenario 4: Browser Compatibility

### Test Steps

Repeat Test Scenario 1 in the following browsers:

1. **Chrome**
   - Complete the entire workflow in Chrome
   - Note any Chrome-specific behaviors or issues

2. **Safari**
   - Complete the entire workflow in Safari
   - Note any Safari-specific behaviors or issues

3. **Firefox** (if available)
   - Complete the entire workflow in Firefox
   - Note any Firefox-specific behaviors or issues

### Expected Results

- The application should function correctly in all tested browsers
- Any browser-specific behaviors should be documented
- The core functionality should be consistent across browsers

## Test Results Documentation

For each test scenario, document the following:

1. Test scenario and steps executed
2. Pass/Fail status for each step
3. Any error messages encountered
4. Browser-specific observations
5. Screenshots of key steps (if available)
6. Any unexpected behavior

## Troubleshooting Common End-to-End Issues

- **Stale Browser Cache**: Clear browser cache if unexpected behaviors occur after code updates
- **WebAuthn State**: Some browsers cache WebAuthn credentials - try in a private/incognito window if issues persist
- **YubiKey Detection**: Ensure the YubiKey is properly connected and not in use by another application
- **Session Issues**: Check for cookie/session problems if authentication state is not maintained properly

## Completion Criteria

The end-to-end test is considered successful if:

1. All test scenarios pass in the primary browser (Chrome)
2. Browser compatibility tests identify any browser-specific issues
3. The application correctly handles the full workflow from seed generation to retrieval
4. Error cases are handled gracefully
5. No unexpected behaviors or security issues are identified 