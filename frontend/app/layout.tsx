import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Hack Knight',
  description: 'Full-stack app with Next.js and FastAPI',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}

