import React, { useState, useEffect } from 'react';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Badge from '../../components/common/Badge';
import Button from '../../components/common/Button';
import { formatDate } from '../../utils/helpers';
import { Check, X } from 'lucide-react';
import api from '../../utils/api';
import { useToast } from '../../context/ToastContext';

const AdvertiserRegistrations = () => {
  const [registrations, setRegistrations] = useState([]);
  const [loading, setLoading] = useState(true);
  const toast = useToast();

  useEffect(() => {
    fetchRegistrations();
  }, []);

  const fetchRegistrations = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/advertiser-registrations');
      console.log('Registrations reçues:', response.data);
      setRegistrations(response.data.registrations || []);
    } catch (error) {
      console.error('Error fetching registrations:', error);
      toast.error('Erreur lors du chargement des demandes');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (id) => {
    try {
      setLoading(true);
      await api.post(`/api/advertiser-registrations/${id}/approve`);
      toast.success('Demande approuvée avec succès');
      
      // Rafraîchir la liste
      fetchRegistrations();
    } catch (error) {
      console.error('Error approving registration:', error);
      toast.error('Erreur lors de l\'approbation');
    } finally {
      setLoading(false);
    }
  };

  const handleReject = async (id) => {
    if (!window.confirm('Êtes-vous sûr de vouloir rejeter cette demande ?')) {
      return;
    }
    
    try {
      setLoading(true);
      await api.post(`/api/advertiser-registrations/${id}/reject`);
      toast.success('Demande rejetée');
      
      // Rafraîchir la liste
      fetchRegistrations();
    } catch (error) {
      console.error('Error rejecting registration:', error);
      toast.error('Erreur lors du rejet');
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    {
      header: 'Entreprise',
      accessor: 'company_name',
      render: (row) => (
        <div>
          <div className="font-semibold">{row.company_name}</div>
          <div className="text-xs text-gray-500">{row.email}</div>
        </div>
      ),
    },
    {
      header: 'Pays',
      accessor: 'country',
    },
    {
      header: 'Statut',
      accessor: 'status',
      render: (row) => <Badge status={row.status}>{row.status}</Badge>,
    },
    {
      header: 'Date de demande',
      accessor: 'created_at',
      render: (row) => formatDate(row.created_at),
    },
    {
      header: 'Actions',
      accessor: 'actions',
      render: (row) => (
        <div className="flex space-x-2">
          <Button size="sm" variant="success" disabled={loading} onClick={() => handleApprove(row.id)}>
            <Check size={16} />
          </Button>
          <Button size="sm" variant="danger" disabled={loading} onClick={() => handleReject(row.id)}>
            <X size={16} />
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-6" data-testid="advertiser-registrations">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Demandes d'Inscription - Annonceurs</h1>
        <p className="text-gray-600 mt-2">Approuvez ou rejetez les demandes</p>
      </div>

      <Card>
        {loading && registrations.length === 0 ? (
          <div className="flex justify-center items-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <Table columns={columns} data={registrations} />
        )}
      </Card>
    </div>
  );
};

export default AdvertiserRegistrations;
