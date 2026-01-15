'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getIssues, updateIssueStatus, getIssue } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet'
import { Label } from '@/components/ui/label'

export default function AdminPage() {
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [categoryFilter, setCategoryFilter] = useState<string>('all')
  const [priorityFilter, setPriorityFilter] = useState<string>('all')
  const [selectedIssue, setSelectedIssue] = useState<string | null>(null)
  const queryClient = useQueryClient()

  const { data: issues = [] } = useQuery({
    queryKey: ['issues', statusFilter, categoryFilter, priorityFilter],
    queryFn: () => getIssues({ 
      status: statusFilter === 'all' ? undefined : statusFilter, 
      category: categoryFilter === 'all' ? undefined : categoryFilter,
      priority: priorityFilter === 'all' ? undefined : priorityFilter
    }),
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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      <div className="container mx-auto px-4 py-8">
        {/* CityPulse Branding Header */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-blue-800 bg-clip-text text-transparent mb-2">
            CityPulse
          </h1>
          <div className="w-24 h-1 bg-gradient-to-r from-blue-500 to-purple-500 mx-auto rounded-full"></div>
        </div>

        {/* Header Section */}
        <div className="text-center mb-8 pb-6 border-b-2 border-blue-200">
          <h1 className="text-4xl font-bold mb-2 text-gray-800">
            Admin Dashboard
          </h1>
          <p className="text-gray-600 text-lg">Manage and track civic issues efficiently</p>
        </div>

        {/* Filters Section */}
        <div className="bg-white/70 backdrop-blur-sm rounded-2xl p-6 mb-8 shadow-lg border border-white/50">
          <h2 className="text-xl font-semibold mb-4 text-gray-800 flex items-center">
            <div className="w-1 h-6 bg-blue-500 rounded-full mr-3"></div>
            Filter Issues
          </h2>
          <div className="flex flex-wrap gap-4 justify-center">
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-48 bg-white shadow-md border-blue-200 hover:border-blue-300 transition-colors">
                <SelectValue placeholder="Filter by Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="New">🔴 New</SelectItem>
                <SelectItem value="In Progress">🟡 In Progress</SelectItem>
                <SelectItem value="Resolved">🟢 Resolved</SelectItem>
                <SelectItem value="Waiting for user follow-up">🟠 Waiting for Follow-up</SelectItem>
              </SelectContent>
            </Select>
            <Select value={priorityFilter} onValueChange={setPriorityFilter}>
              <SelectTrigger className="w-48 bg-white shadow-md border-blue-200 hover:border-blue-300 transition-colors">
                <SelectValue placeholder="Filter by Priority" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Priorities</SelectItem>
                <SelectItem value="High">🔴 High Priority</SelectItem>
                <SelectItem value="Medium">🟡 Medium Priority</SelectItem>
                <SelectItem value="Low">🟢 Low Priority</SelectItem>
              </SelectContent>
            </Select>
            <Select value={categoryFilter} onValueChange={setCategoryFilter}>
              <SelectTrigger className="w-48 bg-white shadow-md border-blue-200 hover:border-blue-300 transition-colors">
                <SelectValue placeholder="Filter by Category" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Categories</SelectItem>
                <SelectItem value="pothole">🕳️ Pothole</SelectItem>
                <SelectItem value="graffiti">🎨 Graffiti</SelectItem>
                <SelectItem value="lighting">💡 Street Light</SelectItem>
                <SelectItem value="trash">🗑️ Trash</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Issues Section */}
        <div className="bg-white/60 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-white/50">
          <h2 className="text-xl font-semibold mb-6 text-gray-800 flex items-center">
            <div className="w-1 h-6 bg-purple-500 rounded-full mr-3"></div>
            Issues List
            <span className="ml-2 text-sm font-normal text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
              {issues.length} issue{issues.length !== 1 ? 's' : ''}
            </span>
          </h2>
          <div className="space-y-4 max-w-4xl mx-auto">
            {issues.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">📋</div>
                <h3 className="text-xl font-semibold text-gray-600 mb-2">No issues found</h3>
                <p className="text-gray-500">Try adjusting your filters or check back later for new reports.</p>
              </div>
            ) : (
              issues.map((issue, index) => (
                <div
                  key={issue.id}
                  className={`bg-white rounded-2xl shadow-md hover:shadow-xl transition-all duration-300 cursor-pointer p-5 border-l-4 transform hover:-translate-y-1 ${
                    issue.priority === 'High' ? 'border-red-500 hover:border-red-600' :
                    issue.priority === 'Medium' ? 'border-yellow-500 hover:border-yellow-600' :
                    'border-blue-500 hover:border-purple-500'
                  }`}
                  onClick={() => setSelectedIssue(issue.id)}
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-3">
                        <span className="font-bold text-gray-800 text-lg">#{issue.id}</span>
                        {issue.title && (
                          <>
                            <div className="w-1 h-4 bg-gray-300 rounded-full"></div>
                            <span className="text-gray-700 font-medium">{issue.title}</span>
                          </>
                        )}
                      </div>
                      <p className="text-gray-700 mb-4 leading-relaxed">{issue.description.slice(0, 120)}...</p>
                      <div className="flex gap-2 flex-wrap">
                        <Badge
                          variant={issue.status === 'New' ? 'destructive' : issue.status === 'In Progress' ? 'default' : issue.status === 'Waiting for user follow-up' ? 'outline' : 'secondary'}
                          className="text-xs px-3 py-1"
                        >
                          {issue.status}
                        </Badge>
                        {issue.priority && (
                          <Badge
                            variant="outline"
                            className={`text-xs px-3 py-1 font-semibold ${
                              issue.priority === 'High' ? 'border-red-500 text-red-700 bg-red-50' :
                              issue.priority === 'Medium' ? 'border-yellow-500 text-yellow-700 bg-yellow-50' :
                              'border-green-500 text-green-700 bg-green-50'
                            }`}
                          >
                            {issue.priority === 'High' ? '🔴' : issue.priority === 'Medium' ? '🟡' : '🟢'} {issue.priority} Priority
                          </Badge>
                        )}
                        {issue.severity && (
                          <Badge
                            variant="outline"
                            className={`text-xs px-3 py-1 ${
                              issue.severity === 'Critical' ? 'border-red-600 text-red-800 bg-red-100' :
                              issue.severity === 'High' ? 'border-orange-500 text-orange-700 bg-orange-50' :
                              issue.severity === 'Medium' ? 'border-yellow-500 text-yellow-700 bg-yellow-50' :
                              'border-gray-500 text-gray-700 bg-gray-50'
                            }`}
                          >
                            Risk: {issue.severity}
                          </Badge>
                        )}
                        {issue.category && (
                          <Badge variant="secondary" className="text-xs px-3 py-1 bg-blue-100 text-blue-800">
                            {issue.category}
                          </Badge>
                        )}
                      </div>
                    </div>
                  </div>
                  {index < issues.length - 1 && (
                    <div className="mt-4 pt-4 border-t border-gray-100"></div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>

        <Sheet open={!!selectedIssue} onOpenChange={() => setSelectedIssue(null)}>
          <SheetContent className="bg-gradient-to-br from-blue-50 to-purple-50 border-l border-blue-200">
            <SheetHeader className="border-b border-blue-200 pb-4 mb-4">
              <SheetTitle className="text-gray-800 text-xl flex items-center">
                <div className="w-2 h-6 bg-blue-500 rounded-full mr-3"></div>
                Issue #{selectedIssue}
              </SheetTitle>
            </SheetHeader>
            {issueDetails && (
              <div className="space-y-4">
                {issueDetails.title && (
                  <div className="bg-white/70 rounded-lg p-4 border border-blue-100">
                    <h3 className="text-lg font-semibold text-gray-800 mb-2">Title</h3>
                    <p className="text-gray-700">{issueDetails.title}</p>
                  </div>
                )}
                <div className="bg-white/70 rounded-lg p-4 border border-blue-100">
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Description</h3>
                  <p className="text-gray-700 leading-relaxed">{issueDetails.description}</p>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-white/70 rounded-lg p-4 border border-blue-100">
                    <h3 className="text-sm font-semibold text-gray-600 mb-1">Status</h3>
                    <Badge variant={issueDetails.status === 'New' ? 'destructive' : issueDetails.status === 'In Progress' ? 'default' : issueDetails.status === 'Waiting for user follow-up' ? 'outline' : 'secondary'} className="text-sm">
                      {issueDetails.status}
                    </Badge>
                  </div>
                  {issueDetails.category && (
                    <div className="bg-white/70 rounded-lg p-4 border border-blue-100">
                      <h3 className="text-sm font-semibold text-gray-600 mb-1">Category</h3>
                      <Badge variant="secondary" className="text-sm">{issueDetails.category}</Badge>
                    </div>
                  )}
                  {issueDetails.priority && (
                    <div className="bg-white/70 rounded-lg p-4 border border-blue-100">
                      <h3 className="text-sm font-semibold text-gray-600 mb-1">Priority</h3>
                      <Badge variant="outline" className="text-sm">{issueDetails.priority}</Badge>
                    </div>
                  )}
                  {issueDetails.department && (
                    <div className="bg-white/70 rounded-lg p-4 border border-blue-100">
                      <h3 className="text-sm font-semibold text-gray-600 mb-1">Department</h3>
                      <p className="text-gray-700 text-sm">{issueDetails.department}</p>
                    </div>
                  )}
                </div>
                {issueDetails.images && issueDetails.images.length > 0 && (
                  <div className="bg-white/70 rounded-lg p-4 border border-blue-100">
                    <h3 className="text-lg font-semibold text-gray-800 mb-3">Images</h3>
                    <div className="grid grid-cols-2 gap-3">
                      {issueDetails.images.map((img) => (
                        <img key={img.id} src={img.url} alt="Issue" className="w-full h-24 object-cover rounded-lg border border-gray-200" />
                      ))}
                    </div>
                  </div>
                )}
                <div className="bg-white/70 rounded-lg p-4 border border-blue-100">
                  <Label className="text-gray-800 font-semibold block mb-3">Update Status</Label>
                  <Select value={issueDetails.status} onValueChange={handleStatusChange}>
                    <SelectTrigger className="bg-white border-blue-200">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="New">🔴 New</SelectItem>
                      <SelectItem value="In Progress">🟡 In Progress</SelectItem>
                      <SelectItem value="Resolved">🟢 Resolved</SelectItem>
                      <SelectItem value="Waiting for user follow-up">🟠 Waiting for Follow-up</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            )}
          </SheetContent>
        </Sheet>
      </div>
    </div>
  )
}