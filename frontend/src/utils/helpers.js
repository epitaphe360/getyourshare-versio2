// Format currency
export const formatCurrency = (amount, currency = 'EUR') => {
  if (isNaN(amount) || amount === null || amount === undefined) return '0,00 €';
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: currency,
  }).format(amount);
};

// Format date
export const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('fr-FR', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
};

// Format date short
export const formatDateShort = (dateString) => {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('fr-FR', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(date);
};

// Format number
export const formatNumber = (num) => {
  if (isNaN(num) || num === null || num === undefined) return '0';
  return new Intl.NumberFormat('fr-FR').format(num);
};

// Get status badge color
export const getStatusColor = (status) => {
  // Convert to string and handle null/undefined
  if (!status) return 'bg-gray-100 text-gray-800';
  
  try {
    const statusStr = typeof status === 'string' ? status : String(status);
    
    const colors = {
      approved: 'bg-green-100 text-green-800',
      pending: 'bg-yellow-100 text-yellow-800',
      rejected: 'bg-red-100 text-red-800',
      denied: 'bg-red-100 text-red-800',
      active: 'bg-blue-100 text-blue-800',
      paused: 'bg-gray-100 text-gray-800',
      inactive: 'bg-gray-100 text-gray-800',
      draft: 'bg-purple-100 text-purple-800',
      completed: 'bg-green-100 text-green-800',
      ended: 'bg-red-100 text-red-800',
      archived: 'bg-gray-100 text-gray-800',
    };
    return colors[statusStr.toLowerCase()] || 'bg-gray-100 text-gray-800';
  } catch (e) {
    console.warn('Error getting status color:', e);
    return 'bg-gray-100 text-gray-800';
  }
};

// Truncate text
export const truncateText = (text, maxLength = 50) => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

// Format percentage
export const formatPercentage = (value, decimals = 1) => {
  if (isNaN(value) || value === null || value === undefined) return '0%';
  return `${Number(value).toFixed(decimals)}%`;
};

// Format relative time (il y a X minutes/heures/jours)
export const formatRelativeTime = (dateString) => {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now - date;
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHours = Math.floor(diffMin / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffSec < 60) return 'À l\'instant';
  if (diffMin < 60) return `Il y a ${diffMin} minute${diffMin > 1 ? 's' : ''}`;
  if (diffHours < 24) return `Il y a ${diffHours} heure${diffHours > 1 ? 's' : ''}`;
  if (diffDays < 30) return `Il y a ${diffDays} jour${diffDays > 1 ? 's' : ''}`;
  return formatDateShort(dateString);
};

// Export data to CSV
export const exportToCSV = (data, filename = 'export') => {
  if (!data || data.length === 0) {
    console.warn('No data to export');
    return;
  }

  // Get headers from first object
  const headers = Object.keys(data[0]);

  // Create CSV content
  const csvContent = [
    headers.join(','), // Header row
    ...data.map(row =>
      headers.map(header => {
        const value = row[header];
        // Escape commas and quotes
        if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
          return `"${value.replace(/"/g, '""')}"`;
        }
        return value ?? '';
      }).join(',')
    )
  ].join('\n');

  // Create blob and download
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${filename}_${new Date().toISOString().split('T')[0]}.csv`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

// Copy to clipboard
export const copyToClipboard = async (text) => {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return true;
    } else {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = text;
      textArea.style.position = 'fixed';
      textArea.style.left = '-999999px';
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      const successful = document.execCommand('copy');
      document.body.removeChild(textArea);
      return successful;
    }
  } catch (error) {
    console.error('Failed to copy:', error);
    return false;
  }
};

// Get initials from name
export const getInitials = (name) => {
  if (!name) return '??';
  const parts = name.trim().split(' ');
  if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
};

// Generate random color for avatars
export const generateColorFromString = (str) => {
  if (!str) return '#6B7280'; // gray-500
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  const colors = [
    '#3B82F6', // blue-500
    '#8B5CF6', // violet-500
    '#EC4899', // pink-500
    '#F59E0B', // amber-500
    '#10B981', // emerald-500
    '#EF4444', // red-500
    '#6366F1', // indigo-500
    '#14B8A6', // teal-500
  ];
  return colors[Math.abs(hash) % colors.length];
};

// Debounce function
export const debounce = (func, wait = 300) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

// Get trend indicator
export const getTrendIndicator = (current, previous) => {
  if (!previous || previous === 0) return { value: 0, isPositive: true };
  const change = ((current - previous) / previous) * 100;
  return {
    value: Math.abs(change),
    isPositive: change >= 0
  };
};
