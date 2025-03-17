import { 
  encryptSeedPhrase, 
  decryptSeedPhrase, 
  generateRandomSeedPhrase,
  validateSeedPhrase
} from '../../utils/seedEncryption';

// Mock the crypto API
global.crypto = {
  subtle: {
    importKey: jest.fn(),
    encrypt: jest.fn(),
    decrypt: jest.fn()
  },
  getRandomValues: jest.fn(array => {
    for (let i = 0; i < array.length; i++) {
      array[i] = Math.floor(Math.random() * 256);
    }
    return array;
  })
};

// Mock the TextEncoder and TextDecoder
global.TextEncoder = jest.fn(() => ({
  encode: jest.fn(str => new Uint8Array([...str].map(char => char.charCodeAt(0))))
}));

global.TextDecoder = jest.fn(() => ({
  decode: jest.fn(array => String.fromCharCode.apply(null, array))
}));

describe('Seed Encryption Utilities', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Setup mock implementations for crypto.subtle methods
    crypto.subtle.importKey.mockResolvedValue('mock-crypto-key');
    crypto.subtle.encrypt.mockResolvedValue(new Uint8Array([1, 2, 3, 4]));
    crypto.subtle.decrypt.mockResolvedValue(new TextEncoder().encode('decrypted seed phrase'));
  });

  test('generateRandomSeedPhrase returns a valid seed phrase', () => {
    const seed = generateRandomSeedPhrase();
    expect(seed).toBeDefined();
    expect(typeof seed).toBe('string');
    expect(seed.split(' ').length).toBe(12); // Default is 12 words
  });

  test('validateSeedPhrase validates a correct seed phrase', () => {
    // This is a valid BIP39 test vector
    const validSeed = 'abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about';
    const result = validateSeedPhrase(validSeed);
    expect(result).toBe(true);
  });
  
  test('validateSeedPhrase rejects an invalid seed phrase', () => {
    const invalidSeed = 'not a valid seed phrase at all just random words here';
    const result = validateSeedPhrase(invalidSeed);
    expect(result).toBe(false);
  });

  test('encryptSeedPhrase encrypts a seed phrase', async () => {
    const seedPhrase = 'test seed phrase';
    const salt = 'test-salt';
    
    const result = await encryptSeedPhrase(seedPhrase, salt);
    
    expect(crypto.subtle.importKey).toHaveBeenCalled();
    expect(crypto.subtle.encrypt).toHaveBeenCalled();
    expect(result).toBeDefined();
    // Result should be a base64 string
    expect(typeof result).toBe('string');
    expect(result.length).toBeGreaterThan(0);
  });

  test('decryptSeedPhrase decrypts an encrypted seed phrase', async () => {
    const encryptedData = 'encrypted-data-base64';
    const salt = 'test-salt';
    
    const result = await decryptSeedPhrase(encryptedData, salt);
    
    expect(crypto.subtle.importKey).toHaveBeenCalled();
    expect(crypto.subtle.decrypt).toHaveBeenCalled();
    expect(result).toBe('decrypted seed phrase');
  });

  test('encryptSeedPhrase handles errors', async () => {
    // Override the mock to simulate an error
    crypto.subtle.encrypt.mockRejectedValue(new Error('Encryption failed'));
    
    const seedPhrase = 'test seed phrase';
    const salt = 'test-salt';
    
    await expect(encryptSeedPhrase(seedPhrase, salt)).rejects.toThrow('Encryption failed');
  });

  test('decryptSeedPhrase handles errors', async () => {
    // Override the mock to simulate an error
    crypto.subtle.decrypt.mockRejectedValue(new Error('Decryption failed'));
    
    const encryptedData = 'encrypted-data-base64';
    const salt = 'test-salt';
    
    await expect(decryptSeedPhrase(encryptedData, salt)).rejects.toThrow('Decryption failed');
  });
}); 