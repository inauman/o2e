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
- Clean, modular architecture with separate frontend and backend components
- Well-defined API contracts between components
- SQLite database for persistent storage of all data

## Prerequisites

- Python 3.14+
- Node.js 18+ (for React frontend)
- YubiKey 5 Series device (or compatible WebAuthn authenticator)
- Modern browser with WebAuthn support (Chrome, Firefox, Safari, Edge)
- HTTPS environment (even for localhost - self-signed certificates work for testing)

## Project Structure

This project is organized with a clear separation between frontend and backend components:

```
.
├── backend/                 # Flask backend
│   ├── app.py               # Main Flask application
│   ├── api/                 # API endpoints
│   ├── services/            # Business logic services
│   ├── models/              # Data models and database logic
│   ├── utils/               # Utility functions
│   ├── templates/           # Legacy Flask templates
│   ├── static/              # Static assets (and React build output)
│   ├── yubikey_storage.db   # SQLite database file (created at runtime)
│   └── tests/               # Backend tests
├── frontend/                # React frontend
│   ├── src/                 # React source code
│   ├── public/              # Public assets
│   └── tests/               # Frontend tests
├── doc/                     # Documentation files
│   └── user_guides/         # User documentation
├── .cursor/                 # Cursor IDE configuration
│   └── rules/               # Modular development rules
└── dev.sh                   # Development script
```

For more details on the project structure and organization, see the [Project Structure Documentation](doc/project_structure/project_structure.md).

## Quick Start

### Development Setup

1. Clone this repository
2. Set up backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Set up frontend:
   ```bash
   cd frontend
   npm install
   ```
4. Start the development environment:
   ```bash
   # From the project root
   ./dev.sh
   ```
   This will start both the Flask backend and React frontend in development mode.

5. Navigate to `http://localhost:3000` in your browser for the frontend, or `http://localhost:5000` for the backend API.

For detailed setup and usage instructions, see the [Usage Guide](doc/user_guides/usage.md).

## Storage

This application uses an SQLite database for all persistent storage needs, including:

- User information
- YubiKey credentials
- YubiKey salts
- Encrypted seed phrases
- WebAuthn temporary challenges

The database file is created automatically at `backend/yubikey_storage.db` when the application is first run.

**Note:** Earlier versions of this application used JSON files for storage. This has been fully migrated to a database approach for improved security, reliability, and data integrity.

## Documentation

- [Usage Guide](doc/user_guides/usage.md): Step-by-step instructions for using the application
- [Architecture](doc/architecture.md): Overview of the system design and components
- [API Interface Design](doc/api_interface_design.md): Specifications for the backend API
- [Security Considerations](doc/security.md): Analysis of security measures and limitations
- [Project Plan](doc/project_plan.md): Development tracking and progress
- [React Integration Guide](doc/react_integration_guide.md): Guide for the React frontend integration
- [Project Structure Assessment](doc/project_structure/project_structure_assessment.md): Analysis of the project structure
- [Migration Plan](doc/project_structure/migration_plan.md): Plan for migrating to the new structure

## Development Guidelines

This project follows a set of modular development rules defined in the `.cursor/rules` directory:

- [API Design](/.cursor/rules/api_design.md): Guidelines for designing clean API interfaces
- [Backend Rules](/.cursor/rules/backend_rules.md): Flask-specific development standards
- [Frontend Rules](/.cursor/rules/frontend_rules.md): React-specific development standards
- [Security Rules](/.cursor/rules/security.md): Security requirements and best practices
- [Modular Design Principles](/.cursor/rules/modular_design_principles.md): Guidelines for modular architecture
- [Coding Standards](/.cursor/rules/coding.md): General coding standards and practices
- [Testing Standards](/.cursor/rules/testing.md): Testing requirements and approaches

For a complete overview of the rules structure, see the [Rules README](/.cursor/rules/README.md).

## Security Features

- WebAuthn authentication for YubiKey integration
- Secure memory handling for sensitive data
- Encrypted storage of seed phrases
- HTTPS transport security
- Client-side verification
- Minimal exposure of seed phrases
- Clean API boundaries between frontend and backend

## Contributing

Contributions are welcome! Please follow these steps:

1. Review the project structure and development guidelines
2. Fork the repository
3. Create a feature branch (`git checkout -b feature/amazing-feature`)
4. Make your changes following the development rules
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

Please refer to the [Project Plan](doc/project_plan.md) for current priorities and areas of focus.

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