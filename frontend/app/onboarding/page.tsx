'use client'

import { useState } from 'react'
import { supabase } from '@/lib/client'
import { useRouter } from 'next/navigation'
import RadioRow from '@/components/RadioRow'

type GoalType = 'balanced' | 'loss' | 'gain' | 'diabetes'

const goalOptions = [
  { value: 'balanced', label: 'Balanced Diet – General health and wellness', dbValue: 'maintain' },
  { value: 'loss', label: 'Weight Loss – Focus on portion control and nutrients', dbValue: 'lose_weight' },
  { value: 'gain', label: 'Weight Gain – Calorie-dense, nutritious foods', dbValue: 'gain_weight' },
  { value: 'diabetes', label: 'Diabetes Management – Low-glycemic, balanced meals', dbValue: 'diabetes_management' },
]

export default function OnboardingPage() {
  const router = useRouter()
  const [fullName, setFullName] = useState('')
  const [goal, setGoal] = useState<GoalType>('balanced')
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setMessage('')
    setLoading(true)

    try {
      const { data: { user } } = await supabase.auth.getUser()
      
      if (!user) {
        setMessage('No user session - onboarding not saved')
        setLoading(false)
        return
      }

      // Insert/update user record
      const { error: userError } = await supabase
        .from('users')
        .upsert({
          id: user.id,
          full_name: fullName || null,
        })

      if (userError) throw userError

      // Get the database goal value
      const selectedGoal = goalOptions.find(opt => opt.value === goal)
      
      // Insert new active goal
      const { error: goalError } = await supabase
        .from('user_goals')
        .insert({
          user_id: user.id,
          goal_type: selectedGoal?.dbValue || 'maintain',
          is_active: true,
        })

      if (goalError) throw goalError

      // Redirect to home page
      router.push('/')
    } catch (error: any) {
      console.error('Onboarding error:', error)
      setMessage(error.message || 'Failed to save profile. Please try again.')
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-[#F1FBF6] flex items-center justify-center px-6">
      <div className="bg-white border border-[#D9F1E3] rounded-2xl shadow-md w-full max-w-md p-8 space-y-6">
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-bold text-[#0B3B29]">Welcome to NutriBalance!</h1>
          <p className="text-[#5E7F73]">Let&apos;s personalize your experience</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Optional Name Input */}
          <div>
            <label className="block text-sm font-semibold text-[#0B3B29] mb-3">
              What should we call you? (optional)
            </label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Your name"
              className="w-full border border-[#D9F1E3] rounded-lg px-3 py-2 outline-none focus:border-[#2BAA66]"
            />
          </div>

          {/* Goal Selection */}
          <div>
            <label className="block text-sm font-semibold text-[#0B3B29] mb-3">
              Choose your health goal
            </label>
            <div className="grid gap-3">
              {goalOptions.map(opt => (
                <RadioRow
                  key={opt.value}
                  checked={goal === opt.value}
                  label={opt.label}
                  onChange={() => setGoal(opt.value as GoalType)}
                />
              ))}
            </div>
          </div>

          {message && <p className="text-sm text-center text-red-600">{message}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-[#2BAA66] text-white py-2.5 rounded-lg font-semibold hover:bg-[#27A05F] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Saving...' : 'Get Started'}
          </button>
        </form>
      </div>
    </main>
  )
}

