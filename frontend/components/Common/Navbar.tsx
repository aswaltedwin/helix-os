'use client'

import React from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Box } from 'lucide-react'


export default function Navbar() {
  const pathname = usePathname()

  const navLinks = [
    { href: '/dashboard', label: 'Dashboard' },
    { href: '/agents', label: 'Agents' },
    { href: '/settings', label: 'Settings' },
  ]

  return (
    <nav className="bg-white/80 backdrop-blur-md border-b border-gray-100 px-8 py-4 sticky top-0 z-50 flex items-center justify-between">
      <Link href="/" className="flex items-center gap-2 text-xl font-bold text-gray-900">
        <div className="p-1.5 bg-blue-600 rounded-lg">
          <Box className="h-5 w-5 text-white" />
        </div>
        <span>Helix OS</span>
      </Link>
      <div className="flex gap-8">
        {navLinks.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className={`text-sm font-medium transition-colors ${
              pathname === link.href ? 'text-blue-600' : 'text-gray-500 hover:text-gray-900'
            }`}
          >
            {link.label}
          </Link>
        ))}
      </div>
    </nav>
  )
}

