'use client';

import { useEffect, useState, use } from 'react';
import { pyramidApi } from '@/lib/api';
import { PyramidDetail } from '@/types';
import PyramidView from '@/components/pyramid/PyramidView';

export default function PyramidDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const unwrappedParams = use(params);
  const [pyramid, setPyramid] = useState<PyramidDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPyramid = async () => {
      try {
        const response = await pyramidApi.getById(unwrappedParams.id);
        if (response.success) {
          setPyramid(response.data);
        }
      } catch (error) {
        console.error('Failed to fetch pyramid:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchPyramid();
  }, [unwrappedParams.id]);

  if (loading) return <div>Loading...</div>;
  if (!pyramid) return <div>Pyramid not found</div>;

  return (
    <div className="p-8 h-screen flex flex-col">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">{pyramid.name}</h1>
        <p className="text-gray-600">{pyramid.description}</p>
      </div>
      
      <div className="flex-grow">
         <PyramidView data={pyramid} />
      </div>
    </div>
  );
}
