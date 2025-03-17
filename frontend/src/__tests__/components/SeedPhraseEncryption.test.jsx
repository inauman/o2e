import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import SeedPhraseEncryption from '../../components/SeedPhraseEncryption';
import * as yubikeySaltApi from '../../utils/yubikeySaltApi';
import * as seedEncryption from '../../utils/seedEncryption';

// Mock the APIs
jest.mock('../../utils/yubikeySaltApi');
jest.mock('../../utils/seedEncryption');

describe('SeedPhraseEncryption Component', () => {
  const mockCredentialId = 'test-credential-id';
  const mockSignCallback = jest.fn();
  const mockSalts = [
    { id: 'salt1', purpose: 'encryption', created_at: '2023-01-01' },
    { id: 'salt2', purpose: 'backup', created_at: '2023-01-02' }
  ];

  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    
    // Setup mock implementations
    yubikeySaltApi.getYubiKeySalts.mockResolvedValue({ success: true, salts: mockSalts });
    yubikeySaltApi.registerYubiKeySalt.mockResolvedValue({ success: true, salt: { id: 'new-salt' } });
    yubikeySaltApi.getYubiKeySalt.mockResolvedValue({ success: true, salt: { value: 'test-salt-value' } });
    
    seedEncryption.generateRandomSeedPhrase.mockReturnValue('test seed phrase');
    seedEncryption.encryptSeedPhrase.mockResolvedValue('encrypted-data');
    seedEncryption.decryptSeedPhrase.mockResolvedValue('decrypted seed phrase');
  });

  test('renders the component correctly', async () => {
    render(<SeedPhraseEncryption credentialId={mockCredentialId} signCallback={mockSignCallback} />);
    
    // Component should render with basic elements
    expect(screen.getByText(/Seed Phrase Encryption/i)).toBeInTheDocument();
    
    // Wait for salts to load
    await waitFor(() => {
      expect(yubikeySaltApi.getYubiKeySalts).toHaveBeenCalledWith(mockCredentialId);
    });
  });

  test('generates a new seed phrase when button is clicked', async () => {
    render(<SeedPhraseEncryption credentialId={mockCredentialId} signCallback={mockSignCallback} />);
    
    const generateButton = screen.getByText(/Generate New Seed/i);
    fireEvent.click(generateButton);
    
    expect(seedEncryption.generateRandomSeedPhrase).toHaveBeenCalled();
    await waitFor(() => {
      expect(screen.getByDisplayValue('test seed phrase')).toBeInTheDocument();
    });
  });

  test('encrypts seed phrase when encrypt button is clicked', async () => {
    render(<SeedPhraseEncryption credentialId={mockCredentialId} signCallback={mockSignCallback} />);
    
    // Wait for salts to load and select the first one
    await waitFor(() => {
      expect(screen.getByText('salt1')).toBeInTheDocument();
    });
    
    // Enter seed phrase
    const seedInput = screen.getByLabelText(/Seed Phrase/i);
    fireEvent.change(seedInput, { target: { value: 'test seed phrase' } });
    
    // Select salt
    const saltSelect = screen.getByLabelText(/Select Salt/i);
    fireEvent.change(saltSelect, { target: { value: 'salt1' } });
    
    // Click encrypt button
    const encryptButton = screen.getByText(/Encrypt/i);
    fireEvent.click(encryptButton);
    
    await waitFor(() => {
      expect(yubikeySaltApi.getYubiKeySalt).toHaveBeenCalledWith('salt1');
      expect(seedEncryption.encryptSeedPhrase).toHaveBeenCalled();
      expect(screen.getByText(/Encrypted Data/i)).toBeInTheDocument();
      expect(screen.getByText(/encrypted-data/i)).toBeInTheDocument();
    });
  });

  test('decrypts seed phrase when decrypt button is clicked', async () => {
    render(<SeedPhraseEncryption credentialId={mockCredentialId} signCallback={mockSignCallback} />);
    
    // Wait for salts to load and select the first one
    await waitFor(() => {
      expect(screen.getByText('salt1')).toBeInTheDocument();
    });
    
    // Enter encrypted data
    const encryptedInput = screen.getByLabelText(/Encrypted Data/i);
    fireEvent.change(encryptedInput, { target: { value: 'encrypted-data' } });
    
    // Select salt
    const saltSelect = screen.getByLabelText(/Select Salt/i);
    fireEvent.change(saltSelect, { target: { value: 'salt1' } });
    
    // Click decrypt button
    const decryptButton = screen.getByText(/Decrypt/i);
    fireEvent.click(decryptButton);
    
    await waitFor(() => {
      expect(yubikeySaltApi.getYubiKeySalt).toHaveBeenCalledWith('salt1');
      expect(seedEncryption.decryptSeedPhrase).toHaveBeenCalled();
      expect(screen.getByText(/Decrypted Seed Phrase/i)).toBeInTheDocument();
      expect(screen.getByText(/decrypted seed phrase/i)).toBeInTheDocument();
    });
  });

  test('registers a new salt when button is clicked', async () => {
    render(<SeedPhraseEncryption credentialId={mockCredentialId} signCallback={mockSignCallback} />);
    
    // Enter purpose for new salt
    const purposeInput = screen.getByLabelText(/Salt Purpose/i);
    fireEvent.change(purposeInput, { target: { value: 'test-purpose' } });
    
    // Click register salt button
    const registerButton = screen.getByText(/Register New Salt/i);
    fireEvent.click(registerButton);
    
    await waitFor(() => {
      expect(yubikeySaltApi.registerYubiKeySalt).toHaveBeenCalledWith(
        mockCredentialId,
        'test-purpose',
        expect.any(Function)
      );
      expect(yubikeySaltApi.getYubiKeySalts).toHaveBeenCalledTimes(2); // Initial load + after registration
    });
  });
}); 