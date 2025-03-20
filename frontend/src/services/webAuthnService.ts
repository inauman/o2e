/**
 * Service for handling WebAuthn operations
 */

// Convert base64url to ArrayBuffer
const base64urlToArrayBuffer = (base64url: string): ArrayBuffer => {
  if (!base64url) {
    console.error('base64url is undefined or null');
    throw new Error('Cannot convert undefined or null to ArrayBuffer');
  }

  const base64 = base64url.replace(/-/g, '+').replace(/_/g, '/');
  const binaryString = window.atob(base64);
  const bytes = new Uint8Array(binaryString.length);
  for (let i = 0; i < binaryString.length; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return bytes.buffer;
};

// Convert ArrayBuffer to base64url
const arrayBufferToBase64url = (buffer: ArrayBuffer): string => {
  const bytes = new Uint8Array(buffer);
  let binary = '';
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  const base64 = window.btoa(binary);
  return base64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
};

/**
 * Start the registration process
 * @param username The username to register
 * @returns The user ID if registration is successful
 */
export const startRegistration = async (username: string): Promise<string> => {
  try {
    console.log(`Starting WebAuthn registration for username: ${username}`);
    
    // Create form data for backend compatibility
    const formData = new FormData();
    formData.append('username', username);
    
    // 1. Get registration options from server - try with form data
    console.log('Sending registration request to /api/auth/register/begin');
    const optionsResponse = await fetch('http://localhost:5001/api/auth/register/begin', {
      method: 'POST',
      body: formData,
      credentials: 'include',
    });

    console.log('Registration options response status:', optionsResponse.status);
    
    if (!optionsResponse.ok) {
      const errorText = await optionsResponse.text();
      console.error('Error response text:', errorText);
      try {
        const errorData = JSON.parse(errorText);
        throw new Error(errorData.error || 'Failed to start registration');
      } catch (e) {
        throw new Error(`Failed to start registration: ${errorText}`);
      }
    }

    const responseJson = await optionsResponse.json();
    console.log('Registration options received:', responseJson);
    
    // Extract the publicKey options from the response
    const options = responseJson.publicKey || responseJson;
    console.log('Using registration options:', options);
    
    if (!options || !options.challenge || !options.user || !options.user.id) {
      console.error('Invalid registration options:', options);
      throw new Error('The server returned invalid registration options');
    }
    
    // 2. Convert base64url challenge to ArrayBuffer
    const publicKeyCredentialCreationOptions = {
      ...options,
      challenge: base64urlToArrayBuffer(options.challenge),
      user: {
        ...options.user,
        id: base64urlToArrayBuffer(options.user.id),
      },
    };
    
    // 3. Create credentials
    console.log('Calling navigator.credentials.create with options:', publicKeyCredentialCreationOptions);
    const credential = await navigator.credentials.create({
      publicKey: publicKeyCredentialCreationOptions as PublicKeyCredentialCreationOptions,
    }) as PublicKeyCredential;

    console.log('Credential created:', credential);

    // 4. Convert credential to JSON for server
    const credentialResponse = {
      id: credential.id,
      rawId: arrayBufferToBase64url(credential.rawId),
      response: {
        clientDataJSON: arrayBufferToBase64url(
          (credential.response as AuthenticatorAttestationResponse).clientDataJSON
        ),
        attestationObject: arrayBufferToBase64url(
          (credential.response as AuthenticatorAttestationResponse).attestationObject
        ),
        transports: (credential.response as AuthenticatorAttestationResponse).getTransports?.() || ['usb'],
      },
      type: credential.type,
      clientExtensionResults: credential.getClientExtensionResults(),
    };

    // 5. Complete registration
    console.log('Sending credential to /api/auth/register/complete:', credentialResponse);
    const completeResponse = await fetch('http://localhost:5001/api/auth/register/complete', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentialResponse),
      credentials: 'include',
    });

    console.log('Registration completion response status:', completeResponse.status);
    
    if (!completeResponse.ok) {
      const errorText = await completeResponse.text();
      console.error('Error response text:', errorText);
      try {
        const errorData = JSON.parse(errorText);
        throw new Error(errorData.error || 'Failed to complete registration');
      } catch (e) {
        throw new Error(`Failed to complete registration: ${errorText}`);
      }
    }

    const result = await completeResponse.json();
    console.log('Registration completion data:', result);
    
    if (result.success) {
      // Add proper padding to base64url string
      const padBase64 = (str: string) => {
        const padding = '='.repeat((4 - str.length % 4) % 4);
        return str + padding;
      };

      // Decode the user ID from base64url
      const userIdBase64 = padBase64(result.user_id);
      const userIdDecoded = atob(userIdBase64.replace(/-/g, '+').replace(/_/g, '/'));
      
      return userIdDecoded;
    } else {
      throw new Error(result.error || 'Registration failed for unknown reason');
    }
  } catch (error) {
    console.error('WebAuthn registration error:', error);
    throw error;
  }
};

/**
 * Start the authentication process
 * @param userId The user ID to authenticate (username in this case)
 * @returns The seed phrase if authentication is successful
 */
export const startAuthentication = async (userId: string): Promise<string> => {
  try {
    console.log(`Starting WebAuthn authentication for userId: ${userId}`);
    
    // Create form data for backend compatibility
    const formData = new FormData();
    formData.append('username', userId);
    
    // 1. Get authentication options from server
    console.log('Sending authentication request to /api/auth/authenticate/begin');
    const optionsResponse = await fetch('http://localhost:5001/api/auth/authenticate/begin', {
      method: 'POST',
      body: formData,
      credentials: 'include',
    });

    console.log('Authentication options response status:', optionsResponse.status);
    
    if (!optionsResponse.ok) {
      const errorText = await optionsResponse.text();
      console.error('Error response text:', errorText);
      try {
        const errorData = JSON.parse(errorText);
        throw new Error(errorData.error || 'Failed to start authentication');
      } catch (e) {
        throw new Error(`Failed to start authentication: ${errorText}`);
      }
    }

    const responseJson = await optionsResponse.json();
    console.log('Authentication options received:', responseJson);
    
    // Extract the publicKey options from the response
    const options = responseJson.publicKey || responseJson;
    console.log('Using authentication options:', options);
    
    if (!options || !options.challenge) {
      console.error('Invalid authentication options:', options);
      throw new Error('The server returned invalid authentication options');
    }
    
    // 2. Convert base64url challenge to ArrayBuffer
    const publicKeyCredentialRequestOptions = {
      ...options,
      challenge: base64urlToArrayBuffer(options.challenge),
    };
    
    // 3. Convert allowed credentials to use ArrayBuffer
    if (publicKeyCredentialRequestOptions.allowCredentials) {
      publicKeyCredentialRequestOptions.allowCredentials = publicKeyCredentialRequestOptions.allowCredentials.map(
        (credential: any) => ({
          ...credential,
          id: base64urlToArrayBuffer(credential.id),
        })
      );
    }

    // 4. Get credentials
    console.log('Calling navigator.credentials.get with options:', publicKeyCredentialRequestOptions);
    const credential = await navigator.credentials.get({
      publicKey: publicKeyCredentialRequestOptions as PublicKeyCredentialRequestOptions,
    }) as PublicKeyCredential;

    console.log('Credential received:', credential);

    // 5. Convert credential to JSON for server
    const credentialResponse = {
      id: credential.id,
      rawId: arrayBufferToBase64url(credential.rawId),
      response: {
        clientDataJSON: arrayBufferToBase64url(
          (credential.response as AuthenticatorAssertionResponse).clientDataJSON
        ),
        authenticatorData: arrayBufferToBase64url(
          (credential.response as AuthenticatorAssertionResponse).authenticatorData
        ),
        signature: arrayBufferToBase64url(
          (credential.response as AuthenticatorAssertionResponse).signature
        ),
        userHandle: (credential.response as AuthenticatorAssertionResponse).userHandle
          ? arrayBufferToBase64url((credential.response as AuthenticatorAssertionResponse).userHandle as ArrayBuffer)
          : null,
      },
      type: credential.type,
      clientExtensionResults: credential.getClientExtensionResults(),
    };

    // 6. Complete authentication
    console.log('Sending credential to /api/auth/authenticate/complete:', credentialResponse);
    const completeResponse = await fetch('http://localhost:5001/api/auth/authenticate/complete', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentialResponse),
      credentials: 'include',
    });

    console.log('Authentication completion response status:', completeResponse.status);
    
    if (!completeResponse.ok) {
      const errorText = await completeResponse.text();
      console.error('Error response text:', errorText);
      try {
        const errorData = JSON.parse(errorText);
        throw new Error(errorData.error || 'Failed to complete authentication');
      } catch (e) {
        throw new Error(`Failed to complete authentication: ${errorText}`);
      }
    }

    const result = await completeResponse.json();
    console.log('Authentication completion data:', result);
    
    if (result.success) {
      // Backend doesn't return seed phrase directly, it sets a session
      // For testing purposes, we'll just return a mock seed phrase
      return "test word1 word2 word3 word4 word5 word6 word7 word8 word9 word10 word11 word12";
    } else {
      throw new Error(result.error || 'Authentication failed for unknown reason');
    }
  } catch (error) {
    console.error('WebAuthn authentication error:', error);
    throw error;
  }
}; 