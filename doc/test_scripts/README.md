# YubiKey Bitcoin Seed Storage: Test Scripts

## Overview

This directory contains comprehensive test scripts for the YubiKey Bitcoin Seed Storage proof-of-concept application. These scripts are designed to guide manual testing of all critical functionalities.

## Contents

- [Index of Test Scripts](index.md) - Overview and organization of all test scripts
- [Registration Test](registration_test.md) - Testing WebAuthn registration in Chrome and Safari
- [Authentication Test](authentication_test.md) - Testing WebAuthn authentication in Chrome and Safari
- [Storage Test](storage_test.md) - Testing secure storage and encryption/decryption
- [End-to-End Test](e2e_test.md) - Testing complete application workflows

## Getting Started

1. Start by reading the [Index of Test Scripts](index.md) to understand the organization and purpose of each test script.
2. Follow the recommended test execution order:
   - Registration Test
   - Authentication Test
   - Storage Test
   - End-to-End Test
3. For each test script, carefully follow all prerequisites and setup instructions before beginning.

## Test Documentation

As you execute each test script, document your results in a separate test results document. Include:
- Test date and environment details
- Pass/fail status for each test case
- Any error messages or unexpected behaviors
- Screenshots of key steps, particularly for failures
- Notes on browser-specific behaviors

## Prerequisites for Testing

All tests require:
- A YubiKey 5 Series device
- Chrome and/or Safari browser (latest versions)
- The application running with HTTPS (even on localhost)
- Developer tools enabled in your browser
- Access to application data files

## Reporting Issues

If you encounter any issues during testing:
1. Document the exact step where the issue occurred
2. Capture the full error message and any relevant logs
3. Note the expected behavior versus actual behavior
4. Note the browser and OS versions
5. Record any YubiKey-specific details (model, firmware version if known)

## Completing Test Cycles

After completing all test scripts:
1. Update the project plan to reflect completed test tasks
2. Document any outstanding issues or areas for improvement
3. Provide an overall assessment of application readiness

## Notes for Testers

- Testing WebAuthn functionality requires a physical YubiKey device
- Some tests may behave differently across browsers due to WebAuthn implementation differences
- Chrome provides extra WebAuthn debugging via chrome://webauthn-internals/
- Always execute tests in a clean browser session to avoid credential caching issues
- HTTPS is required for WebAuthn (except on localhost in some browsers) 