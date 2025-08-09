import React from 'react';
import { BarChart3, TrendingUp, Activity } from 'lucide-react';

const Analytics = () => (
  <div className="space-y-6">
    <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Analytics</h2>
    <div className="bg-white dark:bg-gray-800 shadow rounded-lg border p-6 text-center">
      <BarChart3 className="mx-auto h-12 w-12 text-gray-400 mb-4" />
      <p className="text-gray-500 dark:text-gray-400">Analytics dashboard coming soon...</p>
    </div>
  </div>
);

export default Analytics;
