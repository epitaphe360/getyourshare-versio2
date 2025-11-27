import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import InfluencerDashboard from '../pages/dashboards/InfluencerDashboard';
import MerchantDashboard from '../pages/dashboards/MerchantDashboard';
import CommercialDashboard from '../pages/dashboards/CommercialDashboard';
import AdminDashboard from '../pages/dashboards/AdminDashboard';
import { AuthProvider } from '../context/AuthContext';
import { ToastProvider } from '../context/ToastContext';
import { I18nProvider } from '../i18n/i18n';
import api from '../utils/api';
import serviceApi from '../services/api';

// Mock framer-motion to avoid layout/animation issues in JSDOM
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }) => <div {...props}>{children}</div>,
  },
  AnimatePresence: ({ children }) => <>{children}</>,
}));

// Mock dependencies
jest.mock('../utils/api');
jest.mock('../services/api');
// jest.mock('react-chartjs-2'); // Removed as it is not used
jest.mock('recharts', () => ({
  ResponsiveContainer: ({ children }) => <div>{children}</div>,
  LineChart: () => <div>LineChart</div>,
  Line: () => null,
  AreaChart: () => <div>AreaChart</div>,
  Area: () => null,
  BarChart: () => <div>BarChart</div>,
  Bar: () => null,
  PieChart: () => <div>PieChart</div>,
  Pie: () => null,
  Cell: () => null,
  XAxis: () => null,
  YAxis: () => null,
  CartesianGrid: () => null,
  Tooltip: () => null,
  Legend: () => null,
}));

// Mock Contexts
const mockUser = { id: 1, first_name: 'Test', role: 'influencer' };
const MockProviders = ({ children }) => (
  <BrowserRouter>
    <AuthProvider value={{ user: mockUser }}>
      <ToastProvider>
        <I18nProvider>
          {children}
        </I18nProvider>
      </ToastProvider>
    </AuthProvider>
  </BrowserRouter>
);

describe('Dashboards NaN Check', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Default mock implementation for api.get to return safe empty structures
    const defaultResponse = { 
        data: {
            links: [],
            invitations: [],
            requests: [],
            recommendations: [],
            upcoming_lives: [],
            products: [],
            data: [], // for charts
            // Commercial dashboard specific
            nouveau: { count: 0, value: 0 },
            qualifie: { count: 0, value: 0 },
            en_negociation: { count: 0, value: 0 },
            conclu: { count: 0, value: 0 }
        } 
    };

    // Helper to return array directly if needed (for CommercialDashboard lists)
    // But CommercialDashboard expects array in response.data for some endpoints?
    // Let's check CommercialDashboard.js:
    // const leadsRes = await api.get('/api/commercial/leads?limit=20'); setLeads(leadsRes.data);
    // So leadsRes.data MUST be an array.
    
    // We need a smarter mock.
    const smartMock = (url) => {
        if (url.includes('/leads') || url.includes('/tracking-links') || url.includes('/templates')) {
            return Promise.resolve({ data: [] });
        }
        return Promise.resolve(defaultResponse);
    };

    api.get.mockImplementation(smartMock);
    serviceApi.get.mockImplementation(smartMock);
    
    api.post.mockResolvedValue({ data: {} });
    serviceApi.post.mockResolvedValue({ data: {} });
  });

  const checkForNaN = () => {
    const bodyText = document.body.textContent;
    // Check for "NaN" but exclude "Finance" (contains nan) or "Maintenant" (contains nan)
    // We look for "NaN" as a whole word or followed by % or currency
    const nanRegex = /\bNaN\b|NaN%|NaN €|NaN€/i;
    // Actually, "NaN" is case sensitive in JS output usually.
    // But let's be strict.
    // However, "Finance" has "nan". "Maintenant" has "nan".
    // So we must match case sensitive "NaN".
    
    // We search for the literal string "NaN" in the visible text.
    // Note: screen.queryByText(/NaN/) might match "Finance".
    
    // Let's iterate over all elements and check their text content.
    // Or just check document.body.innerHTML for "NaN" surrounded by non-letters?
    
    // A simpler check:
    const allText = document.body.textContent;
    if (allText.includes('NaN')) {
        // Verify it's not part of a word like "Finance"
        // We can use a regex to find "NaN" that is NOT part of a word.
        // But "NaN%" is what we are looking for mostly.
        const matches = allText.match(/NaN/g);
        if (matches) {
            // Check context
            // This is a bit heuristic.
            // Let's try to find elements with exact text "NaN" or "NaN%"
        }
    }
    
    // Using regex with word boundaries for "NaN"
    const hasNaN = /\bNaN\b/.test(allText);
    if (hasNaN) {
        // Double check it's not "Finance" (which matches \bNaN\b ?? No, Finance is one word)
        // \bNaN\b matches " NaN " but not "Finance".
        // It matches "Value: NaN".
        // It matches "NaN%".
        // It does NOT match "Finance".
        // So \bNaN\b is a good check.
        throw new Error(`Found "NaN" in the document!`);
    }
  };

  test('InfluencerDashboard should not display NaN with empty data', async () => {
    // Uses default smartMock

    await act(async () => {
      render(
        <MockProviders>
          <InfluencerDashboard />
        </MockProviders>
      );
    });

    await waitFor(() => {
        expect(screen.queryByText(/Chargement/i)).not.toBeInTheDocument();
    });

    checkForNaN();
  });

  test('MerchantDashboard should not display NaN with empty data', async () => {
    // Uses default smartMock

    await act(async () => {
      render(
        <MockProviders>
          <MerchantDashboard />
        </MockProviders>
      );
    });

    await waitFor(() => {
        expect(screen.queryByText(/Chargement/i)).not.toBeInTheDocument();
    });

    checkForNaN();
  });

  test('CommercialDashboard should not display NaN with empty data', async () => {
    // Uses default smartMock
    
    // Mock localStorage for user profile
    Storage.prototype.getItem = jest.fn(() => JSON.stringify({ subscription_tier: 'starter' }));

    await act(async () => {
      render(
        <MockProviders>
          <CommercialDashboard />
        </MockProviders>
      );
    });

    await waitFor(() => {
        expect(screen.queryByText(/Chargement/i)).not.toBeInTheDocument();
    });

    checkForNaN();
  });

  test('AdminDashboard should not display NaN with empty data', async () => {
    // Uses default smartMock

    await act(async () => {
      render(
        <MockProviders>
          <AdminDashboard />
        </MockProviders>
      );
    });

    await waitFor(() => {
        expect(screen.queryByText(/Chargement/i)).not.toBeInTheDocument();
    });

    checkForNaN();
  });
  
  test('Dashboards should handle null values gracefully', async () => {
     // Force nulls
     api.get.mockResolvedValue({ data: null });
     serviceApi.get.mockResolvedValue({ data: null });

     await act(async () => {
      render(
        <MockProviders>
          <InfluencerDashboard />
        </MockProviders>
      );
    });
    checkForNaN();
  });
});
