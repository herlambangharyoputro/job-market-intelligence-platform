// Location: frontend/app/page.js
/**
 * Dashboard Page
 * Module #5: Skill Validation System
 * 
 * Main dashboard with validation statistics
 * 
 * Author: Herlambang Haryo Putro
 * Date: 2025-12-16
 */

'use client'

import { useEffect, useState } from 'react'
import { validationApi } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import Link from 'next/link'
import { 
  CheckCircle2, 
  Clock, 
  XCircle, 
  ListChecks, 
  TrendingUp,
  ArrowRight
} from 'lucide-react'
import toast from 'react-hot-toast'

export default function DashboardPage() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      const response = await validationApi.getStats()
      setStats(response.data)
    } catch (error) {
      toast.error('Failed to load statistics')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <DashboardSkeleton />
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-foreground">
          Skills Validation Dashboard
        </h1>
        <p className="mt-2 text-muted-foreground">
          Supervised skill curation for job market intelligence
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Total Skills */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Skills
            </CardTitle>
            <ListChecks className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_skills || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">
              In dictionary
            </p>
          </CardContent>
        </Card>

        {/* Validated */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Validated
            </CardTitle>
            <CheckCircle2 className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600 dark:text-green-400">
              {stats?.validated || 0}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {stats?.validation_rate || 0}% validation rate
            </p>
          </CardContent>
        </Card>

        {/* Pending */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Queue Pending
            </CardTitle>
            <Clock className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
              {stats?.queue_pending || 0}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Awaiting review
            </p>
          </CardContent>
        </Card>

        {/* Rejected */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Rejected
            </CardTitle>
            <XCircle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600 dark:text-red-400">
              {stats?.rejected || 0}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Invalid skills
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Queue Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Queue Overview */}
        <Card>
          <CardHeader>
            <CardTitle>Validation Queue</CardTitle>
            <CardDescription>
              Current queue status and progress
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Total Items</span>
              <span className="font-semibold">{stats?.total_queue_items || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Completed</span>
              <Badge variant="outline" className="text-green-600 dark:text-green-400">
                {stats?.queue_completed || 0}
              </Badge>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Pending</span>
              <Badge variant="outline" className="text-yellow-600 dark:text-yellow-400">
                {stats?.queue_pending || 0}
              </Badge>
            </div>
            
            {/* Progress Bar */}
            <div className="pt-4">
              <div className="flex justify-between text-xs text-muted-foreground mb-2">
                <span>Progress</span>
                <span>
                  {stats?.total_queue_items > 0
                    ? Math.round((stats?.queue_completed / stats?.total_queue_items) * 100)
                    : 0}%
                </span>
              </div>
              <div className="w-full bg-muted rounded-full h-2">
                <div
                  className="bg-primary h-2 rounded-full transition-all"
                  style={{
                    width: `${
                      stats?.total_queue_items > 0
                        ? (stats?.queue_completed / stats?.total_queue_items) * 100
                        : 0
                    }%`,
                  }}
                />
              </div>
            </div>

            <Link href="/validation/queue">
              <Button className="w-full mt-4">
                Start Reviewing
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </CardContent>
        </Card>

        {/* Categories Overview */}
        <Card>
          <CardHeader>
            <CardTitle>Categories</CardTitle>
            <CardDescription>
              Skill categorization overview
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Total Categories</span>
              <span className="font-semibold">{stats?.total_categories || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Active</span>
              <Badge variant="outline" className="text-primary">
                {stats?.active_categories || 0}
              </Badge>
            </div>

            <div className="pt-4 space-y-2">
              <Link href="/validation/dictionary">
                <Button variant="outline" className="w-full">
                  Browse Dictionary
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      {stats?.recent_activity && stats.recent_activity.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Latest validation actions</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {stats.recent_activity.slice(0, 5).map((activity, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between py-2 border-b border-border last:border-0"
                >
                  <div className="flex items-center space-x-3">
                    {activity.action === 'approved' && (
                      <CheckCircle2 className="h-4 w-4 text-green-500" />
                    )}
                    {activity.action === 'rejected' && (
                      <XCircle className="h-4 w-4 text-red-500" />
                    )}
                    <div>
                      <p className="text-sm font-medium">
                        Skill {activity.action}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        by {activity.validator_user || 'system'}
                      </p>
                    </div>
                  </div>
                  <Badge variant="outline">
                    {new Date(activity.created_at).toLocaleDateString()}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

function DashboardSkeleton() {
  return (
    <div className="space-y-8">
      <div>
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-4 w-96 mt-2" />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i}>
            <CardHeader>
              <Skeleton className="h-4 w-24" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-8 w-16" />
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}