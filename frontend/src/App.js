import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { 
  Brain, 
  Search, 
  Settings, 
  Activity, 
  Database,
  Cloud,
  Users,
  BarChart3
} from 'lucide-react';

// Components
import Dashboard from './components/Dashboard';
import MemoryManager from './components/MemoryManager';
import SearchInterface from './components/SearchInterface';
import Analytics from './components/Analytics';
import Settings from './components/Settings';
import IntegrationStatus from './components/IntegrationStatus';

// Styles
import './App.css';

function App() {
  const [serverStatus, setServerStatus] = useState('connecting');
  const [stats, setStats] = useState({
    totalMemories: 0,
    activeIntegrations: 0,
    cloudSync: false,
    lastSync: null
  });

  useEffect(() => {
    checkServerStatus();
    fetchStats();
    
    const interval = setInterval(() => {
      checkServerStatus();
      fetchStats();
    }, 30000); // Update every 30 seconds

    return () => clearInterval(interval);
  }, []);

  const checkServerStatus = async () => {
    try {
      const response = await fetch('/api/health');
      if (response.ok) {
        setServerStatus('connected');
      } else {
        setServerStatus('error');
      }
    } catch (error) {
      setServerStatus('disconnected');
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/stats');
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const getStatusColor = () => {
    switch (serverStatus) {
      case 'connected': return 'text-green-500';
      case 'connecting': return 'text-yellow-500';
      case 'error': return 'text-orange-500';
      case 'disconnected': return 'text-red-500';
      default: return 'text-gray-500';
    }
  };

  const getStatusText = () => {
    switch (serverStatus) {
      case 'connected': return 'Connected';
      case 'connecting': return 'Connecting...';
      case 'error': return 'Error';
      case 'disconnected': return 'Disconnected';
      default: return 'Unknown';
    }
  };

  return (
    <Router>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#1f2937',
              color: '#f9fafb',
            },
          }}
        />
        
        {/* Navigation */}
        <nav className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <Link to="/" className="flex items-center space-x-2 text-xl font-bold text-gray-900 dark:text-white">
                  <Brain className="h-8 w-8 text-indigo-600" />
                  <span>MCP Memory</span>
                  <span className="text-sm font-normal text-gray-500 bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
                    Production Ready
                  </span>
                </Link>
              </div>
              
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-6">
                  <Link 
                    to="/" 
                    className="text-gray-700 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400 px-3 py-2 rounded-md text-sm font-medium flex items-center space-x-1"
                  >
                    <Activity className="h-4 w-4" />
                    <span>Dashboard</span>
                  </Link>
                  
                  <Link 
                    to="/search" 
                    className="text-gray-700 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400 px-3 py-2 rounded-md text-sm font-medium flex items-center space-x-1"
                  >
                    <Search className="h-4 w-4" />
                    <span>Search</span>
                  </Link>
                  
                  <Link 
                    to="/memories" 
                    className="text-gray-700 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400 px-3 py-2 rounded-md text-sm font-medium flex items-center space-x-1"
                  >
                    <Database className="h-4 w-4" />
                    <span>Memories</span>
                  </Link>
                  
                  <Link 
                    to="/analytics" 
                    className="text-gray-700 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400 px-3 py-2 rounded-md text-sm font-medium flex items-center space-x-1"
                  >
                    <BarChart3 className="h-4 w-4" />
                    <span>Analytics</span>
                  </Link>
                  
                  <Link 
                    to="/integrations" 
                    className="text-gray-700 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400 px-3 py-2 rounded-md text-sm font-medium flex items-center space-x-1"
                  >
                    <Users className="h-4 w-4" />
                    <span>Integrations</span>
                  </Link>
                  
                  <Link 
                    to="/settings" 
                    className="text-gray-700 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400 px-3 py-2 rounded-md text-sm font-medium flex items-center space-x-1"
                  >
                    <Settings className="h-4 w-4" />
                    <span>Settings</span>
                  </Link>
                </div>
                
                {/* Server Status */}
                <div className="flex items-center space-x-2 px-3 py-1 bg-gray-100 dark:bg-gray-700 rounded-lg">
                  <div className={`w-2 h-2 rounded-full ${getStatusColor().replace('text', 'bg')}`}></div>
                  <span className={`text-xs font-medium ${getStatusColor()}`}>
                    {getStatusText()}
                  </span>
                </div>
                
                {/* Cloud Status */}
                {stats.cloudSync && (
                  <div className="flex items-center space-x-1 text-xs text-green-600 dark:text-green-400">
                    <Cloud className="h-3 w-3" />
                    <span>Cloud</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <Routes>
            <Route path="/" element={<Dashboard stats={stats} serverStatus={serverStatus} />} />
            <Route path="/search" element={<SearchInterface />} />
            <Route path="/memories" element={<MemoryManager />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/integrations" element={<IntegrationStatus />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
