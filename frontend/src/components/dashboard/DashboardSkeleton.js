import React from 'react';

const DashboardSkeleton = () => {
  return (
    <div className="p-6 bg-gray-50 min-h-screen animate-pulse">
      {/* Header Skeleton */}
      <div className="bg-gray-200 rounded-lg h-32 mb-6"></div>

      {/* Navigation Skeleton */}
      <div className="bg-white rounded-lg shadow-md p-4 mb-4 flex gap-3">
        <div className="h-10 w-24 bg-gray-200 rounded-lg"></div>
        <div className="h-10 w-32 bg-gray-200 rounded-lg"></div>
        <div className="h-10 w-32 bg-gray-200 rounded-lg"></div>
      </div>

      {/* Banner Skeleton */}
      <div className="bg-gray-200 rounded-xl h-40 mb-6"></div>

      {/* Stats Grid Skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-white rounded-lg shadow-sm p-6 h-32">
            <div className="h-4 w-24 bg-gray-200 rounded mb-4"></div>
            <div className="h-8 w-16 bg-gray-200 rounded"></div>
          </div>
        ))}
      </div>

      {/* Charts Skeleton */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-white rounded-lg shadow-sm p-6 h-80"></div>
        <div className="bg-white rounded-lg shadow-sm p-6 h-80"></div>
      </div>
    </div>
  );
};

export default DashboardSkeleton;
