import React, { useState } from 'react';
import { startAuthentication } from '../../services/webAuthnService';

const AuthenticationPage: React.FC = () => {
  const [userId, setUserId] = useState('');
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [seedPhrase, setSeedPhrase] = useState('');
  const [isAuthenticating, setIsAuthenticating] = useState(false);

  const handleAuthenticate = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!userId.trim()) {
      setError('User ID is required');
      return;
    }

    setError('');
    setMessage('');
    setSeedPhrase('');
    setIsAuthenticating(true);

    try {
      // Call the WebAuthn service to start authentication
      const retrievedSeedPhrase = await startAuthentication(userId);
      setSeedPhrase(retrievedSeedPhrase);
      setMessage('Authentication successful! Your seed phrase has been retrieved.');
    } catch (error) {
      console.error('Authentication error:', error);
      setError(error instanceof Error ? error.message : 'Authentication failed. Please try again.');
    } finally {
      setIsAuthenticating(false);
    }
  };

  return (
    <div className="card">
      <h2 className="text-xl font-semibold mb-4">Authenticate with YubiKey</h2>
      <p className="mb-4">
        Enter your User ID and click the button below to authenticate with your YubiKey.
      </p>

      {error && (
        <div className="p-4 mb-4 bg-red-50 border border-red-200 text-red-800 rounded">{error}</div>
      )}

      {message && (
        <div className="p-4 mb-4 bg-green-50 border border-green-200 text-green-800 rounded">
          {message}
        </div>
      )}

      {seedPhrase && (
        <div className="p-4 mb-4 bg-blue-50 border border-blue-200 text-blue-800 rounded">
          <h3 className="font-semibold mb-2">Your Seed Phrase:</h3>
          <p className="font-mono bg-gray-100 p-3 rounded break-words">{seedPhrase}</p>
          <p className="mt-2 text-sm text-red-600">
            <strong>Warning:</strong> Never share your seed phrase with anyone!
          </p>
        </div>
      )}

      <form onSubmit={handleAuthenticate} className="mt-4">
        <div className="mb-4">
          <label htmlFor="userId" className="block mb-2 text-sm font-medium">
            User ID
          </label>
          <input
            type="text"
            id="userId"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter your User ID"
            disabled={isAuthenticating}
          />
        </div>

        <button
          type="submit"
          className={`btn-primary w-full ${isAuthenticating ? 'opacity-75 cursor-not-allowed' : ''}`}
          disabled={isAuthenticating}>
          {isAuthenticating ? 'Authenticating...' : 'Authenticate with YubiKey'}
        </button>
      </form>
    </div>
  );
};

export default AuthenticationPage;
