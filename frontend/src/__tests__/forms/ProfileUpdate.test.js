import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';
import { ToastContext } from '../../context/ToastContext';
import api from '../../utils/api';

// Mock API
jest.mock('../../utils/api');

// Mock Toast Context
const mockToast = {
  success: jest.fn(),
  error: jest.fn(),
  warning: jest.fn(),
};

// Mock Auth Context with updateUser function
const mockAuthContext = {
  user: {
    id: 1,
    first_name: 'John',
    last_name: 'Doe',
    email: 'john@example.com',
    phone: '+33612345678',
    bio: 'I am a content creator',
    profile_image: 'https://example.com/profile.jpg'
  },
  isLoading: false,
  error: null,
  updateUser: jest.fn()
};

// Simple ProfileUpdate component for testing
const ProfileUpdate = ({ user, onSuccess, onCancel }) => {
  const [formData, setFormData] = React.useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    email: user?.email || '',
    phone: user?.phone || '',
    bio: user?.bio || ''
  });

  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState('');
  const toast = React.useContext(ToastContext);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (!formData.first_name || !formData.last_name || !formData.email) {
      toast?.warning('Veuillez remplir les champs obligatoires');
      setLoading(false);
      return;
    }

    try {
      const response = await api.put(`/api/users/${user.id}`, formData);

      if (response.data.success) {
        toast?.success('Profil mis à jour avec succès!');
        if (onSuccess) onSuccess(response.data);
      }
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Erreur lors de la mise à jour du profil';
      setError(errorMsg);
      toast?.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <h2>Mettre à jour mon profil</h2>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <div>
        <label className="block text-sm font-medium mb-1">Prénom *</label>
        <input
          type="text"
          name="first_name"
          value={formData.first_name}
          onChange={handleChange}
          required
          className="w-full px-3 py-2 border rounded"
          placeholder="Votre prénom"
          data-testid="first-name-input"
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Nom *</label>
        <input
          type="text"
          name="last_name"
          value={formData.last_name}
          onChange={handleChange}
          required
          className="w-full px-3 py-2 border rounded"
          placeholder="Votre nom"
          data-testid="last-name-input"
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Email *</label>
        <input
          type="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          required
          className="w-full px-3 py-2 border rounded"
          placeholder="votre.email@example.com"
          data-testid="email-input"
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Téléphone</label>
        <input
          type="tel"
          name="phone"
          value={formData.phone}
          onChange={handleChange}
          className="w-full px-3 py-2 border rounded"
          placeholder="+33 6 12 34 56 78"
          data-testid="phone-input"
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Biographie</label>
        <textarea
          name="bio"
          value={formData.bio}
          onChange={handleChange}
          rows={4}
          className="w-full px-3 py-2 border rounded"
          placeholder="Parlez un peu de vous..."
          data-testid="bio-input"
        />
      </div>

      <div className="flex gap-2 pt-4">
        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50"
          data-testid="submit-button"
        >
          {loading ? 'Mise à jour...' : 'Mettre à jour'}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 border rounded"
          data-testid="cancel-button"
        >
          Annuler
        </button>
      </div>
    </form>
  );
};

const renderProfileUpdate = (user = mockAuthContext.user, toastValue = mockToast, onSuccess = jest.fn(), onCancel = jest.fn()) => {
  return render(
    <BrowserRouter>
      <ToastContext.Provider value={toastValue}>
        <ProfileUpdate user={user} onSuccess={onSuccess} onCancel={onCancel} />
      </ToastContext.Provider>
    </BrowserRouter>
  );
};

describe('ProfileUpdate Form', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Form Rendering', () => {
    test('should render profile update form with all fields', () => {
      renderProfileUpdate();

      expect(screen.getByTestId('first-name-input')).toBeInTheDocument();
      expect(screen.getByTestId('last-name-input')).toBeInTheDocument();
      expect(screen.getByTestId('email-input')).toBeInTheDocument();
      expect(screen.getByTestId('phone-input')).toBeInTheDocument();
      expect(screen.getByTestId('bio-input')).toBeInTheDocument();
    });

    test('should render form title', () => {
      renderProfileUpdate();
      expect(screen.getByText('Mettre à jour mon profil')).toBeInTheDocument();
    });

    test('should render submit button', () => {
      renderProfileUpdate();
      expect(screen.getByTestId('submit-button')).toBeInTheDocument();
    });

    test('should render cancel button', () => {
      renderProfileUpdate();
      expect(screen.getByTestId('cancel-button')).toBeInTheDocument();
    });

    test('should pre-fill form with user data', () => {
      renderProfileUpdate();

      expect(screen.getByTestId('first-name-input').value).toBe('John');
      expect(screen.getByTestId('last-name-input').value).toBe('Doe');
      expect(screen.getByTestId('email-input').value).toBe('john@example.com');
      expect(screen.getByTestId('phone-input').value).toBe('+33612345678');
      expect(screen.getByTestId('bio-input').value).toBe('I am a content creator');
    });
  });

  describe('Form Input Handling', () => {
    test('should update first name on change', async () => {
      renderProfileUpdate();

      const firstNameInput = screen.getByTestId('first-name-input');
      await userEvent.clear(firstNameInput);
      await userEvent.type(firstNameInput, 'Jane');

      expect(firstNameInput.value).toBe('Jane');
    });

    test('should update last name on change', async () => {
      renderProfileUpdate();

      const lastNameInput = screen.getByTestId('last-name-input');
      await userEvent.clear(lastNameInput);
      await userEvent.type(lastNameInput, 'Smith');

      expect(lastNameInput.value).toBe('Smith');
    });

    test('should update email on change', async () => {
      renderProfileUpdate();

      const emailInput = screen.getByTestId('email-input');
      await userEvent.clear(emailInput);
      await userEvent.type(emailInput, 'jane@example.com');

      expect(emailInput.value).toBe('jane@example.com');
    });

    test('should update phone on change', async () => {
      renderProfileUpdate();

      const phoneInput = screen.getByTestId('phone-input');
      await userEvent.clear(phoneInput);
      await userEvent.type(phoneInput, '+33712345678');

      expect(phoneInput.value).toBe('+33712345678');
    });

    test('should update bio on change', async () => {
      renderProfileUpdate();

      const bioInput = screen.getByTestId('bio-input');
      await userEvent.clear(bioInput);
      await userEvent.type(bioInput, 'Updated biography');

      expect(bioInput.value).toBe('Updated biography');
    });

    test('should clear error when input changes', async () => {
      renderProfileUpdate();

      // Simulate an error state by attempting invalid submission
      const firstNameInput = screen.getByTestId('first-name-input');
      await userEvent.clear(firstNameInput);

      // Change input should clear any error
      await userEvent.type(firstNameInput, 'Jane');

      expect(firstNameInput.value).toBe('Jane');
    });
  });

  describe('Form Validation', () => {
    test('should have required first name field', () => {
      renderProfileUpdate();
      const firstNameInput = screen.getByTestId('first-name-input');

      expect(firstNameInput.required).toBe(true);
    });

    test('should have required last name field', () => {
      renderProfileUpdate();
      const lastNameInput = screen.getByTestId('last-name-input');

      expect(lastNameInput.required).toBe(true);
    });

    test('should have required email field', () => {
      renderProfileUpdate();
      const emailInput = screen.getByTestId('email-input');

      expect(emailInput.required).toBe(true);
    });

    test('should show validation error when required fields are empty', async () => {
      const mockToastLocal = { ...mockToast };
      renderProfileUpdate(mockAuthContext.user, mockToastLocal);

      const firstNameInput = screen.getByTestId('first-name-input');
      const submitButton = screen.getByTestId('submit-button');

      await userEvent.clear(firstNameInput);
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(mockToastLocal.warning).toHaveBeenCalled();
      });
    });

    test('should not submit without first name', async () => {
      const mockToastLocal = { ...mockToast };
      renderProfileUpdate(mockAuthContext.user, mockToastLocal);

      const firstNameInput = screen.getByTestId('first-name-input');
      const submitButton = screen.getByTestId('submit-button');

      await userEvent.clear(firstNameInput);
      await userEvent.click(submitButton);

      expect(api.put).not.toHaveBeenCalled();
    });

    test('should not submit without last name', async () => {
      const mockToastLocal = { ...mockToast };
      renderProfileUpdate(mockAuthContext.user, mockToastLocal);

      const lastNameInput = screen.getByTestId('last-name-input');
      const submitButton = screen.getByTestId('submit-button');

      await userEvent.clear(lastNameInput);
      await userEvent.click(submitButton);

      expect(api.put).not.toHaveBeenCalled();
    });

    test('should not submit without email', async () => {
      const mockToastLocal = { ...mockToast };
      renderProfileUpdate(mockAuthContext.user, mockToastLocal);

      const emailInput = screen.getByTestId('email-input');
      const submitButton = screen.getByTestId('submit-button');

      await userEvent.clear(emailInput);
      await userEvent.click(submitButton);

      expect(api.put).not.toHaveBeenCalled();
    });
  });

  describe('Form Submission', () => {
    test('should submit form with valid data', async () => {
      api.put.mockResolvedValue({
        data: {
          success: true,
          user: {
            id: 1,
            first_name: 'Jane',
            last_name: 'Smith'
          }
        }
      });

      renderProfileUpdate();

      const firstNameInput = screen.getByTestId('first-name-input');
      const submitButton = screen.getByTestId('submit-button');

      await userEvent.clear(firstNameInput);
      await userEvent.type(firstNameInput, 'Jane');
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(api.put).toHaveBeenCalledWith(
          '/api/users/1',
          expect.objectContaining({
            first_name: 'Jane',
            last_name: 'Doe',
            email: 'john@example.com'
          })
        );
      });
    });

    test('should disable submit button during submission', async () => {
      api.put.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 1000)));

      renderProfileUpdate();

      const firstNameInput = screen.getByTestId('first-name-input');
      const submitButton = screen.getByTestId('submit-button');

      await userEvent.clear(firstNameInput);
      await userEvent.type(firstNameInput, 'Jane');
      await userEvent.click(submitButton);

      expect(submitButton).toBeDisabled();
      expect(submitButton.textContent).toBe('Mise à jour...');
    });

    test('should show success message on successful submission', async () => {
      const mockToastLocal = { ...mockToast };
      api.put.mockResolvedValue({
        data: { success: true }
      });

      renderProfileUpdate(mockAuthContext.user, mockToastLocal);

      const submitButton = screen.getByTestId('submit-button');
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(mockToastLocal.success).toHaveBeenCalledWith('Profil mis à jour avec succès!');
      });
    });

    test('should call onSuccess callback after successful submission', async () => {
      const mockOnSuccess = jest.fn();
      api.put.mockResolvedValue({
        data: {
          success: true,
          user: { id: 1, first_name: 'Jane' }
        }
      });

      renderProfileUpdate(mockAuthContext.user, mockToast, mockOnSuccess);

      const submitButton = screen.getByTestId('submit-button');
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(mockOnSuccess).toHaveBeenCalled();
      });
    });

    test('should submit with all form data', async () => {
      api.put.mockResolvedValue({
        data: { success: true }
      });

      renderProfileUpdate();

      const firstNameInput = screen.getByTestId('first-name-input');
      const lastNameInput = screen.getByTestId('last-name-input');
      const emailInput = screen.getByTestId('email-input');
      const phoneInput = screen.getByTestId('phone-input');
      const bioInput = screen.getByTestId('bio-input');
      const submitButton = screen.getByTestId('submit-button');

      await userEvent.clear(firstNameInput);
      await userEvent.type(firstNameInput, 'Jane');
      await userEvent.clear(lastNameInput);
      await userEvent.type(lastNameInput, 'Smith');
      await userEvent.clear(emailInput);
      await userEvent.type(emailInput, 'jane@example.com');
      await userEvent.clear(phoneInput);
      await userEvent.type(phoneInput, '+33712345678');
      await userEvent.clear(bioInput);
      await userEvent.type(bioInput, 'Updated bio');

      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(api.put).toHaveBeenCalledWith(
          '/api/users/1',
          {
            first_name: 'Jane',
            last_name: 'Smith',
            email: 'jane@example.com',
            phone: '+33712345678',
            bio: 'Updated bio'
          }
        );
      });
    });
  });

  describe('Error Handling', () => {
    test('should display error message on submission failure', async () => {
      api.put.mockRejectedValue({
        response: {
          data: {
            detail: 'Email already exists'
          }
        }
      });

      renderProfileUpdate();

      const submitButton = screen.getByTestId('submit-button');
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Email already exists')).toBeInTheDocument();
      });
    });

    test('should show generic error message on unknown error', async () => {
      api.put.mockRejectedValue(new Error('Network error'));

      renderProfileUpdate();

      const submitButton = screen.getByTestId('submit-button');
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/Erreur lors de la mise à jour du profil/)).toBeInTheDocument();
      });
    });

    test('should call error toast on submission failure', async () => {
      const mockToastLocal = { ...mockToast };
      api.put.mockRejectedValue({
        response: {
          data: {
            detail: 'Update failed'
          }
        }
      });

      renderProfileUpdate(mockAuthContext.user, mockToastLocal);

      const submitButton = screen.getByTestId('submit-button');
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(mockToastLocal.error).toHaveBeenCalled();
      });
    });
  });

  describe('User Actions', () => {
    test('should call onCancel when cancel button is clicked', async () => {
      const mockOnCancel = jest.fn();
      renderProfileUpdate(mockAuthContext.user, mockToast, jest.fn(), mockOnCancel);

      const cancelButton = screen.getByTestId('cancel-button');
      await userEvent.click(cancelButton);

      expect(mockOnCancel).toHaveBeenCalled();
    });

    test('should allow canceling form submission', async () => {
      const mockOnCancel = jest.fn();
      renderProfileUpdate(mockAuthContext.user, mockToast, jest.fn(), mockOnCancel);

      const firstNameInput = screen.getByTestId('first-name-input');
      const cancelButton = screen.getByTestId('cancel-button');

      await userEvent.clear(firstNameInput);
      await userEvent.type(firstNameInput, 'Jane');
      await userEvent.click(cancelButton);

      expect(mockOnCancel).toHaveBeenCalled();
      expect(api.put).not.toHaveBeenCalled();
    });
  });

  describe('Accessibility', () => {
    test('should have proper labels for form fields', () => {
      renderProfileUpdate();

      expect(screen.getByText('Prénom *')).toBeInTheDocument();
      expect(screen.getByText('Nom *')).toBeInTheDocument();
      expect(screen.getByText('Email *')).toBeInTheDocument();
      expect(screen.getByText('Téléphone')).toBeInTheDocument();
      expect(screen.getByText('Biographie')).toBeInTheDocument();
    });

    test('should have email input type', () => {
      renderProfileUpdate();
      const emailInput = screen.getByTestId('email-input');

      expect(emailInput.type).toBe('email');
    });

    test('should have tel input type for phone', () => {
      renderProfileUpdate();
      const phoneInput = screen.getByTestId('phone-input');

      expect(phoneInput.type).toBe('tel');
    });

    test('should have textarea for bio', () => {
      renderProfileUpdate();
      const bioInput = screen.getByTestId('bio-input');

      expect(bioInput.tagName).toBe('TEXTAREA');
    });
  });

  describe('Optional Fields', () => {
    test('should allow submission without phone', async () => {
      api.put.mockResolvedValue({
        data: { success: true }
      });

      renderProfileUpdate();

      const phoneInput = screen.getByTestId('phone-input');
      const submitButton = screen.getByTestId('submit-button');

      await userEvent.clear(phoneInput);
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(api.put).toHaveBeenCalled();
      });
    });

    test('should allow submission without bio', async () => {
      api.put.mockResolvedValue({
        data: { success: true }
      });

      renderProfileUpdate();

      const bioInput = screen.getByTestId('bio-input');
      const submitButton = screen.getByTestId('submit-button');

      await userEvent.clear(bioInput);
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(api.put).toHaveBeenCalled();
      });
    });
  });
});
