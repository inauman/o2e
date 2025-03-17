import { 
  registerYubiKeySalt, 
  getYubiKeySalts, 
  getYubiKeySalt,
  deleteYubiKeySalt
} from '../../utils/yubikeySaltApi';
import axios from 'axios';

// Mock axios
jest.mock('axios');

describe('YubiKey Salt API Utilities', () => {
  const mockCredentialId = 'test-credential-id';
  const mockPurpose = 'encryption';
  const mockSignCallback = jest.fn();
  const mockSignature = 'test-signature';
  const mockSalt = { id: 'salt1', value: 'test-salt-value', purpose: 'encryption' };
  
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock the sign callback to return a signature
    mockSignCallback.mockResolvedValue(mockSignature);
    
    // Mock axios responses
    axios.post.mockImplementation((url) => {
      if (url.includes('register')) {
        return Promise.resolve({ data: { success: true, salt: mockSalt } });
      }
      return Promise.resolve({ data: {} });
    });
    
    axios.get.mockImplementation((url) => {
      if (url.includes('/salts/salt1')) {
        return Promise.resolve({ data: { success: true, salt: mockSalt } });
      } else if (url.includes('/salts')) {
        return Promise.resolve({ data: { success: true, salts: [mockSalt] } });
      }
      return Promise.resolve({ data: {} });
    });
    
    axios.delete.mockResolvedValue({ data: { success: true } });
  });

  test('registerYubiKeySalt registers a new salt', async () => {
    const result = await registerYubiKeySalt(mockCredentialId, mockPurpose, mockSignCallback);
    
    expect(mockSignCallback).toHaveBeenCalled();
    expect(axios.post).toHaveBeenCalledWith(
      '/api/yubikey/salt/register',
      expect.objectContaining({
        credential_id: mockCredentialId,
        purpose: mockPurpose,
        signature: mockSignature
      })
    );
    expect(result).toEqual({ success: true, salt: mockSalt });
  });

  test('getYubiKeySalts retrieves salts for a credential', async () => {
    const result = await getYubiKeySalts(mockCredentialId);
    
    expect(axios.get).toHaveBeenCalledWith(`/api/yubikey/${mockCredentialId}/salts`);
    expect(result).toEqual({ success: true, salts: [mockSalt] });
  });

  test('getYubiKeySalt retrieves a specific salt', async () => {
    const saltId = 'salt1';
    const result = await getYubiKeySalt(saltId);
    
    expect(axios.get).toHaveBeenCalledWith(`/api/yubikey/salt/${saltId}`);
    expect(result).toEqual({ success: true, salt: mockSalt });
  });

  test('deleteYubiKeySalt deletes a salt', async () => {
    const saltId = 'salt1';
    const result = await deleteYubiKeySalt(saltId);
    
    expect(axios.delete).toHaveBeenCalledWith(`/api/yubikey/salt/${saltId}`);
    expect(result).toEqual({ success: true });
  });

  test('registerYubiKeySalt handles network errors', async () => {
    // Override axios mock to simulate an error
    axios.post.mockRejectedValue(new Error('Network error'));
    
    await expect(registerYubiKeySalt(mockCredentialId, mockPurpose, mockSignCallback))
      .rejects.toThrow('Network error');
  });

  test('getYubiKeySalts handles network errors', async () => {
    // Override axios mock to simulate an error
    axios.get.mockRejectedValue(new Error('Network error'));
    
    await expect(getYubiKeySalts(mockCredentialId))
      .rejects.toThrow('Network error');
  });

  test('getYubiKeySalt handles network errors', async () => {
    // Override axios mock to simulate an error
    axios.get.mockRejectedValue(new Error('Network error'));
    
    await expect(getYubiKeySalt('salt1'))
      .rejects.toThrow('Network error');
  });

  test('deleteYubiKeySalt handles network errors', async () => {
    // Override axios mock to simulate an error
    axios.delete.mockRejectedValue(new Error('Network error'));
    
    await expect(deleteYubiKeySalt('salt1'))
      .rejects.toThrow('Network error');
  });

  test('registerYubiKeySalt handles API errors', async () => {
    // Override axios mock to simulate an API error response
    axios.post.mockResolvedValue({ 
      data: { success: false, error: 'Invalid credential' }
    });
    
    const result = await registerYubiKeySalt(mockCredentialId, mockPurpose, mockSignCallback);
    expect(result).toEqual({ success: false, error: 'Invalid credential' });
  });

  test('getYubiKeySalts handles API errors', async () => {
    // Override axios mock to simulate an API error response
    axios.get.mockResolvedValue({ 
      data: { success: false, error: 'Invalid credential' }
    });
    
    const result = await getYubiKeySalts(mockCredentialId);
    expect(result).toEqual({ success: false, error: 'Invalid credential' });
  });
}); 