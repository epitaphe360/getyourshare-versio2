import React, { useState } from 'react';
import { Calculator, DollarSign, Info } from 'lucide-react';

const VAT_RATES = {
  MA: { standard: 20, reduced: 7, exempt: 0 },
  FR: { standard: 20, reduced: 5.5, super_reduced: 2.1, exempt: 0 },
  US: { standard: 0, note: 'TVA gérée état par état (sales tax)' },
};

/**
 * VATCalculator — Calculateur de TVA multi-pays (MA / FR / US)
 */
const VATCalculator = () => {
  const [country, setCountry] = useState('MA');
  const [rate, setRate] = useState(20);
  const [htAmount, setHtAmount] = useState('');
  const [ttcAmount, setTtcAmount] = useState('');
  const [direction, setDirection] = useState('ht_to_ttc');

  const rates = VAT_RATES[country];

  const calculate = () => {
    const value = parseFloat(direction === 'ht_to_ttc' ? htAmount : ttcAmount);
    if (isNaN(value)) return;
    if (direction === 'ht_to_ttc') {
      setTtcAmount((value * (1 + rate / 100)).toFixed(2));
    } else {
      setHtAmount((value / (1 + rate / 100)).toFixed(2));
    }
  };

  const vat = htAmount && ttcAmount
    ? (parseFloat(ttcAmount) - parseFloat(htAmount)).toFixed(2)
    : '—';

  return (
    <div className="p-6 max-w-2xl mx-auto space-y-6">
      <div className="bg-gradient-to-r from-teal-600 to-cyan-600 rounded-2xl p-8 text-white shadow-xl flex items-center gap-4">
        <Calculator size={48} />
        <div>
          <h1 className="text-3xl font-bold">Calculateur de TVA</h1>
          <p className="text-teal-100 mt-1">Multi-pays : Maroc · France · USA</p>
        </div>
      </div>

      <div className="bg-white rounded-2xl shadow p-6 space-y-4">
        {/* Pays */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Pays</label>
          <select
            className="w-full border rounded-lg px-3 py-2"
            value={country}
            onChange={(e) => { setCountry(e.target.value); setRate(VAT_RATES[e.target.value].standard); }}
          >
            <option value="MA">🇲🇦 Maroc</option>
            <option value="FR">🇫🇷 France</option>
            <option value="US">🇺🇸 États-Unis</option>
          </select>
        </div>

        {/* Taux */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Taux de TVA (%)</label>
          <select
            className="w-full border rounded-lg px-3 py-2"
            value={rate}
            onChange={(e) => setRate(Number(e.target.value))}
          >
            {Object.entries(rates)
              .filter(([k]) => k !== 'note')
              .map(([label, value]) => (
                <option key={label} value={value}>{label.replace('_', ' ')} — {value}%</option>
              ))}
          </select>
          {rates.note && (
            <p className="text-xs text-gray-500 mt-1 flex items-center gap-1">
              <Info size={12} /> {rates.note}
            </p>
          )}
        </div>

        {/* Sens de calcul */}
        <div className="flex gap-4">
          <button
            onClick={() => setDirection('ht_to_ttc')}
            className={`flex-1 py-2 rounded-lg font-medium transition ${direction === 'ht_to_ttc' ? 'bg-teal-600 text-white' : 'bg-gray-100 text-gray-700'}`}
          >HT → TTC</button>
          <button
            onClick={() => setDirection('ttc_to_ht')}
            className={`flex-1 py-2 rounded-lg font-medium transition ${direction === 'ttc_to_ht' ? 'bg-teal-600 text-white' : 'bg-gray-100 text-gray-700'}`}
          >TTC → HT</button>
        </div>

        {/* Montant */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {direction === 'ht_to_ttc' ? 'Montant HT' : 'Montant TTC'}
          </label>
          <input
            type="number"
            className="w-full border rounded-lg px-3 py-2"
            placeholder="0.00"
            value={direction === 'ht_to_ttc' ? htAmount : ttcAmount}
            onChange={(e) => direction === 'ht_to_ttc' ? setHtAmount(e.target.value) : setTtcAmount(e.target.value)}
          />
        </div>

        <button
          onClick={calculate}
          className="w-full bg-teal-600 hover:bg-teal-700 text-white font-bold py-3 rounded-xl transition"
        >
          Calculer
        </button>

        {/* Résultat */}
        <div className="bg-gray-50 rounded-xl p-4 grid grid-cols-3 gap-4 text-center">
          <div>
            <p className="text-xs text-gray-500">Montant HT</p>
            <p className="text-xl font-bold text-gray-800">{htAmount || '—'}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500">TVA ({rate}%)</p>
            <p className="text-xl font-bold text-teal-600">{vat}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Montant TTC</p>
            <p className="text-xl font-bold text-gray-800">{ttcAmount || '—'}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VATCalculator;
