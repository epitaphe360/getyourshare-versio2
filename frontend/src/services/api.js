/**
 * Réexport du service API centralisé
 * Ce fichier existe pour la compatibilité avec les imports existants
 * Utilisez plutôt: import api from '../utils/api';
 */
import api, { checkAPIHealth, API_URL } from '../utils/api';

export { checkAPIHealth, API_URL };
export default api;
