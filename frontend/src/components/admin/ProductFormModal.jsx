import React, { useState, useEffect } from 'react';
import { X, Upload, Image as ImageIcon, Save, AlertCircle } from 'lucide-react';
import api from '../../utils/api';

const ProductFormModal = ({ mode, product, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    price: '',
    category: 'electronics',
    stock: '',
    sku: '',
    status: 'active',
    image: '',
    images: []
  });

  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [uploadingImage, setUploadingImage] = useState(false);

  // Charger les données du produit si on est en mode édition
  useEffect(() => {
    if (mode === 'edit' && product) {
      setFormData({
        name: product.name || '',
        description: product.description || '',
        price: product.price || '',
        category: product.category || 'electronics',
        stock: product.stock || '',
        sku: product.sku || '',
        status: product.status || 'active',
        image: product.image || '',
        images: product.images || []
      });
    }
  }, [mode, product]);

  // Gérer les changements de champs
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Effacer l'erreur du champ modifié
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: null
      }));
    }
  };

  // Validation
  const validate = () => {
    const newErrors = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Le nom est requis';
    }

    if (!formData.price || formData.price <= 0) {
      newErrors.price = 'Le prix doit être supérieur à 0';
    }

    if (!formData.stock || formData.stock < 0) {
      newErrors.stock = 'Le stock ne peut pas être négatif';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Upload d'image
  const handleImageUpload = async (e, isGallery = false) => {
    const file = e.target.files[0];
    if (!file) return;

    // Vérifier le type de fichier
    if (!file.type.startsWith('image/')) {
      alert('Veuillez sélectionner une image');
      return;
    }

    // Vérifier la taille (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      alert('L\'image ne doit pas dépasser 5MB');
      return;
    }

    setUploadingImage(true);
    const formDataUpload = new FormData();
    formDataUpload.append('image', file);

    try {
      const response = await api.post('/api/products/upload-image', formDataUpload, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      const imageUrl = response.data.url;

      if (isGallery) {
        setFormData(prev => ({
          ...prev,
          images: [...prev.images, imageUrl]
        }));
      } else {
        setFormData(prev => ({
          ...prev,
          image: imageUrl
        }));
      }
    } catch (error) {
      console.error('Erreur lors de l\'upload:', error);
      alert('Erreur lors de l\'upload de l\'image');
    } finally {
      setUploadingImage(false);
    }
  };

  // Supprimer une image de la galerie
  const removeGalleryImage = (index) => {
    setFormData(prev => ({
      ...prev,
      images: prev.images.filter((_, i) => i !== index)
    }));
  };

  // Soumettre le formulaire
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    setLoading(true);

    try {
      if (mode === 'create') {
        await api.post('/api/products', formData);
      } else {
        await api.put(`/api/products/${product.id}`, formData);
      }
      onSuccess();
    } catch (error) {
      console.error('Erreur lors de la sauvegarde:', error);
      alert('Erreur lors de la sauvegarde du produit');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto">
      <div className="bg-white rounded-lg max-w-4xl w-full my-8">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900">
            {mode === 'create' ? 'Créer un produit' : 'Modifier le produit'}
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition"
          >
            <X size={24} />
          </button>
        </div>

        {/* Formulaire */}
        <form onSubmit={handleSubmit} className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Colonne gauche */}
            <div className="space-y-4">
              {/* Nom */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nom du produit *
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                    errors.name ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="Ex: iPhone 15 Pro"
                />
                {errors.name && (
                  <p className="mt-1 text-sm text-red-600 flex items-center gap-1">
                    <AlertCircle size={14} />
                    {errors.name}
                  </p>
                )}
              </div>

              {/* Description */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description
                </label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  rows={4}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Description détaillée du produit..."
                />
              </div>

              {/* Prix */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Prix (€) *
                </label>
                <input
                  type="number"
                  name="price"
                  value={formData.price}
                  onChange={handleChange}
                  step="0.01"
                  min="0"
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                    errors.price ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="99.99"
                />
                {errors.price && (
                  <p className="mt-1 text-sm text-red-600 flex items-center gap-1">
                    <AlertCircle size={14} />
                    {errors.price}
                  </p>
                )}
              </div>

              {/* Catégorie */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Catégorie
                </label>
                <select
                  name="category"
                  value={formData.category}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="electronics">Électronique</option>
                  <option value="fashion">Mode</option>
                  <option value="home">Maison</option>
                  <option value="beauty">Beauté</option>
                  <option value="sports">Sport</option>
                  <option value="books">Livres</option>
                  <option value="toys">Jouets</option>
                  <option value="food">Alimentation</option>
                  <option value="other">Autre</option>
                </select>
              </div>
            </div>

            {/* Colonne droite */}
            <div className="space-y-4">
              {/* Stock */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Quantité en stock *
                </label>
                <input
                  type="number"
                  name="stock"
                  value={formData.stock}
                  onChange={handleChange}
                  min="0"
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                    errors.stock ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="100"
                />
                {errors.stock && (
                  <p className="mt-1 text-sm text-red-600 flex items-center gap-1">
                    <AlertCircle size={14} />
                    {errors.stock}
                  </p>
                )}
              </div>

              {/* SKU */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  SKU / Référence
                </label>
                <input
                  type="text"
                  name="sku"
                  value={formData.sku}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="PROD-001"
                />
              </div>

              {/* Statut */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Statut
                </label>
                <select
                  name="status"
                  value={formData.status}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="active">Actif</option>
                  <option value="inactive">Inactif</option>
                  <option value="draft">Brouillon</option>
                </select>
              </div>

              {/* Image principale */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Image principale
                </label>
                {formData.image ? (
                  <div className="relative">
                    <img
                      src={formData.image}
                      alt="Aperçu"
                      className="w-full h-48 object-cover rounded-lg"
                    />
                    <button
                      type="button"
                      onClick={() => setFormData(prev => ({ ...prev, image: '' }))}
                      className="absolute top-2 right-2 p-1 bg-red-500 text-white rounded-full hover:bg-red-600"
                    >
                      <X size={16} />
                    </button>
                  </div>
                ) : (
                  <label className="flex flex-col items-center justify-center w-full h-48 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50 transition">
                    <div className="flex flex-col items-center justify-center pt-5 pb-6">
                      {uploadingImage ? (
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                      ) : (
                        <>
                          <Upload className="w-10 h-10 mb-3 text-gray-400" />
                          <p className="mb-2 text-sm text-gray-500">
                            <span className="font-semibold">Cliquez pour uploader</span>
                          </p>
                          <p className="text-xs text-gray-500">PNG, JPG, GIF (MAX. 5MB)</p>
                        </>
                      )}
                    </div>
                    <input
                      type="file"
                      className="hidden"
                      accept="image/*"
                      onChange={(e) => handleImageUpload(e, false)}
                      disabled={uploadingImage}
                    />
                  </label>
                )}
              </div>
            </div>
          </div>

          {/* Galerie d'images */}
          <div className="mt-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Galerie d'images (optionnel)
            </label>
            <div className="grid grid-cols-4 gap-4">
              {formData.images.map((img, index) => (
                <div key={index} className="relative">
                  <img
                    src={img}
                    alt={`Galerie ${index + 1}`}
                    className="w-full h-24 object-cover rounded-lg"
                  />
                  <button
                    type="button"
                    onClick={() => removeGalleryImage(index)}
                    className="absolute top-1 right-1 p-1 bg-red-500 text-white rounded-full hover:bg-red-600"
                  >
                    <X size={12} />
                  </button>
                </div>
              ))}
              {formData.images.length < 4 && (
                <label className="flex items-center justify-center w-full h-24 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50 transition">
                  <ImageIcon className="text-gray-400" size={24} />
                  <input
                    type="file"
                    className="hidden"
                    accept="image/*"
                    onChange={(e) => handleImageUpload(e, true)}
                    disabled={uploadingImage}
                  />
                </label>
              )}
            </div>
          </div>

          {/* Boutons d'action */}
          <div className="flex items-center justify-end gap-3 mt-8 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
              disabled={loading}
            >
              Annuler
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Enregistrement...
                </>
              ) : (
                <>
                  <Save size={18} />
                  {mode === 'create' ? 'Créer le produit' : 'Enregistrer les modifications'}
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ProductFormModal;
