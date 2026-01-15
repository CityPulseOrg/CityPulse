'use client'

import { useState, useEffect } from 'react'
import dynamic from 'next/dynamic'
import { Card, CardContent } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { MapPin, Crosshair } from 'lucide-react'

// Dynamically import map components to avoid SSR issues
const MapContainer = dynamic(() => import('react-leaflet').then(mod => mod.MapContainer), { ssr: false })
const TileLayer = dynamic(() => import('react-leaflet').then(mod => mod.TileLayer), { ssr: false })
const Marker = dynamic(() => import('react-leaflet').then(mod => mod.Marker), { ssr: false })
const Popup = dynamic(() => import('react-leaflet').then(mod => mod.Popup), { ssr: false })

// Import useMapEvents directly since it's a hook, not a component
import { useMapEvents as useMapEventsHook } from 'react-leaflet'

// Component to handle map events
function MapEventHandler({ onMapClick, onMouseMove }: { onMapClick: (e: any) => void, onMouseMove: (e: any) => void }) {
  useMapEventsHook({
    click: onMapClick,
    mousemove: onMouseMove,
  })
  return null
}

interface LocationPickerProps {
  lat?: number
  lng?: number
  onLocationChange: (lat: number, lng: number) => void
}

export default function LocationPicker({ lat, lng, onLocationChange }: LocationPickerProps) {
  const [selectedLocation, setSelectedLocation] = useState<[number, number] | null>(
    lat && lng ? [lat, lng] : null
  )
  const [hoveredLocation, setHoveredLocation] = useState<[number, number] | null>(null)
  const [currentLocation, setCurrentLocation] = useState<[number, number] | null>(null)
  const [isMapReady, setIsMapReady] = useState(false)
  const [isLocationReady, setIsLocationReady] = useState(false)

  // Default to a central location if no coordinates provided
  const defaultCenter: [number, number] = [45.485498, -73.610675] // MTL REPRESENT BABY
  const center = selectedLocation || currentLocation || defaultCenter

  useEffect(() => {
    // Load Leaflet CSS
    const link = document.createElement('link')
    link.rel = 'stylesheet'
    link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css'
    document.head.appendChild(link)

    // Fix for default markers in react-leaflet
    import('leaflet').then(L => {
      delete (L.Icon.Default.prototype as any)._getIconUrl
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
        iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
      })
      setIsMapReady(true)
    })

    return () => {
      document.head.removeChild(link)
    }
  }, [])

  useEffect(() => {
    const hasProvidedLocation = typeof lat === 'number' && typeof lng === 'number'
    if (hasProvidedLocation) {
      setIsLocationReady(true)
      return
    }

    if (!navigator.geolocation) {
      setIsLocationReady(true)
      return
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords
        setCurrentLocation([latitude, longitude])
        setIsLocationReady(true)
      },
      (error) => {
        console.error('Error getting location:', error)
        setIsLocationReady(true)
      }
    )
  }, [lat, lng])

  const handleMapClick = (e: any) => {
    const { lat, lng } = e.latlng
    const newLocation: [number, number] = [lat, lng]
    setSelectedLocation(newLocation)
    onLocationChange(lat, lng)
  }

  const handleMouseMove = (e: any) => {
    const { lat, lng } = e.latlng
    setHoveredLocation([lat, lng])
  }

  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords
          const newLocation: [number, number] = [latitude, longitude]
          setCurrentLocation(newLocation)
          setSelectedLocation(newLocation)
          onLocationChange(latitude, longitude)
        },
        (error) => {
          console.error('Error getting location:', error)
          alert('Unable to get your current location. Please click on the map to select a location.')
        }
      )
    } else {
      alert('Geolocation is not supported by this browser.')
    }
  }

  const formatCoordinates = (coords: [number, number] | null) => {
    if (!coords) return ''
    return `${coords[0].toFixed(6)}, ${coords[1].toFixed(6)}`
  }

  if (!isMapReady || !isLocationReady) {
    return (
      <Card className="w-full">
        <CardContent className="p-4">
          <div className="flex items-center justify-center h-64 bg-gray-100 rounded-lg">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-2"></div>
              <p className="text-gray-600">Loading map...</p>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="w-full">
      <CardContent className="p-4">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <Label className="text-base font-semibold text-gray-800">Location</Label>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={getCurrentLocation}
              className="flex items-center gap-2"
            >
              <Crosshair className="w-4 h-4" />
              Use Current Location
            </Button>
          </div>

          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-3 border border-blue-200">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div className="flex items-center gap-2">
                <MapPin className="w-4 h-4 text-blue-600" />
                <span className="text-gray-600">Selected:</span>
                <span className="font-mono text-blue-700">
                  {selectedLocation ? formatCoordinates(selectedLocation) : 'None selected'}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded-full bg-green-500"></div>
                <span className="text-gray-600">Hovering:</span>
                <span className="font-mono text-green-700">
                  {hoveredLocation ? formatCoordinates(hoveredLocation) : 'Move cursor over map'}
                </span>
              </div>
            </div>
          </div>

          <div className="h-64 rounded-lg overflow-hidden border border-gray-200 shadow-sm">
            <MapContainer
              center={center}
              zoom={11}
              style={{ height: '100%', width: '100%' }}
            >
              <MapEventHandler onMapClick={handleMapClick} onMouseMove={handleMouseMove} />
              <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              />
              {selectedLocation && (
                <Marker position={selectedLocation}>
                  <Popup>
                    <div className="text-center">
                      <strong>Selected Location</strong><br />
                      {formatCoordinates(selectedLocation)}
                    </div>
                  </Popup>
                </Marker>
              )}
            </MapContainer>
          </div>

          <p className="text-sm text-gray-600 text-center">
            Click on the map to select the issue location. The coordinates will update in real-time as you move your cursor.
          </p>
        </div>
      </CardContent>
    </Card>
  )
}
