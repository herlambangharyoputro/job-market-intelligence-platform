// Location: frontend/app/validation/queue-overview/page.js
/**
 * Queue Overview Page - FIXED
 * Module #5: Skill Validation System
 * 
 * Overview of validation queue with pagination support
 * 
 * Author: Herlambang Haryo Putro
 * Date: 2025-12-16
 */

'use client'

import { useEffect, useState } from 'react'
import { validationApi } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { 
  RefreshCw, 
  Edit,
  Clock,
  CheckCircle,
  XCircle,
  SkipForward,
  TrendingUp,
  Search,
  ChevronLeft,
  ChevronRight
} from 'lucide-react'
import toast from 'react-hot-toast'

export default function QueueOverviewPage() {
  const [pendingSkills, setPendingSkills] = useState([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({
    total_queue_items: 0,
    queue_pending: 0,
    queue_in_progress: 0,
    queue_completed: 0,
    queue_skipped: 0
  })
  const [showEditDialog, setShowEditDialog] = useState(false)
  const [selectedItem, setSelectedItem] = useState(null)
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(0)
  const pageSize = 100 // Backend max limit

  // Edit form
  const [editForm, setEditForm] = useState({
    priority: 0,
    status: 'pending'
  })

  useEffect(() => {
    loadStats()
  }, [])

  useEffect(() => {
    loadQueue()
  }, [page])

  const loadStats = async () => {
    try {
      const statsResponse = await validationApi.getStats()
      const statsData = statsResponse.data
      
      setStats({
        total_queue_items: statsData.total_queue_items || 0,
        queue_pending: statsData.queue_pending || 0,
        queue_in_progress: statsData.queue_in_progress || 0,
        queue_completed: statsData.queue_completed || 0,
        queue_skipped: statsData.queue_skipped || 0
      })
    } catch (error) {
      console.error('Stats error:', error)
      toast.error('Failed to load statistics')
    }
  }

  const loadQueue = async () => {
    setLoading(true)
    
    try {
      // Get pending skills with pagination (max 100 per request)
      const queueResponse = await validationApi.getQueue({
        status: 'pending',
        skip: page * pageSize,
        limit: pageSize,
        sort_by: 'priority',
        sort_order: 'desc'
      })
      
      const items = queueResponse.data.items || []
      setPendingSkills(items)
      
    } catch (error) {
      console.error('Queue error:', error)
      toast.error('Failed to load queue')
      setPendingSkills([])
    } finally {
      setLoading(false)
    }
  }

  const handleResetStuck = async () => {
    try {
      const response = await validationApi.resetStuckItems(24)
      const count = response.data?.count || 0
      toast.success(`✅ Reset ${count} stuck items`)
      loadStats()
      loadQueue()
    } catch (error) {
      console.error('Reset error:', error)
      toast.error('Failed to reset stuck items')
    }
  }

  const handleReprioritize = async () => {
    try {
      const response = await validationApi.reprioritize()
      const count = response.data?.count || 0
      toast.success(`✅ Reprioritized ${count} items`)
      loadStats()
      loadQueue()
    } catch (error) {
      console.error('Reprioritize error:', error)
      toast.error('Failed to reprioritize')
    }
  }

  const openEditDialog = (item) => {
    setSelectedItem(item)
    setEditForm({
      priority: item.priority,
      status: item.status
    })
    setShowEditDialog(true)
  }

  const handleUpdate = () => {
    toast.info('Update feature - backend endpoint needed')
    setShowEditDialog(false)
  }

  // Filter skills by search
  const filteredSkills = pendingSkills.filter(skill =>
    skill.skill_name.toLowerCase().includes(search.toLowerCase())
  )

  // Calculate total pages
  const totalPages = Math.ceil(stats.queue_pending / pageSize)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">
            Queue Overview
          </h1>
          <p className="mt-1 text-gray-600">
            Manage validation queue and view pending skills
          </p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline" onClick={handleResetStuck} disabled={loading}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Reset Stuck
          </Button>
          <Button variant="outline" onClick={handleReprioritize} disabled={loading}>
            <TrendingUp className="h-4 w-4 mr-2" />
            Reprioritize
          </Button>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">{stats.total_queue_items}</div>
            <p className="text-xs text-gray-500">Total Items</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-yellow-600">
              {stats.queue_pending}
            </div>
            <p className="text-xs text-gray-500">Pending</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-blue-600">
              {stats.queue_in_progress}
            </div>
            <p className="text-xs text-gray-500">In Progress</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-green-600">
              {stats.queue_completed}
            </div>
            <p className="text-xs text-gray-500">Completed</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-gray-600">
              {stats.queue_skipped}
            </div>
            <p className="text-xs text-gray-500">Skipped</p>
          </CardContent>
        </Card>
      </div>

      {/* Progress Bar */}
      <Card>
        <CardHeader>
          <CardTitle>Completion Progress</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="flex justify-between text-sm text-gray-600">
              <span>Overall Progress</span>
              <span>
                {stats.queue_completed} / {stats.total_queue_items}
                {' '}({stats.total_queue_items > 0
                  ? Math.round((stats.queue_completed / stats.total_queue_items) * 100)
                  : 0}%)
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-4">
              <div
                className="bg-blue-600 h-4 rounded-full transition-all"
                style={{
                  width: `${
                    stats.total_queue_items > 0
                      ? (stats.queue_completed / stats.total_queue_items) * 100
                      : 0
                  }%`,
                }}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Pending Skills List */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>
              Pending Skills (Page {page + 1} of {totalPages || 1})
            </CardTitle>
            <div className="w-64">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search current page..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-2">
              {[1, 2, 3, 4, 5].map((i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : filteredSkills.length === 0 ? (
            <div className="text-center py-12">
              <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
              <p className="text-gray-500">
                {search ? 'No skills match your search on this page' : 'No pending skills on this page'}
              </p>
            </div>
          ) : (
            <>
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-[50px]">ID</TableHead>
                      <TableHead>Skill Name</TableHead>
                      <TableHead className="text-center">Source Count</TableHead>
                      <TableHead className="text-center">Priority</TableHead>
                      <TableHead className="text-center">Status</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredSkills.map((skill) => (
                      <TableRow key={skill.id}>
                        <TableCell className="font-medium">{skill.id}</TableCell>
                        <TableCell>
                          <div className="font-medium">{skill.skill_name}</div>
                          {skill.assigned_to && (
                            <div className="text-xs text-gray-500">
                              Assigned: {skill.assigned_to}
                            </div>
                          )}
                        </TableCell>
                        <TableCell className="text-center">
                          <Badge variant="secondary">
                            {skill.source_count}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-center">
                          <Badge
                            variant="outline"
                            className={
                              skill.priority >= 75
                                ? 'border-red-300 text-red-700'
                                : skill.priority >= 50
                                ? 'border-yellow-300 text-yellow-700'
                                : 'border-blue-300 text-blue-700'
                            }
                          >
                            {skill.priority}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-center">
                          <Badge variant="outline" className="border-yellow-300 text-yellow-700">
                            <Clock className="h-3 w-3 mr-1" />
                            Pending
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => openEditDialog(skill)}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-between mt-4">
                  <p className="text-sm text-gray-500">
                    Showing {filteredSkills.length} of {stats.queue_pending} pending skills
                  </p>
                  <div className="flex space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage(page - 1)}
                      disabled={page === 0 || loading}
                    >
                      <ChevronLeft className="h-4 w-4 mr-1" />
                      Previous
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage(page + 1)}
                      disabled={page >= totalPages - 1 || loading}
                    >
                      Next
                      <ChevronRight className="h-4 w-4 ml-1" />
                    </Button>
                  </div>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>

      {/* Edit Dialog */}
      <Dialog open={showEditDialog} onOpenChange={setShowEditDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Queue Item</DialogTitle>
            <DialogDescription>
              Update queue item priority and status
            </DialogDescription>
          </DialogHeader>
          {selectedItem && (
            <div className="space-y-4">
              <div>
                <Label className="text-gray-500">Skill Name</Label>
                <p className="font-semibold">{selectedItem.skill_name}</p>
              </div>

              <div>
                <Label htmlFor="priority">Priority</Label>
                <Input
                  id="priority"
                  type="number"
                  min="0"
                  max="100"
                  value={editForm.priority}
                  onChange={(e) =>
                    setEditForm({ ...editForm, priority: parseInt(e.target.value) || 0 })
                  }
                />
              </div>

              <div>
                <Label htmlFor="status">Status</Label>
                <Select
                  value={editForm.status}
                  onValueChange={(value) => setEditForm({ ...editForm, status: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="pending">Pending</SelectItem>
                    <SelectItem value="in_progress">In Progress</SelectItem>
                    <SelectItem value="completed">Completed</SelectItem>
                    <SelectItem value="skipped">Skipped</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded p-3">
                <p className="text-sm text-blue-800">
                  <strong>Note:</strong> Backend endpoint needed for update
                </p>
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowEditDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleUpdate}>Update</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}