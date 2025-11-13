import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import Contact from '../../pages/Contact';
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

// Mock Auth Context
const mockAuthContext = {
  user: {
    first_name: 'John',
    last_name: 'Doe',
    email: 'john@example.com',
    phone: '+33612345678'
  },
  isLoading: false,
  error: null
};

const renderContact = (authValue = mockAuthContext, toastValue = mockToast) => {
  return render(
    <BrowserRouter>
      <AuthContext.Provider value={authValue}>
        <ToastContext.Provider value={toastValue}>
          <Contact />
        </ToastContext.Provider>
      </AuthContext.Provider>
    </BrowserRouter>
  );
};

describe('Contact Form', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  describe('Form Rendering', () => {
    test('should render contact form with all fields', () => {
      renderContact();

      expect(screen.getByPlaceholderText(/Votre nom/i)).toBeInTheDocument();
      expect(screen.getByPlaceholderText(/Votre email/i)).toBeInTheDocument();
      expect(screen.getByPlaceholderText(/Votre téléphone/i)).toBeInTheDocument();
      expect(screen.getByPlaceholderText(/Sujet/i)).toBeInTheDocument();
      expect(screen.getByPlaceholderText(/Votre message/i)).toBeInTheDocument();
    });

    test('should pre-fill user data when authenticated', () => {
      renderContact();

      const nameInput = screen.getByPlaceholderText(/Votre nom/i);
      const emailInput = screen.getByPlaceholderText(/Votre email/i);

      expect(nameInput.value).toBe('John Doe');
      expect(emailInput.value).toBe('john@example.com');
    });

    test('should render category selection buttons', () => {
      renderContact();

      expect(screen.getByText(/Question Générale/i)).toBeInTheDocument();
      expect(screen.getByText(/Support Technique/i)).toBeInTheDocument();
      expect(screen.getByText(/Partenariat/i)).toBeInTheDocument();
    });

    test('should render submit button', () => {
      renderContact();
      expect(screen.getByRole('button', { name: /Envoyer/i })).toBeInTheDocument();
    });
  });

  describe('Form Input Handling', () => {
    test('should update name field on change', async () => {
      renderContact();
      const nameInput = screen.getByPlaceholderText(/Votre nom/i);

      await userEvent.clear(nameInput);
      await userEvent.type(nameInput, 'Jane Smith');

      expect(nameInput.value).toBe('Jane Smith');
    });

    test('should update email field on change', async () => {
      renderContact();
      const emailInput = screen.getByPlaceholderText(/Votre email/i);

      await userEvent.clear(emailInput);
      await userEvent.type(emailInput, 'jane@example.com');

      expect(emailInput.value).toBe('jane@example.com');
    });

    test('should update subject field on change', async () => {
      renderContact();
      const subjectInput = screen.getByPlaceholderText(/Sujet/i);

      await userEvent.type(subjectInput, 'Test Subject');

      expect(subjectInput.value).toBe('Test Subject');
    });

    test('should update message field on change', async () => {
      renderContact();
      const messageInput = screen.getByPlaceholderText(/Votre message/i);

      await userEvent.type(messageInput, 'Test message content');

      expect(messageInput.value).toBe('Test message content');
    });

    test('should change category selection', async () => {
      renderContact();
      const supportButton = screen.getByText(/Support Technique/i).closest('button');

      await userEvent.click(supportButton);

      expect(supportButton).toHaveClass('ring-2');
    });
  });

  describe('Form Validation', () => {
    test('should show validation error when required fields are empty', async () => {
      renderContact();
      const submitButton = screen.getByRole('button', { name: /Envoyer/i });

      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(mockToast.warning).toHaveBeenCalledWith(
          expect.stringContaining('champs obligatoires')
        );
      });
    });

    test('should not submit without name', async () => {
      renderContact();
      const nameInput = screen.getByPlaceholderText(/Votre nom/i);
      const emailInput = screen.getByPlaceholderText(/Votre email/i);
      const subjectInput = screen.getByPlaceholderText(/Sujet/i);
      const messageInput = screen.getByPlaceholderText(/Votre message/i);
      const submitButton = screen.getByRole('button', { name: /Envoyer/i });

      await userEvent.clear(nameInput);
      await userEvent.type(emailInput, 'test@example.com');
      await userEvent.type(subjectInput, 'Subject');
      await userEvent.type(messageInput, 'Message');
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(mockToast.warning).toHaveBeenCalled();
      });
    });

    test('should not submit without email', async () => {
      renderContact();
      const emailInput = screen.getByPlaceholderText(/Votre email/i);
      const subjectInput = screen.getByPlaceholderText(/Sujet/i);
      const messageInput = screen.getByPlaceholderText(/Votre message/i);
      const submitButton = screen.getByRole('button', { name: /Envoyer/i });

      await userEvent.clear(emailInput);
      await userEvent.type(subjectInput, 'Subject');
      await userEvent.type(messageInput, 'Message');
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(mockToast.warning).toHaveBeenCalled();
      });
    });

    test('should not submit without subject', async () => {
      renderContact();
      const subjectInput = screen.getByPlaceholderText(/Sujet/i);
      const messageInput = screen.getByPlaceholderText(/Votre message/i);
      const submitButton = screen.getByRole('button', { name: /Envoyer/i });

      await userEvent.clear(subjectInput);
      await userEvent.type(messageInput, 'Message');
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(mockToast.warning).toHaveBeenCalled();
      });
    });

    test('should not submit without message', async () => {
      renderContact();
      const subjectInput = screen.getByPlaceholderText(/Sujet/i);
      const messageInput = screen.getByPlaceholderText(/Votre message/i);
      const submitButton = screen.getByRole('button', { name: /Envoyer/i });

      await userEvent.type(subjectInput, 'Subject');
      await userEvent.clear(messageInput);
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(mockToast.warning).toHaveBeenCalled();
      });
    });
  });

  describe('Form Submission', () => {
    test('should submit form with valid data', async () => {
      api.post.mockResolvedValue({
        data: {
          success: true,
          message: 'Message envoyé avec succès!'
        }
      });

      renderContact();

      const nameInput = screen.getByPlaceholderText(/Votre nom/i);
      const emailInput = screen.getByPlaceholderText(/Votre email/i);
      const subjectInput = screen.getByPlaceholderText(/Sujet/i);
      const messageInput = screen.getByPlaceholderText(/Votre message/i);
      const submitButton = screen.getByRole('button', { name: /Envoyer/i });

      await userEvent.clear(nameInput);
      await userEvent.type(nameInput, 'Test User');
      await userEvent.clear(emailInput);
      await userEvent.type(emailInput, 'test@example.com');
      await userEvent.type(subjectInput, 'Test Subject');
      await userEvent.type(messageInput, 'Test Message');
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(api.post).toHaveBeenCalledWith(
          '/api/contact/submit',
          expect.objectContaining({
            name: 'Test User',
            email: 'test@example.com',
            subject: 'Test Subject',
            message: 'Test Message'
          })
        );
      });
    });

    test('should disable submit button during submission', async () => {
      api.post.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 1000)));

      renderContact();

      const nameInput = screen.getByPlaceholderText(/Votre nom/i);
      const emailInput = screen.getByPlaceholderText(/Votre email/i);
      const subjectInput = screen.getByPlaceholderText(/Sujet/i);
      const messageInput = screen.getByPlaceholderText(/Votre message/i);
      const submitButton = screen.getByRole('button', { name: /Envoyer/i });

      await userEvent.clear(nameInput);
      await userEvent.type(nameInput, 'Test User');
      await userEvent.clear(emailInput);
      await userEvent.type(emailInput, 'test@example.com');
      await userEvent.type(subjectInput, 'Subject');
      await userEvent.type(messageInput, 'Message');
      await userEvent.click(submitButton);

      expect(submitButton).toBeDisabled();
    });

    test('should show success message on successful submission', async () => {
      api.post.mockResolvedValue({
        data: {
          success: true,
          message: 'Message envoyé avec succès!'
        }
      });

      renderContact();

      const nameInput = screen.getByPlaceholderText(/Votre nom/i);
      const emailInput = screen.getByPlaceholderText(/Votre email/i);
      const subjectInput = screen.getByPlaceholderText(/Sujet/i);
      const messageInput = screen.getByPlaceholderText(/Votre message/i);
      const submitButton = screen.getByRole('button', { name: /Envoyer/i });

      await userEvent.clear(nameInput);
      await userEvent.type(nameInput, 'Test User');
      await userEvent.clear(emailInput);
      await userEvent.type(emailInput, 'test@example.com');
      await userEvent.type(subjectInput, 'Subject');
      await userEvent.type(messageInput, 'Message');
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(mockToast.success).toHaveBeenCalled();
      });
    });

    test('should reset form after successful submission', async () => {
      api.post.mockResolvedValue({
        data: {
          success: true,
          message: 'Message envoyé avec succès!'
        }
      });

      renderContact();

      const subjectInput = screen.getByPlaceholderText(/Sujet/i);
      const messageInput = screen.getByPlaceholderText(/Votre message/i);
      const submitButton = screen.getByRole('button', { name: /Envoyer/i });

      await userEvent.type(subjectInput, 'Subject');
      await userEvent.type(messageInput, 'Message');
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(subjectInput.value).toBe('');
        expect(messageInput.value).toBe('');
      });
    });
  });

  describe('Error Handling', () => {
    test('should display error message on submission failure', async () => {
      api.post.mockRejectedValue({
        response: {
          data: {
            detail: 'Erreur lors de l\'envoi du message'
          }
        }
      });

      renderContact();

      const nameInput = screen.getByPlaceholderText(/Votre nom/i);
      const emailInput = screen.getByPlaceholderText(/Votre email/i);
      const subjectInput = screen.getByPlaceholderText(/Sujet/i);
      const messageInput = screen.getByPlaceholderText(/Votre message/i);
      const submitButton = screen.getByRole('button', { name: /Envoyer/i });

      await userEvent.clear(nameInput);
      await userEvent.type(nameInput, 'Test User');
      await userEvent.clear(emailInput);
      await userEvent.type(emailInput, 'test@example.com');
      await userEvent.type(subjectInput, 'Subject');
      await userEvent.type(messageInput, 'Message');
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(mockToast.error).toHaveBeenCalled();
      });
    });

    test('should handle network errors gracefully', async () => {
      api.post.mockRejectedValue(new Error('Network error'));

      renderContact();

      const nameInput = screen.getByPlaceholderText(/Votre nom/i);
      const emailInput = screen.getByPlaceholderText(/Votre email/i);
      const subjectInput = screen.getByPlaceholderText(/Sujet/i);
      const messageInput = screen.getByPlaceholderText(/Votre message/i);
      const submitButton = screen.getByRole('button', { name: /Envoyer/i });

      await userEvent.clear(nameInput);
      await userEvent.type(nameInput, 'Test User');
      await userEvent.clear(emailInput);
      await userEvent.type(emailInput, 'test@example.com');
      await userEvent.type(subjectInput, 'Subject');
      await userEvent.type(messageInput, 'Message');
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(mockToast.error).toHaveBeenCalled();
      });
    });
  });

  describe('Accessibility', () => {
    test('should have proper labels for form fields', () => {
      renderContact();

      expect(screen.getByText(/Nom/i)).toBeInTheDocument();
      expect(screen.getByText(/Email/i)).toBeInTheDocument();
      expect(screen.getByText(/Sujet/i)).toBeInTheDocument();
    });

    test('should have email input type', () => {
      renderContact();
      const emailInput = screen.getByPlaceholderText(/Votre email/i);
      expect(emailInput.type).toBe('email');
    });

    test('should have required attributes on inputs', () => {
      renderContact();
      const nameInput = screen.getByPlaceholderText(/Votre nom/i);
      const emailInput = screen.getByPlaceholderText(/Votre email/i);

      expect(nameInput.required).toBe(true);
      expect(emailInput.required).toBe(true);
    });
  });

  describe('Unauthenticated User', () => {
    test('should have empty fields when user not authenticated', () => {
      const unauthContext = { user: null, isLoading: false, error: null };
      renderContact(unauthContext);

      const nameInput = screen.getByPlaceholderText(/Votre nom/i);
      const emailInput = screen.getByPlaceholderText(/Votre email/i);

      expect(nameInput.value).toBe('');
      expect(emailInput.value).toBe('');
    });
  });
});
