import React from 'react';
import { KnowledgeNode } from '@/lib/api/knowledge';
import { XMarkIcon } from '@heroicons/react/24/outline';

interface NodeDetailSidebarProps {
  node: KnowledgeNode | null;
  onClose: () => void;
}

const NodeDetailSidebar: React.FC<NodeDetailSidebarProps> = ({ node, onClose }) => {
  if (!node) return null;

  return (
    <div className="fixed right-0 top-0 h-full w-96 bg-white shadow-xl transition-transform transform translate-x-0 z-50 overflow-y-auto border-l">
      <div className="p-4 border-b flex justify-between items-center bg-gray-50">
        <h2 className="text-lg font-semibold text-gray-900">{node.name}</h2>
        <button
          onClick={onClose}
          className="rounded-md p-1 hover:bg-gray-200 text-gray-500 hover:text-gray-700"
        >
          <XMarkIcon className="h-5 w-5" />
        </button>
      </div>

      <div className="p-4 space-y-6">
        {/* Basic Info */}
        <div>
          <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-2">
            Basic Info
          </h3>
          <div className="bg-white rounded-lg border p-3 space-y-2">
            <div className="text-sm text-gray-600">
              <span className="font-medium">Type:</span> {node.node_type}
            </div>
            <div className="text-sm text-gray-600">
              <span className="font-medium">Status:</span> 
              <span className={`ml-2 px-2 py-0.5 rounded-full text-xs ${
                node.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
              }`}>
                {node.status}
              </span>
            </div>
            <div className="text-sm text-gray-600">
              <span className="font-medium">Health Score:</span> {node.health_score}
            </div>
            {node.description && (
              <div className="text-sm text-gray-600 mt-2">
                <p className="font-medium mb-1">Description:</p>
                <p className="bg-gray-50 p-2 rounded text-gray-700">{node.description}</p>
              </div>
            )}
          </div>
        </div>

        {/* Cognitive Model */}
        {node.ai_model && (
          <div>
            <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-2">
              Cognitive Model
            </h3>
            <div className="bg-white rounded-lg border p-3 space-y-4">
              {node.ai_model.definition && (
                <div>
                  <h4 className="text-xs font-semibold text-gray-400 mb-1">DEFINITION</h4>
                  <p className="text-sm text-gray-800 leading-relaxed">
                    {node.ai_model.definition}
                  </p>
                </div>
              )}
              
              {node.ai_model.key_attributes && (
                <div>
                  <h4 className="text-xs font-semibold text-gray-400 mb-1">KEY ATTRIBUTES</h4>
                  <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                    {node.ai_model.key_attributes.map((attr: string, i: number) => (
                      <li key={i}>{attr}</li>
                    ))}
                  </ul>
                </div>
              )}

              {node.ai_model.misconceptions && (
                <div>
                  <h4 className="text-xs font-semibold text-gray-400 mb-1">MISCONCEPTIONS</h4>
                  <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                    {node.ai_model.misconceptions.map((m: string, i: number) => (
                      <li key={i}>{m}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Metadata */}
        <div>
          <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-2">
            Metadata
          </h3>
          <div className="text-xs text-gray-400 space-y-1">
            <div>ID: {node.id}</div>
            <div>Created: {new Date(node.created_at).toLocaleString()}</div>
            <div>Updated: {new Date(node.updated_at).toLocaleString()}</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NodeDetailSidebar;
