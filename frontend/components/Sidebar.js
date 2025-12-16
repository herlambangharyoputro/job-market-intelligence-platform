// Location: frontend/components/Sidebar.js
/**
 * Sidebar Component
 * Module #5: Skill Validation System
 * 
 * Sidebar navigation with menu items
 * 
 * Author: Herlambang Haryo Putro
 * Date: 2025-12-16
 */

'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { 
  CheckCircle2, 
  ListChecks, 
  BookOpen, 
  LayoutDashboard,
  History,
  Settings,
  ChevronLeft,
  ChevronRight,
  FolderTree,
  ListTodo
} from 'lucide-react'
import { useState } from 'react'
import { cn } from '@/lib/utils'

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false)
  const pathname = usePathname()

  const navItems = [
    {
      name: 'Dashboard',
      href: '/',
      icon: LayoutDashboard,
    },
    {
      name: 'Validation Queue',
      href: '/validation/queue',
      icon: ListChecks,
    },
    {
      name: 'Queue Overview',
      href: '/validation/queue-overview',
      icon: ListTodo,
    },
    {
      name: 'Skills Dictionary',
      href: '/validation/dictionary',
      icon: BookOpen,
    },
    {
      name: 'Categories',
      href: '/validation/categories',
      icon: FolderTree,
    },
    {
      name: 'History',
      href: '/validation/history',
      icon: History,
    },
  ] 
  
  return (
    <div
      className={cn(
        'h-screen bg-card border-r border-border flex flex-col transition-all duration-300',
        collapsed ? 'w-16' : 'w-64'
      )}
    >
      {/* Header */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-border">
        {!collapsed && (
          <Link href="/" className="flex items-center space-x-2">
            <CheckCircle2 className="h-6 w-6 text-primary" />
            <span className="font-bold text-foreground">
              Skill Validator
            </span>
          </Link>
        )}
        {collapsed && (
          <CheckCircle2 className="h-6 w-6 text-primary mx-auto" />
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-2 py-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = pathname === item.href
          
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors',
                'hover:bg-accent hover:text-accent-foreground',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground',
                collapsed ? 'justify-center' : 'space-x-3'
              )}
              title={collapsed ? item.name : undefined}
            >
              <Icon className="h-5 w-5 flex-shrink-0" />
              {!collapsed && <span>{item.name}</span>}
            </Link>
          )
        })}
      </nav>

      {/* Collapse Toggle */}
      <div className="p-2 border-t border-border">
        <button
          onClick={() => setCollapsed(!collapsed)}
          className={cn(
            'w-full flex items-center px-3 py-2 rounded-md text-sm font-medium',
            'text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-colors',
            collapsed ? 'justify-center' : 'space-x-3'
          )}
        >
          {collapsed ? (
            <ChevronRight className="h-5 w-5" />
          ) : (
            <>
              <ChevronLeft className="h-5 w-5" />
              <span>Collapse</span>
            </>
          )}
        </button>
      </div>

      {/* Footer */}
      {!collapsed && (
        <div className="p-4 border-t border-border">
          <div className="text-xs text-muted-foreground">
            <p className="font-semibold">Skill Validation System</p>
            <p className="mt-1">Module #5 - v1.0.0</p>
          </div>
        </div>
      )}
    </div>
  )
}