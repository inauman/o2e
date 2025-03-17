// Add any Jest setup code needed
import '@testing-library/jest-dom';

// Mock WebAuthn
Object.defineProperty(window, 'PublicKeyCredential', {
  value: {
    isUserVerifyingPlatformAuthenticatorAvailable: jest.fn().mockResolvedValue(true)
  }
});

// Mock navigator.credentials
if (!navigator.credentials) {
  Object.defineProperty(navigator, 'credentials', {
    value: {
      create: jest.fn(),
      get: jest.fn()
    }
  });
} 