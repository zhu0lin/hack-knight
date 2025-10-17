'use client'

import { useEffect, useMemo, useRef, useState } from 'react'
import Section from '@/components/Section'
import RadioRow from '@/components/RadioRow'
import GroupPill from '@/components/GroupPill'
import ProgressBar from '@/components/ProgressBar'
import CardSub from '@/components/CardSub'
import { PrimaryButton, GhostButton } from '@/components/Buttons'
import { soft } from '@/lib/theme'
import { supabase } from '@/lib/client'
import { useRouter } from 'next/navigation'

type Goal = 'balanced' | 'loss' | 'gain' | 'diabetes'

export default function Page() {
  const [goal, setGoal] = useState<Goal>('balanced')
  const [message, setMessage] = useState('Loading...')
  const [session, setSession] = useState<any>(null)
  const [foodGroups, setFoodGroups] = useState<Record<string, boolean>>({
    Fruits: false,
    Vegetables: false,
    Grains: false,
    Protein: false,
    Dairy: false,
    'Healthy Fats': false,
  })

  const cameraRef = useRef<HTMLInputElement>(null)
  const uploadRef = useRef<HTMLInputElement>(null)
  const router = useRouter()

  useEffect(() => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    fetch(`${apiUrl}/`)
      .then(r => r.json())
      .then(d => setMessage(d.message))
      .catch(() => setMessage('Error connecting to backend'))
  }, [])

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
    })

    const { data: listener } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session)
    })

    return () => {
      listener.subscription.unsubscribe()
    }
  }, [])

  const completed = useMemo(
    () => Object.values(foodGroups).filter(Boolean).length,
    [foodGroups]
  )
  const progressPct = Math.round(
    (completed / Object.keys(foodGroups).length) * 100
  )

  const handleFiles = (files: FileList | null) => {
    if (!files?.length) return
    setFoodGroups(prev => {
      const next = { ...prev }
      const keys = Object.keys(next)
      for (let i = 0; i < Math.min(2, keys.length); i++) {
        const k = keys[(Math.random() * keys.length) | 0]
        next[k] = true
      }
      return next
    })
  }

  const handleSignOut = async () => {
    await supabase.auth.signOut()
  }

  const recs = [
    'Add some fruit for vitamins and fiber',
    'Include vegetables for essential nutrients',
    'Add whole grains for sustained energy',
  ]

  return (
    <>
      <header className="text-center space-y-2">
        <div className="flex justify-end mb-2">
          {session ? (
            <GhostButton onClick={handleSignOut}>Log Out</GhostButton>
          ) : (
            <PrimaryButton onClick={() => router.push('/login')}>Sign In</PrimaryButton>
          )}
        </div>
        <h1 className="text-4xl font-bold text-[#0B3B29]">NutriBalance</h1>
        <p className="text-[#5E7F73] text-lg">
          Track your daily food groups and build a balanced diet
        </p>
      </header>

      <Section
        title="Your Goal"
        subtitle="Customize recommendations based on your health goals"
      >
        <div className="grid gap-3">
          {goalOptions.map(opt => (
            <RadioRow
              key={opt.value}
              checked={goal === opt.value}
              label={opt.label}
              onChange={() => setGoal(opt.value as Goal)}
            />
          ))}
        </div>
      </Section>

      <Section
        title="Today's Progress"
        subtitle={`${completed} of ${Object.keys(foodGroups).length} food groups completed`}
      >
        <ProgressBar percent={progressPct} />

        <div className="grid gap-3 grid-cols-[repeat(auto-fit,minmax(180px,1fr))]">
          {Object.entries(foodGroups).map(([name, done]) => (
            <GroupPill
              key={name}
              name={name}
              done={done}
              onToggle={() =>
                setFoodGroups(prev => ({ ...prev, [name]: !prev[name] }))
              }
            />
          ))}
        </div>

        <CardSub>
          <h3 className="font-semibold text-[#0B3B29] mb-2">Recommendations</h3>
          <ul className="list-disc pl-5 text-[#5E7F73]">
            {recs.map(r => (
              <li key={r}>{r}</li>
            ))}
          </ul>
        </CardSub>
      </Section>

      <Section
        title="Add a Meal"
        subtitle="Take a photo or upload an image of your food"
      >
        <div className="flex flex-wrap gap-3">
          <PrimaryButton onClick={() => cameraRef.current?.click()}>
            📷 Take Photo
          </PrimaryButton>
          <GhostButton onClick={() => uploadRef.current?.click()}>
            ⬆️ Upload
          </GhostButton>
        </div>

        <input
          ref={cameraRef}
          type="file"
          accept="image/*"
          capture="environment"
          className="hidden"
          onChange={e => handleFiles(e.target.files)}
        />
        <input
          ref={uploadRef}
          type="file"
          accept="image/*"
          className="hidden"
          onChange={e => handleFiles(e.target.files)}
        />
      </Section>

      {/* <Section title="Debug" subtitle="Backend Connection">
        <p className="text-sm text-[#5E7F73]">
          <strong>Backend Response:</strong> {message}
        </p>
      </Section> */}

      <footer className="text-center text-[#5E7F73] mt-6">
        <small>© {new Date().getFullYear()} NutriBalance</small>
      </footer>
    </>
  )
}

const goalOptions = [
  { value: 'balanced', label: 'Balanced Diet – General health and wellness' },
  { value: 'loss', label: 'Weight Loss – Focus on portion control and nutrients' },
  { value: 'gain', label: 'Weight Gain – Calorie-dense, nutritious foods' },
  { value: 'diabetes', label: 'Diabetes Management – Low-glycemic, balanced meals' },
]
