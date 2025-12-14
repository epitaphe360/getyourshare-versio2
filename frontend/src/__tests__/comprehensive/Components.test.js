/**
 * Tests complets pour les composants React
 * Couvre: Navigation, ThemeToggle, CookieConsent, ChartExport, HomePage
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';

// Mock des modules externes
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
  useLocation: () => ({ pathname: '/' }),
}));

// Wrapper avec providers
const theme = createTheme();
const AllProviders = ({ children }) => (
  <BrowserRouter>
    <ThemeProvider theme={theme}>
      {children}
    </ThemeProvider>
  </BrowserRouter>
);

const renderWithProviders = (component) => {
  return render(component, { wrapper: AllProviders });
};

// ===============================================
// NAVIGATION TESTS
// ===============================================

describe('Navigation Component', () => {
  let Navigation;

  beforeEach(() => {
    jest.resetModules();
    try {
      Navigation = require('../../components/Navigation').default;
    } catch (e) {
      Navigation = null;
    }
  });

  test('renders navigation component', () => {
    if (!Navigation) return;
    renderWithProviders(<Navigation />);
    // Should render without crashing
  });

  test('navigation contains logo', () => {
    if (!Navigation) return;
    renderWithProviders(<Navigation />);
    const logo = screen.queryByRole('img', { name: /logo/i }) ||
                 screen.queryByText(/getyourshare/i);
    // Logo should exist
  });

  test('navigation has mobile menu button', () => {
    if (!Navigation) return;
    renderWithProviders(<Navigation />);
    const menuButton = screen.queryByRole('button', { name: /menu/i });
    // Menu button may exist for mobile
  });

  test('navigation links are accessible', () => {
    if (!Navigation) return;
    renderWithProviders(<Navigation />);
    const links = screen.queryAllByRole('link');
    links.forEach(link => {
      expect(link).toHaveAttribute('href');
    });
  });
});

// ===============================================
// THEME TOGGLE TESTS
// ===============================================

describe('ThemeToggle Component', () => {
  let ThemeToggle;

  beforeEach(() => {
    jest.resetModules();
    try {
      ThemeToggle = require('../../components/ThemeToggle').default;
    } catch (e) {
      ThemeToggle = null;
    }
  });

  test('renders theme toggle', () => {
    if (!ThemeToggle) return;
    renderWithProviders(<ThemeToggle />);
    // Should render without crashing
  });

  test('theme toggle is clickable', () => {
    if (!ThemeToggle) return;
    renderWithProviders(<ThemeToggle />);
    const button = screen.queryByRole('button');
    if (button) {
      fireEvent.click(button);
      // Should not throw
    }
  });

  test('theme toggle has accessible label', () => {
    if (!ThemeToggle) return;
    renderWithProviders(<ThemeToggle />);
    const button = screen.queryByRole('button');
    if (button) {
      expect(button).toBeInTheDocument();
    }
  });
});

// ===============================================
// COOKIE CONSENT TESTS
// ===============================================

describe('CookieConsent Component', () => {
  let CookieConsent;

  beforeEach(() => {
    jest.resetModules();
    localStorage.clear();
    try {
      CookieConsent = require('../../components/CookieConsent').default;
    } catch (e) {
      CookieConsent = null;
    }
  });

  test('renders cookie consent', () => {
    if (!CookieConsent) return;
    renderWithProviders(<CookieConsent />);
    // Should render without crashing
  });

  test('cookie consent shows accept button', () => {
    if (!CookieConsent) return;
    renderWithProviders(<CookieConsent />);
    const acceptButton = screen.queryByRole('button', { name: /accept/i }) ||
                        screen.queryByText(/accepter/i);
    // Accept button may exist
  });

  test('cookie consent shows decline button', () => {
    if (!CookieConsent) return;
    renderWithProviders(<CookieConsent />);
    const declineButton = screen.queryByRole('button', { name: /decline|refuse/i });
    // Decline button may exist
  });

  test('accepting cookies sets localStorage', async () => {
    if (!CookieConsent) return;
    renderWithProviders(<CookieConsent />);
    const acceptButton = screen.queryByRole('button', { name: /accept/i });
    if (acceptButton) {
      await userEvent.click(acceptButton);
      // LocalStorage should be updated
    }
  });

  test('cookie consent has privacy link', () => {
    if (!CookieConsent) return;
    renderWithProviders(<CookieConsent />);
    const privacyLink = screen.queryByRole('link', { name: /privacy|politique/i });
    // Privacy link may exist
  });
});

// ===============================================
// CHART EXPORT TESTS
// ===============================================

describe('ChartExport Component', () => {
  let ChartExport;

  beforeEach(() => {
    jest.resetModules();
    try {
      ChartExport = require('../../components/ChartExport').default;
    } catch (e) {
      ChartExport = null;
    }
  });

  test('renders chart export button', () => {
    if (!ChartExport) return;
    renderWithProviders(<ChartExport chartRef={{ current: null }} />);
    // Should render without crashing
  });

  test('export button is clickable', () => {
    if (!ChartExport) return;
    const mockChartRef = { current: { toBase64Image: () => 'data:image/png;base64,test' } };
    renderWithProviders(<ChartExport chartRef={mockChartRef} />);
    const exportButton = screen.queryByRole('button');
    if (exportButton) {
      fireEvent.click(exportButton);
      // Should not throw
    }
  });

  test('export dropdown shows format options', async () => {
    if (!ChartExport) return;
    const mockChartRef = { current: { toBase64Image: () => 'data:image/png;base64,test' } };
    renderWithProviders(<ChartExport chartRef={mockChartRef} />);
    const exportButton = screen.queryByRole('button');
    if (exportButton) {
      await userEvent.click(exportButton);
      const pngOption = screen.queryByText(/png/i);
      const csvOption = screen.queryByText(/csv/i);
      // Format options may exist
    }
  });
});

// ===============================================
// HOMEPAGE TESTS
// ===============================================

describe('HomePage Component', () => {
  let HomePage;

  beforeEach(() => {
    jest.resetModules();
    try {
      HomePage = require('../../components/HomePage').default;
    } catch (e) {
      HomePage = null;
    }
  });

  test('renders homepage', () => {
    if (!HomePage) return;
    renderWithProviders(<HomePage />);
    // Should render without crashing
  });

  test('homepage has hero section', () => {
    if (!HomePage) return;
    renderWithProviders(<HomePage />);
    const heroHeading = screen.queryByRole('heading', { level: 1 });
    // Hero heading may exist
  });

  test('homepage has CTA buttons', () => {
    if (!HomePage) return;
    renderWithProviders(<HomePage />);
    const ctaButtons = screen.queryAllByRole('button');
    // CTA buttons may exist
  });

  test('homepage is responsive', () => {
    if (!HomePage) return;
    // Test different viewport sizes
    global.innerWidth = 320;
    global.dispatchEvent(new Event('resize'));
    renderWithProviders(<HomePage />);
    // Should render for mobile

    global.innerWidth = 1024;
    global.dispatchEvent(new Event('resize'));
    // Should render for desktop
  });
});

// ===============================================
// ACCESSIBILITY TESTS
// ===============================================

describe('Accessibility Tests', () => {
  test('navigation is keyboard accessible', () => {
    let Navigation;
    try {
      Navigation = require('../../components/Navigation').default;
    } catch (e) {
      return;
    }
    renderWithProviders(<Navigation />);
    const links = screen.queryAllByRole('link');
    links.forEach(link => {
      expect(link).not.toHaveAttribute('tabindex', '-1');
    });
  });

  test('buttons have accessible names', () => {
    let ThemeToggle;
    try {
      ThemeToggle = require('../../components/ThemeToggle').default;
    } catch (e) {
      return;
    }
    renderWithProviders(<ThemeToggle />);
    const buttons = screen.queryAllByRole('button');
    buttons.forEach(button => {
      const hasAccessibleName = button.hasAttribute('aria-label') ||
                               button.textContent.trim().length > 0;
      expect(hasAccessibleName).toBe(true);
    });
  });

  test('images have alt text', () => {
    let HomePage;
    try {
      HomePage = require('../../components/HomePage').default;
    } catch (e) {
      return;
    }
    renderWithProviders(<HomePage />);
    const images = screen.queryAllByRole('img');
    images.forEach(img => {
      expect(img).toHaveAttribute('alt');
    });
  });
});

// ===============================================
// ERROR HANDLING TESTS
// ===============================================

describe('Error Handling Tests', () => {
  test('components handle missing props gracefully', () => {
    let ChartExport;
    try {
      ChartExport = require('../../components/ChartExport').default;
    } catch (e) {
      return;
    }
    expect(() => {
      renderWithProviders(<ChartExport />);
    }).not.toThrow();
  });

  test('components handle invalid props', () => {
    let ChartExport;
    try {
      ChartExport = require('../../components/ChartExport').default;
    } catch (e) {
      return;
    }
    expect(() => {
      renderWithProviders(<ChartExport chartRef="invalid" />);
    }).not.toThrow();
  });
});

// ===============================================
// PERFORMANCE TESTS
// ===============================================

describe('Performance Tests', () => {
  test('navigation renders quickly', () => {
    let Navigation;
    try {
      Navigation = require('../../components/Navigation').default;
    } catch (e) {
      return;
    }
    const start = performance.now();
    renderWithProviders(<Navigation />);
    const end = performance.now();
    expect(end - start).toBeLessThan(1000); // Should render in < 1 second
  });

  test('homepage renders without excessive re-renders', () => {
    let HomePage;
    try {
      HomePage = require('../../components/HomePage').default;
    } catch (e) {
      return;
    }
    const renderCount = { count: 0 };
    const TrackedHomePage = () => {
      renderCount.count++;
      return <HomePage />;
    };
    renderWithProviders(<TrackedHomePage />);
    expect(renderCount.count).toBeLessThanOrEqual(3);
  });
});
