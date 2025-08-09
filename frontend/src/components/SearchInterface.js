import React, { useState } from 'react';
import { Search, Filter, Clock, Star } from 'lucide-react';

const SearchInterface = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [filters, setFilters] = useState({
    project: 'all',
    memory_type: 'all',
    importance: 0
  });

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    try {
      const params = new URLSearchParams({
        query,
        ...filters,
        limit: 20
      });
      
      const response = await fetch(`/api/memories/search?${params}`);
      if (response.ok) {
        const data = await response.json();
        setResults(data.memories || []);
      }
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          Search Memories
        </h2>
        
        <form onSubmit={handleSearch} className="space-y-4">
          <div className="flex space-x-2">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search your memories..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
            <button
              type="submit"
              disabled={isLoading}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
            >
              {isLoading ? 'Searching...' : 'Search'}
            </button>
          </div>
          
          <div className="flex space-x-4">
            <select
              value={filters.project}
              onChange={(e) => setFilters(prev => ({ ...prev, project: e.target.value }))}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="all">All Projects</option>
              <option value="default">Default</option>
            </select>
            
            <select
              value={filters.memory_type}
              onChange={(e) => setFilters(prev => ({ ...prev, memory_type: e.target.value }))}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="all">All Types</option>
              <option value="conversation">Conversation</option>
              <option value="function">Function</option>
              <option value="knowledge">Knowledge</option>
            </select>
          </div>
        </form>
      </div>

      {/* Results */}
      <div className="space-y-4">
        {results.map((memory) => (
          <div key={memory.id} className="bg-white dark:bg-gray-800 shadow rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                  {memory.title || 'Untitled Memory'}
                </h3>
                <p className="mt-2 text-gray-600 dark:text-gray-300">
                  {memory.content.substring(0, 200)}...
                </p>
                <div className="mt-4 flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                  <span className="flex items-center">
                    <Clock className="h-4 w-4 mr-1" />
                    {new Date(memory.created_at).toLocaleDateString()}
                  </span>
                  <span className="flex items-center">
                    <Star className="h-4 w-4 mr-1" />
                    {(memory.importance * 5).toFixed(1)}/5
                  </span>
                  <span className="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
                    {memory.memory_type}
                  </span>
                </div>
              </div>
            </div>
          </div>
        ))}
        
        {results.length === 0 && !isLoading && (
          <div className="text-center py-8">
            <Search className="mx-auto h-12 w-12 text-gray-400" />
            <p className="mt-2 text-gray-500 dark:text-gray-400">
              No memories found. Try a different search term.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchInterface;
