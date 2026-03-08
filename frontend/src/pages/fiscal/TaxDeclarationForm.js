import React, { useState } from 'react';
import { FileText, Send, CheckCircle } from 'lucide-react';
import { toast } from 'react-toastify';
import api from '../../utils/api';

const PERIODS = [
  'T1 2024 (Jan–Mar)', 'T2 2024 (Avr–Jun)',
  'T3 2024 (Jul–Sep)', 'T4 2024 (Oct–Déc)',
];

/**
 * TaxDeclarationForm — Formulaire de déclaration fiscale multi-pays
 */
const TaxDeclarationForm = () => {
  const [form, setForm] = useState({
    country: 'MA',
    period: PERIODS[0],
    revenue_ht: '',
    vat_collected: '',
    vat_deductible: '',
    expenses: '',
    notes: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const vatDue = form.vat_collected && form.vat_deductible
    ? (parseFloat(form.vat_collected) - parseFloat(form.vat_deductible)).toFixed(2)
    : '—';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api.post('/api/fiscal/declarations', form);
      setSubmitted(true);
      toast.success('Déclaration fiscale soumise avec succès !');
    } catch (error) {
      toast.error('Erreur lors de la soumission : ' + (error.response?.data?.detail || error.message));
    } finally {
      setSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <div className="p-6 flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <CheckCircle size={80} className="text-green-500" />
        <h2 className="text-2xl font-bold text-gray-800">Déclaration soumise !</h2>
        <p className="text-gray-500">Votre déclaration fiscale a été enregistrée.</p>
        <button
          onClick={() => setSubmitted(false)}
          className="mt-4 bg-blue-600 text-white px-6 py-2 rounded-xl hover:bg-blue-700 transition"
        >
          Nouvelle déclaration
        </button>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-2xl mx-auto space-y-6">
      <div className="bg-gradient-to-r from-indigo-600 to-blue-600 rounded-2xl p-8 text-white shadow-xl flex items-center gap-4">
        <FileText size={48} />
        <div>
          <h1 className="text-3xl font-bold">Déclaration Fiscale</h1>
          <p className="text-indigo-100 mt-1">Soumettez vos déclarations TVA et IS</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow p-6 space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Pays</label>
            <select
              className="w-full border rounded-lg px-3 py-2"
              value={form.country}
              onChange={(e) => setForm({ ...form, country: e.target.value })}
            >
              <option value="MA">🇲🇦 Maroc</option>
              <option value="FR">🇫🇷 France</option>
              <option value="US">🇺🇸 États-Unis</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Période</label>
            <select
              className="w-full border rounded-lg px-3 py-2"
              value={form.period}
              onChange={(e) => setForm({ ...form, period: e.target.value })}
            >
              {PERIODS.map(p => <option key={p}>{p}</option>)}
            </select>
          </div>
        </div>

        {[
          { key: 'revenue_ht', label: "Chiffre d'affaires HT" },
          { key: 'vat_collected', label: 'TVA collectée' },
          { key: 'vat_deductible', label: 'TVA déductible' },
          { key: 'expenses', label: 'Charges déductibles HT' },
        ].map(({ key, label }) => (
          <div key={key}>
            <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
            <input
              type="number"
              className="w-full border rounded-lg px-3 py-2"
              placeholder="0.00"
              value={form[key]}
              onChange={(e) => setForm({ ...form, [key]: e.target.value })}
            />
          </div>
        ))}

        <div className="bg-blue-50 rounded-xl p-4 flex justify-between items-center">
          <span className="font-medium text-gray-700">TVA nette à payer</span>
          <span className="text-xl font-bold text-blue-700">{vatDue} MAD</span>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
          <textarea
            rows={3}
            className="w-full border rounded-lg px-3 py-2"
            value={form.notes}
            onChange={(e) => setForm({ ...form, notes: e.target.value })}
          />
        </div>

        <button
          type="submit"
          disabled={submitting}
          className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:opacity-60 text-white font-bold py-3 rounded-xl transition flex items-center justify-center gap-2"
        >
          <Send size={20} />
          {submitting ? 'Envoi en cours...' : 'Soumettre la déclaration'}
        </button>
      </form>
    </div>
  );
};

export default TaxDeclarationForm;
