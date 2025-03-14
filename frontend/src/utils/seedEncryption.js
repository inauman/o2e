/**
 * Utility functions for encrypting and decrypting seed phrases using YubiKey-derived keys.
 */
import { hexToBytes, bytesToHex, deriveEncryptionKey } from './yubikeySaltApi';

// Crypto constants
const ALGORITHM = 'AES-GCM';
const KEY_LENGTH = 256; // bits
const IV_LENGTH = 12; // bytes
const TAG_LENGTH = 16; // bytes

/**
 * Encrypt a seed phrase using a YubiKey-derived key
 * @param {string} seedPhrase - The seed phrase to encrypt
 * @param {string} credentialId - The credential ID of the YubiKey
 * @param {string} saltHex - The salt in hex format
 * @param {Function} signCallback - Function to sign data with the YubiKey
 * @returns {Promise<string>} The encrypted seed phrase in hex format
 */
export const encryptSeedPhrase = async (seedPhrase, credentialId, saltHex, signCallback) => {
  try {
    // Convert seed phrase to bytes
    const seedBytes = new TextEncoder().encode(seedPhrase);
    
    // Derive encryption key from YubiKey
    const keyBytes = await deriveEncryptionKey(credentialId, saltHex, signCallback);
    
    // Import the key
    const key = await window.crypto.subtle.importKey(
      'raw',
      keyBytes,
      { name: ALGORITHM, length: KEY_LENGTH },
      false,
      ['encrypt']
    );
    
    // Generate a random initialization vector
    const iv = window.crypto.getRandomValues(new Uint8Array(IV_LENGTH));
    
    // Encrypt the seed phrase
    const encryptedBytes = await window.crypto.subtle.encrypt(
      {
        name: ALGORITHM,
        iv,
        tagLength: TAG_LENGTH * 8 // in bits
      },
      key,
      seedBytes
    );
    
    // Combine IV and encrypted data
    const result = new Uint8Array(IV_LENGTH + encryptedBytes.byteLength);
    result.set(iv, 0);
    result.set(new Uint8Array(encryptedBytes), IV_LENGTH);
    
    // Convert to hex string
    return bytesToHex(result);
  } catch (error) {
    console.error('Error encrypting seed phrase:', error);
    throw error;
  }
};

/**
 * Decrypt a seed phrase using a YubiKey-derived key
 * @param {string} encryptedHex - The encrypted seed phrase in hex format
 * @param {string} credentialId - The credential ID of the YubiKey
 * @param {string} saltHex - The salt in hex format
 * @param {Function} signCallback - Function to sign data with the YubiKey
 * @returns {Promise<string>} The decrypted seed phrase
 */
export const decryptSeedPhrase = async (encryptedHex, credentialId, saltHex, signCallback) => {
  try {
    // Convert hex to bytes
    const encryptedBytes = hexToBytes(encryptedHex);
    
    // Extract IV and encrypted data
    const iv = encryptedBytes.slice(0, IV_LENGTH);
    const ciphertext = encryptedBytes.slice(IV_LENGTH);
    
    // Derive encryption key from YubiKey
    const keyBytes = await deriveEncryptionKey(credentialId, saltHex, signCallback);
    
    // Import the key
    const key = await window.crypto.subtle.importKey(
      'raw',
      keyBytes,
      { name: ALGORITHM, length: KEY_LENGTH },
      false,
      ['decrypt']
    );
    
    // Decrypt the seed phrase
    const decryptedBytes = await window.crypto.subtle.decrypt(
      {
        name: ALGORITHM,
        iv,
        tagLength: TAG_LENGTH * 8 // in bits
      },
      key,
      ciphertext
    );
    
    // Convert to string
    return new TextDecoder().decode(decryptedBytes);
  } catch (error) {
    console.error('Error decrypting seed phrase:', error);
    throw error;
  }
};

/**
 * Generate a random seed phrase (for testing purposes)
 * @param {number} wordCount - The number of words in the seed phrase (12, 15, 18, 21, or 24)
 * @returns {Promise<string>} The generated seed phrase
 */
export const generateRandomSeedPhrase = async (wordCount = 12) => {
  try {
    // Validate word count
    if (![12, 15, 18, 21, 24].includes(wordCount)) {
      throw new Error('Invalid word count. Must be 12, 15, 18, 21, or 24.');
    }
    
    // Generate random bytes (ENT)
    const entropyBits = wordCount * 11 - wordCount / 3;
    const entropyBytes = Math.ceil(entropyBits / 8);
    const entropy = window.crypto.getRandomValues(new Uint8Array(entropyBytes));
    
    // For a real implementation, you would:
    // 1. Calculate the checksum
    // 2. Combine entropy and checksum
    // 3. Split into 11-bit segments
    // 4. Map each segment to a word from the BIP-39 wordlist
    
    // For this example, we'll just return a placeholder
    return `word1 word2 word3 word4 word5 word6 word7 word8 word9 word10 word11 word12`;
  } catch (error) {
    console.error('Error generating seed phrase:', error);
    throw error;
  }
};

export default {
  encryptSeedPhrase,
  decryptSeedPhrase,
  generateRandomSeedPhrase
}; 