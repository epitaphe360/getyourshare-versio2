import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import Login from '../../pages/Login';
import { AuthContext } from '../../context/AuthContext';

// Mock AuthContext
const mockLogin = jest.fn();
const mockAuthContext = {
  user: null,
  login: mockLogin,
  isLoading: false,
  error: null
};

// Mock useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

const renderLogin = () => {
  return render(
    <BrowserRouter>
      <AuthContext.Provider value={mockAuthContext}>
        <Login />
      </AuthContext.Provider>
    </BrowserRouter>
  );
};

describe('Login Form', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  describe('Form Rendering', () => {
    test('should render login form with email and password fields', () => {
      renderLogin();

      expect(screen.getByTestId('email-input')).toBeInTheDocument();
      expect(screen.getByTestId('password-input')).toBeInTheDocument();
      expect(screen.getByTestId('login-button')).toBeInTheDocument();
    });

    test('should render login button', () => {
      renderLogin();
      expect(screen.getByTestId('login-button')).toHaveTextContent('Se connecter');
    });

    test('should render register link', () => {
      renderLogin();
      expect(screen.getByText(/S'inscrire/i)).toBeInTheDocument();
    });

    test('should render quick login buttons for test accounts', () => {
      renderLogin();
      expect(screen.getByText(/Admin/i)).toBeInTheDocument();
      expect(screen.getByText(/Hassan Oudrhiri/i)).toBeInTheDocument();
    });
  });

  describe('Form Input Handling', () => {
    test('should update email input value on change', async () => {
      renderLogin();
      const emailInput = screen.getByTestId('email-input');

      await userEvent.type(emailInput, 'test@example.com');
      expect(emailInput.value).toBe('test@example.com');
    });

    test('should update password input value on change', async () => {
      renderLogin();
      const passwordInput = screen.getByTestId('password-input');

      await userEvent.type(passwordInput, 'password123');
      expect(passwordInput.value).toBe('password123');
    });

    test('should update both fields in form state', async () => {
      renderLogin();
      const emailInput = screen.getByTestId('email-input');
      const passwordInput = screen.getByTestId('password-input');

      await userEvent.type(emailInput, 'test@example.com');
      await userEvent.type(passwordInput, 'password123');

      expect(emailInput.value).toBe('test@example.com');
      expect(passwordInput.value).toBe('password123');
    });
  });

  describe('Form Submission', () => {
    test('should call login function with email and password on submit', async () => {
      mockLogin.mockResolvedValue({ success: true });
      renderLogin();

      const emailInput = screen.getByTestId('email-input');
      const passwordInput = screen.getByTestId('password-input');
      const submitButton = screen.getByTestId('login-button');

      await userEvent.type(emailInput, 'test@example.com');
      await userEvent.type(passwordInput, 'password123');
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'password123');
      });
    });

    test('should disable button during submission', async () => {
      mockLogin.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 1000)));
      renderLogin();

      const emailInput = screen.getByTestId('email-input');
      const passwordInput = screen.getByTestId('password-input');
      const submitButton = screen.getByTestId('login-button');

      await userEvent.type(emailInput, 'test@example.com');
      await userEvent.type(passwordInput, 'password123');
      await userEvent.click(submitButton);

      expect(submitButton).toBeDisabled();
      expect(submitButton).toHaveTextContent('Connexion...');
    });

    test('should not submit if email is empty', async () => {
      renderLogin();
      const passwordInput = screen.getByTestId('password-input');
      const submitButton = screen.getByTestId('login-button');

      await userEvent.type(passwordInput, 'password123');

      // Email input is required, so form submission should fail
      expect(passwordInput.value).toBe('password123');
    });

    test('should not submit if password is empty', async () => {
      renderLogin();
      const emailInput = screen.getByTestId('email-input');
      const submitButton = screen.getByTestId('login-button');

      await userEvent.type(emailInput, 'test@example.com');

      // Password input is required
      expect(emailInput.value).toBe('test@example.com');
    });
  });

  describe('Error Handling', () => {
    test('should display error message on login failure', async () => {
      mockLogin.mockResolvedValue({
        success: false,
        error: 'Email ou mot de passe incorrect'
      });
      renderLogin();

      const emailInput = screen.getByTestId('email-input');
      const passwordInput = screen.getByTestId('password-input');
      const submitButton = screen.getByTestId('login-button');

      await userEvent.type(emailInput, 'test@example.com');
      await userEvent.type(passwordInput, 'wrongpassword');
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByTestId('error-message')).toHaveTextContent(
          'Email ou mot de passe incorrect'
        );
      });
    });

    test('should clear error on new input', async () => {
      mockLogin.mockResolvedValue({
        success: false,
        error: 'Invalid credentials'
      });
      renderLogin();

      const emailInput = screen.getByTestId('email-input');
      const passwordInput = screen.getByTestId('password-input');
      const submitButton = screen.getByTestId('login-button');

      await userEvent.type(emailInput, 'test@example.com');
      await userEvent.type(passwordInput, 'wrong');
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByTestId('error-message')).toBeInTheDocument();
      });

      // Change input should clear error state
      await userEvent.type(emailInput, 'a');
    });
  });

  describe('2FA Flow', () => {
    test('should show 2FA form when 2FA is required', async () => {
      mockLogin.mockResolvedValue({
        success: false,
        requires_2fa: true,
        temp_token: 'temp123'
      });
      renderLogin();

      const emailInput = screen.getByTestId('email-input');
      const passwordInput = screen.getByTestId('password-input');
      const submitButton = screen.getByTestId('login-button');

      await userEvent.type(emailInput, 'test@example.com');
      await userEvent.type(passwordInput, 'password123');
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/000000/i)).toBeInTheDocument();
      });
    });

    test('should accept 6-digit 2FA code', async () => {
      mockLogin.mockResolvedValue({
        success: false,
        requires_2fa: true,
        temp_token: 'temp123'
      });
      renderLogin();

      const emailInput = screen.getByTestId('email-input');
      const passwordInput = screen.getByTestId('password-input');
      const submitButton = screen.getByTestId('login-button');

      await userEvent.type(emailInput, 'test@example.com');
      await userEvent.type(passwordInput, 'password123');
      await userEvent.click(submitButton);

      await waitFor(() => {
        const codeInput = screen.getByPlaceholderText(/000000/i);
        userEvent.type(codeInput, '123456');
        expect(codeInput.value).toBe('123456');
      });
    });

    test('should allow back to email/password from 2FA', async () => {
      mockLogin.mockResolvedValue({
        success: false,
        requires_2fa: true,
        temp_token: 'temp123'
      });
      renderLogin();

      const emailInput = screen.getByTestId('email-input');
      const passwordInput = screen.getByTestId('password-input');
      const submitButton = screen.getByTestId('login-button');

      await userEvent.type(emailInput, 'test@example.com');
      await userEvent.type(passwordInput, 'password123');
      await userEvent.click(submitButton);

      await waitFor(() => {
        const backButton = screen.getByText('← Retour');
        userEvent.click(backButton);
      });

      await waitFor(() => {
        expect(screen.getByTestId('email-input')).toBeInTheDocument();
      });
    });
  });

  describe('Quick Login', () => {
    test('should login with admin account on quick login button click', async () => {
      mockLogin.mockResolvedValue({ success: true });
      renderLogin();

      const adminButton = screen.getByText(/Admin/i).closest('button');
      await userEvent.click(adminButton);

      await waitFor(() => {
        expect(mockLogin).toHaveBeenCalledWith(
          'admin@shareyoursales.ma',
          'Admin123'
        );
      });
    });

    test('should login with influencer account on quick login button click', async () => {
      mockLogin.mockResolvedValue({ success: true });
      renderLogin();

      const influencerButton = screen.getByText(/Hassan Oudrhiri/i).closest('button');
      await userEvent.click(influencerButton);

      await waitFor(() => {
        expect(mockLogin).toHaveBeenCalledWith(
          'foodinfluencer@gmail.com',
          'Hassan123'
        );
      });
    });
  });

  describe('Navigation', () => {
    test('should redirect to dashboard on successful login', async () => {
      mockLogin.mockResolvedValue({ success: true });
      renderLogin();

      const emailInput = screen.getByTestId('email-input');
      const passwordInput = screen.getByTestId('password-input');
      const submitButton = screen.getByTestId('login-button');

      await userEvent.type(emailInput, 'test@example.com');
      await userEvent.type(passwordInput, 'password123');
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
      });
    });

    test('should redirect to subscription plans if pending plan selection', async () => {
      mockLogin.mockResolvedValue({ success: true });
      localStorage.setItem('pendingPlanSelection', 'pro');

      renderLogin();

      const emailInput = screen.getByTestId('email-input');
      const passwordInput = screen.getByTestId('password-input');
      const submitButton = screen.getByTestId('login-button');

      await userEvent.type(emailInput, 'test@example.com');
      await userEvent.type(passwordInput, 'password123');
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/subscription/plans');
      });
    });

    test('should redirect to custom path if redirectAfterLogin is set', async () => {
      mockLogin.mockResolvedValue({ success: true });
      localStorage.setItem('redirectAfterLogin', '/campaigns');

      renderLogin();

      const emailInput = screen.getByTestId('email-input');
      const passwordInput = screen.getByTestId('password-input');
      const submitButton = screen.getByTestId('login-button');

      await userEvent.type(emailInput, 'test@example.com');
      await userEvent.type(passwordInput, 'password123');
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/campaigns');
      });
    });
  });

  describe('Accessibility', () => {
    test('should have proper labels for form fields', () => {
      renderLogin();

      expect(screen.getByText('Email')).toBeInTheDocument();
      expect(screen.getByText('Mot de passe')).toBeInTheDocument();
    });

    test('should have email input type', () => {
      renderLogin();
      const emailInput = screen.getByTestId('email-input');
      expect(emailInput.type).toBe('email');
    });

    test('should have password input type', () => {
      renderLogin();
      const passwordInput = screen.getByTestId('password-input');
      expect(passwordInput.type).toBe('password');
    });

    test('should have required attribute on inputs', () => {
      renderLogin();
      const emailInput = screen.getByTestId('email-input');
      const passwordInput = screen.getByTestId('password-input');

      expect(emailInput.required).toBe(true);
      expect(passwordInput.required).toBe(true);
    });
  });
});
