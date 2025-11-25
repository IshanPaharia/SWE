import React from 'react'
import { Sparkles } from 'lucide-react'

const Header = () => {
  return (
    <header className="bg-gradient-to-r from-primary-600 to-primary-800 text-white shadow-lg">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Sparkles className="w-8 h-8" />
            <div>
              <h1 className="text-2xl font-bold">Automated Test Case Generator</h1>
              <p className="text-primary-100 text-sm">
                Genetic Algorithm-based Testing with Fault Localization
              </p>
            </div>
          </div>
          
          <div className="hidden md:flex items-center space-x-4">
            <div className="text-right">
              <p className="text-sm text-primary-100">API Status</p>
              <p className="text-xs text-primary-200">http://localhost:8000</p>
            </div>
            <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header

