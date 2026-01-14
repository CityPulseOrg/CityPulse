'use client'

import { useState, useEffect } from 'react'
import { useMutation } from '@tanstack/react-query'
import { useRouter } from 'next/navigation'
import { createIssue } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import LocationPicker from '@/components/LocationPicker'

export default function ReportPage() {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [photos, setPhotos] = useState<{ id: string; file: File }[]>([])
  const [photoUrls, setPhotoUrls] = useState<string[]>([])
  const [lat, setLat] = useState<number | undefined>()
  const [lng, setLng] = useState<number | undefined>()
  const router = useRouter()

  useEffect(() => {
    const urls = photos.map(({ file }) => URL.createObjectURL(file))
    setPhotoUrls(urls)
    return () => urls.forEach(url => URL.revokeObjectURL(url))
  }, [photos])

  const mutation = useMutation({
    mutationFn: createIssue,
    onSuccess: (data) => {
      router.push(`/report/${data.id}`)
    },
    onError: (error) => {
      console.error('Failed to submit report:', error)
      alert('Failed to submit report. Please try again.')
    },
  })

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files)
      if (photos.length + files.length > 5) {
        alert('Max 5 files')
        return
      }
      const validFiles = files.filter(file => file.size <= 5 * 1024 * 1024) // 5MB
      const rejectedFiles = files.length - validFiles.length
      if (rejectedFiles > 0) {
        alert(`${rejectedFiles} file(s) exceeded 5MB and were not added.`)
      }
      setPhotos(prev => [...prev, ...validFiles.map(file => ({ id: crypto.randomUUID(), file }))])
    }
  }

  const removePhoto = (index: number) => {
    setPhotos(prev => prev.filter((_, i) => i !== index))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    mutation.mutate({ title: title || undefined, description, photos: photos.length > 0 ? photos.map(p => p.file) : undefined, lat, lng })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 py-8">
      <div className="container mx-auto px-4">
        {/* CityPulse Branding Header */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-blue-800 bg-clip-text text-transparent mb-2">
            CityPulse
          </h1>
          <div className="w-24 h-1 bg-gradient-to-r from-blue-500 to-purple-500 mx-auto rounded-full"></div>
        </div>

        <Card className="max-w-2xl mx-auto">
          <CardHeader>
            <CardTitle>Report a Civic Issue</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label htmlFor="title">Title</Label>
                <Input
                  id="title"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Brief title for the issue"
                />
              </div>
              <div>
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Describe the issue..."
                  required
                />
              </div>
              <div>
                <Label htmlFor="photos">Photos (max 5, 5MB each)</Label>
                <Input
                  id="photos"
                  type="file"
                  multiple
                  accept="image/*"
                  onChange={handleFileChange}
                />
                <div className="flex flex-wrap gap-2 mt-2">
                  {photos.map(({ id, file }, index) => (
                    <div key={id} className="relative">
                      <img
                        src={photoUrls[index]}
                        alt={`Preview ${index}`}
                        className="w-20 h-20 object-cover rounded"
                      />
                      <button
                        type="button"
                        onClick={() => removePhoto(index)}
                        className="absolute top-0 right-0 bg-red-500 text-white rounded-full w-5 h-5 text-xs"
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <Label>Location (optional)</Label>
                <LocationPicker
                  lat={lat}
                  lng={lng}
                  onLocationChange={(newLat, newLng) => {
                    setLat(newLat)
                    setLng(newLng)
                  }}
                />
              </div>
              <Button type="submit" disabled={mutation.isPending}>
                {mutation.isPending ? 'Analyzing report...' : 'Submit Report'}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}