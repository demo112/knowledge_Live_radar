'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { pyramidApi } from '@/lib/api';
import { Pyramid } from '@/types';

export default function PyramidListPage() {
  const [pyramids, setPyramids] = useState<Pyramid[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPyramids = async () => {
      try {
        const response = await pyramidApi.getAll();
        if (response.success) {
            setPyramids(response.data.items);
        }
      } catch (error) {
        console.error('Failed to fetch pyramids:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchPyramids();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Knowledge Pyramids</h1>
        <button 
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          onClick={() => alert('Create logic pending')}
        >
          Create New
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {pyramids.map((pyramid) => (
          <Link 
            key={pyramid.id} 
            href={`/pyramid/${pyramid.id}`}
            className="block p-6 bg-white border border-gray-200 rounded-lg shadow hover:bg-gray-50 transition"
          >
            <h5 className="mb-2 text-xl font-bold tracking-tight text-gray-900">{pyramid.name}</h5>
            <p className="font-normal text-gray-700">{pyramid.description || 'No description'}</p>
            <div className="mt-4 text-sm text-gray-500">
                Created: {new Date(pyramid.created_at).toLocaleDateString()}
            </div>
          </Link>
        ))}
        {pyramids.length === 0 && (
            <div className="col-span-3 text-center text-gray-500 py-10">
                No pyramids found. Create one to get started.
            </div>
        )}
      </div>
    </div>
  );
}
