/**
 * Error Handler Utility
 * Formats API errors for display in toasts and UI
 */

/**
 * Extract user-friendly error message from API response
 * @param {Error} error - Axios error object
 * @param {string} fallbackMessage - Default message if extraction fails
 * @returns {string} - Formatted error message
 */
export const getErrorMessage = (error, fallbackMessage = 'Une erreur est survenue') => {
  // No error provided
  if (!error) {
    return fallbackMessage;
  }

  // Direct string error
  if (typeof error === 'string') {
    return error;
  }

  // Axios error with response
  if (error.response?.data) {
    const { detail } = error.response.data;

    // FastAPI validation error (array of objects)
    if (Array.isArray(detail)) {
      // Extract first error message
      const firstError = detail[0];
      if (firstError && firstError.msg) {
        // Format: "field: message"
        const field = firstError.loc && firstError.loc.length > 0
          ? firstError.loc[firstError.loc.length - 1]
          : '';
        return field ? `${field}: ${firstError.msg}` : firstError.msg;
      }
      return 'Erreur de validation';
    }

    // Simple string detail
    if (typeof detail === 'string') {
      return detail;
    }

    // Object with message
    if (detail && typeof detail === 'object' && detail.message) {
      return detail.message;
    }

    // Fallback to checking for 'message' field
    if (error.response.data.message) {
      return error.response.data.message;
    }
  }

  // Error object with message
  if (error.message) {
    return error.message;
  }

  return fallbackMessage;
};

/**
 * Format validation errors for form display
 * @param {Error} error - Axios error object
 * @returns {Object} - Object mapping field names to error messages
 */
export const getValidationErrors = (error) => {
  const errors = {};

  if (error.response?.data?.detail && Array.isArray(error.response.data.detail)) {
    error.response.data.detail.forEach((err) => {
      if (err.loc && err.loc.length > 0) {
        const field = err.loc[err.loc.length - 1];
        errors[field] = err.msg;
      }
    });
  }

  return errors;
};

/**
 * Check if error is a specific HTTP status code
 * @param {Error} error - Axios error object
 * @param {number} statusCode - HTTP status code to check
 * @returns {boolean}
 */
export const isErrorStatus = (error, statusCode) => {
  return error.response?.status === statusCode;
};

/**
 * Check if error is authentication related (401 or 403)
 * @param {Error} error - Axios error object
 * @returns {boolean}
 */
export const isAuthError = (error) => {
  return isErrorStatus(error, 401) || isErrorStatus(error, 403);
};

/**
 * Check if error is validation error (422)
 * @param {Error} error - Axios error object
 * @returns {boolean}
 */
export const isValidationError = (error) => {
  return isErrorStatus(error, 422);
};

export default {
  getErrorMessage,
  getValidationErrors,
  isErrorStatus,
  isAuthError,
  isValidationError,
};
