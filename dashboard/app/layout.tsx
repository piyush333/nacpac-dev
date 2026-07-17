// Phase 6: Dashboard Layout
// Root layout with Tailwind CSS setup

import type { Metadata } from 'next'
import '../styles/globals.css'

export const metadata: Metadata = {
  title: 'NacPac Dev Agent Dashboard',
  description: 'Real-time monitoring for NacPac Dev Agent',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50">
        <div className="min-h-screen">
          {/* Header */}
          <header className="bg-white shadow">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
              <h1 className="text-3xl font-bold text-gray-900">
                🤖 NacPac Dev Agent Dashboard
              </h1>
              <p className="text-gray-600 text-sm mt-1">
                Real-time monitoring and control
              </p>
            </div>
          </header>

          {/* Main Content */}
          <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {children}
          </main>

          {/* Footer */}
          <footer className="bg-white shadow mt-12">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 text-center text-gray-600 text-sm">
              <p>
                Phase 6: Dashboard UI • Real-time Supabase integration • NacPac
                Agent v1.0
              </p>
            </div>
          </footer>
        </div>
      </body>
    </html>
  )
}
