import Link from 'next/link'
import { Button } from '@/components/ui/button'

export default function Home() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-center space-y-4">
        <div className="text-5xl font-bold text-black dark:text-white">
          CityPulse
        </div>
        <h1 className="text-3xl font-bold">AI-Powered Report Submission</h1>
        <p className="text-lg">Report and track city problems with AI assistance</p>
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
