import jsPDF from 'jspdf';
import 'jspdf-autotable';
import Papa from 'papaparse';
import { toast } from 'react-toastify';

/**
 * Utilitaires d'export pour les leads
 * Supporte: PDF, CSV, Excel
 */

export const exportToCSV = (data, filename = 'leads_export.csv') => {
  if (!data || data.length === 0) {
    toast.warning('Aucune donnée à exporter');
    return;
  }

  const csvData = Papa.unparse(
    data.map(lead => ({
      'Prénom': lead.first_name || '',
      'Nom': lead.last_name || '',
      'Email': lead.email || '',
      'Téléphone': lead.phone || '',
      'Entreprise': lead.company || '',
      'Statut': lead.status || '',
      'Température': lead.temperature || '',
      'Valeur estimée (€)': lead.estimated_value || 0,
      'Date création': lead.created_at ? new Date(lead.created_at).toLocaleDateString('fr-FR') : '',
      'Notes': lead.notes || ''
    }))
  );

  const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  link.style.visibility = 'hidden';
  
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  
  toast.success(`✅ Export CSV: ${data.length} leads`);
};

export const exportToPDF = (data, filename = 'leads_export.pdf') => {
  if (!data || data.length === 0) {
    toast.warning('Aucune donnée à exporter');
    return;
  }

  const pdf = new jsPDF();
  
  // En-tête
  pdf.setFontSize(16);
  pdf.text('Rapport Leads Commerciaux', 14, 15);
  
  pdf.setFontSize(10);
  pdf.setTextColor(100);
  pdf.text(`Export du ${new Date().toLocaleDateString('fr-FR')}`, 14, 22);
  pdf.text(`Total: ${data.length} leads`, 14, 28);

  // Tableau
  const tableData = data.map(lead => [
    `${lead.first_name || ''} ${lead.last_name || ''}`,
    lead.email || '',
    lead.company || '',
    lead.status || '',
    lead.temperature || '',
    lead.estimated_value ? `${lead.estimated_value}€` : '0€'
  ]);

  pdf.autoTable({
    startY: 35,
    head: [['Contact', 'Email', 'Entreprise', 'Statut', 'Température', 'Valeur']],
    body: tableData,
    theme: 'grid',
    headStyles: {
      fillColor: [139, 92, 246],
      textColor: 255,
      fontStyle: 'bold'
    },
    bodyStyles: {
      textColor: 50
    },
    alternateRowStyles: {
      fillColor: [245, 245, 245]
    },
    margin: { top: 35, left: 14, right: 14 },
    columnStyles: {
      5: { halign: 'right' }
    },
    didDrawPage: (data) => {
      // Footer
      const pageCount = pdf.internal.pages.length - 1;
      pdf.setFontSize(8);
      pdf.setTextColor(150);
      pdf.text(
        `Page ${data.pageNumber}/${pageCount}`,
        pdf.internal.pageSize.getWidth() / 2,
        pdf.internal.pageSize.getHeight() - 10,
        { align: 'center' }
      );
    }
  });

  pdf.save(filename);
  toast.success(`✅ Export PDF: ${data.length} leads`);
};

export const exportToExcel = (data, filename = 'leads_export.xlsx') => {
  // Pour Excel, on utilise une approche simple avec un tableau HTML
  // Une meilleure solution serait d'utiliser xlsx library
  
  if (!data || data.length === 0) {
    toast.warning('Aucune donnée à exporter');
    return;
  }

  const csvData = Papa.unparse(
    data.map(lead => ({
      'Prénom': lead.first_name || '',
      'Nom': lead.last_name || '',
      'Email': lead.email || '',
      'Téléphone': lead.phone || '',
      'Entreprise': lead.company || '',
      'Statut': lead.status || '',
      'Température': lead.temperature || '',
      'Valeur estimée (€)': lead.estimated_value || 0,
      'Date création': lead.created_at ? new Date(lead.created_at).toLocaleDateString('fr-FR') : '',
      'Notes': lead.notes || ''
    }))
  );

  const blob = new Blob([csvData], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  link.setAttribute('href', url);
  link.setAttribute('download', filename.replace('.xlsx', '.csv')); // Chrome convertira
  link.style.visibility = 'hidden';
  
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  
  toast.info('💡 Astuce: Ouvrez le fichier CSV dans Excel pour meilleure mise en forme');
};

export const shareExport = async (data, format = 'pdf') => {
  try {
    if (format === 'pdf') {
      exportToPDF(data, `leads_${new Date().getTime()}.pdf`);
    } else {
      exportToCSV(data, `leads_${new Date().getTime()}.csv`);
    }
    toast.success('Export prêt à être partagé');
  } catch (error) {
    console.error('Erreur export:', error);
    toast.error('Erreur lors de l\'export');
  }
};
