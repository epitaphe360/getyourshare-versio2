import React from 'react';
import Card from '../components/common/Card';

const PrivacyPolicy = () => {
  return (
    <div className="max-w-4xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
      <Card className="p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Politique de Confidentialité</h1>
        
        <div className="prose prose-indigo max-w-none space-y-6 text-gray-600">
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">1. Introduction</h2>
            <p>
              Chez ShareYourSales ("nous", "notre"), nous accordons une importance capitale à la protection de vos données personnelles. 
              Cette politique de confidentialité explique comment nous collectons, utilisons et protégeons vos informations lorsque vous utilisez notre plateforme.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">2. Données collectées</h2>
            <p>Nous collectons les informations suivantes :</p>
            <ul className="list-disc pl-5 space-y-1">
              <li>Informations d'identité (Nom, Email, Téléphone)</li>
              <li>Informations de paiement (via notre partenaire sécurisé Stripe)</li>
              <li>Données de navigation et d'utilisation (Logs, IP anonymisée)</li>
              <li>Données relatives aux campagnes et performances (Clics, Ventes)</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">3. Utilisation des données</h2>
            <p>Vos données sont utilisées pour :</p>
            <ul className="list-disc pl-5 space-y-1">
              <li>Fournir et maintenir nos services</li>
              <li>Traiter vos paiements et commissions</li>
              <li>Améliorer la sécurité et prévenir la fraude</li>
              <li>Vous envoyer des notifications importantes</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">4. Vos droits (RGPD & CCPA)</h2>
            <p>Conformément aux réglementations en vigueur, vous disposez des droits suivants :</p>
            <ul className="list-disc pl-5 space-y-1">
              <li><strong>Droit d'accès :</strong> Vous pouvez demander une copie de vos données (Export).</li>
              <li><strong>Droit à l'oubli :</strong> Vous pouvez demander la suppression de votre compte.</li>
              <li><strong>Droit de rectification :</strong> Vous pouvez modifier vos informations à tout moment.</li>
              <li><strong>Droit d'opposition :</strong> Vous pouvez refuser certains traitements (cookies).</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">5. Sécurité</h2>
            <p>
              Nous utilisons des mesures de sécurité avancées (chiffrement, HTTPS, authentification forte) pour protéger vos données. 
              Vos mots de passe sont hachés et nous ne stockons jamais vos informations bancaires complètes.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">6. Contact</h2>
            <p>
              Pour toute question concernant vos données, contactez notre Délégué à la Protection des Données (DPO) à : 
              <a href="mailto:privacy@shareyoursales.com" className="text-indigo-600 ml-1">privacy@shareyoursales.com</a>
            </p>
          </section>
        </div>
      </Card>
    </div>
  );
};

export default PrivacyPolicy;
