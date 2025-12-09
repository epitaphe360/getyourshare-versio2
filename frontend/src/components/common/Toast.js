import React, { useEffect } from 'react';
import { CheckCircle, XCircle, Info, AlertTriangle, X } from 'lucide-react';

const Toast = ({
  message,
  type = 'success', // success, error, info, warning
  onClose,
  duration = 3000,
  action,
  id
}) => {
  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        onClose();
      }, duration);
      return () => clearTimeout(timer);
    }
  }, [duration, onClose]);

  const icons = {
    success: <CheckCircle className="text-green-500" size={24} aria-hidden="true" />,
    error: <XCircle className="text-red-500" size={24} aria-hidden="true" />,
    info: <Info className="text-blue-500" size={24} aria-hidden="true" />,
    warning: <AlertTriangle className="text-yellow-500" size={24} aria-hidden="true" />
  };

  const bgColors = {
    success: 'bg-green-50 border-green-200',
    error: 'bg-red-50 border-red-200',
    info: 'bg-blue-50 border-blue-200',
    warning: 'bg-yellow-50 border-yellow-200'
  };

  const typeLabel = {
    success: 'Success',
    error: 'Error',
    info: 'Information',
    warning: 'Warning'
  };

  // Ensure message is always a string to prevent React error #31
  const displayMessage = typeof message === 'string'
    ? message
    : typeof message === 'object' && message !== null
      ? JSON.stringify(message)
      : String(message);

  return (
    <div
      role="alert"
      aria-live="polite"
      aria-atomic="true"
      className={`fixed top-4 right-4 z-50 max-w-md w-full ${bgColors[type]} border rounded-lg shadow-lg p-4 flex items-start gap-3 animate-slide-in`}
      id={`toast-${id}`}
    >
      <div className="flex-shrink-0 mt-0.5" aria-label={typeLabel[type]}>
        {icons[type]}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-900">{displayMessage}</p>
        {action && (
          <button
            onClick={action.onClick}
            className="mt-2 text-sm font-medium text-blue-600 hover:text-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded px-1"
            type="button"
          >
            {action.label}
          </button>
        )}
      </div>
      <button
        onClick={onClose}
        className="flex-shrink-0 text-gray-400 hover:text-gray-600 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-400 rounded p-0.5"
        aria-label={`Dismiss ${typeLabel[type]} notification`}
        type="button"
      >
        <X size={18} aria-hidden="true" />
      </button>
    </div>
  );
};

// Toast Container for managing multiple toasts
export const ToastContainer = ({ toasts, removeToast }) => {
  return (
    <div className="fixed top-4 right-4 z-50 space-y-2" role="region" aria-label="Notifications" aria-live="polite">
      {toasts.map((toast, index) => (
        <Toast
          key={toast.id || index}
          {...toast}
          id={toast.id || index}
          onClose={() => removeToast(toast.id || index)}
        />
      ))}
    </div>
  );
};

export default Toast;
