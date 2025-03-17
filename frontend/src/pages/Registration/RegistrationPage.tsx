import React, { useState } from 'react';
import { startRegistration } from '../../services/webAuthnService';

const RegistrationPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [userId, setUserId] = useState('');
  const [isRegistering, setIsRegistering] = useState(false);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!username.trim()) {
      setError('Username is required');
      return;
    }

    setError('');
    setMessage('');
    setIsRegistering(true);

    try {
      // Call the WebAuthn service to start registration
      const newUserId = await startRegistration(username);
      setUserId(newUserId);
      setMessage(`Registration successful! Your user ID is: ${newUserId}`);
    } catch (error) {
      console.error('Registration error:', error);
      setError(error instanceof Error ? error.message : 'Registration failed. Please try again.');
    } finally {
      setIsRegistering(false);
    }
  };

  return (
    <div className="card">
      <h2 className="text-xl font-semibold mb-4">Register YubiKey</h2>
      <p className="mb-4">Enter a username and click the button below to register your YubiKey.</p>

      {error && (
        <div className="p-4 mb-4 bg-red-50 border border-red-200 text-red-800 rounded">{error}</div>
      )}

      {message && (
        <div className="p-4 mb-4 bg-green-50 border border-green-200 text-green-800 rounded">
          {message}
        </div>
      )}

      {userId && (
        <div className="p-4 mb-4 bg-blue-50 border border-blue-200 text-blue-800 rounded">
          <h3 className="font-semibold mb-2">Important!</h3>
          <p>Save your User ID: <span className="font-mono bg-gray-100 p-1">{userId}</span></p>
          <p className="mt-2 text-sm">You will need this ID to authenticate and retrieve your seed phrase.</p>
        </div>
      )}

      <form onSubmit={handleRegister} className="mt-4">
        <div className="mb-4">
          <label htmlFor="username" className="block mb-2 text-sm font-medium">
            Username
          </label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter your username"
            disabled={isRegistering}
          />
        </div>

        <button 
          type="submit" 
          className={`btn-primary w-full ${isRegistering ? 'opacity-75 cursor-not-allowed' : ''}`}
          disabled={isRegistering}
        >
          {isRegistering ? 'Registering...' : 'Register YubiKey'}
        </button>
      </form>
    </div>
  );
};

export default RegistrationPage;
