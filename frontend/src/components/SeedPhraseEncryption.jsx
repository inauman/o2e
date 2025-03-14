import React, { useState, useEffect } from 'react';
import { 
  registerYubiKeySalt, 
  getYubiKeySalts, 
  getYubiKeySalt 
} from '../utils/yubikeySaltApi';
import { 
  encryptSeedPhrase, 
  decryptSeedPhrase, 
  generateRandomSeedPhrase 
} from '../utils/seedEncryption';

/**
 * Component for encrypting and decrypting seed phrases using YubiKey-derived keys
 */
const SeedPhraseEncryption = ({ credentialId, signCallback }) => {
  const [salts, setSalts] = useState([]);
  const [selectedSaltId, setSelectedSaltId] = useState('');
  const [seedPhrase, setSeedPhrase] = useState('');
  const [encryptedSeed, setEncryptedSeed] = useState('');
  const [decryptedSeed, setDecryptedSeed] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);

  // Load salts when credential ID changes
  useEffect(() => {
    if (credentialId) {
      loadSalts();
    }
  }, [credentialId]);

  // Load salts for the current credential ID
  const loadSalts = async () => {
    if (!credentialId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const saltList = await getYubiKeySalts(credentialId);
      setSalts(saltList);
      
      // Select the first salt by default
      if (saltList.length > 0 && !selectedSaltId) {
        setSelectedSaltId(saltList[0].salt_id);
      }
    } catch (err) {
      setError(`Failed to load salts: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Generate a random seed phrase
  const handleGenerateSeed = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const seed = await generateRandomSeedPhrase();
      setSeedPhrase(seed);
      setMessage('Random seed phrase generated');
    } catch (err) {
      setError(`Failed to generate seed phrase: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Encrypt the seed phrase
  const handleEncrypt = async () => {
    if (!credentialId) {
      setError('Credential ID is required');
      return;
    }
    
    if (!selectedSaltId) {
      setError('Please select a salt');
      return;
    }
    
    if (!seedPhrase) {
      setError('Seed phrase is required');
      return;
    }
    
    if (!signCallback) {
      setError('Sign callback is required');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      // Get the selected salt
      const salt = await getYubiKeySalt(selectedSaltId);
      
      // Encrypt the seed phrase
      const encrypted = await encryptSeedPhrase(
        seedPhrase,
        credentialId,
        salt.salt,
        signCallback
      );
      
      setEncryptedSeed(encrypted);
      setMessage('Seed phrase encrypted successfully');
    } catch (err) {
      setError(`Failed to encrypt seed phrase: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Decrypt the seed phrase
  const handleDecrypt = async () => {
    if (!credentialId) {
      setError('Credential ID is required');
      return;
    }
    
    if (!selectedSaltId) {
      setError('Please select a salt');
      return;
    }
    
    if (!encryptedSeed) {
      setError('Encrypted seed is required');
      return;
    }
    
    if (!signCallback) {
      setError('Sign callback is required');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      // Get the selected salt
      const salt = await getYubiKeySalt(selectedSaltId);
      
      // Decrypt the seed phrase
      const decrypted = await decryptSeedPhrase(
        encryptedSeed,
        credentialId,
        salt.salt,
        signCallback
      );
      
      setDecryptedSeed(decrypted);
      setMessage('Seed phrase decrypted successfully');
    } catch (err) {
      setError(`Failed to decrypt seed phrase: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Register a new salt
  const handleRegisterSalt = async () => {
    if (!credentialId) {
      setError('Credential ID is required');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const result = await registerYubiKeySalt(credentialId);
      if (result.success) {
        await loadSalts();
        setSelectedSaltId(result.salt_id);
        setMessage('New salt registered successfully');
      }
    } catch (err) {
      setError(`Failed to register salt: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="seed-phrase-encryption">
      <h2>Seed Phrase Encryption with YubiKey</h2>
      
      {error && (
        <div className="alert alert-danger">
          {error}
        </div>
      )}
      
      {message && (
        <div className="alert alert-success">
          {message}
        </div>
      )}
      
      <div className="card mb-4">
        <div className="card-header">
          <h3>YubiKey Information</h3>
        </div>
        <div className="card-body">
          <div className="form-group">
            <label htmlFor="credential-id">Credential ID:</label>
            <input
              type="text"
              id="credential-id"
              value={credentialId || ''}
              readOnly
              className="form-control"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="salt-select">Select Salt:</label>
            <select
              id="salt-select"
              value={selectedSaltId}
              onChange={(e) => setSelectedSaltId(e.target.value)}
              className="form-control"
              disabled={loading || salts.length === 0}
            >
              <option value="">-- Select a salt --</option>
              {salts.map(salt => (
                <option key={salt.salt_id} value={salt.salt_id}>
                  {salt.salt_id} ({salt.purpose})
                </option>
              ))}
            </select>
          </div>
          
          <button
            onClick={handleRegisterSalt}
            disabled={loading || !credentialId}
            className="btn btn-primary"
          >
            Register New Salt
          </button>
        </div>
      </div>
      
      <div className="card mb-4">
        <div className="card-header">
          <h3>Seed Phrase</h3>
        </div>
        <div className="card-body">
          <div className="form-group">
            <label htmlFor="seed-phrase">Seed Phrase:</label>
            <textarea
              id="seed-phrase"
              value={seedPhrase}
              onChange={(e) => setSeedPhrase(e.target.value)}
              className="form-control"
              rows="3"
              placeholder="Enter your seed phrase or generate a random one"
            />
          </div>
          
          <button
            onClick={handleGenerateSeed}
            disabled={loading}
            className="btn btn-secondary"
          >
            Generate Random Seed
          </button>
          
          <button
            onClick={handleEncrypt}
            disabled={loading || !credentialId || !selectedSaltId || !seedPhrase}
            className="btn btn-primary ml-2"
          >
            Encrypt Seed
          </button>
        </div>
      </div>
      
      <div className="card mb-4">
        <div className="card-header">
          <h3>Encrypted Seed</h3>
        </div>
        <div className="card-body">
          <div className="form-group">
            <label htmlFor="encrypted-seed">Encrypted Seed (Hex):</label>
            <textarea
              id="encrypted-seed"
              value={encryptedSeed}
              onChange={(e) => setEncryptedSeed(e.target.value)}
              className="form-control"
              rows="3"
              placeholder="Encrypted seed will appear here"
            />
          </div>
          
          <button
            onClick={handleDecrypt}
            disabled={loading || !credentialId || !selectedSaltId || !encryptedSeed}
            className="btn btn-primary"
          >
            Decrypt Seed
          </button>
        </div>
      </div>
      
      <div className="card">
        <div className="card-header">
          <h3>Decrypted Seed</h3>
        </div>
        <div className="card-body">
          <div className="form-group">
            <label htmlFor="decrypted-seed">Decrypted Seed Phrase:</label>
            <textarea
              id="decrypted-seed"
              value={decryptedSeed}
              readOnly
              className="form-control"
              rows="3"
              placeholder="Decrypted seed will appear here"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default SeedPhraseEncryption; 