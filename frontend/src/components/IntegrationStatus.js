import React from 'react';
import { Users } from 'lucide-react';

const IntegrationStatus = () => (
  <div className="space-y-6">
    <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Integration Status</h2>
    <div className="bg-white dark:bg-gray-800 shadow rounded-lg border p-6 text-center">
      <Users className="mx-auto h-12 w-12 text-gray-400 mb-4" />
      <p className="text-gray-500 dark:text-gray-400">Integration management coming soon...</p>
    </div>
  </div>
);

export default IntegrationStatus;
