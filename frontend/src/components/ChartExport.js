import React, { useRef } from 'react';
import { Download, FileDown, FileSpreadsheet } from 'lucide-react';
import html2canvas from 'html2canvas';
import './ChartExport.css';

/**
 * Component pour exporter des graphiques en PNG ou CSV
 * 
 * Usage:
 * <ChartExport 
 *   chartRef={chartContainerRef}
 *   data={chartData}
 *   filename="revenue-chart"
 *   showPNG={true}
 *   showCSV={true}
 * />
 */
const ChartExport = ({ 
  chartRef, 
  data = [], 
  filename = 'chart',
  showPNG = true,
  showCSV = true,
  className = ''
}) => {
  
  const exportToPNG = async () => {
    if (!chartRef || !chartRef.current) {
      console.error('Chart ref not available');
      return;
    }

    try {
      // Capturer le graphique en canvas
      const canvas = await html2canvas(chartRef.current, {
        backgroundColor: '#ffffff',
        scale: 2, // Higher resolution
        logging: false,
        useCORS: true
      });

      // Créer le téléchargement
      const link = document.createElement('a');
      link.download = `${filename}-${new Date().toISOString().split('T')[0]}.png`;
      link.href = canvas.toDataURL('image/png');
      link.click();
      
      console.log(`✅ Exported chart as PNG: ${link.download}`);
    } catch (error) {
      console.error('Error exporting PNG:', error);
      alert('Erreur lors de l\'export PNG');
    }
  };

  const exportToCSV = () => {
    if (!data || data.length === 0) {
      alert('Aucune donnée à exporter');
      return;
    }

    try {
      // Récupérer les colonnes du premier élément
      const headers = Object.keys(data[0]);
      
      // Créer le CSV
      const csvContent = [
        headers.join(','), // Headers
        ...data.map(row => 
          headers.map(header => {
            const value = row[header];
            // Échapper les virgules et guillemets
            if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
              return `"${value.replace(/"/g, '""')}"`;
            }
            return value;
          }).join(',')
        )
      ].join('\n');

      // Créer le blob et télécharger
      const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      link.download = `${filename}-${new Date().toISOString().split('T')[0]}.csv`;
      link.href = URL.createObjectURL(blob);
      link.click();
      URL.revokeObjectURL(link.href);
      
      console.log(`✅ Exported data as CSV: ${link.download}`);
    } catch (error) {
      console.error('Error exporting CSV:', error);
      alert('Erreur lors de l\'export CSV');
    }
  };

  const exportToJSON = () => {
    if (!data || data.length === 0) {
      alert('Aucune donnée à exporter');
      return;
    }

    try {
      const jsonContent = JSON.stringify(data, null, 2);
      const blob = new Blob([jsonContent], { type: 'application/json' });
      const link = document.createElement('a');
      link.download = `${filename}-${new Date().toISOString().split('T')[0]}.json`;
      link.href = URL.createObjectURL(blob);
      link.click();
      URL.revokeObjectURL(link.href);
      
      console.log(`✅ Exported data as JSON: ${link.download}`);
    } catch (error) {
      console.error('Error exporting JSON:', error);
      alert('Erreur lors de l\'export JSON');
    }
  };

  return (
    <div className={`chart-export ${className}`}>
      {showPNG && (
        <button
          onClick={exportToPNG}
          className="export-btn export-png"
          title="Exporter en PNG"
        >
          <FileDown size={16} />
          <span>PNG</span>
        </button>
      )}
      
      {showCSV && (
        <button
          onClick={exportToCSV}
          className="export-btn export-csv"
          title="Exporter en CSV"
        >
          <FileSpreadsheet size={16} />
          <span>CSV</span>
        </button>
      )}
      
      <button
        onClick={exportToJSON}
        className="export-btn export-json"
        title="Exporter en JSON"
      >
        <Download size={16} />
        <span>JSON</span>
      </button>
    </div>
  );
};

export default ChartExport;
