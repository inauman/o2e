# Python Best Practices for Bitcoin Multisig POC

## Core Principles
- **Modularity First**: Design systems, documents, config, and rules with clear separation of concerns
- **Don't Trust, Validate**: Every component must validate its inputs regardless of source
- **Security by Design**: Implement security at every level of the application
- **Modern Python**: Leverage latest Python features, tools, and packages
- **Testability**: Design for comprehensive testing from the start
- **Documentation**: Clear, consistent documentation at all levels

## Python Environment

### Version and Setup
- Use Python 3.14.0a5 (alpha version currently installed)
- Use `uv` for package management instead of pip
- Use `pyproject.toml` for project configuration (PEP 621)
- Use virtual environments for isolation

### Dependency Management
- Pin all dependency versions with exact versions
- Use `uv` for faster, more secure package installation
- Document all dependencies with purpose and license
- Regularly audit dependencies for security vulnerabilities
- Use `pip-audit` or `safety` for dependency security checks
- Be aware of potential compatibility issues with Python 3.14.0a5 (alpha version)

## Code Structure

### Modularity
- Maximum class size: 300 lines (break larger classes into logical components)
- Maximum function size: 50 lines
- Maximum module size: 500 lines
- One class per file (with rare, justified exceptions)
- Group related functionality in packages
- Use composition over inheritance

### Architecture
- Follow clean architecture principles
- Separate interface from implementation
- Use dependency injection for testability
- Implement clear boundaries between modules
- Use abstract base classes or protocols for interfaces
- Follow SOLID principles

## Code Quality

### Style and Formatting
- Follow PEP 8 with Black's modifications
- Line length: 88 characters (Black default)
- Use Black for code formatting
- Use isort for import sorting
- Use Ruff for fast, comprehensive linting

### Type Annotations
- Use type hints for all function parameters and return values
- Use mypy for static type checking
- Use Protocol for interface definitions
- Use TypeVar for generic types
- Document complex type relationships
- Leverage Python 3.14 type annotation improvements

### Documentation
- Use Google-style docstrings
- Document all public APIs
- Include examples in docstrings for complex functions
- Document exceptions that may be raised
- Keep documentation in sync with code

### Naming Conventions
- Classes: PascalCase
- Functions and variables: snake_case
- Constants: UPPER_SNAKE_CASE
- Private attributes/methods: _leading_underscore
- Protected attributes/methods: __double_underscore
- Use descriptive, intention-revealing names

## Security Practices

### Cryptocurrency-Specific
- Never store private keys in code or logs
- Use hardware security modules when possible
- Implement BIP32/39/44 standards for HD wallets
- Use strong encryption for any sensitive data storage
- Validate all transaction inputs and outputs
- Implement transaction signing in secure contexts
- Double-check recipient addresses

### General Security
- Use environment variables for configuration (via python-dotenv)
- Validate all input data at every layer
- Use secure random number generation (secrets module)
- Follow principle of least privilege
- Implement proper error handling without leaking sensitive information
- Use constant-time comparisons for sensitive data
- Regular security audits of code

## Error Handling

### Exception Management
- Create domain-specific exception hierarchy
- Always catch specific exceptions
- Provide meaningful error messages
- Use context managers (with statements) where appropriate
- Log exceptions with appropriate context
- Never expose sensitive information in error messages

### Validation
- Validate all inputs at system boundaries
- Use dataclasses or Pydantic for data validation
- Implement pre-condition and post-condition checks
- Fail fast and explicitly
- Return rich error information (without exposing internals)

## Testing

### Test Coverage
- Minimum 80% test coverage across all modules
- 100% test coverage for critical paths (crypto operations)
- Write tests before code (TDD approach)
- Test both positive and negative cases
- Test edge cases and boundary conditions

### Test Types
- Unit tests for individual components
- Integration tests for component interactions
- Functional tests for end-to-end workflows
- Security tests for vulnerability detection
- Performance tests for critical operations

### Test Tools
- Use pytest as the test framework
- Use pytest-mock for mocking
- Use pytest-cov for coverage reporting
- Use hypothesis for property-based testing
- Use pytest-benchmark for performance testing

## Tooling and Automation

### Development Tools
- Use pre-commit hooks for code quality checks
- Implement CI/CD pipelines for automated testing
- Use bandit for security linting
- Use vulture for dead code detection
- Use pyright as an alternative type checker

### Git Practices
- Meaningful commit messages following conventional commits
  - Commit summaries should be concise and clear, limited to 2-3 sentences
  - First line: Brief summary of changes (max 50 characters)
  - Body: More detailed explanation (if needed) with specifics
  - Avoid lengthy descriptions in favor of precise statements
  - Reference relevant issue numbers when applicable
- One feature/fix per commit
- Branch naming: feature/, bugfix/, hotfix/
- Pull request required for all changes
- Code review required for all changes

## Logging and Monitoring

### Logging
- Use structured logging
- Include context in log messages
- Use appropriate log levels
- Never log sensitive data
- Implement log rotation
- Consider using JSON logging for machine readability

### Monitoring
- Monitor transaction operations
- Track system health metrics
- Log security events
- Implement performance monitoring
- Set up alerting for critical issues

## Bitcoin-Specific Best Practices

### Wallet Management
- Implement proper key derivation paths
- Use multisig for enhanced security
- Implement proper backup procedures
- Validate all addresses before use
- Implement proper fee estimation
- Handle network disruptions gracefully

### Transaction Handling
- Verify transaction data before signing
- Implement proper change address management
- Double-check fee calculations
- Implement transaction monitoring
- Handle blockchain reorganizations
- Implement proper error recovery

## Python 3.14 Alpha Considerations
- Be aware of potential instability in the alpha release
- Document any workarounds for alpha-specific issues
- Consider fallback options for critical functionality
- Test thoroughly with the alpha version
- Stay updated on Python 3.14 release notes and changes
- Be prepared to adapt code as Python 3.14 moves toward stable release

## Updates
This document should be reviewed and updated quarterly or when significant changes are made to the project requirements or when new Python best practices emerge. 