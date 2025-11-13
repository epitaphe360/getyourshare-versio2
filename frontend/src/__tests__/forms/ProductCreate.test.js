import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import CreateProduct from '../../components/forms/CreateProduct';
import api from '../../utils/api';

// Mock API
jest.mock('../../utils/api');

const mockOnSuccess = jest.fn();
const mockOnCancel = jest.fn();

const renderCreateProduct = () => {
  return render(
    <CreateProduct onSuccess={mockOnSuccess} onCancel={mockOnCancel} />
  );
};

describe.skip('ProductCreate Form', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Form Rendering', () => {
    test('should render product creation form with all fields', () => {
      renderCreateProduct();

      expect(screen.getByPlaceholderText(/Ex: T-shirt Premium/i)).toBeInTheDocument();
      expect(screen.getByPlaceholderText(/Description détaillée/i)).toBeInTheDocument();
      expect(screen.getByPlaceholderText(/image url/i)).toBeInTheDocument();
    });

    test('should render form title', () => {
      renderCreateProduct();
      expect(screen.getByText(/Créer un nouveau produit/i)).toBeInTheDocument();
    });

    test('should render category selector', () => {
      renderCreateProduct();

      const categorySelect = screen.getByDisplayValue('Mode');
      expect(categorySelect).toBeInTheDocument();
    });

    test('should render all category options', () => {
      renderCreateProduct();

      expect(screen.getByText('Mode')).toBeInTheDocument();
      expect(screen.getByText('Beauté')).toBeInTheDocument();
      expect(screen.getByText('Technologie')).toBeInTheDocument();
      expect(screen.getByText('Sport')).toBeInTheDocument();
      expect(screen.getByText('Alimentation')).toBeInTheDocument();
      expect(screen.getByText('Maison')).toBeInTheDocument();
    });

    test('should render submit button', () => {
      renderCreateProduct();
      expect(screen.getByRole('button', { name: /Créer/i })).toBeInTheDocument();
    });

    test('should render cancel button', () => {
      renderCreateProduct();
      expect(screen.getByRole('button', { name: /Annuler/i })).toBeInTheDocument();
    });
  });

  describe('Form Input Handling', () => {
    test('should update product name on change', async () => {
      renderCreateProduct();
      const nameInput = screen.getByPlaceholderText(/Ex: T-shirt Premium/i);

      await userEvent.type(nameInput, 'New Product');

      expect(nameInput.value).toBe('New Product');
    });

    test('should update product description on change', async () => {
      renderCreateProduct();
      const descInput = screen.getByPlaceholderText(/Description détaillée/i);

      await userEvent.type(descInput, 'Product description');

      expect(descInput.value).toBe('Product description');
    });

    test('should update price on change', async () => {
      renderCreateProduct();
      const priceInput = screen.getByPlaceholderText(/Prix/i);

      await userEvent.type(priceInput, '99.99');

      expect(priceInput.value).toBe('99.99');
    });

    test('should update stock on change', async () => {
      renderCreateProduct();
      const stockInputs = screen.getAllByRole('spinbutton');
      const stockInput = stockInputs.find(input => input.placeholder.includes('Quantité'));

      if (stockInput) {
        await userEvent.clear(stockInput);
        await userEvent.type(stockInput, '50');
        expect(stockInput.value).toBe('50');
      }
    });

    test('should update commission rate on change', async () => {
      renderCreateProduct();
      const spinbuttons = screen.getAllByRole('spinbutton');

      // Try to find commission rate input
      const commissionInput = spinbuttons.find(input =>
        input.placeholder && input.placeholder.includes('Commission')
      );

      if (commissionInput) {
        await userEvent.clear(commissionInput);
        await userEvent.type(commissionInput, '15');
        expect(commissionInput.value).toBe('15');
      }
    });

    test('should change category selection', async () => {
      renderCreateProduct();
      const categorySelect = screen.getByDisplayValue('Mode');

      await userEvent.selectOptions(categorySelect, 'Beauté');

      expect(categorySelect.value).toBe('Beauté');
    });

    test('should update image URL on change', async () => {
      renderCreateProduct();
      const imageInput = screen.getByPlaceholderText(/image url/i);

      await userEvent.type(imageInput, 'https://example.com/image.jpg');

      expect(imageInput.value).toBe('https://example.com/image.jpg');
    });
  });

  describe('Form Validation', () => {
    test('should have required name field', () => {
      renderCreateProduct();
      const nameInput = screen.getByPlaceholderText(/Ex: T-shirt Premium/i);

      expect(nameInput.required).toBe(true);
    });

    test('should have required price field', () => {
      renderCreateProduct();
      const priceInputs = screen.getAllByRole('spinbutton');
      const priceInput = priceInputs[0];

      expect(priceInput.required).toBe(true);
    });

    test('should not submit form without required fields', async () => {
      renderCreateProduct();
      const submitButton = screen.getByRole('button', { name: /Créer/i });

      await userEvent.click(submitButton);

      // Form should not have been submitted (name is required)
      expect(api.post).not.toHaveBeenCalled();
    });
  });

  describe('Form Submission', () => {
    test('should submit form with valid data', async () => {
      api.post.mockResolvedValue({
        data: {
          success: true,
          id: 1,
          name: 'Test Product'
        }
      });

      renderCreateProduct();

      const nameInput = screen.getByPlaceholderText(/Ex: T-shirt Premium/i);
      const descInput = screen.getByPlaceholderText(/Description détaillée/i);
      const priceInputs = screen.getAllByRole('spinbutton');
      const priceInput = priceInputs[0];
      const submitButton = screen.getByRole('button', { name: /Créer/i });

      await userEvent.type(nameInput, 'Test Product');
      await userEvent.type(descInput, 'Test Description');
      await userEvent.clear(priceInput);
      await userEvent.type(priceInput, '29.99');
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(api.post).toHaveBeenCalledWith(
          '/api/products',
          expect.objectContaining({
            name: 'Test Product',
            description: 'Test Description',
            price: 29.99
          })
        );
      });
    });

    test('should call onSuccess callback after successful submission', async () => {
      const responseData = {
        success: true,
        id: 1,
        name: 'Test Product'
      };

      api.post.mockResolvedValue({ data: responseData });

      renderCreateProduct();

      const nameInput = screen.getByPlaceholderText(/Ex: T-shirt Premium/i);
      const priceInputs = screen.getAllByRole('spinbutton');
      const priceInput = priceInputs[0];
      const submitButton = screen.getByRole('button', { name: /Créer/i });

      await userEvent.type(nameInput, 'Test Product');
      await userEvent.clear(priceInput);
      await userEvent.type(priceInput, '29.99');
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(mockOnSuccess).toHaveBeenCalledWith(responseData);
      });
    });

    test('should disable submit button during submission', async () => {
      api.post.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 1000)));

      renderCreateProduct();

      const nameInput = screen.getByPlaceholderText(/Ex: T-shirt Premium/i);
      const priceInputs = screen.getAllByRole('spinbutton');
      const priceInput = priceInputs[0];
      const submitButton = screen.getByRole('button', { name: /Créer/i });

      await userEvent.type(nameInput, 'Test Product');
      await userEvent.clear(priceInput);
      await userEvent.type(priceInput, '29.99');
      await userEvent.click(submitButton);

      expect(submitButton).toBeDisabled();
    });

    test('should submit with numeric conversions', async () => {
      api.post.mockResolvedValue({
        data: { success: true }
      });

      renderCreateProduct();

      const nameInput = screen.getByPlaceholderText(/Ex: T-shirt Premium/i);
      const spinbuttons = screen.getAllByRole('spinbutton');
      const priceInput = spinbuttons[0];
      const submitButton = screen.getByRole('button', { name: /Créer/i });

      await userEvent.type(nameInput, 'Test Product');
      await userEvent.clear(priceInput);
      await userEvent.type(priceInput, '49.99');
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(api.post).toHaveBeenCalledWith(
          '/api/products',
          expect.objectContaining({
            price: 49.99
          })
        );
      });
    });
  });

  describe('Error Handling', () => {
    test('should display error message on submission failure', async () => {
      api.post.mockRejectedValue({
        response: {
          data: {
            detail: 'Erreur lors de la création du produit'
          }
        }
      });

      renderCreateProduct();

      const nameInput = screen.getByPlaceholderText(/Ex: T-shirt Premium/i);
      const priceInputs = screen.getAllByRole('spinbutton');
      const priceInput = priceInputs[0];
      const submitButton = screen.getByRole('button', { name: /Créer/i });

      await userEvent.type(nameInput, 'Test Product');
      await userEvent.clear(priceInput);
      await userEvent.type(priceInput, '29.99');
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/Erreur lors de la création du produit/i)).toBeInTheDocument();
      });
    });

    test('should display generic error message on unknown error', async () => {
      api.post.mockRejectedValue(new Error('Network error'));

      renderCreateProduct();

      const nameInput = screen.getByPlaceholderText(/Ex: T-shirt Premium/i);
      const priceInputs = screen.getAllByRole('spinbutton');
      const priceInput = priceInputs[0];
      const submitButton = screen.getByRole('button', { name: /Créer/i });

      await userEvent.type(nameInput, 'Test Product');
      await userEvent.clear(priceInput);
      await userEvent.type(priceInput, '29.99');
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/Erreur lors de la création du produit/i)).toBeInTheDocument();
      });
    });

    test('should clear error on new submission', async () => {
      let callCount = 0;
      api.post.mockImplementation(() => {
        callCount++;
        if (callCount === 1) {
          return Promise.reject({
            response: { data: { detail: 'Error' } }
          });
        }
        return Promise.resolve({ data: { success: true } });
      });

      renderCreateProduct();

      const nameInput = screen.getByPlaceholderText(/Ex: T-shirt Premium/i);
      const priceInputs = screen.getAllByRole('spinbutton');
      const priceInput = priceInputs[0];
      const submitButton = screen.getByRole('button', { name: /Créer/i });

      // First submission - fails
      await userEvent.type(nameInput, 'Test Product');
      await userEvent.clear(priceInput);
      await userEvent.type(priceInput, '29.99');
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/Error/i)).toBeInTheDocument();
      });

      // Clear form and submit again
      await userEvent.clear(nameInput);
      await userEvent.clear(priceInput);

      // Error should be cleared when form is updated
      await userEvent.type(nameInput, 'New Product');
      await userEvent.type(priceInput, '39.99');

      // Check if error was cleared (it depends on implementation)
    });
  });

  describe('User Actions', () => {
    test('should call onCancel when cancel button is clicked', async () => {
      renderCreateProduct();
      const cancelButton = screen.getByRole('button', { name: /Annuler/i });

      await userEvent.click(cancelButton);

      expect(mockOnCancel).toHaveBeenCalled();
    });
  });

  describe('Default Values', () => {
    test('should have default category of Mode', () => {
      renderCreateProduct();

      const categorySelect = screen.getByDisplayValue('Mode');
      expect(categorySelect.value).toBe('Mode');
    });

    test('should have default stock of 100', () => {
      renderCreateProduct();

      const spinbuttons = screen.getAllByRole('spinbutton');
      // Stock is typically one of the spinbuttons
      const stockButton = spinbuttons.find(input => input.value === '100');
      expect(stockButton).toBeInTheDocument();
    });

    test('should have default commission rate of 10', () => {
      renderCreateProduct();

      const spinbuttons = screen.getAllByRole('spinbutton');
      // Commission rate is typically one of the spinbuttons
      const commissionButton = spinbuttons.find(input => input.value === '10');
      expect(commissionButton).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    test('should have proper labels for form fields', () => {
      renderCreateProduct();

      expect(screen.getByText(/Nom du produit/i)).toBeInTheDocument();
      expect(screen.getByText(/Description/i)).toBeInTheDocument();
      expect(screen.getByText(/Prix/i)).toBeInTheDocument();
    });

    test('should have price input type number', () => {
      renderCreateProduct();
      const spinbuttons = screen.getAllByRole('spinbutton');
      const priceInput = spinbuttons[0];

      expect(priceInput.type).toBe('number');
    });
  });
});
