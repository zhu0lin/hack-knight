'use client'

import { useEffect, useState } from 'react'
import { supabase } from '@/lib/client'
import { useRouter } from 'next/navigation'
import RadioRow from '@/components/RadioRow'
import { PrimaryButton, GhostButton } from '@/components/Buttons'

type GoalType = 'balanced' | 'loss' | 'gain' | 'diabetes'

const goalOptions = [
  { value: 'balanced', label: 'Balanced Diet – General health and wellness', dbValue: 'maintain' },
  { value: 'loss', label: 'Weight Loss – Focus on portion control and nutrients', dbValue: 'lose_weight' },
  { value: 'gain', label: 'Weight Gain – Calorie-dense, nutritious foods', dbValue: 'gain_weight' },
  { value: 'diabetes', label: 'Diabetes Management – Low-glycemic, balanced meals', dbValue: 'diabetes_management' },
]

export default function ProfilePage() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')
  
  const [email, setEmail] = useState('')
  const [fullName, setFullName] = useState('')
  const [goal, setGoal] = useState<GoalType>('balanced')
  const [currentWeight, setCurrentWeight] = useState('')
  const [targetWeight, setTargetWeight] = useState('')
  const [height, setHeight] = useState('')
  const [age, setAge] = useState('')
  const [streak, setStreak] = useState<number | null>(null)
  const [lastCompletedDate, setLastCompletedDate] = useState<string | null>(null)
  const [streakError, setStreakError] = useState('')

  useEffect(() => {
    loadProfile()
  }, [])

  const loadProfile = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser()
      
      if (!user) {
        router.push('/login')
        return
      }

      setEmail(user.email || '')

      // Fetch user data
      const { data: userData, error: userError } = await supabase
        .from('users')
        .select('*')
        .eq('id', user.id)
        .single()

      if (userError && userError.code !== 'PGRST116') { // Ignore "not found" error
        console.error('Error loading user:', userError)
      }

      if (userData) {
        setFullName(userData.full_name || '')
        setCurrentWeight(userData.current_weight?.toString() || '')
        setTargetWeight(userData.target_weight?.toString() || '')
        setHeight(userData.height?.toString() || '')
        setAge(userData.age?.toString() || '')
      }

      // Fetch active goal
      const { data: goalData, error: goalError } = await supabase
        .from('user_goals')
        .select('goal_type')
        .eq('user_id', user.id)
        .eq('is_active', true)
        .single()

      if (goalError && goalError.code !== 'PGRST116') {
        console.error('Error loading goal:', goalError)
      }

      if (goalData) {
        // Map database value to frontend value
        const frontendGoal = goalOptions.find(opt => opt.dbValue === goalData.goal_type)
        if (frontendGoal) {
          setGoal(frontendGoal.value as GoalType)
        }
      }

      // Fetch streak data from backend
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
        const response = await fetch(`${apiUrl}/api/users/${user.id}/streak`)

        if (!response.ok) {
          throw new Error('Failed to load streak')
        }

        const data = await response.json()
        setStreak(typeof data.current_streak === 'number' ? data.current_streak : 0)
        setLastCompletedDate(data.last_completed_date || null)
        setStreakError('')
      } catch (error) {
        console.error('Streak fetch error:', error)
        setStreak(0)
        setLastCompletedDate(null)
        setStreakError('Unable to load streak right now')
      }

      setLoading(false)
    } catch (error) {
      console.error('Profile load error:', error)
      setMessage('Failed to load profile')
      setLoading(false)
    }
  }

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    setMessage('')
    setSaving(true)

    try {
      const { data: { user } } = await supabase.auth.getUser()
      
      if (!user) {
        setMessage('Not authenticated')
        setSaving(false)
        return
      }

      // Update user data
      const { error: userError } = await supabase
        .from('users')
        .upsert({
          id: user.id,
          full_name: fullName || null,
          current_weight: currentWeight ? parseFloat(currentWeight) : null,
          target_weight: targetWeight ? parseFloat(targetWeight) : null,
          height: height ? parseFloat(height) : null,
          age: age ? parseInt(age) : null,
        })

      if (userError) throw userError

      // Deactivate old goals
      await supabase
        .from('user_goals')
        .update({ is_active: false })
        .eq('user_id', user.id)
        .eq('is_active', true)

      // Insert new active goal
      const selectedGoal = goalOptions.find(opt => opt.value === goal)
      const { error: goalError } = await supabase
        .from('user_goals')
        .insert({
          user_id: user.id,
          goal_type: selectedGoal?.dbValue || 'maintain',
          is_active: true,
        })

      if (goalError) throw goalError

      setMessage('Profile updated successfully!')
      setTimeout(() => setMessage(''), 3000)
    } catch (error: any) {
      console.error('Save error:', error)
      setMessage(error.message || 'Failed to save changes')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-[#F1FBF6] flex items-center justify-center">
        <p className="text-[#5E7F73]">Loading...</p>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-[#F1FBF6] flex items-center justify-center px-6 py-12">
      <div className="bg-white border border-[#D9F1E3] rounded-2xl shadow-md w-full max-w-2xl p-8 space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold text-[#0B3B29]">Your Profile</h1>
          <GhostButton onClick={() => router.push('/')}>← Back to Home</GhostButton>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="border border-[#D9F1E3] rounded-xl p-4 bg-[#F8FFFB]">
            <p className="text-sm text-[#5E7F73]">Current Streak</p>
            <p className="text-3xl font-semibold text-[#0B3B29] mt-1">
              {streak !== null ? `${streak} day${streak === 1 ? '' : 's'}` : '—'}
            </p>
            {lastCompletedDate && (
              <p className="text-xs text-[#5E7F73] mt-1">
                Last completion: {new Date(lastCompletedDate).toLocaleDateString()}
              </p>
            )}
          </div>

          <div className="border border-[#D9F1E3] rounded-xl p-4 bg-white">
            <p className="text-sm text-[#5E7F73]">Keep it going!</p>
            <p className="text-sm text-[#0B3B29] mt-1">
              Log every food group each day to build your streak.
            </p>
            {streakError && (
              <p className="text-xs text-red-500 mt-2">{streakError}</p>
            )}
          </div>
        </div>

        <form onSubmit={handleSave} className="space-y-6">
          {/* Basic Info */}
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-[#0B3B29]">Basic Information</h2>
            
            <div>
              <label className="block text-sm text-[#5E7F73] mb-1">Email</label>
              <input
                type="email"
                value={email}
                disabled
                className="w-full border border-[#D9F1E3] rounded-lg px-3 py-2 bg-gray-50 text-gray-600"
              />
            </div>

            <div>
              <label className="block text-sm text-[#5E7F73] mb-1">Full Name</label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Your name"
                className="w-full border border-[#D9F1E3] rounded-lg px-3 py-2 outline-none focus:border-[#2BAA66]"
              />
            </div>
          </div>

          {/* Health Goal */}
          <div className="space-y-3">
            <h2 className="text-lg font-semibold text-[#0B3B29]">Health Goal</h2>
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

          {/* Optional Health Metrics */}
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-[#0B3B29]">Health Metrics (optional)</h2>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-[#5E7F73] mb-1">Current Weight (kg)</label>
                <input
                  type="number"
                  step="0.1"
                  value={currentWeight}
                  onChange={(e) => setCurrentWeight(e.target.value)}
                  placeholder="70"
                  className="w-full border border-[#D9F1E3] rounded-lg px-3 py-2 outline-none focus:border-[#2BAA66]"
                />
              </div>

              <div>
                <label className="block text-sm text-[#5E7F73] mb-1">Target Weight (kg)</label>
                <input
                  type="number"
                  step="0.1"
                  value={targetWeight}
                  onChange={(e) => setTargetWeight(e.target.value)}
                  placeholder="65"
                  className="w-full border border-[#D9F1E3] rounded-lg px-3 py-2 outline-none focus:border-[#2BAA66]"
                />
              </div>

              <div>
                <label className="block text-sm text-[#5E7F73] mb-1">Height (cm)</label>
                <input
                  type="number"
                  step="0.1"
                  value={height}
                  onChange={(e) => setHeight(e.target.value)}
                  placeholder="170"
                  className="w-full border border-[#D9F1E3] rounded-lg px-3 py-2 outline-none focus:border-[#2BAA66]"
                />
              </div>

              <div>
                <label className="block text-sm text-[#5E7F73] mb-1">Age</label>
                <input
                  type="number"
                  value={age}
                  onChange={(e) => setAge(e.target.value)}
                  placeholder="25"
                  className="w-full border border-[#D9F1E3] rounded-lg px-3 py-2 outline-none focus:border-[#2BAA66]"
                />
              </div>
            </div>
          </div>

          {message && (
            <p className={`text-sm text-center ${message.includes('success') ? 'text-green-600' : 'text-red-600'}`}>
              {message}
            </p>
          )}

          <button
            type="submit"
            disabled={saving}
            className="w-full bg-[#2BAA66] text-white py-2.5 rounded-lg font-semibold hover:bg-[#27A05F] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </form>
      </div>
    </main>
  )
}
