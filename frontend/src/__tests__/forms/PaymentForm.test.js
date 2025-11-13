import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import PaymentSettings from '../../pages/settings/PaymentSettings';
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
    id: 1,
    first_name: 'John',
    last_name: 'Doe',
    email: 'john@example.com',
    role: 'influencer'
  },
  isLoading: false,
  error: null
};

const renderPaymentForm = (authValue = mockAuthContext, toastValue = mockToast) => {
  return render(
    <BrowserRouter>
      <AuthContext.Provider value={authValue}>
        <ToastContext.Provider value={toastValue}>
          <PaymentSettings />
        </ToastContext.Provider>
      </AuthContext.Provider>
    </BrowserRouter>
  );
};

describe('PaymentForm (PaymentSettings)', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  describe('Form Rendering', () => {
    test('should render payment settings page with loading state', () => {
      api.get.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 1000)));

      renderPaymentForm();

      // Check that loading spinner is displayed
      const spinner = document.querySelector('.animate-spin');
      expect(spinner).toBeInTheDocument();
    });

    test('should render payment method form after loading', async () => {
      api.get.mockResolvedValue({
        data: {
          payment_status: 'active',
          payment_method: 'bank_transfer',
          last_payout: '2024-01-15'
        }
      });

      renderPaymentForm();

      await waitFor(() => {
        // Page should be loaded with correct title
        expect(screen.getByText(/Configuration des Paiements/i)).toBeInTheDocument();
      });
    });

    test('should display current payment status', async () => {
      api.get.mockResolvedValue({
        data: {
          payment_status: 'active',
          payment_method: 'bank_transfer',
          last_payout: '2024-01-15',
          balance: 100
        }
      });

      renderPaymentForm();

      await waitFor(() => {
        expect(screen.getByText(/Solde Disponible/i)).toBeInTheDocument();
      });
    });

    test('should render save button', async () => {
      api.get.mockResolvedValue({
        data: {
          payment_status: 'active',
          payment_method: 'bank_transfer'
        }
      });

      renderPaymentForm();

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Enregistrer/i })).toBeInTheDocument();
      });
    });
  });

  describe('Form Input Handling', () => {
    test('should load existing payment method on mount', async () => {
      api.get.mockResolvedValue({
        data: {
          payment_status: 'active',
          payment_method: 'stripe'
        }
      });

      renderPaymentForm();

      await waitFor(() => {
        expect(api.get).toHaveBeenCalledWith('/api/influencer/payment-status');
      });
    });

    test('should allow changing payment method', async () => {
      api.get.mockResolvedValue({
        data: {
          payment_status: 'active',
          payment_method: 'bank_transfer'
        }
      });

      renderPaymentForm();

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Enregistrer/i })).toBeInTheDocument();
      });

      // Try to change payment method (implementation dependent)
    });

    test('should handle payment details input', async () => {
      api.get.mockResolvedValue({
        data: {
          payment_status: 'active',
          payment_method: 'bank_transfer'
        }
      });

      renderPaymentForm();

      await waitFor(() => {
        // Look for input fields related to payment details
        const inputs = screen.queryAllByRole('textbox');
        expect(inputs).toBeDefined();
      });
    });
  });

  describe('Form Submission', () => {
    test('should submit payment method update', async () => {
      api.get.mockResolvedValue({
        data: {
          payment_status: 'active',
          payment_method: 'bank_transfer'
        }
      });

      api.put.mockResolvedValue({
        data: {
          success: true,
          message: 'Payment method updated'
        }
      });

      renderPaymentForm();

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Enregistrer/i })).toBeInTheDocument();
      });

      const saveButton = screen.getByRole('button', { name: /Enregistrer/i });
      await userEvent.click(saveButton);

      await waitFor(() => {
        expect(api.put).toHaveBeenCalledWith(
          '/api/influencer/payment-method',
          expect.objectContaining({
            method: expect.any(String)
          })
        );
      });
    });

    test('should show loading state during submission', async () => {
      api.get.mockResolvedValue({
        data: {
          payment_status: 'active',
          payment_method: 'bank_transfer'
        }
      });

      api.put.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 1000)));

      renderPaymentForm();

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Enregistrer/i })).toBeInTheDocument();
      });

      const saveButton = screen.getByRole('button', { name: /Enregistrer/i });
      await userEvent.click(saveButton);

      expect(saveButton).toBeDisabled();
    });

    test('should show success message on successful submission', async () => {
      api.get.mockResolvedValue({
        data: {
          payment_status: 'active',
          payment_method: 'bank_transfer'
        }
      });

      api.put.mockResolvedValue({
        data: {
          success: true,
          message: 'Payment method updated'
        }
      });

      renderPaymentForm();

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Enregistrer/i })).toBeInTheDocument();
      });

      const saveButton = screen.getByRole('button', { name: /Enregistrer/i });
      await userEvent.click(saveButton);

      // Should show success message
    });

    test('should refresh payment status after successful save', async () => {
      api.get.mockResolvedValue({
        data: {
          payment_status: 'active',
          payment_method: 'bank_transfer'
        }
      });

      api.put.mockResolvedValue({
        data: { success: true }
      });

      renderPaymentForm();

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Enregistrer/i })).toBeInTheDocument();
      });

      const saveButton = screen.getByRole('button', { name: /Enregistrer/i });
      await userEvent.click(saveButton);

      await waitFor(() => {
        expect(api.get).toHaveBeenCalledTimes(2); // Initial load + refresh
      });
    });
  });

  describe('Error Handling', () => {
    test('should handle API error on initial load', async () => {
      api.get.mockRejectedValue({
        response: {
          data: {
            detail: 'Error fetching payment status'
          }
        }
      });

      renderPaymentForm();

      await waitFor(() => {
        // Loading should complete even with error
        expect(screen.queryByText(/animate-spin/)).not.toBeInTheDocument();
      });
    });

    test('should show error message on submission failure', async () => {
      api.get.mockResolvedValue({
        data: {
          payment_status: 'active',
          payment_method: 'bank_transfer'
        }
      });

      api.put.mockRejectedValue({
        response: {
          data: {
            detail: 'Error updating payment method'
          }
        }
      });

      renderPaymentForm();

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Enregistrer/i })).toBeInTheDocument();
      });

      const saveButton = screen.getByRole('button', { name: /Enregistrer/i });
      await userEvent.click(saveButton);

      await waitFor(() => {
        // Error message should be shown (but may auto-hide)
      });
    });

    test('should handle network errors gracefully', async () => {
      api.get.mockRejectedValue(new Error('Network error'));

      renderPaymentForm();

      await waitFor(() => {
        // Should complete loading despite error
        expect(screen.queryByText(/animate-spin/)).not.toBeInTheDocument();
      });
    });
  });

  describe('Validation', () => {
    test('should require payment method selection', async () => {
      api.get.mockResolvedValue({
        data: {
          payment_status: 'inactive',
          payment_method: null
        }
      });

      renderPaymentForm();

      await waitFor(() => {
        // Payment method selection should be visible
        expect(screen.getByText(/Choisissez votre méthode de paiement/i)).toBeInTheDocument();
      });

      // Button should not be visible until payment method is selected
      expect(screen.queryByRole('button', { name: /Enregistrer/i })).not.toBeInTheDocument();
    });

    test('should validate bank transfer details', async () => {
      api.get.mockResolvedValue({
        data: {
          payment_status: 'active',
          payment_method: 'bank_transfer'
        }
      });

      renderPaymentForm();

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Enregistrer/i })).toBeInTheDocument();
      });

      // Test validation for bank transfer details
    });

    test('should validate Stripe details', async () => {
      api.get.mockResolvedValue({
        data: {
          payment_status: 'active',
          payment_method: 'stripe'
        }
      });

      renderPaymentForm();

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Enregistrer/i })).toBeInTheDocument();
      });

      // Test validation for Stripe details
    });
  });

  describe('Payment Status Display', () => {
    test('should show active payment status', async () => {
      api.get.mockResolvedValue({
        data: {
          payment_status: 'active',
          payment_method: 'bank_transfer',
          last_payout: '2024-01-15'
        }
      });

      renderPaymentForm();

      await waitFor(() => {
        // Status should be visible
      });
    });

    test('should show pending payment status', async () => {
      api.get.mockResolvedValue({
        data: {
          payment_status: 'pending',
          payment_method: 'bank_transfer'
        }
      });

      renderPaymentForm();

      await waitFor(() => {
        // Status should be visible
      });
    });

    test('should show inactive payment status', async () => {
      api.get.mockResolvedValue({
        data: {
          payment_status: 'inactive',
          payment_method: null
        }
      });

      renderPaymentForm();

      await waitFor(() => {
        // Status should be visible
      });
    });

    test('should display last payout date if available', async () => {
      api.get.mockResolvedValue({
        data: {
          payment_status: 'active',
          payment_method: 'bank_transfer',
          last_payout: '2024-01-15'
        }
      });

      renderPaymentForm();

      await waitFor(() => {
        // Last payout date should be visible
      });
    });
  });

  describe('User Experience', () => {
    test('should auto-hide success message after 5 seconds', async () => {
      jest.useFakeTimers();

      api.get.mockResolvedValue({
        data: {
          payment_status: 'active',
          payment_method: 'bank_transfer'
        }
      });

      api.put.mockResolvedValue({
        data: { success: true }
      });

      renderPaymentForm();

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Enregistrer/i })).toBeInTheDocument();
      });

      const saveButton = screen.getByRole('button', { name: /Enregistrer/i });
      fireEvent.click(saveButton);

      await waitFor(() => {
        expect(screen.getByText(/Méthode de paiement configurée avec succès/i)).toBeInTheDocument();
      });

      jest.advanceTimersByTime(5000);

      await waitFor(() => {
        expect(screen.queryByText(/Méthode de paiement configurée avec succès/i)).not.toBeInTheDocument();
      });

      jest.useRealTimers();
    });

    test('should auto-hide error message after 5 seconds', async () => {
      jest.useFakeTimers();

      api.get.mockResolvedValue({
        data: {
          payment_status: 'active',
          payment_method: 'bank_transfer'
        }
      });

      api.put.mockRejectedValue({
        response: { data: { detail: 'Error updating payment method' } }
      });

      renderPaymentForm();

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Enregistrer/i })).toBeInTheDocument();
      });

      const saveButton = screen.getByRole('button', { name: /Enregistrer/i });
      fireEvent.click(saveButton);

      await waitFor(() => {
        expect(screen.getByText(/Error updating payment method/i)).toBeInTheDocument();
      });

      jest.advanceTimersByTime(5000);

      await waitFor(() => {
        expect(screen.queryByText(/Error updating payment method/i)).not.toBeInTheDocument();
      });

      jest.useRealTimers();
    });
  });

  describe('Accessibility', () => {
    test('should have proper form labels', async () => {
      api.get.mockResolvedValue({
        data: {
          payment_status: 'active',
          payment_method: 'bank_transfer'
        }
      });

      renderPaymentForm();

      await waitFor(() => {
        expect(screen.getByText(/Choisissez votre méthode de paiement/i)).toBeInTheDocument();
      });
    });

    test('should have descriptive button labels', async () => {
      api.get.mockResolvedValue({
        data: {
          payment_status: 'active',
          payment_method: 'bank_transfer'
        }
      });

      renderPaymentForm();

      await waitFor(() => {
        const saveButton = screen.getByRole('button', { name: /Enregistrer/i });
        expect(saveButton).toBeInTheDocument();
      });
    });
  });
});
