// Location: frontend/app/validation/dictionary/page.js
/**
 * Skills Dictionary Page
 * Module #5: Skill Validation System
 * 
 * Browse and manage validated skills
 * 
 * Author: Herlambang Haryo Putro
 * Date: 2025-12-16
 */

'use client'

import { useEffect, useState } from 'react'
import { skillsApi, categoriesApi, handleApiError } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { 
  Search, 
  CheckCircle2, 
  XCircle,
  TrendingUp,
  ArrowLeft,
  ArrowRight,
  Eye,
  Download
} from 'lucide-react'
import toast from 'react-hot-toast'

export default function DictionaryPage() {
  const [skills, setSkills] = useState([])
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedSkill, setSelectedSkill] = useState(null)
  const [showDetailDialog, setShowDetailDialog] = useState(false)

  // Filters
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('approved')
  const [categoryFilter, setCategoryFilter] = useState('all')
  const [page, setPage] = useState(0)
  const [pageSize] = useState(50)

  // Stats
  const [stats, setStats] = useState({
    total: 0,
    validated: 0,
    pending: 0,
    rejected: 0
  })

  useEffect(() => {
    loadCategories()
  }, [])

  useEffect(() => {
    loadSkills()
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

  const loadSkills = async () => {
    setLoading(true)
    try {
      const params = {
        skip: page * pageSize,
        limit: pageSize,
      }

      if (statusFilter !== 'all') params.status = statusFilter
      if (categoryFilter !== 'all') params.category_id = parseInt(categoryFilter)
      if (search) params.search = search

      const response = await skillsApi.getSkills(params)

      setSkills(response.data.skills)
      setStats({
        total: response.data.total,
        validated: response.data.validated,
        pending: response.data.pending,
        rejected: response.data.rejected
      })
    } catch (error) {
      const apiError = handleApiError(error)
      toast.error(apiError.message)
    } finally {
      setLoading(false)
    }
  }

  const viewSkillDetails = async (skillId) => {
    try {
      const response = await skillsApi.getSkill(skillId)
      setSelectedSkill(response.data)
      setShowDetailDialog(true)
    } catch (error) {
      const apiError = handleApiError(error)
      toast.error(apiError.message)
    }
  }

  const exportToCSV = () => {
    if (skills.length === 0) {
      toast.error('No skills to export')
      return
    }

    // Create CSV content
    const headers = ['ID', 'Skill Name', 'Category', 'Status', 'Usage Count', 'Validated']
    const rows = skills.map(skill => [
      skill.id,
      skill.skill_name,
      getCategoryName(skill.category_id),
      skill.validation_status,
      skill.usage_count,
      skill.is_validated ? 'Yes' : 'No'
    ])

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.join(','))
    ].join('\n')

    // Download
    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `skills_dictionary_${new Date().toISOString().split('T')[0]}.csv`
    a.click()
    window.URL.revokeObjectURL(url)

    toast.success('Exported to CSV')
  }

  const getCategoryName = (categoryId) => {
    const category = categories.find(c => c.id === categoryId)
    return category ? category.display_name : 'Uncategorized'
  }

  const getCategoryIcon = (categoryId) => {
    const category = categories.find(c => c.id === categoryId)
    return category?.icon || '❓'
  }

  const totalPages = Math.ceil(stats.total / pageSize)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">
            Skills Dictionary
          </h1>
          <p className="mt-1 text-gray-600">
            Browse validated skills
          </p>
        </div>
        <Button onClick={exportToCSV} variant="outline">
          <Download className="h-4 w-4 mr-2" />
          Export CSV
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">{stats.total}</div>
            <p className="text-xs text-gray-500">Total Skills</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-green-600">{stats.validated}</div>
            <p className="text-xs text-gray-500">Validated</p>
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
            <div className="text-2xl font-bold text-red-600">{stats.rejected}</div>
            <p className="text-xs text-gray-500">Rejected</p>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Search */}
            <div className="md:col-span-1">
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
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="approved">Approved</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="rejected">Rejected</SelectItem>
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
        </CardContent>
      </Card>

      {/* Skills Table */}
      <Card>
        <CardHeader>
          <CardTitle>Skills ({stats.total})</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-2">
              {[1, 2, 3, 4, 5].map((i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : skills.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500">No skills found</p>
              <Button
                variant="link"
                onClick={() => {
                  setSearch('')
                  setCategoryFilter('all')
                  setStatusFilter('approved')
                }}
              >
                Clear filters
              </Button>
            </div>
          ) : (
            <>
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-[50px]">ID</TableHead>
                      <TableHead>Skill Name</TableHead>
                      <TableHead>Category</TableHead>
                      <TableHead className="text-center">Status</TableHead>
                      <TableHead className="text-right">Usage</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {skills.map((skill) => (
                      <TableRow key={skill.id}>
                        <TableCell className="font-medium">{skill.id}</TableCell>
                        <TableCell>
                          <div className="font-medium">{skill.skill_name}</div>
                          <div className="text-xs text-gray-500">
                            {skill.normalized_name}
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center space-x-2">
                            <span>{getCategoryIcon(skill.category_id)}</span>
                            <span className="text-sm">
                              {getCategoryName(skill.category_id)}
                            </span>
                          </div>
                        </TableCell>
                        <TableCell className="text-center">
                          {skill.validation_status === 'approved' && (
                            <Badge variant="outline" className="border-green-300 text-green-700">
                              <CheckCircle2 className="h-3 w-3 mr-1" />
                              Approved
                            </Badge>
                          )}
                          {skill.validation_status === 'rejected' && (
                            <Badge variant="outline" className="border-red-300 text-red-700">
                              <XCircle className="h-3 w-3 mr-1" />
                              Rejected
                            </Badge>
                          )}
                          {skill.validation_status === 'pending' && (
                            <Badge variant="outline" className="border-yellow-300 text-yellow-700">
                              Pending
                            </Badge>
                          )}
                        </TableCell>
                        <TableCell className="text-right">
                          <Badge variant="secondary">
                            <TrendingUp className="h-3 w-3 mr-1" />
                            {skill.usage_count}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => viewSkillDetails(skill.id)}
                          >
                            <Eye className="h-4 w-4" />
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
                    Page {page + 1} of {totalPages}
                  </p>
                  <div className="flex space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage(page - 1)}
                      disabled={page === 0}
                    >
                      <ArrowLeft className="h-4 w-4 mr-2" />
                      Previous
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage(page + 1)}
                      disabled={page >= totalPages - 1}
                    >
                      Next
                      <ArrowRight className="h-4 w-4 ml-2" />
                    </Button>
                  </div>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>

      {/* Skill Detail Dialog */}
      <Dialog open={showDetailDialog} onOpenChange={setShowDetailDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Skill Details</DialogTitle>
            <DialogDescription>
              Detailed information about this skill
            </DialogDescription>
          </DialogHeader>
          {selectedSkill && (
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-500">Skill Name</label>
                <p className="text-lg font-semibold">{selectedSkill.skill_name}</p>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-500">Normalized</label>
                <p>{selectedSkill.normalized_name}</p>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-500">Category</label>
                <div className="flex items-center space-x-2 mt-1">
                  <span>{selectedSkill.category_icon}</span>
                  <span>{selectedSkill.category_display_name || 'Uncategorized'}</span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">Status</label>
                  <Badge className="mt-1">
                    {selectedSkill.validation_status}
                  </Badge>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Usage Count</label>
                  <p className="text-lg font-semibold">{selectedSkill.usage_count}</p>
                </div>
              </div>

              {selectedSkill.description && (
                <div>
                  <label className="text-sm font-medium text-gray-500">Description</label>
                  <p className="text-sm text-gray-700 mt-1">{selectedSkill.description}</p>
                </div>
              )}

              <div className="grid grid-cols-2 gap-4 text-xs text-gray-500">
                <div>
                  <label>Created</label>
                  <p>{new Date(selectedSkill.created_at).toLocaleString()}</p>
                </div>
                <div>
                  <label>Updated</label>
                  <p>{new Date(selectedSkill.updated_at).toLocaleString()}</p>
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}