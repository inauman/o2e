import {
  arrayBufferToBase64,
  base64ToArrayBuffer,
  preparePublicKeyCredentialCreationOptions,
  preparePublicKeyCredentialRequestOptions,
  formatCredentialForServer,
  formatAssertionForServer
} from '../../utils/webauthn';

// Mock fetch
global.fetch = jest.fn();

// Mock WebAuthn API
Object.defineProperty(window, 'PublicKeyCredential', {
  value: {
    isUserVerifyingPlatformAuthenticatorAvailable: jest.fn().mockResolvedValue(true)
  }
});

// Mock navigator.credentials
Object.defineProperty(navigator, 'credentials', {
  value: {
    create: jest.fn(),
    get: jest.fn()
  }
});

describe('WebAuthn Utilities', () => {
  const mockUsername = 'testuser';
  const mockUserId = 'test-user-id';
  const mockChallenge = 'challenge-base64';
  const mockCredentialId = 'credential-id-base64';
  
  // Mock response objects
  const mockPublicKeyCredentialCreationOptions = {
    challenge: new Uint8Array([1, 2, 3]),
    rp: { name: 'Test Site', id: 'localhost' },
    user: {
      id: new Uint8Array([4, 5, 6]),
      name: mockUsername,
      displayName: mockUsername
    },
    pubKeyCredParams: [],
    timeout: 60000,
    attestation: 'direct',
    authenticatorSelection: {
      authenticatorAttachment: 'cross-platform',
      userVerification: 'preferred'
    }
  };
  
  const mockPublicKeyCredentialRequestOptions = {
    challenge: new Uint8Array([1, 2, 3]),
    rpId: 'localhost',
    allowCredentials: [{
      id: new Uint8Array([7, 8, 9]),
      type: 'public-key',
      transports: ['usb']
    }],
    timeout: 60000,
    userVerification: 'preferred'
  };
  
  const mockCredentialCreationResponse = {
    id: 'new-credential-id',
    rawId: new ArrayBuffer(3),
    response: {
      clientDataJSON: new ArrayBuffer(10),
      attestationObject: new ArrayBuffer(20)
    },
    type: 'public-key',
    getClientExtensionResults: () => ({})
  };
  
  const mockCredentialRequestResponse = {
    id: mockCredentialId,
    rawId: new ArrayBuffer(3),
    response: {
      clientDataJSON: new ArrayBuffer(10),
      authenticatorData: new ArrayBuffer(20),
      signature: new ArrayBuffer(30),
      userHandle: new ArrayBuffer(5)
    },
    type: 'public-key',
    getClientExtensionResults: () => ({})
  };
  
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock fetch responses
    (fetch as jest.Mock).mockImplementation((url: string) => {
      if (url.includes('register/begin')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ 
            publicKey: mockPublicKeyCredentialCreationOptions
          })
        });
      } else if (url.includes('register/complete')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ 
            success: true, 
            userId: mockUserId, 
            credentialId: mockCredentialId 
          })
        });
      } else if (url.includes('authenticate/begin')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ 
            publicKey: mockPublicKeyCredentialRequestOptions
          })
        });
      } else if (url.includes('authenticate/complete')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ 
            success: true, 
            userId: mockUserId 
          })
        });
      }
      
      return Promise.resolve({
        ok: false,
        json: () => Promise.resolve({ success: false, error: 'Unknown endpoint' })
      });
    });
    
    // Mock navigator.credentials responses
    (navigator.credentials.create as jest.Mock).mockResolvedValue(mockCredentialCreationResponse);
    (navigator.credentials.get as jest.Mock).mockResolvedValue(mockCredentialRequestResponse);
  });
  
  test('arrayBufferToBase64 converts ArrayBuffer to base64 string', () => {
    const buffer = new Uint8Array([1, 2, 3]).buffer;
    const result = arrayBufferToBase64(buffer);
    expect(typeof result).toBe('string');
    expect(result.length).toBeGreaterThan(0);
  });
  
  test('base64ToArrayBuffer converts base64 string to ArrayBuffer', () => {
    const base64 = 'AQID'; // Base64 for [1,2,3]
    const result = base64ToArrayBuffer(base64);
    expect(result).toBeInstanceOf(ArrayBuffer);
    expect(new Uint8Array(result)).toEqual(new Uint8Array([1, 2, 3]));
  });
  
  test('preparePublicKeyCredentialCreationOptions transforms server options to browser format', () => {
    const serverOptions = {
      publicKey: {
        challenge: 'AQID', // Base64 encoded challenge
        rp: { name: 'Test Site', id: 'localhost' },
        user: {
          id: 'BAUG', // Base64 encoded user ID
          name: 'testuser',
          displayName: 'testuser'
        },
        pubKeyCredParams: [{ type: 'public-key', alg: -7 }],
        timeout: 60000,
        attestation: 'direct',
        authenticatorSelection: {
          authenticatorAttachment: 'cross-platform',
          userVerification: 'preferred'
        }
      }
    };
    
    const result = preparePublicKeyCredentialCreationOptions(serverOptions);
    
    // Check that challenge is converted to ArrayBuffer
    expect(result.challenge).toBeInstanceOf(ArrayBuffer);
    // Check that user.id is converted to ArrayBuffer
    expect(result.user.id).toBeInstanceOf(ArrayBuffer);
    // Other properties should be passed through
    expect(result.rp.name).toBe('Test Site');
    expect(result.attestation).toBe('direct');
  });
  
  test('preparePublicKeyCredentialRequestOptions transforms server options to browser format', () => {
    const serverOptions = {
      publicKey: {
        challenge: 'AQID', // Base64 encoded challenge
        rpId: 'localhost',
        allowCredentials: [{
          id: 'BwgJ', // Base64 encoded credential ID
          type: 'public-key',
          transports: ['usb']
        }],
        timeout: 60000,
        userVerification: 'preferred'
      }
    };
    
    const result = preparePublicKeyCredentialRequestOptions(serverOptions);
    
    // Check that challenge is converted to ArrayBuffer
    expect(result.challenge).toBeInstanceOf(ArrayBuffer);
    // Check that allowCredentials[0].id is converted to ArrayBuffer
    expect(result.allowCredentials?.[0].id).toBeInstanceOf(ArrayBuffer);
    // Other properties should be passed through
    expect(result.rpId).toBe('localhost');
    expect(result.userVerification).toBe('preferred');
  });
  
  test('formatCredentialForServer converts credential to server format', () => {
    // Mock PublicKeyCredential
    const mockCredential = {
      id: 'credential-id',
      rawId: new ArrayBuffer(3),
      response: {
        clientDataJSON: new ArrayBuffer(10),
        attestationObject: new ArrayBuffer(20)
      },
      type: 'public-key',
      getClientExtensionResults: () => ({})
    } as unknown as PublicKeyCredential;
    
    const result = formatCredentialForServer(mockCredential);
    
    // Check that ArrayBuffers are converted to base64 strings
    expect(typeof result.rawId).toBe('string');
    expect(typeof result.response.clientDataJSON).toBe('string');
    expect(typeof result.response.attestationObject).toBe('string');
    // Other properties should be passed through
    expect(result.id).toBe('credential-id');
    expect(result.type).toBe('public-key');
  });
  
  test('formatAssertionForServer converts assertion to server format', () => {
    // Mock PublicKeyCredential
    const mockCredential = {
      id: 'credential-id',
      rawId: new ArrayBuffer(3),
      response: {
        clientDataJSON: new ArrayBuffer(10),
        authenticatorData: new ArrayBuffer(20),
        signature: new ArrayBuffer(30),
        userHandle: new ArrayBuffer(5)
      },
      type: 'public-key',
      getClientExtensionResults: () => ({})
    } as unknown as PublicKeyCredential;
    
    const result = formatAssertionForServer(mockCredential);
    
    // Check that ArrayBuffers are converted to base64 strings
    expect(typeof result.rawId).toBe('string');
    expect(typeof result.response.clientDataJSON).toBe('string');
    expect(typeof result.response.authenticatorData).toBe('string');
    expect(typeof result.response.signature).toBe('string');
    expect(typeof result.response.userHandle).toBe('string');
    // Other properties should be passed through
    expect(result.id).toBe('credential-id');
    expect(result.type).toBe('public-key');
  });
}); 