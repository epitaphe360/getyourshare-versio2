import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import SwipeMatching from '../components/features/SwipeMatching';
import { ArrowLeft, Filter } from 'lucide-react';

const InfluencerMatchingPage = () => {
  const navigate = useNavigate();
  
  // Dummy data for Influencers
  const influencers = [
    {
      id: 1,
      title: 'Sarah Mode',
      subtitle: '@sarah.style • 45k abonnés',
      description: 'Influenceuse mode et lifestyle basée à Casablanca. Taux d\'engagement de 5.2%. Spécialisée dans les marques de luxe et prêt-à-porter.',
      image: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
      budget: '200€ / post',
      audience: 'Femmes 18-35'
    },
    {
      id: 2,
      title: 'Tech Karim',
      subtitle: '@karim.tech • 120k abonnés',
      description: 'Le geek préféré du Maroc. Je teste tout ce qui a un écran. Audience très masculine et CSP+.',
      image: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
      budget: '500€ / vidéo',
      audience: 'Hommes 20-45'
    },
    {
      id: 3,
      title: 'Beauty Amina',
      subtitle: '@amina.glam • 85k abonnés',
      description: 'Makeup artist pro. Je crée des tutoriels détaillés. Mes abonnés font confiance à mes recommandations aveuglément.',
      image: 'https://images.unsplash.com/photo-1531123897727-8f129e1688ce?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
      budget: '350€ / reel',
      audience: 'Femmes 16-40'
    },
    {
      id: 4,
      title: 'Fit Youssef',
      subtitle: '@youssef.fit • 60k abonnés',
      description: 'Coach sportif et nutrition. Je promeus un mode de vie sain. Idéal pour compléments alimentaires et vêtements de sport.',
      image: 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
      budget: '300€ / post',
      audience: 'Mixte 20-35'
    }
  ];

  const handleMatch = (influencer) => {
    console.log('Matched with', influencer.title);
    // API call to send proposal
  };

  const handleReject = (influencer) => {
    console.log('Rejected', influencer.title);
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-4 md:p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <button 
            onClick={() => navigate(-1)}
            className="p-2 bg-gray-800 rounded-full hover:bg-gray-700 transition"
          >
            <ArrowLeft size={24} />
          </button>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-pink-500 to-rose-500 bg-clip-text text-transparent">
            Matching Influenceurs
          </h1>
          <button className="p-2 bg-gray-800 rounded-full hover:bg-gray-700 transition">
            <Filter size={24} />
          </button>
        </div>

        {/* Main Content */}
        <div className="relative min-h-[650px] flex flex-col items-center justify-center">
          <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
            <div className="absolute top-[10%] left-[10%] w-[30%] h-[30%] bg-blue-600/20 rounded-full blur-[100px]" />
            <div className="absolute bottom-[10%] right-[10%] w-[30%] h-[30%] bg-purple-600/20 rounded-full blur-[100px]" />
          </div>

          <div className="z-10 w-full">
            <SwipeMatching 
              items={influencers} 
              onMatch={handleMatch} 
              onReject={handleReject} 
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default InfluencerMatchingPage;
