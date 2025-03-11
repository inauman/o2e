# YubiKey Bitcoin Seed Storage

A proof-of-concept application for securely generating and storing Bitcoin seed phrases using YubiKey's WebAuthn capabilities.

## Overview

This project demonstrates how to use YubiKey hardware security devices in combination with the WebAuthn standard to secure Bitcoin seed phrases. It provides a practical implementation of secure storage techniques that could be developed further for production use.

**⚠️ DISCLAIMER: This is a PROOF OF CONCEPT for educational purposes only. DO NOT use this for production or with real Bitcoin funds without substantial security enhancements.**

## Features

- Generate cryptographically secure BIP39 seed phrases
- Import existing seed phrases
- Register YubiKey devices using WebAuthn
- Securely encrypt seed phrases with keys derived from YubiKey authentication
- Retrieve seed phrases securely with YubiKey authentication
- Secure memory handling with automatic clearing of sensitive data

## Prerequisites

- Python 3.14+
- YubiKey 5 Series device (or compatible WebAuthn authenticator)
- Modern browser with WebAuthn support (Chrome, Firefox, Safari, Edge)
- HTTPS environment (even for localhost - self-signed certificates work for testing)

## Quick Start

1. Clone this repository
2. Set up a Python virtual environment
3. Install dependencies with `uv install -r requirements.txt`
4. Configure the application in `config.py`
5. Run the application with `python app.py`
6. Navigate to `https://localhost:5000` in your browser

For detailed setup and usage instructions, see the [Usage Guide](doc/usage.md).

## Documentation

- [Usage Guide](doc/usage.md): Step-by-step instructions for using the application
- [Architecture](doc/architecture.md): Overview of the system design and components
- [Security Considerations](doc/security.md): Analysis of security measures and limitations
- [Future Roadmap](doc/roadmap.md): Planned enhancements and future development paths
- [Project Plan](doc/project_plan.md): Development tracking and progress

## Directory Structure

```
.
├── app.py                   # Main Flask application
├── bitcoin_utils.py         # Bitcoin seed generation and handling
├── config.py                # Application configuration
├── data/                    # Storage for credentials and encrypted seeds
├── doc/                     # Documentation files
├── requirements.txt         # Python dependencies
├── static/                  # Static assets (CSS, JS)
├── templates/               # HTML templates
└── yubikey_utils.py         # YubiKey WebAuthn utilities
```

## Security Features

- WebAuthn authentication for YubiKey integration
- Secure memory handling for sensitive data
- Encrypted storage of seed phrases
- HTTPS transport security
- Client-side verification
- Minimal exposure of seed phrases

## Contributing

While this is primarily a proof-of-concept, contributions are welcome! Please refer to the [Future Roadmap](doc/roadmap.md) for potential areas of improvement.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Resident Keys

Resident keys, also known as discoverable credentials, are stored directly on the YubiKey. Unlike non-discoverable credentials, they can be listed and managed using tools like YubiKey Manager (`ykman`). Resident keys are useful for scenarios where you want the YubiKey to manage credentials independently of the server.

### Benefits of Resident Keys
- **Discoverability**: Easily list and manage credentials on the YubiKey.
- **Portability**: Credentials are stored on the YubiKey, allowing for use across different devices without server-side records.
- **Security**: Provides an additional layer of security by storing credentials on a hardware device.

## Testing Resident Keys

To test the application with resident keys, follow these steps:

1. **Modify Credential Creation**: Ensure the application is configured to create resident keys by setting the `residentKey` option to `required` in both server-side and client-side code.

2. **Run the Application**: Start the application using the provided quick start guide.

3. **Register a YubiKey**: Follow the registration process to create a resident key.

4. **Verify Resident Keys**:
   - Use `ykman` to list resident keys on your YubiKey:
     ```bash
     ykman fido credentials list
     ```

5. **Delete Resident Keys**:
   - Use `ykman` to delete specific resident keys:
     ```bash
     ykman fido credentials delete <credential_id>
     ```

6. **Reset FIDO2 Credentials** (if needed):
   - Reset all FIDO2 credentials on the YubiKey:
     ```bash
     ykman fido reset
     ```

These steps will help you test the application with resident keys, allowing you to manage and verify credentials directly on your YubiKey. 