/**
 * Utility functions for interacting with the YubiKey Salt API.
 */
import axios from 'axios';
import { getAuthToken } from './auth';

// Base URL for API requests
const API_BASE_URL = '/api/v1/yubikeys';

/**
 * Configure axios with authentication headers
 * @returns {Object} Axios instance with auth headers
 */
const getAuthenticatedAxios = () => {
  const token = getAuthToken();
  return axios.create({
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
};

/**
 * Register a new YubiKey salt
 * @param {string} credentialId - The credential ID of the YubiKey
 * @param {string} purpose - Optional purpose of the salt
 * @returns {Promise<Object>} The created salt
 */
export const registerYubiKeySalt = async (credentialId, purpose = 'seed_encryption') => {
  try {
    const api = getAuthenticatedAxios();
    const response = await api.post(`${API_BASE_URL}/register`, {
      credential_id: credentialId,
      purpose
    });
    return response.data;
  } catch (error) {
    console.error('Error registering YubiKey salt:', error);
    throw error;
  }
};

/**
 * Get all salts for a YubiKey credential
 * @param {string} credentialId - The credential ID of the YubiKey
 * @param {string} purpose - Optional purpose to filter by
 * @returns {Promise<Array>} Array of salts
 */
export const getYubiKeySalts = async (credentialId, purpose = null) => {
  try {
    const api = getAuthenticatedAxios();
    let url = `${API_BASE_URL}/salts?credential_id=${encodeURIComponent(credentialId)}`;
    
    if (purpose) {
      url += `&purpose=${encodeURIComponent(purpose)}`;
    }
    
    const response = await api.get(url);
    return response.data.salts;
  } catch (error) {
    console.error('Error getting YubiKey salts:', error);
    throw error;
  }
};

/**
 * Get a specific YubiKey salt by ID
 * @param {string} saltId - The ID of the salt to retrieve
 * @returns {Promise<Object>} The salt object
 */
export const getYubiKeySalt = async (saltId) => {
  try {
    const api = getAuthenticatedAxios();
    const response = await api.get(`${API_BASE_URL}/salt/${saltId}`);
    return response.data.salt;
  } catch (error) {
    console.error('Error getting YubiKey salt:', error);
    throw error;
  }
};

/**
 * Delete a YubiKey salt
 * @param {string} saltId - The ID of the salt to delete
 * @returns {Promise<boolean>} True if deletion was successful
 */
export const deleteYubiKeySalt = async (saltId) => {
  try {
    const api = getAuthenticatedAxios();
    const response = await api.delete(`${API_BASE_URL}/salt/${saltId}`);
    return response.data.success;
  } catch (error) {
    console.error('Error deleting YubiKey salt:', error);
    throw error;
  }
};

/**
 * Generate a random salt
 * @returns {Promise<string>} The generated salt in hex format
 */
export const generateSalt = async () => {
  try {
    const api = getAuthenticatedAxios();
    const response = await api.post(`${API_BASE_URL}/generate-salt`);
    return response.data.salt;
  } catch (error) {
    console.error('Error generating salt:', error);
    throw error;
  }
};

/**
 * Convert a hex string to a Uint8Array
 * @param {string} hexString - The hex string to convert
 * @returns {Uint8Array} The resulting byte array
 */
export const hexToBytes = (hexString) => {
  const bytes = new Uint8Array(hexString.length / 2);
  for (let i = 0; i < hexString.length; i += 2) {
    bytes[i / 2] = parseInt(hexString.substring(i, i + 2), 16);
  }
  return bytes;
};

/**
 * Convert a Uint8Array to a hex string
 * @param {Uint8Array} bytes - The byte array to convert
 * @returns {string} The resulting hex string
 */
export const bytesToHex = (bytes) => {
  return Array.from(bytes)
    .map(byte => byte.toString(16).padStart(2, '0'))
    .join('');
};

/**
 * Derive an encryption key from a YubiKey credential and salt
 * @param {string} credentialId - The credential ID of the YubiKey
 * @param {string} saltHex - The salt in hex format
 * @param {Function} signCallback - Function to sign data with the YubiKey
 * @returns {Promise<Uint8Array>} The derived encryption key
 */
export const deriveEncryptionKey = async (credentialId, saltHex, signCallback) => {
  try {
    // Convert salt from hex to bytes
    const salt = hexToBytes(saltHex);
    
    // Create data to sign (credential ID + salt)
    const dataToSign = new Uint8Array(credentialId.length + salt.length);
    dataToSign.set(new TextEncoder().encode(credentialId), 0);
    dataToSign.set(salt, credentialId.length);
    
    // Sign the data with the YubiKey
    const signature = await signCallback(dataToSign);
    
    // Use the signature as the encryption key
    return signature;
  } catch (error) {
    console.error('Error deriving encryption key:', error);
    throw error;
  }
};

export default {
  registerYubiKeySalt,
  getYubiKeySalts,
  getYubiKeySalt,
  deleteYubiKeySalt,
  generateSalt,
  hexToBytes,
  bytesToHex,
  deriveEncryptionKey
}; 