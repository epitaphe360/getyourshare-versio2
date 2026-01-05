import React, { useState } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  IconButton,
  Box,
  Typography,
  CircularProgress,
  Toolbar,
  Tooltip
} from '@mui/material';
import {
  Close as CloseIcon,
  ZoomIn,
  ZoomOut,
  Download,
  ChevronLeft,
  ChevronRight
} from '@mui/icons-material';

// Configuration PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

/**
 * PDFViewer - Composant pour afficher des PDF inline avec contrôles
 * 
 * @param {Object} props
 * @param {boolean} props.open - Dialog ouvert/fermé
 * @param {function} props.onClose - Callback fermeture
 * @param {string} props.pdfUrl - URL du PDF à afficher (blob ou http)
 * @param {string} props.fileName - Nom du fichier pour téléchargement
 * @param {string} props.title - Titre du dialog
 */
const PDFViewer = ({ open, onClose, pdfUrl, fileName = 'document.pdf', title = 'Aperçu PDF' }) => {
  const [numPages, setNumPages] = useState(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [scale, setScale] = useState(1.0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Callback - Document chargé avec succès
  const onDocumentLoadSuccess = ({ numPages }) => {
    setNumPages(numPages);
    setLoading(false);
    setError(null);
  };

  // Callback - Erreur de chargement
  const onDocumentLoadError = (error) => {
    console.error('Erreur chargement PDF:', error);
    setError('Impossible de charger le PDF');
    setLoading(false);
  };

  // Navigation entre pages
  const goToPreviousPage = () => {
    setPageNumber((prev) => Math.max(prev - 1, 1));
  };

  const goToNextPage = () => {
    setPageNumber((prev) => Math.min(prev + 1, numPages || 1));
  };

  // Zoom
  const zoomIn = () => {
    setScale((prev) => Math.min(prev + 0.2, 3.0));
  };

  const zoomOut = () => {
    setScale((prev) => Math.max(prev - 0.2, 0.5));
  };

  // Téléchargement
  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = pdfUrl;
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Reset state quand dialog se ferme
  const handleClose = () => {
    setPageNumber(1);
    setScale(1.0);
    setLoading(true);
    setError(null);
    onClose();
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="lg"
      fullWidth
      PaperProps={{
        sx: {
          height: '90vh',
          display: 'flex',
          flexDirection: 'column'
        }
      }}
    >
      {/* Header */}
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Typography variant="h6">{title}</Typography>
        <IconButton onClick={handleClose} size="small">
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      {/* Toolbar de contrôle */}
      <Toolbar
        sx={{
          borderTop: 1,
          borderBottom: 1,
          borderColor: 'divider',
          display: 'flex',
          justifyContent: 'space-between',
          gap: 2,
          px: 2
        }}
      >
        {/* Navigation pages */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Tooltip title="Page précédente">
            <span>
              <IconButton
                onClick={goToPreviousPage}
                disabled={pageNumber <= 1 || loading}
                size="small"
              >
                <ChevronLeft />
              </IconButton>
            </span>
          </Tooltip>
          
          <Typography variant="body2" sx={{ minWidth: 100, textAlign: 'center' }}>
            {loading ? '...' : `Page ${pageNumber} / ${numPages}`}
          </Typography>
          
          <Tooltip title="Page suivante">
            <span>
              <IconButton
                onClick={goToNextPage}
                disabled={pageNumber >= (numPages || 1) || loading}
                size="small"
              >
                <ChevronRight />
              </IconButton>
            </span>
          </Tooltip>
        </Box>

        {/* Contrôles zoom */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Tooltip title="Zoom arrière">
            <span>
              <IconButton onClick={zoomOut} disabled={scale <= 0.5 || loading} size="small">
                <ZoomOut />
              </IconButton>
            </span>
          </Tooltip>
          
          <Typography variant="body2" sx={{ minWidth: 60, textAlign: 'center' }}>
            {Math.round(scale * 100)}%
          </Typography>
          
          <Tooltip title="Zoom avant">
            <span>
              <IconButton onClick={zoomIn} disabled={scale >= 3.0 || loading} size="small">
                <ZoomIn />
              </IconButton>
            </span>
          </Tooltip>
        </Box>

        {/* Téléchargement */}
        <Tooltip title="Télécharger le PDF">
          <span>
            <IconButton onClick={handleDownload} disabled={loading} color="primary">
              <Download />
            </IconButton>
          </span>
        </Tooltip>
      </Toolbar>

      {/* Contenu PDF */}
      <DialogContent
        sx={{
          flex: 1,
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          overflow: 'auto',
          bgcolor: 'grey.100',
          p: 2
        }}
      >
        {loading && !error && (
          <Box sx={{ textAlign: 'center' }}>
            <CircularProgress />
            <Typography variant="body2" sx={{ mt: 2 }}>
              Chargement du PDF...
            </Typography>
          </Box>
        )}

        {error && (
          <Box sx={{ textAlign: 'center', color: 'error.main' }}>
            <Typography variant="h6">{error}</Typography>
            <Typography variant="body2" sx={{ mt: 1 }}>
              Veuillez réessayer ou télécharger le fichier.
            </Typography>
          </Box>
        )}

        {pdfUrl && (
          <Document
            file={pdfUrl}
            onLoadSuccess={onDocumentLoadSuccess}
            onLoadError={onDocumentLoadError}
            loading={null} // On gère le loading nous-mêmes
          >
            <Page
              pageNumber={pageNumber}
              scale={scale}
              renderTextLayer={false}
              renderAnnotationLayer={false}
            />
          </Document>
        )}
      </DialogContent>

      {/* Footer actions */}
      <DialogActions sx={{ borderTop: 1, borderColor: 'divider', px: 3, py: 2 }}>
        <Button onClick={handleDownload} disabled={loading} variant="contained">
          Télécharger
        </Button>
        <Button onClick={handleClose}>Fermer</Button>
      </DialogActions>
    </Dialog>
  );
};

export default PDFViewer;
