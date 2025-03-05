# YubiKey Bitcoin Seed Storage POC: Usage Guide

## Overview

This application demonstrates a proof-of-concept for securely storing a Bitcoin seed phrase using a YubiKey. The seed can only be retrieved when the same YubiKey is present, providing a high level of security for your Bitcoin wallet seed phrase.

**Important Note**: This is a proof-of-concept application for educational purposes. It should not be used for storing actual Bitcoin wallet seeds in production without further security auditing and enhancements.

## Prerequisites

- A YubiKey 5 series device (or compatible security key that supports WebAuthn)
- A modern browser that supports WebAuthn (Chrome, Safari, Firefox, Edge)
- Python 3.14+ with the `uv` package manager installed
- An activated Python virtual environment

## Setup & Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/yubikey-bitcoin-seed.git
   cd yubikey-bitcoin-seed
   ```

2. Activate your virtual environment:
   ```bash
   source .venv/bin/activate
   ```

3. Install the required dependencies:
   ```bash
   uv pip install -r requirements.txt
   ```

4. Configure the application by editing `config.yaml` if needed.

5. Run the application:
   ```bash
   python app.py
   ```

6. Access the application in your browser at `https://localhost:5000`.

   Note: The application uses a self-signed certificate for HTTPS, which is required for WebAuthn. You may need to accept security warnings in your browser.

## Step-by-Step Usage

### Testing Your YubiKey

1. Before using the application, it's recommended to test if your YubiKey works correctly with the system:
   - Navigate to the "Test YubiKey" page from the main menu
   - Click "Start WebAuthn Test"
   - When prompted, insert your YubiKey and touch it to confirm
   - The test will check if your YubiKey can be used for registration and authentication

### Generating or Importing a Seed Phrase

You have two options:

#### Option 1: Generate a New Seed

1. On the home page, click "Generate New Seed"
2. A new seed will be generated and temporarily stored in memory
3. You'll see a preview of the beginning and end of the seed phrase
4. Click "Register YubiKey to Store This Seed"

#### Option 2: Import an Existing Seed

1. Navigate to "Store Seed" after registering your YubiKey
2. Select "Import an existing seed phrase"
3. Enter your BIP39 seed phrase (12, 15, 18, 21, or 24 words)
4. Click "Validate & Import"

### Registering Your YubiKey

1. Enter a username to identify this registration
2. Click "Register YubiKey"
3. When prompted, insert your YubiKey (if not already inserted)
4. Touch your YubiKey when the light flashes
5. After successful registration, you'll receive a User ID
6. **Important**: Save this User ID securely. You'll need it to authenticate and retrieve your seed.

### Storing a Seed Phrase

If you've already registered your YubiKey:

1. Navigate to "Store Seed"
2. Follow the instructions to either generate a new seed or import an existing one
3. Review the seed phrase preview
4. Confirm that you've backed up the seed phrase
5. Click "Encrypt and Store with YubiKey"

### Retrieving Your Seed Phrase

1. Navigate to "Retrieve Seed"
2. Enter your User ID that you received during registration
3. Click "Authenticate with YubiKey"
4. When prompted, insert your YubiKey and touch it
5. After successful authentication, your seed phrase will be displayed
6. The seed phrase will be automatically cleared from memory when you leave the page or after a timeout period

### Ending Your Session

1. After viewing your seed, click "End Session and Clear Seed" to securely remove the seed from memory
2. Always log out when you're done with the application

## Security Features

This proof-of-concept implements several security features:

1. **WebAuthn Authentication**: Requires physical possession of the registered YubiKey
2. **Secure Memory Handling**: Sensitive data is automatically cleared from memory after a timeout
3. **HTTPS Requirement**: All WebAuthn operations require a secure context (HTTPS)
4. **Client-Side Verification**: Seed phrase validation uses BIP39 standards
5. **Minimal Exposure**: Seed phrases are displayed only when needed and with security warnings

## Troubleshooting

### YubiKey Not Detected

- Ensure your YubiKey is properly inserted
- Try a different USB port
- Restart your browser
- Check if your browser supports WebAuthn

### Registration or Authentication Fails

- Make sure you're using the same YubiKey that was registered
- Check that you're accessing the site over HTTPS
- Use a supported browser (Chrome, Safari, Firefox, Edge)
- Try the "Test YubiKey" page to verify your device is working correctly

### Cannot View Seed

- Verify you're using the correct User ID
- Ensure you're using the same YubiKey that was registered
- Try authenticating again

## Security Considerations

1. This is a proof-of-concept and not intended for production use without further security enhancements
2. In a real-world implementation, proper encryption keys would be derived from the WebAuthn attestation
3. The current implementation uses simple encoding instead of proper cryptographic encryption
4. For actual Bitcoin wallet security, consider using hardware wallets specifically designed for that purpose
5. Always maintain offline backups of your seed phrases 