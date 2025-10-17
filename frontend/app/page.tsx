'use client'

import { useState, useEffect } from 'react'
import styles from './page.module.css'

export default function Home() {
  const [message, setMessage] = useState<string>('Loading...')
  const [health, setHealth] = useState<any>(null)

  useEffect(() => {
    // Fetch from backend API
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    
    fetch(`${apiUrl}/`)
      .then(res => res.json())
      .then(data => setMessage(data.message))
      .catch(err => setMessage('Error connecting to backend'))

    fetch(`${apiUrl}/health`)
      .then(res => res.json())
      .then(data => setHealth(data))
      .catch(err => console.error('Health check failed:', err))
  }, [])

  return (
    <main className={styles.main}>
      <div className={styles.container}>
        <h1 className={styles.title}>🏰 Hack Knight</h1>
        <p className={styles.subtitle}>Next.js + FastAPI + Docker</p>
        
        <div className={styles.card}>
          <h2>Backend Response:</h2>
          <p>{message}</p>
        </div>

        {health && (
          <div className={styles.card}>
            <h2>API Health:</h2>
            <pre>{JSON.stringify(health, null, 2)}</pre>
          </div>
        )}

        <div className={styles.features}>
          <div className={styles.feature}>
            <h3>⚡ Next.js 14</h3>
            <p>React framework with App Router</p>
          </div>
          <div className={styles.feature}>
            <h3>🚀 FastAPI</h3>
            <p>Modern Python web framework</p>
          </div>
          <div className={styles.feature}>
            <h3>🐳 Docker</h3>
            <p>Containerized deployment</p>
          </div>
        </div>
      </div>
    </main>
  )
}

