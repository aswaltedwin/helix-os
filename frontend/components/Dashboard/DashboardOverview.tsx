'use client'

import React from 'react'
import { Users, Activity, FileText } from 'lucide-react'


export default function DashboardOverview() {
  const stats = [
    { label: 'Total Agents', value: '3', icon: Users, color: 'text-blue-600' },
    { label: 'Active Tasks', value: '0', icon: Activity, color: 'text-green-600' },
    { label: 'Audit Events', value: '12', icon: FileText, color: 'text-purple-600' },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {stats.map((stat) => (
        <div key={stat.label} className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider">{stat.label}</h3>
            <stat.icon className={`h-5 w-5 ${stat.color}`} />
          </div>
          <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
        </div>
      ))}
    </div>
  )
}

