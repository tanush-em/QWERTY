'use client';

import { useState, useEffect } from 'react';
import { Database, Users, Calendar, BookOpen, TrendingUp, RefreshCw } from 'lucide-react';

export default function Home() {
  const [collections, setCollections] = useState([]);
  const [selectedCollection, setSelectedCollection] = useState(null);
  const [collectionData, setCollectionData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchCollections();
  }, []);

  const fetchCollections = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/collections');
      const data = await response.json();
      if (data.success) {
        setCollections(data.collections);
      } else {
        setError(data.error);
      }
    } catch (err) {
      setError('Failed to fetch collections');
    } finally {
      setLoading(false);
    }
  };

  const fetchCollectionData = async (collectionName) => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`/api/data/${collectionName}`);
      const data = await response.json();
      if (data.success) {
        setCollectionData(data.data);
        setSelectedCollection(collectionName);
      } else {
        setError(data.error);
      }
    } catch (err) {
      setError('Failed to fetch collection data');
    } finally {
      setLoading(false);
    }
  };

  const getCollectionIcon = (collectionName) => {
    const name = collectionName.toLowerCase();
    if (name.includes('user') || name.includes('employee')) return <Users className="w-5 h-5" />;
    if (name.includes('attendance') || name.includes('time')) return <Calendar className="w-5 h-5" />;
    if (name.includes('course') || name.includes('training')) return <BookOpen className="w-5 h-5" />;
    if (name.includes('leave') || name.includes('holiday')) return <Calendar className="w-5 h-5" />;
    if (name.includes('analytics') || name.includes('report')) return <TrendingUp className="w-5 h-5" />;
    return <Database className="w-5 h-5" />;
  };

  const renderValue = (value) => {
    if (value === null || value === undefined) return 'null';
    if (typeof value === 'object') return JSON.stringify(value, null, 2);
    if (typeof value === 'boolean') return value.toString();
    return value.toString();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-3">
              <Database className="w-8 h-8 text-blue-600" />
              <h1 className="text-2xl font-bold text-gray-900">ERP Portal</h1>
            </div>
            <button
              onClick={fetchCollections}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex">
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <div className="mt-2 text-sm text-red-700">{error}</div>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Collections Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border">
              <div className="p-6 border-b">
                <h2 className="text-lg font-semibold text-gray-900">Collections</h2>
                <p className="text-sm text-gray-500 mt-1">
                  {collections.length} collections found
                </p>
              </div>
              <div className="p-4">
                {loading && collections.length === 0 ? (
                  <div className="text-center py-8">
                    <RefreshCw className="w-6 h-6 animate-spin mx-auto text-gray-400" />
                    <p className="text-sm text-gray-500 mt-2">Loading collections...</p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {collections.map((collection) => (
                      <button
                        key={collection.name}
                        onClick={() => fetchCollectionData(collection.name)}
                        className={`w-full text-left p-3 rounded-lg transition-colors flex items-center space-x-3 ${
                          selectedCollection === collection.name
                            ? 'bg-blue-50 text-blue-700 border border-blue-200'
                            : 'hover:bg-gray-50 text-gray-700'
                        }`}
                      >
                        {getCollectionIcon(collection.name)}
                        <span className="font-medium">{collection.name}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Data Display */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-lg shadow-sm border">
              <div className="p-6 border-b">
                <h2 className="text-lg font-semibold text-gray-900">
                  {selectedCollection ? `${selectedCollection} Data` : 'Select a Collection'}
                </h2>
                {selectedCollection && (
                  <p className="text-sm text-gray-500 mt-1">
                    {collectionData.length} records found
                  </p>
                )}
              </div>
              <div className="p-6">
                {!selectedCollection ? (
                  <div className="text-center py-12">
                    <Database className="w-12 h-12 mx-auto text-gray-400" />
                    <h3 className="mt-4 text-lg font-medium text-gray-900">No Collection Selected</h3>
                    <p className="mt-2 text-sm text-gray-500">
                      Choose a collection from the sidebar to view its data
                    </p>
                  </div>
                ) : loading ? (
                  <div className="text-center py-12">
                    <RefreshCw className="w-8 h-8 animate-spin mx-auto text-gray-400" />
                    <p className="text-sm text-gray-500 mt-2">Loading data...</p>
                  </div>
                ) : collectionData.length === 0 ? (
                  <div className="text-center py-12">
                    <Database className="w-12 h-12 mx-auto text-gray-400" />
                    <h3 className="mt-4 text-lg font-medium text-gray-900">No Data Found</h3>
                    <p className="mt-2 text-sm text-gray-500">
                      This collection appears to be empty
                    </p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          {Object.keys(collectionData[0] || {}).map((key) => (
                            <th
                              key={key}
                              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                            >
                              {key}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {collectionData.slice(0, 50).map((row, index) => (
                          <tr key={index} className="hover:bg-gray-50">
                            {Object.values(row).map((value, valueIndex) => (
                              <td
                                key={valueIndex}
                                className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 max-w-xs truncate"
                                title={renderValue(value)}
                              >
                                {renderValue(value)}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    {collectionData.length > 50 && (
                      <div className="mt-4 text-center">
                        <p className="text-sm text-gray-500">
                          Showing first 50 records of {collectionData.length} total
                        </p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
