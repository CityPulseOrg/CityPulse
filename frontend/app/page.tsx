import Link from 'next/link'
import { Button } from '@/components/ui/button'

export default function Home() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold">CityPulse</h1>
        <p className="text-lg">AI-powered civic issue reporting system</p>
        <div className="space-x-4">
          <Link href="/report">
            <Button>Report an Issue</Button>
          </Link>
          <Link href="/admin">
            <Button variant="outline">Admin Dashboard</Button>
          </Link>
        </div>
      </div>
    </div>
  )
}
