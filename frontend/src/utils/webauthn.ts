/**
 * Types for WebAuthn API
 */
export interface PublicKeyCredentialWithAttestationJSON {
  id: string;
  rawId: string;
  type: string;
  response: {
    attestationObject: string;
    clientDataJSON: string;
  };
}

export interface PublicKeyCredentialWithAssertionJSON {
  id: string;
  rawId: string;
  type: string;
  response: {
    authenticatorData: string;
    clientDataJSON: string;
    signature: string;
    userHandle: string | null;
  };
}

export interface ServerCredentialCreationOptions {
  publicKey: {
    challenge: string;
    rp: {
      name: string;
      id?: string;
    };
    user: {
      id: string;
      name: string;
      displayName: string;
    };
    pubKeyCredParams: Array<{
      type: string;
      alg: number;
    }>;
    timeout?: number;
    excludeCredentials?: Array<{
      id: string;
      type: string;
      transports?: string[];
    }>;
    authenticatorSelection?: {
      authenticatorAttachment?: string;
      requireResidentKey?: boolean;
      residentKey?: string;
      userVerification?: string;
    };
    attestation?: string;
    extensions?: Record<string, unknown>;
  };
}

export interface ServerCredentialRequestOptions {
  publicKey: {
    challenge: string;
    timeout?: number;
    rpId?: string;
    allowCredentials?: Array<{
      id: string;
      type: string;
      transports?: string[];
    }>;
    userVerification?: string;
    extensions?: Record<string, unknown>;
  };
}

/**
 * Converts a base64 string to an ArrayBuffer
 * @param base64 - Base64 encoded string
 * @returns ArrayBuffer representation
 */
export function base64ToArrayBuffer(base64: string): ArrayBuffer {
  const binary = window.atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes.buffer;
}

/**
 * Converts an ArrayBuffer to a base64 string
 * @param buffer - ArrayBuffer to convert
 * @returns Base64 encoded string
 */
export function arrayBufferToBase64(buffer: ArrayBuffer): string {
  // Use Array.from instead of spread to avoid TypeScript ES5 compatibility issues
  const binary = String.fromCharCode.apply(null, Array.from(new Uint8Array(buffer)));
  return window.btoa(binary);
}

/**
 * Prepares WebAuthn credential creation options by converting base64 strings to ArrayBuffers
 * @param credentialCreationOptions - Options from the server
 * @returns Prepared options for WebAuthn API
 */
export function preparePublicKeyCredentialCreationOptions(
  credentialCreationOptions: ServerCredentialCreationOptions
): PublicKeyCredentialCreationOptions {
  // Create a new object with the necessary type conversions
  const publicKey = credentialCreationOptions.publicKey;

  // Create the output object
  const output = {
    // Copy most properties directly
    rp: publicKey.rp,
    pubKeyCredParams: publicKey.pubKeyCredParams,
    timeout: publicKey.timeout,
    attestation: publicKey.attestation,
    extensions: publicKey.extensions,
    authenticatorSelection: publicKey.authenticatorSelection,

    // Convert buffers
    challenge: base64ToArrayBuffer(publicKey.challenge),
    user: {
      name: publicKey.user.name,
      displayName: publicKey.user.displayName,
      id: base64ToArrayBuffer(publicKey.user.id),
    },
  };

  // Convert excludeCredentials if present
  if (publicKey.excludeCredentials) {
    // Type assertion needed due to ArrayBuffer vs string type difference
    (output as Record<string, unknown>).excludeCredentials = publicKey.excludeCredentials.map(
      (credential) => ({
        type: credential.type,
        transports: credential.transports,
        id: base64ToArrayBuffer(credential.id),
      })
    );
  }

  return output as unknown as PublicKeyCredentialCreationOptions;
}

/**
 * Prepares WebAuthn credential request options by converting base64 strings to ArrayBuffers
 * @param credentialRequestOptions - Options from the server
 * @returns Prepared options for WebAuthn API
 */
export function preparePublicKeyCredentialRequestOptions(
  credentialRequestOptions: ServerCredentialRequestOptions
): PublicKeyCredentialRequestOptions {
  // Create a new object with the necessary type conversions
  const publicKey = credentialRequestOptions.publicKey;

  // Create the output object
  const output = {
    // Copy most properties directly
    timeout: publicKey.timeout,
    rpId: publicKey.rpId,
    extensions: publicKey.extensions,
    userVerification: publicKey.userVerification,

    // Convert buffer
    challenge: base64ToArrayBuffer(publicKey.challenge),
  };

  // Convert allowCredentials if present
  if (publicKey.allowCredentials) {
    // Type assertion needed due to ArrayBuffer vs string type difference
    (output as Record<string, unknown>).allowCredentials = publicKey.allowCredentials.map(
      (credential) => ({
        type: credential.type,
        transports: credential.transports,
        id: base64ToArrayBuffer(credential.id),
      })
    );
  }

  return output as unknown as PublicKeyCredentialRequestOptions;
}

/**
 * Formats a credential for sending to the server
 * @param credential - The credential from navigator.credentials.create()
 * @returns Formatted credential for API submission
 */
export function formatCredentialForServer(
  credential: PublicKeyCredential
): PublicKeyCredentialWithAttestationJSON {
  return {
    id: credential.id,
    rawId: arrayBufferToBase64(credential.rawId as ArrayBuffer),
    type: credential.type,
    response: {
      attestationObject: arrayBufferToBase64(
        (credential.response as AuthenticatorAttestationResponse).attestationObject
      ),
      clientDataJSON: arrayBufferToBase64(credential.response.clientDataJSON),
    },
  };
}

/**
 * Formats an assertion for sending to the server
 * @param credential - The credential from navigator.credentials.get()
 * @returns Formatted assertion for API submission
 */
export function formatAssertionForServer(
  credential: PublicKeyCredential
): PublicKeyCredentialWithAssertionJSON {
  return {
    id: credential.id,
    rawId: arrayBufferToBase64(credential.rawId as ArrayBuffer),
    type: credential.type,
    response: {
      authenticatorData: arrayBufferToBase64(
        (credential.response as AuthenticatorAssertionResponse).authenticatorData
      ),
      clientDataJSON: arrayBufferToBase64(credential.response.clientDataJSON),
      signature: arrayBufferToBase64(
        (credential.response as AuthenticatorAssertionResponse).signature
      ),
      userHandle: (credential.response as AuthenticatorAssertionResponse).userHandle
        ? arrayBufferToBase64(
            (credential.response as AuthenticatorAssertionResponse).userHandle as ArrayBuffer
          )
        : null,
    },
  };
}
