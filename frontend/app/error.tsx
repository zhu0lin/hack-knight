'use client'

import { useEffect } from 'react'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error('Application error:', error)
  }, [error])

  return (
    <div className="min-h-screen bg-[#F1FBF6] flex items-center justify-center px-6">
      <div className="bg-white border border-red-200 rounded-2xl shadow-md w-full max-w-md p-8 space-y-6">
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-bold text-red-600">⚠️ Error</h1>
          <p className="text-[#5E7F73]">Something went wrong!</p>
        </div>

        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-sm text-red-800 font-mono break-words">
            {error.message || 'An unexpected error occurred'}
          </p>
        </div>

        <div className="space-y-3">
          <button
            onClick={reset}
            className="w-full bg-[#2BAA66] text-white py-2.5 rounded-lg font-semibold hover:bg-[#27A05F] transition-all"
          >
            Try Again
          </button>
          
          <button
            onClick={() => window.location.href = '/'}
            className="w-full bg-gray-200 text-gray-700 py-2.5 rounded-lg font-semibold hover:bg-gray-300 transition-all"
          >
            Go to Home
          </button>
        </div>

        <div className="text-xs text-center text-[#5E7F73]">
          <p>Check the browser console for more details</p>
        </div>
      </div>
    </div>
  )
}

