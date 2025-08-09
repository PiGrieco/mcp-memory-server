import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  Database, 
  Cloud, 
  Zap, 
  TrendingUp,
  Users,
  Clock,
  Brain,
  ChevronRight
} from 'lucide-react';

const StatCard = ({ title, value, icon: Icon, trend, color = "indigo" }) => (
  <div className={`bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg border border-gray-200 dark:border-gray-700`}>
    <div className="p-5">
      <div className="flex items-center">
        <div className="flex-shrink-0">
          <Icon className={`h-6 w-6 text-${color}-600`} />
        </div>
        <div className="ml-5 w-0 flex-1">
          <dl>
            <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
              {title}
            </dt>
            <dd className="flex items-baseline">
              <div className="text-2xl font-semibold text-gray-900 dark:text-white">
                {value}
              </div>
              {trend && (
                <div className={`ml-2 flex items-baseline text-sm font-semibold ${
                  trend > 0 ? 'text-green-600' : trend < 0 ? 'text-red-600' : 'text-gray-500'
                }`}>
                  <TrendingUp className="h-3 w-3 mr-1" />
                  {Math.abs(trend)}%
                </div>
              )}
            </dd>
          </dl>
        </div>
      </div>
    </div>
  </div>
);

const QuickAction = ({ title, description, icon: Icon, onClick, color = "indigo" }) => (
  <button
    onClick={onClick}
    className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-indigo-300 dark:hover:border-indigo-600 transition-colors duration-200 text-left w-full group"
  >
    <div className="flex items-center justify-between">
      <div className="flex items-center space-x-3">
        <div className={`p-2 bg-${color}-100 dark:bg-${color}-900 rounded-lg`}>
          <Icon className={`h-5 w-5 text-${color}-600 dark:text-${color}-400`} />
        </div>
        <div>
          <h3 className="text-sm font-medium text-gray-900 dark:text-white">
            {title}
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            {description}
          </p>
        </div>
      </div>
      <ChevronRight className="h-4 w-4 text-gray-400 group-hover:text-gray-600 dark:group-hover:text-gray-300" />
    </div>
  </button>
);

const RecentActivity = ({ activities = [] }) => (
  <div className="bg-white dark:bg-gray-800 shadow rounded-lg border border-gray-200 dark:border-gray-700">
    <div className="px-4 py-5 sm:p-6">
      <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white mb-4">
        Recent Activity
      </h3>
      <div className="space-y-3">
        {activities.length > 0 ? (
          activities.map((activity, index) => (
            <div key={index} className="flex items-center space-x-3">
              <div className="flex-shrink-0">
                <div className="h-2 w-2 bg-indigo-500 rounded-full"></div>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-gray-900 dark:text-white">
                  {activity.description}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {activity.timestamp}
                </p>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-4">
            <Activity className="mx-auto h-8 w-8 text-gray-400" />
            <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
              No recent activity
            </p>
          </div>
        )}
      </div>
    </div>
  </div>
);

const Dashboard = ({ stats, serverStatus }) => {
  const [recentActivity, setRecentActivity] = useState([]);
  const [integrationStatus, setIntegrationStatus] = useState({});
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchRecentActivity();
    fetchIntegrationStatus();
  }, []);

  const fetchRecentActivity = async () => {
    try {
      const response = await fetch('/api/activity/recent');
      if (response.ok) {
        const data = await response.json();
        setRecentActivity(data);
      }
    } catch (error) {
      console.error('Failed to fetch recent activity:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchIntegrationStatus = async () => {
    try {
      const response = await fetch('/api/integrations/status');
      if (response.ok) {
        const data = await response.json();
        setIntegrationStatus(data);
      }
    } catch (error) {
      console.error('Failed to fetch integration status:', error);
    }
  };

  const quickActions = [
    {
      title: "Search Memories",
      description: "Find relevant information",
      icon: Database,
      onClick: () => window.location.href = '/search',
      color: "blue"
    },
    {
      title: "Create Memory",
      description: "Save new information",
      icon: Brain,
      onClick: () => window.location.href = '/memories?action=create',
      color: "green"
    },
    {
      title: "View Analytics",
      description: "Memory usage insights",
      icon: TrendingUp,
      onClick: () => window.location.href = '/analytics',
      color: "purple"
    },
    {
      title: "Sync to Cloud",
      description: "Backup your memories",
      icon: Cloud,
      onClick: async () => {
        try {
          await fetch('/api/sync/force', { method: 'POST' });
          alert('Sync initiated successfully!');
        } catch (error) {
          alert('Sync failed. Please try again.');
        }
      },
      color: "indigo"
    }
  ];

  const systemStats = [
    {
      title: "Total Memories",
      value: stats.totalMemories?.toLocaleString() || "0",
      icon: Database,
      trend: stats.memoryGrowth,
      color: "blue"
    },
    {
      title: "Active Integrations",
      value: stats.activeIntegrations || "0",
      icon: Users,
      color: "green"
    },
    {
      title: "Server Uptime",
      value: stats.uptime || "0h",
      icon: Clock,
      color: "purple"
    },
    {
      title: "Memory Usage",
      value: stats.memoryUsage || "0MB",
      icon: Activity,
      trend: stats.usageGrowth,
      color: "orange"
    }
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="md:flex md:items-center md:justify-between">
        <div className="flex-1 min-w-0">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 dark:text-white sm:text-3xl sm:truncate">
            Dashboard
          </h2>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Monitor your MCP Memory Server activity and performance
          </p>
        </div>
        <div className="mt-4 flex md:mt-0 md:ml-4">
          <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${
            serverStatus === 'connected' 
              ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
              : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
          }`}>
            <div className={`w-1.5 h-1.5 rounded-full mr-2 ${
              serverStatus === 'connected' ? 'bg-green-400' : 'bg-red-400'
            }`}></div>
            {serverStatus === 'connected' ? 'Server Online' : 'Server Offline'}
          </span>
        </div>
      </div>

      {/* Statistics Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {systemStats.map((stat, index) => (
          <StatCard key={index} {...stat} />
        ))}
      </div>

      {/* Quick Actions and Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Quick Actions */}
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white mb-4">
              Quick Actions
            </h3>
            <div className="space-y-3">
              {quickActions.map((action, index) => (
                <QuickAction key={index} {...action} />
              ))}
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <RecentActivity activities={recentActivity} />
      </div>

      {/* Integration Status Overview */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg border border-gray-200 dark:border-gray-700">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white mb-4">
            Integration Status
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {Object.entries(integrationStatus).map(([platform, status]) => (
              <div key={platform} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className="flex items-center space-x-2">
                  <div className={`w-2 h-2 rounded-full ${
                    status?.active ? 'bg-green-400' : 'bg-gray-400'
                  }`}></div>
                  <span className="text-sm font-medium text-gray-900 dark:text-white capitalize">
                    {platform}
                  </span>
                </div>
                <span className={`text-xs px-2 py-1 rounded-full ${
                  status?.active 
                    ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                    : 'bg-gray-100 text-gray-800 dark:bg-gray-600 dark:text-gray-200'
                }`}>
                  {status?.active ? 'Active' : 'Inactive'}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
