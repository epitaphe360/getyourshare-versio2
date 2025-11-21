import React, { useEffect, useState, useRef } from 'react';
import PropTypes from 'prop-types';
import api from '../../utils/api';
import Card from '../common/Card';
import Button from '../common/Button';
import { X, Search, Plus, Check, MessageSquare } from 'lucide-react';

const InvitationModal = ({ onClose, onSent }) => {
  const [users, setUsers] = useState([]);
  const [products, setProducts] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [selectedProducts, setSelectedProducts] = useState(new Set());
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [search, setSearch] = useState('');
  const modalRef = useRef(null);
  const previousActiveElement = useRef(null);

  useEffect(() => {
    fetchData();
  }, []);

  // Focus trap and keyboard handling
  useEffect(() => {
    previousActiveElement.current = document.activeElement;

    const handleKeyDown = (e) => {
      // Escape key
      if (e.key === 'Escape') {
        onClose();
        return;
      }

      // Tab trap - keep focus within modal
      if (e.key === 'Tab' && modalRef.current) {
        const focusableElements = modalRef.current.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        if (focusableElements.length === 0) return;

        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        if (e.shiftKey) {
          if (document.activeElement === firstElement) {
            e.preventDefault();
            lastElement.focus();
          }
        } else {
          if (document.activeElement === lastElement) {
            e.preventDefault();
            firstElement.focus();
          }
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);

    // Focus first focusable element
    if (modalRef.current) {
      const focusableElements = modalRef.current.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      if (focusableElements.length > 0) {
        focusableElements[0].focus();
      }
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      if (previousActiveElement.current) {
        previousActiveElement.current.focus();
      }
    };
  }, [onClose]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [usersRes, productsRes] = await Promise.allSettled([
        api.get('/api/influencers?limit=50'),
        api.get('/api/marketplace/products')
      ]);

      if (usersRes.status === 'fulfilled') {
        // adapt to possible response shapes
        setUsers(usersRes.value.data.influencers || usersRes.value.data || []);
      } else {
        setUsers([]);
      }

      if (productsRes.status === 'fulfilled') {
        setProducts(productsRes.value.data.products || productsRes.value.data || []);
      } else {
        setProducts([]);
      }
    } catch (err) {
      console.error('Error loading invite modal data', err);
    } finally {
      setLoading(false);
    }
  };

  const toggleProduct = (productId) => {
    const next = new Set(selectedProducts);
    if (next.has(productId)) next.delete(productId);
    else next.add(productId);
    setSelectedProducts(next);
  };

  const sendInvitation = async () => {
    if (!selectedUser) return alert('Sélectionnez un affilié');
    if (selectedProducts.size === 0) return alert('Sélectionnez au moins un produit');
    try {
      setSending(true);
      const payload = {
        invitee_id: selectedUser.id || selectedUser.user_id || selectedUser._id,
        product_ids: Array.from(selectedProducts),
        message
      };

      const res = await api.post('/api/invitations/send', payload);
      if (res.data && res.data.success) {
        if (onSent) onSent(res.data.invitation);
      } else {
        alert(res.data?.message || 'Erreur lors de l\'envoi');
      }
    } catch (err) {
      console.error('Send invitation error', err);
      alert('Erreur lors de l\'envoi de l\'invitation');
    } finally {
      setSending(false);
    }
  };

  const filteredUsers = users.filter(u => {
    const s = search.toLowerCase();
    if (!s) return true;
    return (u.first_name?.toLowerCase().includes(s) || u.last_name?.toLowerCase().includes(s) || u.username?.toLowerCase().includes(s) || u.email?.toLowerCase().includes(s));
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40" role="presentation" aria-hidden="true">
      <div className="w-full max-w-4xl mx-4">
        <Card className="relative">
          <div
            ref={modalRef}
            role="dialog"
            aria-modal="true"
            aria-labelledby="invitation-modal-title"
            aria-describedby="invitation-modal-description"
            className="relative"
          >
            <button
              onClick={onClose}
              className="absolute right-4 top-4 p-2 rounded-md hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              aria-label="Close invitation modal"
              type="button"
            >
              <X aria-hidden="true" />
            </button>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="md:col-span-1">
              <h3 id="invitation-modal-title" className="text-lg font-semibold">Sélectionnez un affilié</h3>
              <div className="mt-3">
                <div className="relative mb-3">
                  <Search className="absolute left-3 top-3 text-gray-400" size={18} aria-hidden="true" />
                  <input
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                    placeholder="Rechercher..."
                    className="w-full pl-10 pr-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    aria-label="Search affiliates"
                  />
                </div>

                <div
                  className="h-64 overflow-auto border rounded-lg p-2 space-y-2"
                  role="listbox"
                  aria-label="Available affiliates"
                >
                  {loading ? (
                    <div>Chargement...</div>
                  ) : filteredUsers.length === 0 ? (
                    <div className="text-sm text-gray-500">Aucun affilié trouvé</div>
                  ) : (
                    filteredUsers.map(user => {
                      const userId = user.id || user.user_id || user._id;
                      const isSelected = selectedUser && (selectedUser.id || selectedUser.user_id || selectedUser._id) === userId;
                      return (
                        <button
                          key={userId}
                          type="button"
                          role="option"
                          aria-selected={isSelected}
                          className={`w-full text-left p-2 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 ${isSelected ? 'bg-indigo-50 border border-indigo-200' : ''}`}
                          onClick={() => setSelectedUser(user)}
                        >
                          <div className="font-medium">{user.first_name} {user.last_name} {user.username ? `(${user.username})` : ''}</div>
                          <div className="text-xs text-gray-500">{user.email}</div>
                        </button>
                      );
                    })
                  )}
                </div>
              </div>
            </div>

            <div className="md:col-span-2">
              <h3 className="text-lg font-semibold">Sélectionnez les produits</h3>
              <fieldset>
                <legend className="sr-only">Products selection</legend>
                <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3 max-h-60 overflow-auto">
                  {products.length === 0 ? (
                    <div className="text-sm text-gray-500">Aucun produit</div>
                  ) : products.map(prod => {
                    const prodId = prod.id || prod._id;
                    const isChecked = selectedProducts.has(prodId);
                    return (
                      <label
                        key={prodId}
                        className="flex items-center gap-3 p-3 border rounded-lg hover:bg-gray-50 cursor-pointer focus-within:ring-2 focus-within:ring-indigo-500"
                      >
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={() => toggleProduct(prodId)}
                          className="w-4 h-4 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                          aria-label={`Select ${prod.name || prod.title}`}
                        />
                        <div className="flex-1">
                          <div className="font-medium">{prod.name || prod.title}</div>
                          <div className="text-sm text-gray-500">{prod.price ? `${prod.price}€` : ''}</div>
                        </div>
                      </label>
                    );
                  })}
                </div>
              </fieldset>

              <div className="mt-4">
                <label htmlFor="invitation-message" className="font-medium">Message</label>
                <textarea
                  id="invitation-message"
                  value={message}
                  onChange={e => setMessage(e.target.value)}
                  placeholder="Message optionnel à l'affilié"
                  className="w-full mt-2 p-3 border rounded-lg h-28 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  aria-label="Optional message for affiliate"
                ></textarea>
              </div>

              <div className="mt-4 flex items-center gap-3 justify-end">
                <Button onClick={onClose} className="bg-gray-100 text-gray-800">Annuler</Button>
                <Button onClick={sendInvitation} disabled={sending} className="bg-indigo-600 text-white">
                  {sending ? 'Envoi...' : (<><MessageSquare size={16} className="inline mr-2"/> Envoyer l'invitation</>)}
                </Button>
              </div>
            </div>
            </div>

            <div id="invitation-modal-description" className="sr-only">
              Send invitations to affiliates for selected products with an optional message
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

InvitationModal.propTypes = {
  onClose: PropTypes.func.isRequired,
  onSent: PropTypes.func,
};

export default InvitationModal;
