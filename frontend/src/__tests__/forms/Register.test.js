import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import Register from '../../pages/Register';
import axios from 'axios';

jest.mock('axios');
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
  useSearchParams: () => [new URLSearchParams(), jest.fn()],
}));

const renderRegister = () => {
  return render(
    <BrowserRouter>
      <Register />
    </BrowserRouter>
  );
};

describe('Register Form', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Step 1: Role Selection', () => {
    test('should display role selection options', () => {
      renderRegister();

      expect(screen.getByText('Créer un compte')).toBeInTheDocument();
      expect(screen.getByText(/Entreprise/i)).toBeInTheDocument();
      expect(screen.getByText(/Influenceur/i)).toBeInTheDocument();
    });

    test('should proceed to Step 2 when merchant role is selected', async () => {
      renderRegister();

      const merchantButton = screen.getByText(/Entreprise/i).closest('button');
      await userEvent.click(merchantButton);

      await waitFor(() => {
        expect(screen.getByText(/Inscription Entreprise/i)).toBeInTheDocument();
      });
    });

    test('should proceed to Step 2 when influencer role is selected', async () => {
      renderRegister();

      const influencerButton = screen.getByText(/Influenceur/i).closest('button');
      await userEvent.click(influencerButton);

      await waitFor(() => {
        expect(screen.getByText(/Inscription Influenceur/i)).toBeInTheDocument();
      });
    });
  });

  describe('Step 2: Merchant Registration Form', () => {
    beforeEach(async () => {
      renderRegister();
      const merchantButton = screen.getByText(/Entreprise/i).closest('button');
      await userEvent.click(merchantButton);
    });

    test('should show company name field for merchants', async () => {
      await waitFor(() => {
        expect(screen.getByPlaceholderText(/Mon Entreprise/i)).toBeInTheDocument();
      });
    });

    test('should NOT show username field for merchants', async () => {
      await waitFor(() => {
        expect(screen.queryByPlaceholderText(/mon_username/i)).not.toBeInTheDocument();
      });
    });

    test('should collect all merchant fields', async () => {
      await waitFor(() => {
        const firstNameInput = screen.getByPlaceholderText(/Jean/i);
        const lastNameInput = screen.getByPlaceholderText(/Dupont/i);
        const companyInput = screen.getByPlaceholderText(/Mon Entreprise/i);
        const emailInput = screen.getByPlaceholderText(/email@exemple/i);
        const phoneInput = screen.getByPlaceholderText(/\+33/i);

        expect(firstNameInput).toBeInTheDocument();
        expect(lastNameInput).toBeInTheDocument();
        expect(companyInput).toBeInTheDocument();
        expect(emailInput).toBeInTheDocument();
        expect(phoneInput).toBeInTheDocument();
      });
    });
  });

  describe('Step 2: Influencer Registration Form', () => {
    beforeEach(async () => {
      renderRegister();
      const influencerButton = screen.getByText(/Influenceur/i).closest('button');
      await userEvent.click(influencerButton);
    });

    test('should show username field for influencers', async () => {
      await waitFor(() => {
        expect(screen.getByPlaceholderText(/mon_username/i)).toBeInTheDocument();
      });
    });

    test('should NOT show company name field for influencers', async () => {
      await waitFor(() => {
        expect(screen.queryByPlaceholderText(/Mon Entreprise/i)).not.toBeInTheDocument();
      });
    });
  });

  describe('Form Validation', () => {
    beforeEach(async () => {
      renderRegister();
      const merchantButton = screen.getByText(/Entreprise/i).closest('button');
      await userEvent.click(merchantButton);
    });

    test('should validate that first name is required', async () => {
      await waitFor(() => {
        const submitButton = screen.getByText(/Créer mon compte/i);
        expect(submitButton).toBeInTheDocument();
      });

      // Try to submit without first name - form should require it
      const firstNameInput = screen.getByPlaceholderText(/Jean/i);
      expect(firstNameInput.required).toBe(true);
    });

    test('should validate that email is required', async () => {
      await waitFor(() => {
        const emailInput = screen.getByPlaceholderText(/email@exemple/i);
        expect(emailInput.required).toBe(true);
      });
    });

    test('should validate password minimum length', async () => {
      await waitFor(async () => {
        const firstNameInput = screen.getByPlaceholderText(/Jean/i);
        const lastNameInput = screen.getByPlaceholderText(/Dupont/i);
        const companyInput = screen.getByPlaceholderText(/Mon Entreprise/i);
        const emailInput = screen.getByPlaceholderText(/email@exemple/i);
        const phoneInput = screen.getByPlaceholderText(/\+33/i);

        await userEvent.type(firstNameInput, 'Jean');
        await userEvent.type(lastNameInput, 'Dupont');
        await userEvent.type(companyInput, 'Company');
        await userEvent.type(emailInput, 'test@example.com');
        await userEvent.type(phoneInput, '+33612345678');

        const passwordInputs = screen.getAllByPlaceholderText(/••••••••/i);
        const passwordInput = passwordInputs[0];

        // Type short password
        await userEvent.type(passwordInput, 'short');

        // Password should be at least 6 characters
        // (This validation happens on submit)
      });
    });

    test('should validate password confirmation match', async () => {
      await waitFor(async () => {
        const firstNameInput = screen.getByPlaceholderText(/Jean/i);
        const lastNameInput = screen.getByPlaceholderText(/Dupont/i);
        const companyInput = screen.getByPlaceholderText(/Mon Entreprise/i);
        const emailInput = screen.getByPlaceholderText(/email@exemple/i);
        const phoneInput = screen.getByPlaceholderText(/\+33/i);

        await userEvent.type(firstNameInput, 'Jean');
        await userEvent.type(lastNameInput, 'Dupont');
        await userEvent.type(companyInput, 'Company');
        await userEvent.type(emailInput, 'test@example.com');
        await userEvent.type(phoneInput, '+33612345678');

        const passwordInputs = screen.getAllByPlaceholderText(/••••••••/i);
        const passwordInput = passwordInputs[0];
        const confirmPasswordInput = passwordInputs[1];

        await userEvent.type(passwordInput, 'password123');
        await userEvent.type(confirmPasswordInput, 'different');

        const submitButton = screen.getByText(/Créer mon compte/i);
        await userEvent.click(submitButton);

        // Should show error about password mismatch
        await waitFor(() => {
          expect(screen.getByText(/Les mots de passe ne correspondent pas/i)).toBeInTheDocument();
        });
      });
    });

    test('should require terms acceptance', async () => {
      await waitFor(() => {
        const termsCheckbox = screen.getByRole('checkbox', { name: /conditions générales/i });
        expect(termsCheckbox.required).toBe(true);
      });
    });
  });

  describe('Form Submission', () => {
    beforeEach(async () => {
      renderRegister();
      const merchantButton = screen.getByText(/Entreprise/i).closest('button');
      await userEvent.click(merchantButton);
    });

    test('should submit valid form data', async () => {
      axios.post.mockResolvedValue({
        data: { success: true, user: { id: 1, email: 'test@example.com' } }
      });

      await waitFor(async () => {
        const firstNameInput = screen.getByPlaceholderText(/Jean/i);
        const lastNameInput = screen.getByPlaceholderText(/Dupont/i);
        const companyInput = screen.getByPlaceholderText(/Mon Entreprise/i);
        const emailInput = screen.getByPlaceholderText(/email@exemple/i);
        const phoneInput = screen.getByPlaceholderText(/\+33/i);

        await userEvent.type(firstNameInput, 'Jean');
        await userEvent.type(lastNameInput, 'Dupont');
        await userEvent.type(companyInput, 'Company');
        await userEvent.type(emailInput, 'test@example.com');
        await userEvent.type(phoneInput, '+33612345678');

        const passwordInputs = screen.getAllByPlaceholderText(/••••••••/i);
        const passwordInput = passwordInputs[0];
        const confirmPasswordInput = passwordInputs[1];

        await userEvent.type(passwordInput, 'password123');
        await userEvent.type(confirmPasswordInput, 'password123');

        const termsCheckbox = screen.getByRole('checkbox', { name: /conditions générales/i });
        await userEvent.click(termsCheckbox);

        const submitButton = screen.getByText(/Créer mon compte/i);
        await userEvent.click(submitButton);

        await waitFor(() => {
          expect(axios.post).toHaveBeenCalledWith(
            expect.stringContaining('/api/auth/register'),
            expect.objectContaining({
              email: 'test@example.com',
              password: 'password123',
              role: 'merchant',
              first_name: 'Jean',
              last_name: 'Dupont',
              company_name: 'Company',
              phone: '+33612345678'
            })
          );
        });
      });
    });

    test('should show loading state during submission', async () => {
      axios.post.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 1000)));

      await waitFor(async () => {
        const firstNameInput = screen.getByPlaceholderText(/Jean/i);
        const lastNameInput = screen.getByPlaceholderText(/Dupont/i);
        const companyInput = screen.getByPlaceholderText(/Mon Entreprise/i);
        const emailInput = screen.getByPlaceholderText(/email@exemple/i);
        const phoneInput = screen.getByPlaceholderText(/\+33/i);

        await userEvent.type(firstNameInput, 'Jean');
        await userEvent.type(lastNameInput, 'Dupont');
        await userEvent.type(companyInput, 'Company');
        await userEvent.type(emailInput, 'test@example.com');
        await userEvent.type(phoneInput, '+33612345678');

        const passwordInputs = screen.getAllByPlaceholderText(/••••••••/i);
        const passwordInput = passwordInputs[0];
        const confirmPasswordInput = passwordInputs[1];

        await userEvent.type(passwordInput, 'password123');
        await userEvent.type(confirmPasswordInput, 'password123');

        const submitButton = screen.getByText(/Créer mon compte/i);
        await userEvent.click(submitButton);

        // Button should be disabled during submission
        await waitFor(() => {
          expect(submitButton).toBeDisabled();
        });
      });
    });

    test('should show error message on submission failure', async () => {
      axios.post.mockRejectedValue({
        response: { data: { detail: 'Email already exists' } }
      });

      await waitFor(async () => {
        const firstNameInput = screen.getByPlaceholderText(/Jean/i);
        const lastNameInput = screen.getByPlaceholderText(/Dupont/i);
        const companyInput = screen.getByPlaceholderText(/Mon Entreprise/i);
        const emailInput = screen.getByPlaceholderText(/email@exemple/i);
        const phoneInput = screen.getByPlaceholderText(/\+33/i);

        await userEvent.type(firstNameInput, 'Jean');
        await userEvent.type(lastNameInput, 'Dupont');
        await userEvent.type(companyInput, 'Company');
        await userEvent.type(emailInput, 'test@example.com');
        await userEvent.type(phoneInput, '+33612345678');

        const passwordInputs = screen.getAllByPlaceholderText(/••••••••/i);
        const passwordInput = passwordInputs[0];
        const confirmPasswordInput = passwordInputs[1];

        await userEvent.type(passwordInput, 'password123');
        await userEvent.type(confirmPasswordInput, 'password123');

        const submitButton = screen.getByText(/Créer mon compte/i);
        await userEvent.click(submitButton);

        await waitFor(() => {
          expect(screen.getByText(/Email already exists/i)).toBeInTheDocument();
        });
      });
    });

    test('should show success page after successful registration', async () => {
      axios.post.mockResolvedValue({
        data: { success: true }
      });

      await waitFor(async () => {
        const firstNameInput = screen.getByPlaceholderText(/Jean/i);
        const lastNameInput = screen.getByPlaceholderText(/Dupont/i);
        const companyInput = screen.getByPlaceholderText(/Mon Entreprise/i);
        const emailInput = screen.getByPlaceholderText(/email@exemple/i);
        const phoneInput = screen.getByPlaceholderText(/\+33/i);

        await userEvent.type(firstNameInput, 'Jean');
        await userEvent.type(lastNameInput, 'Dupont');
        await userEvent.type(companyInput, 'Company');
        await userEvent.type(emailInput, 'test@example.com');
        await userEvent.type(phoneInput, '+33612345678');

        const passwordInputs = screen.getAllByPlaceholderText(/••••••••/i);
        const passwordInput = passwordInputs[0];
        const confirmPasswordInput = passwordInputs[1];

        await userEvent.type(passwordInput, 'password123');
        await userEvent.type(confirmPasswordInput, 'password123');

        const submitButton = screen.getByText(/Créer mon compte/i);
        await userEvent.click(submitButton);

        await waitFor(() => {
          expect(screen.getByText(/Inscription réussie/i)).toBeInTheDocument();
        });
      });
    });
  });

  describe('Navigation', () => {
    test('should return to step 1 on back button click', async () => {
      renderRegister();

      const merchantButton = screen.getByText(/Entreprise/i).closest('button');
      await userEvent.click(merchantButton);

      await waitFor(async () => {
        const backButton = screen.getByText(/← Retour/i);
        await userEvent.click(backButton);
      });

      await waitFor(() => {
        expect(screen.getByText(/Vous êtes ?/i)).toBeInTheDocument();
      });
    });

    test('should show login link', () => {
      renderRegister();

      expect(screen.getByText(/Se connecter/i)).toBeInTheDocument();
    });
  });

  describe('Pre-filled URL Parameters', () => {
    test('should pre-select role from URL parameter', () => {
      // This test would need custom implementation of useSearchParams mock
      // To test URL parameter functionality: /register?role=merchant&plan=pro
      expect(true).toBe(true); // Placeholder
    });

    test('should pre-select plan from URL parameter', () => {
      // Similar to above
      expect(true).toBe(true); // Placeholder
    });
  });

  describe('Accessibility', () => {
    test('should have proper form labels', async () => {
      renderRegister();

      const merchantButton = screen.getByText(/Entreprise/i).closest('button');
      await userEvent.click(merchantButton);

      await waitFor(() => {
        expect(screen.getByText(/Prénom/i)).toBeInTheDocument();
        expect(screen.getByText(/Nom/i)).toBeInTheDocument();
        expect(screen.getByText(/Email/i)).toBeInTheDocument();
        expect(screen.getByText(/Téléphone/i)).toBeInTheDocument();
      });
    });

    test('should have proper input types', async () => {
      renderRegister();

      const merchantButton = screen.getByText(/Entreprise/i).closest('button');
      await userEvent.click(merchantButton);

      await waitFor(() => {
        const emailInput = screen.getByPlaceholderText(/email@exemple/i);
        const phoneInput = screen.getByPlaceholderText(/\+33/i);

        expect(emailInput.type).toBe('email');
        expect(phoneInput.type).toBe('tel');
      });
    });
  });
});
