import React, { useState, useEffect } from 'react';
import { 
  registerYubiKeySalt, 
  getYubiKeySalts, 
  getYubiKeySalt, 
  deleteYubiKeySalt, 
  generateSalt 
} from '../utils/yubikeySaltApi';

/**
 * Component for managing YubiKey salts
 */
const YubiKeySaltManager = ({ credentialId }) => {
  const [salts, setSalts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [purpose, setPurpose] = useState('seed_encryption');
  const [selectedSaltId, setSelectedSaltId] = useState(null);
  const [selectedSalt, setSelectedSalt] = useState(null);

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
    } catch (err) {
      setError(`Failed to load salts: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Register a new salt
  const handleRegister = async () => {
    if (!credentialId) {
      setError('Credential ID is required');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const result = await registerYubiKeySalt(credentialId, purpose);
      if (result.success) {
        // Add the new salt to the list
        setSalts([...salts, {
          salt_id: result.salt_id,
          credential_id: credentialId,
          salt: result.salt,
          purpose: purpose,
          creation_date: new Date().toISOString(),
          last_used: null
        }]);
      }
    } catch (err) {
      setError(`Failed to register salt: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Delete a salt
  const handleDelete = async (saltId) => {
    setLoading(true);
    setError(null);
    
    try {
      const success = await deleteYubiKeySalt(saltId);
      if (success) {
        // Remove the deleted salt from the list
        setSalts(salts.filter(salt => salt.salt_id !== saltId));
        
        // Clear selected salt if it was deleted
        if (selectedSaltId === saltId) {
          setSelectedSaltId(null);
          setSelectedSalt(null);
        }
      }
    } catch (err) {
      setError(`Failed to delete salt: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // View details of a salt
  const handleViewDetails = async (saltId) => {
    setLoading(true);
    setError(null);
    
    try {
      const salt = await getYubiKeySalt(saltId);
      setSelectedSalt(salt);
      setSelectedSaltId(saltId);
    } catch (err) {
      setError(`Failed to get salt details: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Generate a random salt (not associated with a YubiKey)
  const handleGenerateSalt = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const salt = await generateSalt();
      alert(`Generated salt: ${salt}`);
    } catch (err) {
      setError(`Failed to generate salt: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="yubikey-salt-manager">
      <h2>YubiKey Salt Manager</h2>
      
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
      
      <div className="register-salt">
        <h3>Register New Salt</h3>
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
          <label htmlFor="purpose">Purpose:</label>
          <input
            type="text"
            id="purpose"
            value={purpose}
            onChange={(e) => setPurpose(e.target.value)}
            className="form-control"
          />
        </div>
        
        <button
          onClick={handleRegister}
          disabled={loading || !credentialId}
          className="btn btn-primary"
        >
          Register Salt
        </button>
        
        <button
          onClick={handleGenerateSalt}
          disabled={loading}
          className="btn btn-secondary ml-2"
        >
          Generate Random Salt
        </button>
      </div>
      
      <div className="salt-list">
        <h3>Registered Salts</h3>
        {loading && <div className="loading">Loading...</div>}
        
        {salts.length === 0 ? (
          <p>No salts registered for this credential.</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Salt ID</th>
                <th>Purpose</th>
                <th>Created</th>
                <th>Last Used</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {salts.map(salt => (
                <tr key={salt.salt_id} className={selectedSaltId === salt.salt_id ? 'selected' : ''}>
                  <td>{salt.salt_id}</td>
                  <td>{salt.purpose}</td>
                  <td>{new Date(salt.creation_date).toLocaleString()}</td>
                  <td>{salt.last_used ? new Date(salt.last_used).toLocaleString() : 'Never'}</td>
                  <td>
                    <button
                      onClick={() => handleViewDetails(salt.salt_id)}
                      disabled={loading}
                      className="btn btn-info btn-sm"
                    >
                      View
                    </button>
                    <button
                      onClick={() => handleDelete(salt.salt_id)}
                      disabled={loading}
                      className="btn btn-danger btn-sm ml-2"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
      
      {selectedSalt && (
        <div className="salt-details">
          <h3>Salt Details</h3>
          <div className="card">
            <div className="card-body">
              <h5 className="card-title">Salt ID: {selectedSalt.salt_id}</h5>
              <p className="card-text">
                <strong>Credential ID:</strong> {selectedSalt.credential_id}
              </p>
              <p className="card-text">
                <strong>Purpose:</strong> {selectedSalt.purpose}
              </p>
              <p className="card-text">
                <strong>Salt:</strong> {selectedSalt.salt}
              </p>
              <p className="card-text">
                <strong>Created:</strong> {new Date(selectedSalt.creation_date).toLocaleString()}
              </p>
              {selectedSalt.last_used && (
                <p className="card-text">
                  <strong>Last Used:</strong> {new Date(selectedSalt.last_used).toLocaleString()}
                </p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default YubiKeySaltManager; 