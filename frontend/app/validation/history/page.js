// Location: frontend/app/validation/history/page.js
/**
 * Validation History Page
 * Module #5: Skill Validation System
 * 
 * View validation activity and audit trail
 * 
 * Author: Herlambang Haryo Putro
 * Date: 2025-12-16
 */

'use client'

import { useEffect, useState } from 'react'
import { validationApi, handleApiError } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { 
  CheckCircle2, 
  XCircle, 
  Edit, 
  GitMerge,
  Trash2,
  Clock
} from 'lucide-react'
import toast from 'react-hot-toast'

export default function HistoryPage() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadHistory()
  }, [])

  const loadHistory = async () => {
    try {
      const response = await validationApi.getStats()
      setStats(response.data)
    } catch (error) {
      const apiError = handleApiError(error)
      toast.error(apiError.message)
    } finally {
      setLoading(false)
    }
  }

  const getActionIcon = (action) => {
    switch (action) {
      case 'approved':
        return <CheckCircle2 className="h-5 w-5 text-green-500" />
      case 'rejected':
        return <XCircle className="h-5 w-5 text-red-500" />
      case 'updated':
        return <Edit className="h-5 w-5 text-blue-500" />
      case 'merged':
        return <GitMerge className="h-5 w-5 text-purple-500" />
      case 'deleted':
        return <Trash2 className="h-5 w-5 text-gray-500" />
      default:
        return <Clock className="h-5 w-5 text-gray-400" />
    }
  }

  const getActionBadge = (action) => {
    const variants = {
      approved: 'border-green-300 text-green-700',
      rejected: 'border-red-300 text-red-700',
      updated: 'border-blue-300 text-blue-700',
      merged: 'border-purple-300 text-purple-700',
      deleted: 'border-gray-300 text-gray-700',
      created: 'border-gray-300 text-gray-700'
    }

    return (
      <Badge variant="outline" className={variants[action] || 'border-gray-300 text-gray-700'}>
        {action}
      </Badge>
    )
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))

    if (days === 0) {
      const hours = Math.floor(diff / (1000 * 60 * 60))
      if (hours === 0) {
        const minutes = Math.floor(diff / (1000 * 60))
        return `${minutes} minute${minutes !== 1 ? 's' : ''} ago`
      }
      return `${hours} hour${hours !== 1 ? 's' : ''} ago`
    } else if (days === 1) {
      return 'Yesterday'
    } else if (days < 7) {
      return `${days} days ago`
    } else {
      return date.toLocaleDateString()
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-4 w-96 mt-2" />
        </div>
        <div className="space-y-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <Card key={i}>
              <CardContent className="pt-6">
                <Skeleton className="h-20 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">
          Validation History
        </h1>
        <p className="mt-1 text-gray-600">
          Recent validation activity and changes
        </p>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">{stats?.total_skills || 0}</div>
            <p className="text-xs text-gray-500">Total Skills</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-green-600">{stats?.validated || 0}</div>
            <p className="text-xs text-gray-500">Validated</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-blue-600">
              {stats?.validation_rate || 0}%
            </div>
            <p className="text-xs text-gray-500">Validation Rate</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">{stats?.total_categories || 0}</div>
            <p className="text-xs text-gray-500">Categories</p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          {!stats?.recent_activity || stats.recent_activity.length === 0 ? (
            <div className="text-center py-12">
              <Clock className="h-12 w-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">No recent activity</p>
            </div>
          ) : (
            <div className="space-y-4">
              {stats.recent_activity.map((activity, index) => (
                <div
                  key={index}
                  className="flex items-start space-x-4 p-4 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
                >
                  {/* Icon */}
                  <div className="flex-shrink-0 mt-1">
                    {getActionIcon(activity.action)}
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-1">
                      {getActionBadge(activity.action)}
                      <span className="text-sm text-gray-500">
                        by {activity.validator_user || 'system'}
                      </span>
                    </div>

                    <div className="space-y-1">
                      <p className="text-sm font-medium text-gray-900">
                        Skill ID: {activity.skill_id}
                      </p>

                      {/* Category Change */}
                      {activity.old_category_id && activity.new_category_id && (
                        <p className="text-sm text-gray-600">
                          Category changed from ID {activity.old_category_id} to ID {activity.new_category_id}
                        </p>
                      )}

                      {/* Status Change */}
                      {activity.old_status && activity.new_status && (
                        <p className="text-sm text-gray-600">
                          Status: {activity.old_status} → {activity.new_status}
                        </p>
                      )}

                      {/* Notes */}
                      {activity.notes && (
                        <p className="text-sm text-gray-500 italic">
                          "{activity.notes}"
                        </p>
                      )}
                    </div>

                    {/* Timestamp */}
                    <p className="text-xs text-gray-400 mt-2">
                      {formatDate(activity.created_at)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Queue Progress */}
      <Card>
        <CardHeader>
          <CardTitle>Queue Progress</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Progress Bar */}
            <div>
              <div className="flex justify-between text-sm text-gray-600 mb-2">
                <span>Completion Progress</span>
                <span>
                  {stats?.queue_completed || 0} / {stats?.total_queue_items || 0}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-blue-600 h-3 rounded-full transition-all"
                  style={{
                    width: `${
                      stats?.total_queue_items > 0
                        ? (stats.queue_completed / stats.total_queue_items) * 100
                        : 0
                    }%`,
                  }}
                />
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-yellow-600">
                  {stats?.queue_pending || 0}
                </div>
                <p className="text-xs text-gray-500">Pending</p>
              </div>
              <div>
                <div className="text-2xl font-bold text-green-600">
                  {stats?.queue_completed || 0}
                </div>
                <p className="text-xs text-gray-500">Completed</p>
              </div>
              <div>
                <div className="text-2xl font-bold text-blue-600">
                  {stats?.total_queue_items > 0
                    ? Math.round((stats.queue_completed / stats.total_queue_items) * 100)
                    : 0}%
                </div>
                <p className="text-xs text-gray-500">Complete</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}