'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getIssues, updateIssueStatus, getIssue } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet'
import { Label } from '@/components/ui/label'

export default function AdminPage() {
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [categoryFilter, setCategoryFilter] = useState<string>('')
  const [selectedIssue, setSelectedIssue] = useState<string | null>(null)
  const queryClient = useQueryClient()

  const { data: issues = [] } = useQuery({
    queryKey: ['issues', statusFilter, categoryFilter],
    queryFn: () => getIssues({ status: statusFilter || undefined, category: categoryFilter || undefined }),
  })

  const { data: issueDetails } = useQuery({
    queryKey: ['issue', selectedIssue],
    queryFn: () => selectedIssue ? getIssue(selectedIssue) : null,
    enabled: !!selectedIssue,
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) => updateIssueStatus(id, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['issues'] })
      queryClient.invalidateQueries({ queryKey: ['issue', selectedIssue] })
    },
  })

  const handleStatusChange = (status: string) => {
    if (selectedIssue) {
      updateMutation.mutate({ id: selectedIssue, status })
    }
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Admin Dashboard</h1>
      <div className="flex gap-4 mb-4">
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Filter by Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">All</SelectItem>
            <SelectItem value="open">Open</SelectItem>
            <SelectItem value="in_progress">In Progress</SelectItem>
            <SelectItem value="resolved">Resolved</SelectItem>
          </SelectContent>
        </Select>
        <Select value={categoryFilter} onValueChange={setCategoryFilter}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Filter by Category" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">All</SelectItem>
            <SelectItem value="pothole">Pothole</SelectItem>
            <SelectItem value="graffiti">Graffiti</SelectItem>
            {/* Add more */}
          </SelectContent>
        </Select>
      </div>
      <div className="space-y-2">
        {issues.map((issue) => (
          <Card key={issue.id} className="cursor-pointer" onClick={() => setSelectedIssue(issue.id)}>
            <CardContent className="p-4">
              <div className="flex justify-between items-center">
                <div>
                  <span className="font-semibold">#{issue.id}</span> - {issue.category || 'Uncategorized'} - {issue.description.slice(0, 50)}...
                </div>
                <div className="flex gap-2">
                  <Badge variant={issue.status === 'open' ? 'destructive' : 'default'}>{issue.status}</Badge>
                  <Badge variant="outline">{issue.priority || 'Unknown'}</Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Sheet open={!!selectedIssue} onOpenChange={() => setSelectedIssue(null)}>
        <SheetContent>
          <SheetHeader>
            <SheetTitle>Issue #{selectedIssue}</SheetTitle>
          </SheetHeader>
          {issueDetails && (
            <div className="space-y-4 mt-4">
              <p><strong>Description:</strong> {issueDetails.description}</p>
              <p><strong>Status:</strong> {issueDetails.status}</p>
              <p><strong>Category:</strong> {issueDetails.category}</p>
              <p><strong>Priority:</strong> {issueDetails.priority}</p>
              <p><strong>Department:</strong> {issueDetails.department}</p>
              {issueDetails.images && (
                <div>
                  <strong>Images:</strong>
                  <div className="grid grid-cols-2 gap-2 mt-2">
                    {issueDetails.images.map((img) => (
                      <img key={img.id} src={img.url} alt="Issue" className="w-full h-32 object-cover rounded" />
                    ))}
                  </div>
                </div>
              )}
              <div>
                <Label>Update Status</Label>
                <Select value={issueDetails.status} onValueChange={handleStatusChange}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="open">Open</SelectItem>
                    <SelectItem value="in_progress">In Progress</SelectItem>
                    <SelectItem value="resolved">Resolved</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          )}
        </SheetContent>
      </Sheet>
    </div>
  )
}