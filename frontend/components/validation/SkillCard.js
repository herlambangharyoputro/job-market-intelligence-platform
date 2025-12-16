// Location: frontend/components/validation/SkillCard.js
/**
 * SkillCard Component
 * Module #5: Skill Validation System
 * 
 * Card component for displaying skill with validation actions
 * 
 * Author: Herlambang Haryo Putro
 * Date: 2025-12-16
 */

'use client'

import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { CheckCircle2, XCircle, SkipForward, TrendingUp } from 'lucide-react'
import { useState } from 'react'

export default function SkillCard({ 
  skill, 
  categories, 
  onApprove, 
  onReject, 
  onSkip,
  isProcessing = false 
}) {
  const [selectedCategory, setSelectedCategory] = useState(
    skill.suggested_category_id?.toString() || ''
  )

  const handleApprove = () => {
    if (!selectedCategory) {
      alert('Please select a category first')
      return
    }
    onApprove(skill.id, parseInt(selectedCategory))
  }

  // Parse context sample
  const contextSamples = skill.context_sample 
    ? (typeof skill.context_sample === 'string' 
        ? JSON.parse(skill.context_sample) 
        : skill.context_sample)
    : []

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="space-y-1 flex-1">
            <h3 className="text-xl font-bold text-gray-900">
              {skill.skill_name}
            </h3>
            <div className="flex items-center space-x-2">
              <Badge variant="outline" className="text-xs">
                <TrendingUp className="h-3 w-3 mr-1" />
                {skill.source_count} occurrences
              </Badge>
              <Badge 
                variant="outline" 
                className={`text-xs ${
                  skill.priority >= 75 
                    ? 'border-red-300 text-red-700'
                    : skill.priority >= 50
                    ? 'border-yellow-300 text-yellow-700'
                    : 'border-blue-300 text-blue-700'
                }`}
              >
                Priority: {skill.priority}
              </Badge>
            </div>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Context Samples */}
        {contextSamples.length > 0 && (
          <div>
            <p className="text-sm font-medium text-gray-700 mb-2">
              Found in jobs:
            </p>
            <div className="space-y-1">
              {contextSamples.slice(0, 3).map((context, index) => (
                <div 
                  key={index}
                  className="text-sm text-gray-600 bg-gray-50 px-3 py-2 rounded border border-gray-200"
                >
                  "{context.original}"
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Category Selection */}
        <div>
          <label className="text-sm font-medium text-gray-700 mb-2 block">
            Select Category *
          </label>
          <Select 
            value={selectedCategory} 
            onValueChange={setSelectedCategory}
            disabled={isProcessing}
          >
            <SelectTrigger>
              <SelectValue placeholder="Choose a category..." />
            </SelectTrigger>
            <SelectContent>
              {categories.map((category) => (
                <SelectItem 
                  key={category.id} 
                  value={category.id.toString()}
                >
                  <div className="flex items-center space-x-2">
                    <span>{category.icon}</span>
                    <span>{category.display_name}</span>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </CardContent>

      <CardFooter className="flex space-x-2">
        {/* Approve */}
        <Button
          onClick={handleApprove}
          disabled={isProcessing || !selectedCategory}
          className="flex-1 bg-green-600 hover:bg-green-700"
        >
          <CheckCircle2 className="h-4 w-4 mr-2" />
          Approve
        </Button>

        {/* Reject */}
        <Button
          onClick={() => onReject(skill.id)}
          disabled={isProcessing}
          variant="destructive"
          className="flex-1"
        >
          <XCircle className="h-4 w-4 mr-2" />
          Reject
        </Button>

        {/* Skip */}
        <Button
          onClick={() => onSkip(skill.id)}
          disabled={isProcessing}
          variant="outline"
        >
          <SkipForward className="h-4 w-4" />
        </Button>
      </CardFooter>
    </Card>
  )
}