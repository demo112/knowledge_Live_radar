import React from 'react';
import Link from 'next/link';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-200">
        <div className="p-6">
          <h1 className="text-xl font-bold text-gray-800">AI Radar</h1>
        </div>
        <nav className="mt-6">
          <Link href="/pyramid" className="block px-6 py-3 text-gray-700 hover:bg-gray-50 hover:text-blue-600">
            Pyramids
          </Link>
          <Link href="/sources" className="block px-6 py-3 text-gray-700 hover:bg-gray-50 hover:text-blue-600">
            Sources
          </Link>
          <Link href="/contents" className="block px-6 py-3 text-gray-700 hover:bg-gray-50 hover:text-blue-600">
            Contents
          </Link>
          <Link href="/feed" className="block px-6 py-3 text-gray-700 hover:bg-gray-50 hover:text-blue-600">
            Feed
          </Link>
          <Link href="/approval" className="block px-6 py-3 text-gray-700 hover:bg-gray-50 hover:text-blue-600">
            Approval
          </Link>
          <Link href="/health" className="block px-6 py-3 text-gray-700 hover:bg-gray-50 hover:text-blue-600">
            Health
          </Link>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        {children}
      </main>
    </div>
  );
}
