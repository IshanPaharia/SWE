import React from 'react'
import { Check } from 'lucide-react'

const colorMap = {
  blue: 'from-blue-500 to-blue-600',
  purple: 'from-purple-500 to-purple-600',
  green: 'from-green-500 to-green-600',
  yellow: 'from-yellow-500 to-yellow-600',
  red: 'from-red-500 to-red-600',
  indigo: 'from-indigo-500 to-indigo-600'
}

const StepCard = ({ step, isActive, onClick }) => {
  const Icon = step.icon
  const gradientClass = colorMap[step.color] || colorMap.blue

  return (
    <button
      onClick={onClick}
      className={`
        relative overflow-hidden rounded-xl p-6 text-left transition-all duration-300
        ${isActive 
          ? 'ring-4 ring-primary-500 shadow-2xl scale-105' 
          : 'shadow-md hover:shadow-xl hover:scale-102'
        }
        bg-white
      `}
    >
      {/* Gradient Background for Icon */}
      <div className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-br ${gradientClass} opacity-10 rounded-full -mr-16 -mt-16`}></div>
      
      <div className="relative">
        <div className="flex items-start justify-between mb-3">
          <div className={`p-3 rounded-lg bg-gradient-to-br ${gradientClass}`}>
            <Icon className="w-6 h-6 text-white" />
          </div>
          {isActive && (
            <div className="flex items-center space-x-1 text-primary-600 text-sm font-medium">
              <Check className="w-4 h-4" />
              <span>Active</span>
            </div>
          )}
        </div>
        
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          {step.title}
        </h3>
        
        <p className="text-sm text-gray-600">
          {step.description}
        </p>
      </div>
    </button>
  )
}

export default StepCard

