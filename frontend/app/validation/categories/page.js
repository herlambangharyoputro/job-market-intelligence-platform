// Location: frontend/app/validation/categories/page.js
/**
 * Categories Management Page
 * Module #5: Skill Validation System
 * 
 * Create, Read, Update skill categories
 * 
 * Author: Herlambang Haryo Putro
 * Date: 2025-12-16
 */

'use client'

import { useEffect, useState } from 'react'
import { categoriesApi, handleApiError } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
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
import { Label } from '@/components/ui/label'
import { Skeleton } from '@/components/ui/skeleton'
import { Plus, Edit, Trash2, Eye } from 'lucide-react'
import toast from 'react-hot-toast'

export default function CategoriesPage() {
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [showEditDialog, setShowEditDialog] = useState(false)
  const [showDetailDialog, setShowDetailDialog] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState(null)
  const [categorySkills, setCategorySkills] = useState([])

  // Form state
  const [formData, setFormData] = useState({
    category_name: '',
    display_name: '',
    description: '',
    icon: '',
    color: '#3B82F6',
    sort_order: 0,
    is_active: true
  })

  useEffect(() => {
    loadCategories()
  }, [])

  const loadCategories = async () => {
    setLoading(true)
    try {
      const response = await categoriesApi.getCategories()
      setCategories(response.data.categories)
    } catch (error) {
      const apiError = handleApiError(error)
      toast.error(apiError.message)
    } finally {
      setLoading(false)
    }
  }

  const loadCategorySkills = async (categoryId) => {
    try {
      const response = await categoriesApi.getCategorySkills(categoryId, { limit: 100 })
      setCategorySkills(response.data.skills)
    } catch (error) {
      const apiError = handleApiError(error)
      toast.error(apiError.message)
    }
  }

  const resetForm = () => {
    setFormData({
      category_name: '',
      display_name: '',
      description: '',
      icon: '',
      color: '#3B82F6',
      sort_order: 0,
      is_active: true
    })
  }

  const handleCreate = async () => {
    try {
      await categoriesApi.createCategory(formData)
      toast.success('✅ Category created successfully')
      setShowCreateDialog(false)
      resetForm()
      loadCategories()
    } catch (error) {
      const apiError = handleApiError(error)
      toast.error(apiError.message)
    }
  }

  const handleUpdate = async () => {
    try {
      await categoriesApi.updateCategory(selectedCategory.id, formData)
      toast.success('✅ Category updated successfully')
      setShowEditDialog(false)
      resetForm()
      setSelectedCategory(null)
      loadCategories()
    } catch (error) {
      const apiError = handleApiError(error)
      toast.error(apiError.message)
    }
  }

  const openEditDialog = (category) => {
    setSelectedCategory(category)
    setFormData({
      category_name: category.category_name,
      display_name: category.display_name || '',
      description: category.description || '',
      icon: category.icon || '',
      color: category.color || '#3B82F6',
      sort_order: category.sort_order || 0,
      is_active: category.is_active
    })
    setShowEditDialog(true)
  }

  const openDetailDialog = async (category) => {
    setSelectedCategory(category)
    setShowDetailDialog(true)
    await loadCategorySkills(category.id)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">
            Skill Categories
          </h1>
          <p className="mt-1 text-gray-600">
            Manage skill categorization taxonomy
          </p>
        </div>
        <Button onClick={() => setShowCreateDialog(true)}>
          <Plus className="h-4 w-4 mr-2" />
          New Category
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">{categories.length}</div>
            <p className="text-xs text-gray-500">Total Categories</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-green-600">
              {categories.filter(c => c.is_active).length}
            </div>
            <p className="text-xs text-gray-500">Active</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-gray-600">
              {categories.filter(c => !c.is_active).length}
            </div>
            <p className="text-xs text-gray-500">Inactive</p>
          </CardContent>
        </Card>
      </div>

      {/* Categories Table */}
      <Card>
        <CardHeader>
          <CardTitle>Categories List</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-2">
              {[1, 2, 3, 4, 5].map((i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : (
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-[50px]">Icon</TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Display Name</TableHead>
                    <TableHead className="text-center">Order</TableHead>
                    <TableHead className="text-center">Status</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {categories.map((category) => (
                    <TableRow key={category.id}>
                      <TableCell className="text-2xl">{category.icon}</TableCell>
                      <TableCell>
                        <code className="text-sm bg-gray-100 px-2 py-1 rounded">
                          {category.category_name}
                        </code>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center space-x-2">
                          <div
                            className="w-3 h-3 rounded-full"
                            style={{ backgroundColor: category.color }}
                          />
                          <span className="font-medium">{category.display_name}</span>
                        </div>
                      </TableCell>
                      <TableCell className="text-center">
                        <Badge variant="outline">{category.sort_order}</Badge>
                      </TableCell>
                      <TableCell className="text-center">
                        {category.is_active ? (
                          <Badge variant="outline" className="border-green-300 text-green-700">
                            Active
                          </Badge>
                        ) : (
                          <Badge variant="outline" className="border-gray-300 text-gray-700">
                            Inactive
                          </Badge>
                        )}
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end space-x-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => openDetailDialog(category)}
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => openEditDialog(category)}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Create Category Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Create New Category</DialogTitle>
            <DialogDescription>
              Add a new skill category to the taxonomy
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="category_name">Category Name (internal) *</Label>
              <Input
                id="category_name"
                placeholder="e.g., programming_language"
                value={formData.category_name}
                onChange={(e) => setFormData({ ...formData, category_name: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="display_name">Display Name *</Label>
              <Input
                id="display_name"
                placeholder="e.g., Programming Languages"
                value={formData.display_name}
                onChange={(e) => setFormData({ ...formData, display_name: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="icon">Icon (emoji)</Label>
              <Input
                id="icon"
                placeholder="e.g., 💻"
                value={formData.icon}
                onChange={(e) => setFormData({ ...formData, icon: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="color">Color</Label>
              <Input
                id="color"
                type="color"
                value={formData.color}
                onChange={(e) => setFormData({ ...formData, color: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="sort_order">Sort Order</Label>
              <Input
                id="sort_order"
                type="number"
                value={formData.sort_order}
                onChange={(e) => setFormData({ ...formData, sort_order: parseInt(e.target.value) })}
              />
            </div>
            <div>
              <Label htmlFor="description">Description</Label>
              <Input
                id="description"
                placeholder="Category description..."
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreate}>Create</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Category Dialog */}
      <Dialog open={showEditDialog} onOpenChange={setShowEditDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Edit Category</DialogTitle>
            <DialogDescription>
              Update category information
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="edit_display_name">Display Name *</Label>
              <Input
                id="edit_display_name"
                value={formData.display_name}
                onChange={(e) => setFormData({ ...formData, display_name: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="edit_icon">Icon</Label>
              <Input
                id="edit_icon"
                value={formData.icon}
                onChange={(e) => setFormData({ ...formData, icon: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="edit_color">Color</Label>
              <Input
                id="edit_color"
                type="color"
                value={formData.color}
                onChange={(e) => setFormData({ ...formData, color: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="edit_sort_order">Sort Order</Label>
              <Input
                id="edit_sort_order"
                type="number"
                value={formData.sort_order}
                onChange={(e) => setFormData({ ...formData, sort_order: parseInt(e.target.value) })}
              />
            </div>
            <div>
              <Label htmlFor="edit_description">Description</Label>
              <Input
                id="edit_description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              />
            </div>
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="edit_is_active"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                className="w-4 h-4"
              />
              <Label htmlFor="edit_is_active">Active</Label>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowEditDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleUpdate}>Update</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Detail Dialog */}
      <Dialog open={showDetailDialog} onOpenChange={setShowDetailDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Category Details</DialogTitle>
            <DialogDescription>
              View category information and associated skills
            </DialogDescription>
          </DialogHeader>
          {selectedCategory && (
            <div className="space-y-4">
              <div className="flex items-center space-x-4">
                <div className="text-4xl">{selectedCategory.icon}</div>
                <div>
                  <h3 className="text-xl font-bold">{selectedCategory.display_name}</h3>
                  <code className="text-sm text-gray-500">{selectedCategory.category_name}</code>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-gray-500">Color</Label>
                  <div className="flex items-center space-x-2 mt-1">
                    <div
                      className="w-6 h-6 rounded border"
                      style={{ backgroundColor: selectedCategory.color }}
                    />
                    <span className="text-sm">{selectedCategory.color}</span>
                  </div>
                </div>
                <div>
                  <Label className="text-gray-500">Sort Order</Label>
                  <p className="mt-1">{selectedCategory.sort_order}</p>
                </div>
              </div>

              {selectedCategory.description && (
                <div>
                  <Label className="text-gray-500">Description</Label>
                  <p className="mt-1 text-sm">{selectedCategory.description}</p>
                </div>
              )}

              <div>
                <Label className="text-gray-500">Skills in Category ({categorySkills.length})</Label>
                <div className="mt-2 max-h-60 overflow-y-auto border rounded p-2">
                  {categorySkills.length === 0 ? (
                    <p className="text-sm text-gray-500 text-center py-4">No skills yet</p>
                  ) : (
                    <div className="space-y-1">
                      {categorySkills.map((skill) => (
                        <div
                          key={skill.id}
                          className="flex items-center justify-between text-sm p-2 hover:bg-gray-50 rounded"
                        >
                          <span>{skill.skill_name}</span>
                          <Badge variant="secondary">{skill.usage_count}</Badge>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}