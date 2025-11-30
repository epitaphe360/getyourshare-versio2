import React, { useState } from 'react';
import AffiliateLinksGenerator from '../../components/commercial/AffiliateLinksGenerator';
import AffiliateLinksTable from '../../components/commercial/AffiliateLinksTable';
import CommissionsTable from '../../components/commercial/CommissionsTable';

const TrackingPage = () => {
  const [activeTab, setActiveTab] = useState('links');

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">🔗 Tracking & Commissions</h1>
        <p className="text-gray-500 mt-2">
          Générez des liens affiliés et suivez vos commissions en temps réel
        </p>
      </div>

      <div className="w-full">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8" aria-label="Tabs">
            <button
              onClick={() => setActiveTab('generator')}
              className={`${
                activeTab === 'generator'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              Générer
            </button>
            <button
              onClick={() => setActiveTab('links')}
              className={`${
                activeTab === 'links'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              Mes liens
            </button>
            <button
              onClick={() => setActiveTab('commissions')}
              className={`${
                activeTab === 'commissions'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              Commissions
            </button>
          </nav>
        </div>

        <div className="mt-6">
          {activeTab === 'generator' && <AffiliateLinksGenerator />}
          {activeTab === 'links' && <AffiliateLinksTable />}
          {activeTab === 'commissions' && <CommissionsTable />}
        </div>
      </div>
    </div>
  );
};

export default TrackingPage;
