# Code Review Checklist

## General Code Quality

### Modularity
- [ ] Classes are under 300 lines
- [ ] Functions are under 50 lines
- [ ] Modules are under 500 lines
- [ ] Clear separation of concerns
- [ ] Follows single responsibility principle
- [ ] Uses composition over inheritance

### Style and Formatting
- [ ] Follows PEP 8 guidelines
- [ ] Passes Black formatting check
- [ ] Passes isort import sorting check
- [ ] Passes Ruff linting check
- [ ] Consistent naming conventions
- [ ] Descriptive variable and function names

### Documentation
- [ ] All public functions have docstrings
- [ ] All modules have docstrings
- [ ] Docstrings follow Google style
- [ ] Complex logic is explained with comments
- [ ] Comments explain why, not what
- [ ] No commented-out code

### Type Annotations
- [ ] All function parameters have type hints
- [ ] All return values have type hints
- [ ] Complex types are documented
- [ ] Passes mypy type checking
- [ ] Uses Protocol for interfaces
- [ ] No unnecessary `Any` types

## Security Considerations

### Input Validation
- [ ] All external inputs are validated
- [ ] Validation happens at system boundaries
- [ ] Input validation is comprehensive
- [ ] Error messages don't leak sensitive information
- [ ] Validation failures are logged appropriately
- [ ] Edge cases are handled

### Sensitive Data Handling
- [ ] No hardcoded secrets or keys
- [ ] Sensitive data is not logged
- [ ] Sensitive data is cleared from memory when no longer needed
- [ ] Environment variables are used for configuration
- [ ] Secure random number generation is used
- [ ] Constant-time comparisons for sensitive data

### Bitcoin-Specific Security
- [ ] Transaction data is validated
- [ ] Addresses are validated
- [ ] Fee calculations are bounded
- [ ] Signatures are verified
- [ ] Error handling for network issues
- [ ] Proper multisig implementation

### Device Integration Security
- [ ] Secure communication with hardware devices
- [ ] Proper error handling for device failures
- [ ] Timeout handling for device operations
- [ ] Device authentication is implemented
- [ ] Device state is validated
- [ ] Graceful handling of device disconnection

## Error Handling

### Exception Management
- [ ] Specific exceptions are caught
- [ ] Custom exceptions for domain-specific errors
- [ ] Exceptions include context
- [ ] Error recovery is implemented
- [ ] System state is validated after errors
- [ ] Errors are logged with appropriate level

### Edge Cases
- [ ] Boundary conditions are handled
- [ ] Empty/null inputs are handled
- [ ] Resource exhaustion is handled
- [ ] Timeout handling is implemented
- [ ] Concurrent access is handled
- [ ] Network failures are handled

## Testing

### Test Coverage
- [ ] Unit tests for all functions
- [ ] Integration tests for component interactions
- [ ] Edge cases are tested
- [ ] Error conditions are tested
- [ ] Minimum 80% test coverage
- [ ] 100% coverage for critical paths

### Test Quality
- [ ] Tests are independent
- [ ] Tests are deterministic
- [ ] Mocks are used appropriately
- [ ] Test names are descriptive
- [ ] Tests validate both positive and negative cases
- [ ] Tests are fast and efficient

## Performance and Efficiency

### Resource Usage
- [ ] Appropriate data structures are used
- [ ] Memory usage is reasonable
- [ ] CPU usage is reasonable
- [ ] I/O operations are minimized
- [ ] Network calls are optimized
- [ ] Database queries are efficient

### Concurrency
- [ ] Race conditions are prevented
- [ ] Deadlocks are prevented
- [ ] Resources are properly released
- [ ] Async operations are properly awaited
- [ ] Cancellation is handled
- [ ] Backpressure is implemented where needed

## Maintainability

### Code Structure
- [ ] Follows project structure
- [ ] Logical file organization
- [ ] Consistent coding patterns
- [ ] No code duplication
- [ ] Appropriate abstraction level
- [ ] Clear module dependencies

### Dependencies
- [ ] Dependencies are properly declared
- [ ] Minimal dependencies
- [ ] Dependencies have appropriate versions
- [ ] No deprecated dependencies
- [ ] No vulnerable dependencies
- [ ] Dependencies are used efficiently

## Bitcoin Multisig Specific

### Wallet Management
- [ ] Proper key derivation paths
- [ ] Correct multisig script construction
- [ ] Address validation
- [ ] Proper change address handling
- [ ] Balance calculation is accurate
- [ ] UTXO management is correct

### Transaction Handling
- [ ] Transaction building is correct
- [ ] Fee estimation is reasonable
- [ ] Transaction signing is secure
- [ ] Transaction broadcasting has retry logic
- [ ] Transaction monitoring is implemented
- [ ] Error handling for transaction failures

### Device Integration
- [ ] YubiKey integration follows best practices
- [ ] Ledger integration follows best practices
- [ ] Hardcoded key is clearly marked as testing only
- [ ] Device detection is robust
- [ ] Device communication is secure
- [ ] Device errors are handled gracefully

## CLI Interface

### User Experience
- [ ] Commands are intuitive
- [ ] Help text is clear
- [ ] Error messages are helpful
- [ ] Progress is indicated
- [ ] Confirmation for destructive operations
- [ ] Consistent command structure

### Input Handling
- [ ] All user input is validated
- [ ] Input errors are handled gracefully
- [ ] Sensitive input is masked
- [ ] Command options are documented
- [ ] Default values are reasonable
- [ ] Required options are enforced

## Documentation

### Code Documentation
- [ ] Code is self-documenting
- [ ] Complex algorithms are explained
- [ ] Security considerations are documented
- [ ] Performance considerations are documented
- [ ] Error handling is documented
- [ ] API contracts are documented

### User Documentation
- [ ] Installation instructions are clear
- [ ] Usage examples are provided
- [ ] Configuration options are documented
- [ ] Error messages are explained
- [ ] Security warnings are included
- [ ] Troubleshooting guide is provided

## Updates
This checklist should be used for all code reviews and updated as new best practices emerge. 