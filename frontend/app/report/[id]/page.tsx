'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getIssue, followupIssue } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { ClarificationQuestion } from '@/lib/types'

interface PageProps {
  params: { id: string }
}

export default function IssuePage({ params }: PageProps) {
  const { id } = params
  const queryClient = useQueryClient()
  const [answers, setAnswers] = useState<{ [key: string]: string }>({})

  const { data: issue, isLoading } = useQuery({
    queryKey: ['issue', id],
    queryFn: () => getIssue(id),
  })

  const followupMutation = useMutation({
    mutationFn: (answers: { [key: string]: string }) => followupIssue(id, answers),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['issue', id] })
      setAnswers({})
    },
  })

  const handleFollowupSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    followupMutation.mutate(answers)
  }

  if (isLoading) return <div>Loading...</div>
  if (!issue) return <div>Issue not found</div>

  return (
    <div className="container mx-auto p-4">
      <Card className="max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle>Issue #{issue.id}</CardTitle>
          <Badge variant={issue.status === 'open' ? 'destructive' : 'default'}>{issue.status}</Badge>
        </CardHeader>
        <CardContent className="space-y-4">
          <p><strong>Description:</strong> {issue.description}</p>
          {issue.category && <p><strong>Category:</strong> {issue.category}</p>}
          {issue.priority && <p><strong>Priority:</strong> {issue.priority}</p>}
          {issue.department && <p><strong>Department:</strong> {issue.department}</p>}

          {issue.images && issue.images.length > 0 && (
            <div>
              <strong>Images:</strong>
              <div className="grid grid-cols-2 gap-2 mt-2">
                {issue.images.map((img) => (
                  <img key={img.id} src={img.url} alt="Issue" className="w-full h-32 object-cover rounded" />
                ))}
              </div>
            </div>
          )}

          {issue.clarification_questions && issue.clarification_questions.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Additional Information Needed</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleFollowupSubmit} className="space-y-4">
                  {issue.clarification_questions.map((q: ClarificationQuestion) => (
                    <div key={q.id}>
                      <Label>{q.question}</Label>
                      {q.type === 'text' ? (
                        <Input
                          value={answers[q.id] || ''}
                          onChange={(e) => setAnswers(prev => ({ ...prev, [q.id]: e.target.value }))}
                          required
                        />
                      ) : (
                        <select
                          value={answers[q.id] || ''}
                          onChange={(e) => setAnswers(prev => ({ ...prev, [q.id]: e.target.value }))}
                          className="w-full p-2 border rounded"
                          required
                        >
                          <option value="">Select...</option>
                          {q.choices?.map(choice => (
                            <option key={choice} value={choice}>{choice}</option>
                          ))}
                        </select>
                      )}
                    </div>
                  ))}
                  <Button type="submit" disabled={followupMutation.isPending}>
                    {followupMutation.isPending ? 'Submitting...' : 'Submit Answers'}
                  </Button>
                </form>
              </CardContent>
            </Card>
          )}
        </CardContent>
      </Card>
    </div>
  )
}