import React from 'react';
import { Scale, Building, Mail, Phone, MapPin } from 'lucide-react';

const Legal = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-8">
          <div className="flex items-center space-x-4 mb-6">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center">
              <Scale className="w-8 h-8 text-gray-600" />
            </div>
            <div>
              <h1 className="text-4xl font-bold text-gray-900">Mentions Légales</h1>
              <p className="text-gray-600 mt-2">Conformément à la loi n° 31-08 édictant des mesures de protection du consommateur</p>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="bg-white rounded-2xl shadow-lg p-8 space-y-8">
          
          {/* Éditeur */}
          <section>
            <div className="flex items-start space-x-3 mb-4">
              <Building className="w-6 h-6 text-gray-600 mt-1" />
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-3">1. Éditeur du Site</h2>
                <div className="bg-gray-50 p-6 rounded-lg space-y-2">
                  <p className="text-gray-700"><strong>Dénomination sociale :</strong> SHAREYOURSALES SARL</p>
                  <p className="text-gray-700"><strong>Forme juridique :</strong> Société à Responsabilité Limitée</p>
                  <p className="text-gray-700"><strong>Capital social :</strong> 100.000 DH</p>
                  <p className="text-gray-700"><strong>Siège social :</strong> Technopark, Route de Nouaceur, Casablanca, Maroc</p>
                  <p className="text-gray-700"><strong>RC :</strong> 123456</p>
                  <p className="text-gray-700"><strong>ICE :</strong> 001234567890000</p>
                  <p className="text-gray-700"><strong>IF :</strong> 12345678</p>
                </div>
              </div>
            </div>
          </section>

          {/* Contact */}
          <section className="border-t pt-8">
            <div className="flex items-start space-x-3 mb-4">
              <Mail className="w-6 h-6 text-gray-600 mt-1" />
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-3">2. Contact</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-gray-50 p-4 rounded-lg flex items-center space-x-3">
                    <Mail className="w-5 h-5 text-blue-600" />
                    <a href="mailto:contact@shareyoursales.ma" className="text-gray-700 hover:text-blue-600">contact@shareyoursales.ma</a>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg flex items-center space-x-3">
                    <Phone className="w-5 h-5 text-green-600" />
                    <a href="tel:+212522000000" className="text-gray-700 hover:text-green-600">+212 5 22 00 00 00</a>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg flex items-center space-x-3 md:col-span-2">
                    <MapPin className="w-5 h-5 text-red-600" />
                    <span className="text-gray-700">Technopark, Route de Nouaceur, Casablanca</span>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* Hébergement */}
          <section className="border-t pt-8">
            <div className="flex items-start space-x-3 mb-4">
              <Globe className="w-6 h-6 text-gray-600 mt-1" />
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-3">3. Hébergement</h2>
                <div className="bg-gray-50 p-6 rounded-lg">
                  <p className="text-gray-700 mb-2">Le site est hébergé par :</p>
                  <p className="text-gray-900 font-semibold">Vercel Inc.</p>
                  <p className="text-gray-600 text-sm">340 S Lemon Ave #4133</p>
                  <p className="text-gray-600 text-sm">Walnut, CA 91789</p>
                  <p className="text-gray-600 text-sm">États-Unis</p>
                  <a href="https://vercel.com" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline text-sm mt-2 inline-block">https://vercel.com</a>
                </div>
              </div>
            </div>
          </section>

          {/* Propriété Intellectuelle */}
          <section className="border-t pt-8">
            <div className="flex items-start space-x-3 mb-4">
              <Shield className="w-6 h-6 text-gray-600 mt-1" />
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-3">4. Propriété Intellectuelle</h2>
                <p className="text-gray-700 leading-relaxed">
                  L'ensemble de ce site relève de la législation marocaine et internationale sur le droit d'auteur et la propriété intellectuelle. 
                  Tous les droits de reproduction sont réservés, y compris pour les documents téléchargeables et les représentations iconographiques et photographiques.
                  La reproduction de tout ou partie de ce site sur un support électronique quel qu'il soit est formellement interdite sauf autorisation expresse du directeur de la publication.
                </p>
              </div>
            </div>
          </section>

        </div>
      </div>
    </div>
  );
};

import { Globe } from 'lucide-react';

export default Legal;
