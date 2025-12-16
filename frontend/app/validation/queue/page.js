// Location: frontend/app/validation/queue/page.js
/**
 * Validation Queue Page
 * Module #5: Skill Validation System
 * 
 * Main page for reviewing and validating skills
 * 
 * Author: Herlambang Haryo Putro
 * Date: 2025-12-16
 */

'use client'

import { useEffect, useState } from 'react'
import { validationApi, categoriesApi, handleApiError } from '@/lib/api'
import SkillCard from '@/components/validation/SkillCard'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { 
  Search, 
  Filter, 
  RefreshCw,
  ArrowLeft,
  ArrowRight,
  Zap
} from 'lucide-react'
import toast from 'react-hot-toast'

export default function ValidationQueuePage() {
  const [queue, setQueue] = useState([])
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [processing, setProcessing] = useState(false)
  
  // Filters
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('pending')
  const [categoryFilter, setCategoryFilter] = useState('all')
  const [page, setPage] = useState(0)
  const [pageSize] = useState(10)
  
  // Stats
  const [stats, setStats] = useState({
    total: 0,
    pending: 0,
    completed: 0,
    in_progress: 0,
    skipped: 0
  })

  useEffect(() => {
    loadCategories()
  }, [])

  useEffect(() => {
    loadQueue()
  }, [page, statusFilter, categoryFilter, search])

  const loadCategories = async () => {
    try {
      const response = await categoriesApi.getCategories(true)
      setCategories(response.data.categories)
    } catch (error) {
      const apiError = handleApiError(error)
      toast.error(apiError.message)
    }
  }

  const loadQueue = async () => {
    setLoading(true)
    try {
      const params = {
        skip: page * pageSize,
        limit: pageSize,
        sort_by: 'priority',
        sort_order: 'desc'
      }

      if (statusFilter) params.status = statusFilter
      if (categoryFilter && categoryFilter !== 'all') params.category_id = parseInt(categoryFilter)
      if (search) params.search = search

      const response = await validationApi.getQueue(params)
      
      setQueue(response.data.items)
      setStats({
        total: response.data.total,
        pending: response.data.pending,
        completed: response.data.completed,
        in_progress: response.data.in_progress,
        skipped: response.data.skipped
      })
    } catch (error) {
      const apiError = handleApiError(error)
      toast.error(apiError.message)
    } finally {
      setLoading(false)
    }
  }

  const handleApprove = async (queueId, categoryId) => {
    setProcessing(true)
    try {
      const response = await validationApi.validateSkill(queueId, {
        action: 'approve',
        category_id: categoryId,
        validator_user: 'frontend_user'
      })

      if (response.data.success) {
        toast.success(`✅ ${response.data.message}`)
        loadQueue() // Reload queue
      }
    } catch (error) {
      const apiError = handleApiError(error)
      toast.error(apiError.message)
    } finally {
      setProcessing(false)
    }
  }

  const handleReject = async (queueId) => {
    setProcessing(true)
    try {
      const response = await validationApi.validateSkill(queueId, {
        action: 'reject',
        validator_user: 'frontend_user'
      })

      if (response.data.success) {
        toast.success(`❌ ${response.data.message}`)
        loadQueue()
      }
    } catch (error) {
      const apiError = handleApiError(error)
      toast.error(apiError.message)
    } finally {
      setProcessing(false)
    }
  }

  const handleSkip = async (queueId) => {
    setProcessing(true)
    try {
      const response = await validationApi.validateSkill(queueId, {
        action: 'skip',
        validator_user: 'frontend_user'
      })

      if (response.data.success) {
        toast.success(`⏭️ ${response.data.message}`)
        loadQueue()
      }
    } catch (error) {
      const apiError = handleApiError(error)
      toast.error(apiError.message)
    } finally {
      setProcessing(false)
    }
  }

  const handleNextItem = async () => {
    setLoading(true)
    try {
      const response = await validationApi.getNextItem('frontend_user')
      
      // Load queue at specific item
      setQueue([response.data])
      toast.success('Loaded next item to review')
    } catch (error) {
      const apiError = handleApiError(error)
      toast.error(apiError.message)
    } finally {
      setLoading(false)
    }
  }

  const totalPages = Math.ceil(stats.total / pageSize)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold ">
            Validation Queue
          </h1>
          <p className="mt-1 text-gray-600">
            Review and categorize skills
          </p>
        </div>
        <Button onClick={handleNextItem} disabled={loading}>
          <Zap className="h-4 w-4 mr-2" />
          Quick Review
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">{stats.total}</div>
            <p className="text-xs text-gray-500">Total</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-yellow-600">{stats.pending}</div>
            <p className="text-xs text-gray-500">Pending</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-blue-600">{stats.in_progress}</div>
            <p className="text-xs text-gray-500">In Progress</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-green-600">{stats.completed}</div>
            <p className="text-xs text-gray-500">Completed</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-gray-600">{stats.skipped}</div>
            <p className="text-xs text-gray-500">Skipped</p>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Search */}
            <div className="md:col-span-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search skills..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            {/* Status Filter */}
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="in_progress">In Progress</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="skipped">Skipped</SelectItem>
              </SelectContent>
            </Select>

            {/* Category Filter */}
            <Select value={categoryFilter} onValueChange={setCategoryFilter}>
              <SelectTrigger>
                <SelectValue placeholder="All Categories" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Categories</SelectItem>
                {categories.map((cat) => (
                  <SelectItem key={cat.id} value={cat.id.toString()}>
                    {cat.icon} {cat.display_name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Active Filters */}
          {(search || (categoryFilter && categoryFilter !== 'all')) && (
            <div className="mt-4 flex items-center space-x-2">
              <span className="text-sm text-gray-500">Active filters:</span>
              {search && (
                <Badge variant="secondary">
                  Search: {search}
                </Badge>
              )}
              {categoryFilter && categoryFilter !== 'all' && (
                <Badge variant="secondary">
                  Category: {categories.find(c => c.id.toString() === categoryFilter)?.display_name}
                </Badge>
              )}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  setSearch('')
                  setCategoryFilter('all')
                }}
              >
                Clear all
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Skills List */}
      {loading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <Card key={i}>
              <CardContent className="pt-6">
                <Skeleton className="h-32 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : queue.length === 0 ? (
        <Card>
          <CardContent className="pt-6 text-center py-12">
            <p className="text-gray-500">No skills found matching your filters</p>
            <Button 
              variant="link" 
              onClick={() => {
                setSearch('')
                setCategoryFilter('all')
                setStatusFilter('pending')
              }}
            >
              Clear filters
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {queue.map((skill) => (
            <SkillCard
              key={skill.id}
              skill={skill}
              categories={categories}
              onApprove={handleApprove}
              onReject={handleReject}
              onSkip={handleSkip}
              isProcessing={processing}
            />
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-gray-500">
            Page {page + 1} of {totalPages}
          </p>
          <div className="flex space-x-2">
            <Button
              variant="outline"
              onClick={() => setPage(page - 1)}
              disabled={page === 0}
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Previous
            </Button>
            <Button
              variant="outline"
              onClick={() => setPage(page + 1)}
              disabled={page >= totalPages - 1}
            >
              Next
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}