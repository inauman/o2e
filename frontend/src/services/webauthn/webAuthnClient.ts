import apiClient from '../api/apiClient';
import {
  preparePublicKeyCredentialCreationOptions,
  preparePublicKeyCredentialRequestOptions,
  formatCredentialForServer,
  formatAssertionForServer,
} from '../../utils/webauthn';

/**
 * Handles WebAuthn registration process
 * @param username - The username to register
 * @returns Promise resolving to the registration response
 */
export const startRegistration = async (username: string) => {
  try {
    // 1. Request registration options from server
    const optionsResponse = await apiClient.post('/webauthn/register/begin', { username });
    const credentialCreationOptions = optionsResponse.data;

    // 2. Convert base64 options to ArrayBuffer for WebAuthn API
    const publicKey = preparePublicKeyCredentialCreationOptions(credentialCreationOptions);

    // 3. Create credential with WebAuthn browser API
    const credential = (await navigator.credentials.create({
      publicKey,
    })) as PublicKeyCredential;

    // 4. Prepare credential for sending to server
    const credentialResponse = formatCredentialForServer(credential);

    // 5. Send the response to server to complete registration
    return await apiClient.post('/webauthn/register/complete', credentialResponse);
  } catch (error) {
    console.error('WebAuthn Registration Error:', error);
    throw error;
  }
};

/**
 * Handles WebAuthn authentication process
 * @param username - The username to authenticate
 * @returns Promise resolving to the authentication response
 */
export const startAuthentication = async (username: string) => {
  try {
    // 1. Request authentication options from server
    const optionsResponse = await apiClient.post('/webauthn/authenticate/begin', { username });
    const credentialRequestOptions = optionsResponse.data;

    // 2. Convert base64 options to ArrayBuffer for WebAuthn API
    const publicKey = preparePublicKeyCredentialRequestOptions(credentialRequestOptions);

    // 3. Get credential with WebAuthn browser API
    const credential = (await navigator.credentials.get({
      publicKey,
    })) as PublicKeyCredential;

    // 4. Prepare assertion for sending to server
    const assertionResponse = formatAssertionForServer(credential);

    // 5. Send the response to server to complete authentication
    return await apiClient.post('/webauthn/authenticate/complete', assertionResponse);
  } catch (error) {
    console.error('WebAuthn Authentication Error:', error);
    throw error;
  }
};
