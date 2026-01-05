/**
 * Service API pour système fiscal
 * Connexion frontend → backend fiscal endpoints
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8003/api';

class FiscalService {
  constructor() {
    this.baseURL = `${API_BASE_URL}/fiscal`;
  }

  /**
   * Récupérer le token JWT depuis localStorage
   */
  getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    };
  }

  /**
   * Gestion erreurs HTTP
   */
  async handleResponse(response) {
    if (!response.ok) {
      const error = await response.json().catch(() => ({ 
        detail: `HTTP ${response.status}: ${response.statusText}` 
      }));
      throw new Error(error.detail || error.message || 'Erreur API');
    }
    return response.json();
  }

  // ═══════════════════════════════════════════════════════════
  // INVOICES (Factures)
  // ═══════════════════════════════════════════════════════════

  /**
   * Créer nouvelle facture
   * POST /api/fiscal/invoices
   */
  async createInvoice(invoiceData) {
    try {
      const response = await fetch(`${this.baseURL}/invoices`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(invoiceData)
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error('Error creating invoice:', error);
      throw error;
    }
  }

  /**
   * Récupérer toutes les factures
   * GET /api/fiscal/invoices
   */
  async getInvoices(filters = {}) {
    try {
      const params = new URLSearchParams();
      if (filters.status) params.append('status', filters.status);
      if (filters.country) params.append('country', filters.country);
      if (filters.start_date) params.append('start_date', filters.start_date);
      if (filters.end_date) params.append('end_date', filters.end_date);
      
      const url = `${this.baseURL}/invoices${params.toString() ? '?' + params.toString() : ''}`;
      const response = await fetch(url, {
        headers: this.getAuthHeaders()
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error('Error fetching invoices:', error);
      throw error;
    }
  }

  /**
   * Récupérer une facture par ID
   * GET /api/fiscal/invoices/{id}
   */
  async getInvoiceById(invoiceId) {
    try {
      const response = await fetch(`${this.baseURL}/invoices/${invoiceId}`, {
        headers: this.getAuthHeaders()
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error('Error fetching invoice:', error);
      throw error;
    }
  }

  /**
   * Mettre à jour une facture
   * PUT /api/fiscal/invoices/{id}
   */
  async updateInvoice(invoiceId, updateData) {
    try {
      const response = await fetch(`${this.baseURL}/invoices/${invoiceId}`, {
        method: 'PUT',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(updateData)
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error('Error updating invoice:', error);
      throw error;
    }
  }

  /**
   * Supprimer une facture
   * DELETE /api/fiscal/invoices/{id}
   */
  async deleteInvoice(invoiceId) {
    try {
      const response = await fetch(`${this.baseURL}/invoices/${invoiceId}`, {
        method: 'DELETE',
        headers: this.getAuthHeaders()
      });
      if (response.status === 204) return { success: true };
      return await this.handleResponse(response);
    } catch (error) {
      console.error('Error deleting invoice:', error);
      throw error;
    }
  }

  /**
   * Générer PDF de facture
   * POST /api/fiscal/invoices/{id}/generate-pdf
   */
  async generateInvoicePDF(invoiceId) {
    try {
      const response = await fetch(`${this.baseURL}/invoices/${invoiceId}/generate-pdf`, {
        method: 'POST',
        headers: this.getAuthHeaders()
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error('Error generating PDF:', error);
      throw error;
    }
  }

  /**
   * Télécharger PDF de facture
   */
  async downloadInvoicePDF(invoiceId) {
    try {
      const result = await this.generateInvoicePDF(invoiceId);
      if (result.pdf_url) {
        // Ouvrir dans nouvel onglet
        window.open(result.pdf_url, '_blank');
        return result;
      }
      throw new Error('PDF URL non disponible');
    } catch (error) {
      console.error('Error downloading PDF:', error);
      throw error;
    }
  }

  /**
   * Envoyer facture par email
   * POST /api/fiscal/invoices/{id}/send-email
   */
  async sendInvoiceEmail(invoiceId, emailOptions = {}) {
    try {
      const response = await fetch(`${this.baseURL}/invoices/${invoiceId}/send-email`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(emailOptions)
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error('Error sending invoice email:', error);
      throw error;
    }
  }

  // ═══════════════════════════════════════════════════════════
  // VAT CALCULATIONS (Calculs TVA)
  // ═══════════════════════════════════════════════════════════

  /**
   * Calculer TVA Maroc
   * POST /api/fiscal/morocco/vat
   */
  async calculateMoroccoVAT(revenue, expenses = 0) {
    try {
      const response = await fetch(`${this.baseURL}/morocco/vat`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({ revenue, expenses })
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error('Error calculating Morocco VAT:', error);
      throw error;
    }
  }

  /**
   * Calculer IR progressif Maroc
   * POST /api/fiscal/morocco/ir-progressive
   */
  async calculateMoroccoIR(annual_income, dependents = 0, deductions = 0) {
    try {
      const response = await fetch(`${this.baseURL}/morocco/ir-progressive`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({ annual_income, dependents, deductions })
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error('Error calculating Morocco IR:', error);
      throw error;
    }
  }

  /**
   * Calculer TVA France
   * POST /api/fiscal/france/vat
   */
  async calculateFranceVAT(revenue, vat_regime = 'normal') {
    try {
      const response = await fetch(`${this.baseURL}/france/vat`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({ revenue, vat_regime })
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error('Error calculating France VAT:', error);
      throw error;
    }
  }

  /**
   * Calculer URSSAF détaillé France
   * POST /api/fiscal/france/urssaf-detailed
   */
  async calculateFranceURSSAF(revenue, status = 'auto_entrepreneur_bnc') {
    try {
      const response = await fetch(`${this.baseURL}/france/urssaf-detailed`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({ revenue, status })
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error('Error calculating France URSSAF:', error);
      throw error;
    }
  }

  /**
   * Calculer Sales Tax USA
   * POST /api/fiscal/usa/state-tax/{state}
   */
  async calculateUSASalesTax(state, gross_sales, taxable_sales) {
    try {
      const response = await fetch(`${this.baseURL}/usa/state-tax/${state}`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({ gross_sales, taxable_sales })
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error('Error calculating USA sales tax:', error);
      throw error;
    }
  }

  /**
   * Calculer Federal Tax USA
   * POST /api/fiscal/usa/federal-tax
   */
  async calculateUSAFederalTax(taxable_income, filing_status = 'single') {
    try {
      const response = await fetch(`${this.baseURL}/usa/federal-tax`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({ taxable_income, filing_status })
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error('Error calculating USA federal tax:', error);
      throw error;
    }
  }

  /**
   * Calculer Self-Employment Tax USA
   * POST /api/fiscal/usa/self-employment-tax
   */
  async calculateUSASelfEmploymentTax(net_earnings) {
    try {
      const response = await fetch(`${this.baseURL}/usa/self-employment-tax`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({ net_earnings })
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error('Error calculating USA SE tax:', error);
      throw error;
    }
  }

  // ═══════════════════════════════════════════════════════════
  // VAT DECLARATIONS (Déclarations TVA)
  // ═══════════════════════════════════════════════════════════

  /**
   * Créer déclaration TVA
   * POST /api/fiscal/vat-declarations
   */
  async createVATDeclaration(declarationData) {
    try {
      const response = await fetch(`${this.baseURL}/vat-declarations`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(declarationData)
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error('Error creating VAT declaration:', error);
      throw error;
    }
  }

  /**
   * Récupérer déclarations TVA
   * GET /api/fiscal/vat-declarations
   */
  async getVATDeclarations(filters = {}) {
    try {
      const params = new URLSearchParams();
      if (filters.year) params.append('year', filters.year);
      if (filters.quarter) params.append('quarter', filters.quarter);
      
      const url = `${this.baseURL}/vat-declarations${params.toString() ? '?' + params.toString() : ''}`;
      const response = await fetch(url, {
        headers: this.getAuthHeaders()
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error('Error fetching VAT declarations:', error);
      throw error;
    }
  }

  // ═══════════════════════════════════════════════════════════
  // ACCOUNTING EXPORTS (Exports comptables)
  // ═══════════════════════════════════════════════════════════

  /**
   * Exporter FEC (Fichier Échanges Comptables) France
   * POST /api/fiscal/france/export-fec
   */
  async exportFranceFEC(start_date, end_date) {
    try {
      const response = await fetch(`${this.baseURL}/france/export-fec`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({ start_date, end_date })
      });
      const result = await this.handleResponse(response);
      
      // Télécharger le fichier
      if (result.file_url) {
        window.open(result.file_url, '_blank');
      }
      return result;
    } catch (error) {
      console.error('Error exporting FEC:', error);
      throw error;
    }
  }

  /**
   * Exporter CSV général
   * POST /api/fiscal/export-csv
   */
  async exportCSV(start_date, end_date, export_type = 'invoices') {
    try {
      const response = await fetch(`${this.baseURL}/export-csv`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({ start_date, end_date, export_type })
      });
      const result = await this.handleResponse(response);
      
      if (result.file_url) {
        window.open(result.file_url, '_blank');
      }
      return result;
    } catch (error) {
      console.error('Error exporting CSV:', error);
      throw error;
    }
  }

  // ═══════════════════════════════════════════════════════════
  // SETTINGS (Paramètres fiscaux)
  // ═══════════════════════════════════════════════════════════

  /**
   * Récupérer paramètres fiscaux utilisateur
   * GET /api/fiscal/settings
   */
  async getFiscalSettings() {
    try {
      const response = await fetch(`${this.baseURL}/settings`, {
        headers: this.getAuthHeaders()
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error('Error fetching fiscal settings:', error);
      throw error;
    }
  }

  /**
   * Mettre à jour paramètres fiscaux
   * PUT /api/fiscal/settings
   */
  async updateFiscalSettings(settings) {
    try {
      const response = await fetch(`${this.baseURL}/settings`, {
        method: 'PUT',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(settings)
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error('Error updating fiscal settings:', error);
      throw error;
    }
  }

  // ═══════════════════════════════════════════════════════════
  // WEBHOOKS (Paiements)
  // ═══════════════════════════════════════════════════════════

  /**
   * Générer lien paiement Stripe/PayPal
   * POST /api/payment-links/generate
   */
  async generatePaymentLink(invoice_id, payment_provider = 'stripe') {
    try {
      const response = await fetch(`${API_BASE_URL}/payment-links/generate`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({ invoice_id, payment_provider })
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error('Error generating payment link:', error);
      throw error;
    }
  }

  // ═══════════════════════════════════════════════════════════
  // STATISTICS (Statistiques)
  // ═══════════════════════════════════════════════════════════

  /**
   * Récupérer statistiques dashboard fiscal
   */
  async getFiscalStats(period = 'month') {
    try {
      const response = await fetch(`${this.baseURL}/stats?period=${period}`, {
        headers: this.getAuthHeaders()
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error('Error fetching fiscal stats:', error);
      // Retourner données mockées en cas d'erreur
      return {
        total_revenue: 0,
        total_invoices: 0,
        paid_invoices: 0,
        pending_invoices: 0,
        overdue_invoices: 0,
        total_tax: 0
      };
    }
  }
}

// Export singleton
const fiscalService = new FiscalService();
export default fiscalService;
