import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import YubiKeySaltManager from '../../components/YubiKeySaltManager';
import * as yubikeySaltApi from '../../utils/yubikeySaltApi';

// Mock the API
jest.mock('../../utils/yubikeySaltApi');

describe('YubiKeySaltManager Component', () => {
  const mockCredentialId = 'test-credential-id';
  const mockSignCallback = jest.fn();
  const mockSalts = [
    { id: 'salt1', purpose: 'encryption', created_at: '2023-01-01', last_used: '2023-01-10' },
    { id: 'salt2', purpose: 'backup', created_at: '2023-01-02', last_used: null }
  ];

  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    
    // Setup mock implementations
    yubikeySaltApi.getYubiKeySalts.mockResolvedValue({ success: true, salts: mockSalts });
    yubikeySaltApi.registerYubiKeySalt.mockResolvedValue({ 
      success: true, 
      salt: { id: 'new-salt', purpose: 'test-purpose', created_at: '2023-01-03' } 
    });
    yubikeySaltApi.deleteYubiKeySalt.mockResolvedValue({ success: true });
  });

  test('renders the component correctly', async () => {
    render(<YubiKeySaltManager credentialId={mockCredentialId} signCallback={mockSignCallback} />);
    
    // Component should render with basic elements
    expect(screen.getByText(/YubiKey Salt Manager/i)).toBeInTheDocument();
    
    // Wait for salts to load
    await waitFor(() => {
      expect(yubikeySaltApi.getYubiKeySalts).toHaveBeenCalledWith(mockCredentialId);
      expect(screen.getByText(/encryption/i)).toBeInTheDocument();
      expect(screen.getByText(/backup/i)).toBeInTheDocument();
    });
  });

  test('registers a new salt when form is submitted', async () => {
    render(<YubiKeySaltManager credentialId={mockCredentialId} signCallback={mockSignCallback} />);
    
    // Enter purpose for new salt
    const purposeInput = screen.getByLabelText(/Salt Purpose/i);
    fireEvent.change(purposeInput, { target: { value: 'test-purpose' } });
    
    // Submit the form
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

  test('deletes a salt when delete button is clicked', async () => {
    render(<YubiKeySaltManager credentialId={mockCredentialId} signCallback={mockSignCallback} />);
    
    // Wait for salts to load
    await waitFor(() => {
      expect(screen.getByText(/encryption/i)).toBeInTheDocument();
    });
    
    // Find and click the delete button for the first salt
    const deleteButtons = screen.getAllByText(/Delete/i);
    fireEvent.click(deleteButtons[0]);
    
    // Confirm deletion in the modal
    const confirmButton = screen.getByText(/Confirm Delete/i);
    fireEvent.click(confirmButton);
    
    await waitFor(() => {
      expect(yubikeySaltApi.deleteYubiKeySalt).toHaveBeenCalledWith('salt1');
      expect(yubikeySaltApi.getYubiKeySalts).toHaveBeenCalledTimes(2); // Initial load + after deletion
    });
  });

  test('shows error message when salt registration fails', async () => {
    // Override the mock to simulate an error
    yubikeySaltApi.registerYubiKeySalt.mockRejectedValue(new Error('Registration failed'));
    
    render(<YubiKeySaltManager credentialId={mockCredentialId} signCallback={mockSignCallback} />);
    
    // Enter purpose for new salt
    const purposeInput = screen.getByLabelText(/Salt Purpose/i);
    fireEvent.change(purposeInput, { target: { value: 'test-purpose' } });
    
    // Submit the form
    const registerButton = screen.getByText(/Register New Salt/i);
    fireEvent.click(registerButton);
    
    await waitFor(() => {
      expect(screen.getByText(/Error: Registration failed/i)).toBeInTheDocument();
    });
  });

  test('shows error message when salt deletion fails', async () => {
    // Override the mock to simulate an error
    yubikeySaltApi.deleteYubiKeySalt.mockRejectedValue(new Error('Deletion failed'));
    
    render(<YubiKeySaltManager credentialId={mockCredentialId} signCallback={mockSignCallback} />);
    
    // Wait for salts to load
    await waitFor(() => {
      expect(screen.getByText(/encryption/i)).toBeInTheDocument();
    });
    
    // Find and click the delete button for the first salt
    const deleteButtons = screen.getAllByText(/Delete/i);
    fireEvent.click(deleteButtons[0]);
    
    // Confirm deletion in the modal
    const confirmButton = screen.getByText(/Confirm Delete/i);
    fireEvent.click(confirmButton);
    
    await waitFor(() => {
      expect(screen.getByText(/Error: Deletion failed/i)).toBeInTheDocument();
    });
  });

  test('closes the delete confirmation modal when cancel is clicked', async () => {
    render(<YubiKeySaltManager credentialId={mockCredentialId} signCallback={mockSignCallback} />);
    
    // Wait for salts to load
    await waitFor(() => {
      expect(screen.getByText(/encryption/i)).toBeInTheDocument();
    });
    
    // Find and click the delete button for the first salt
    const deleteButtons = screen.getAllByText(/Delete/i);
    fireEvent.click(deleteButtons[0]);
    
    // Modal should be visible
    expect(screen.getByText(/Confirm Salt Deletion/i)).toBeInTheDocument();
    
    // Click cancel
    const cancelButton = screen.getByText(/Cancel/i);
    fireEvent.click(cancelButton);
    
    // Modal should be closed
    await waitFor(() => {
      expect(screen.queryByText(/Confirm Salt Deletion/i)).not.toBeInTheDocument();
    });
    
    // deleteYubiKeySalt should not have been called
    expect(yubikeySaltApi.deleteYubiKeySalt).not.toHaveBeenCalled();
  });
}); 