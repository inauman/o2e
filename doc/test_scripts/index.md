# YubiKey Bitcoin Seed Storage: Test Scripts

This document serves as an index for all test scripts available for the YubiKey Bitcoin Seed Storage proof-of-concept application. These test scripts are designed to verify that all components of the application function correctly.

## Overview

The test scripts cover all critical aspects of the application, including:

1. WebAuthn registration in Chrome and Safari
2. WebAuthn authentication in Chrome and Safari
3. Secure storage and encryption/decryption
4. End-to-end workflows
5. UI flows and error handling

## Test Scripts

| Test Script | Description | Target Tasks |
|-------------|-------------|-------------|
| [Registration Test](registration_test.md) | Tests the WebAuthn registration process in Chrome and Safari | Tasks 3.5, 3.6 |
| [Authentication Test](authentication_test.md) | Tests the WebAuthn authentication process in Chrome and Safari | Tasks 4.4, 4.5 |
| [Storage Test](storage_test.md) | Tests secure storage and encryption/decryption functionality | Task 5.6 |
| [End-to-End Test](e2e_test.md) | Tests complete workflows from seed generation to retrieval | Tasks 7.1, 7.2, 7.3, 7.4 |
| UI Flow Tests | Covered within the other test scripts | Tasks 6.6, 6.7 |

## How to Use These Scripts

1. **Preparation**: Ensure you have all prerequisites installed and configured as specified in each test script.
2. **Execution**: Follow each test script step by step, documenting results as you go.
3. **Documentation**: Record pass/fail status, any error messages, and screenshots as appropriate.
4. **Issue Resolution**: For any failures, debug and resolve before proceeding to the next test.

## Test Execution Order

For best results, execute the tests in the following order:

1. Registration Test
2. Authentication Test
3. Storage Test
4. End-to-End Test

This order ensures that each component is validated before testing integrated workflows.

## Test Environment

All tests should be performed in a controlled environment with:

- A dedicated YubiKey that can be used exclusively for testing
- Clean browser profiles to avoid cached credentials
- The application running in development mode to allow for easy access to logs
- Developer tools open to monitor network traffic and console logs

## Reporting Results

After completing each test script, update the project plan to reflect the completion status. For any failed tests:

1. Document the exact step that failed
2. Capture any error messages or logs
3. Note the expected vs. actual behavior
4. Create an issue in the issue tracker for follow-up

## Compatibility Testing

All WebAuthn tests should be performed in both Chrome and Safari to ensure cross-browser compatibility. Note any differences in behavior between browsers. 