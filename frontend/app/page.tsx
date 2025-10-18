'use client'

import { useEffect, useMemo, useRef, useState } from 'react'
import Section from '@/components/Section'
import GroupPill from '@/components/GroupPill'
import ProgressBar from '@/components/ProgressBar'
import CardSub from '@/components/CardSub'
import { PrimaryButton, GhostButton } from '@/components/Buttons'
import ChatDialog from '@/components/ChatDialog'
import { soft } from '@/lib/theme'
import { supabase } from '@/lib/client'
import { useRouter } from 'next/navigation'
import { Upload, Camera, MessageCircle } from 'lucide-react'

export default function Page() {
  const [message, setMessage] = useState('Loading...')
  const [session, setSession] = useState<any>(null)
  const [isChatOpen, setIsChatOpen] = useState(false)
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
        <div className="flex justify-end gap-2 mb-2">
          {session ? (
            <>
              <GhostButton onClick={() => router.push('/connections')}>Friends</GhostButton>
              <GhostButton onClick={() => router.push('/profile')}>Profile</GhostButton>
              <GhostButton onClick={handleSignOut}>Log Out</GhostButton>
            </>
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
        <div className="space-y-4">
          {/* Upload Box - Clickable */}
          <button
            onClick={() => uploadRef.current?.click()}
            className="w-full bg-white border-4 border-[#2BAA66] rounded-2xl p-12 hover:bg-[#F1FBF6] transition-all cursor-pointer group"
          >
            <div className="text-center space-y-4">
              <div className="flex justify-center">
                <Upload size={48} className="text-[#2BAA66]" strokeWidth={2} />
              </div>
              <div className="space-y-2">
                <h3 className="text-2xl font-bold text-[#0B3B29] group-hover:text-[#2BAA66] transition-colors">
                  Upload Image
                </h3>
                {/*<p className="text-[#5E7F73]">
                  Click anywhere in this box to upload a photo of your meal
                </p>*/}
              </div>
            </div>
          </button>

          {/* Take Photo Button - Separate */}
          <button
            onClick={() => cameraRef.current?.click()}
            className="w-full bg-[#2BAA66] text-white px-8 py-4 rounded-xl font-semibold text-lg hover:bg-[#27A05F] transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-1 flex items-center justify-center gap-3"
          >
            <Camera size={20} strokeWidth={2} />
            Take Photo
          </button>
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

      {/* Floating Chat Button */}
      {session && (
        <button
          onClick={() => setIsChatOpen(true)}
          className="fixed bottom-6 right-6 bg-[#2BAA66] text-white p-4 rounded-full shadow-lg hover:bg-[#27A05F] hover:scale-110 transition-all z-30"
          aria-label="Open chat"
        >
          <MessageCircle size={24} />
        </button>
      )}

      {/* Chat Dialog */}
      <ChatDialog isOpen={isChatOpen} onClose={() => setIsChatOpen(false)} />
    </>
  )
}
