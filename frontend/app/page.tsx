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
  const [meals, setMeals] = useState<FoodLog[]>([])
  const [message, setMessage] = useState('Loading...')
  const [isChatOpen, setIsChatOpen] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [uploadError, setUploadError] = useState('')
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

  type FoodLog = {
  id: string
  user_id: string | null
  detected_food_name: string
  food_category: string
  healthiness_score: number
  image_url: string
  logged_at?: string
  calories?: number
  meal_type?: string
}

  useEffect(() => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    fetch(`${apiUrl}/`)
      .then(r => r.json())
      .then(d => setMessage(d.message))
      .catch(() => setMessage('Error connecting to backend'))
  }, [])

  useEffect(() => {
    getMeals()
    updateFoodGroupsFromMeals()
  }, [])

  const completed = useMemo(
    () => Object.values(foodGroups).filter(Boolean).length,
    [foodGroups]
  )
  const progressPct = Math.round(
    (completed / Object.keys(foodGroups).length) * 100
  )

  const handleFiles = async (files: FileList | null) => {
    if (!files?.length) return
    
    const file = files[0]
    setUploading(true)
    setUploadError('')

    try {
      // Get current user (optional)
      const { data: { user } } = await supabase.auth.getUser()
      const userId = user?.id || null

      // Create FormData
      const formData = new FormData()
      formData.append('image', file)
      if (userId) {
        formData.append('user_id', userId)
      }

      // Upload to backend
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/api/food/upload`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || 'Failed to upload image')
      }

      const data = await response.json()
      console.log('✅ Upload successful:', data)
      console.log('📝 New meal ID:', data.log_id)
      console.log('🍎 Detected food:', data.detected_food_name, '| Category:', data.food_category)

      // Small delay to ensure DB commit
      console.log('⏳ Waiting for database to commit...')
      await new Promise(resolve => setTimeout(resolve, 500))

      // Refresh meals list
      console.log('🔄 Refreshing meals...')
      console.log('📊 Current meals count before refresh:', meals.length)
      await getMeals()

      // Update food groups based on all meals from today
      console.log('🔄 Updating food groups...')
      await updateFoodGroupsFromMeals()

      console.log('✨ All updates complete!')
      console.log('📊 Current meals count after refresh:', meals.length)
      setUploadError('')
    } catch (error) {
      console.error('Upload error:', error)
      setUploadError(error instanceof Error ? error.message : 'Failed to upload image. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  const updateFoodGroupsFromMeals = async () => {
    try {
      // Get today's date range
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      const todayStart = today.toISOString()
      
      // Fetch ALL meals from today (no user filter - get everyone's meals)
      const { data, error } = await supabase
        .from('food_logs')
        .select('*')
        .gte('logged_at', todayStart)
        .order('logged_at', { ascending: false })
      
      if (error) {
        console.error('Error fetching meals for food groups:', error)
        return
      }

      // Count categories from today's meals
      const categoryCounts: Record<string, number> = {
        'fruit': 0,
        'vegetable': 0,
        'grain': 0,
        'protein': 0,
        'dairy': 0,
      }

      data?.forEach(meal => {
        const category = meal.food_category?.toLowerCase()
        if (category && categoryCounts.hasOwnProperty(category)) {
          categoryCounts[category]++
        }
      })

      // Update food groups state
      setFoodGroups({
        'Fruits': categoryCounts['fruit'] > 0,
        'Vegetables': categoryCounts['vegetable'] > 0,
        'Grains': categoryCounts['grain'] > 0,
        'Protein': categoryCounts['protein'] > 0,
        'Dairy': categoryCounts['dairy'] > 0,
        'Healthy Fats': false, // Not tracked yet
      })
    } catch (error) {
      console.error('Error updating food groups:', error)
    }
  }

  const getMeals = async () => {
    console.log('📥 Fetching meals from database...')
    
    try {
      // Force a fresh query by adding a timestamp to prevent caching
      const timestamp = Date.now()
      console.log('🕐 Query timestamp:', timestamp)
      
      // Try to fetch with detailed logging
      const { data, error, count } = await supabase
        .from('food_logs')
        .select('*', { count: 'exact', head: false })
        .order('logged_at', { ascending: false })
        .limit(20)

      if (error) {
        console.error('❌ Error fetching meals:', error)
        console.error('❌ Error details:', JSON.stringify(error, null, 2))
        return
      }

      console.log('✅ Fetched', data?.length || 0, 'meals')
      console.log('📊 Total count in DB:', count)
      console.log('📊 Meals data:', data)
      
      if (data && data.length > 0) {
        console.log('🔍 First meal:', data[0])
        console.log('🔍 Last meal:', data[data.length - 1])
      }
      
      // Create a new array to ensure React sees it as changed
      const newMeals = data ? [...data] : []
      console.log('📝 Setting meals state with', newMeals.length, 'meals')
      setMeals(newMeals)
      
      console.log('✅ Meals state updated')
    } catch (err) {
      console.error('❌ Exception in getMeals:', err)
    }
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
          <GhostButton onClick={() => router.push('/connections')}>Friends</GhostButton>
          <GhostButton onClick={() => router.push('/profile')}>Profile</GhostButton>
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
        title="Recorded Meals" 
        subtitle={meals.length > 0 ? `${meals.length} meal${meals.length === 1 ? '' : 's'} logged today` : 'No meals logged yet'}
      >
        {meals.length === 0 ? (
          <div className="text-center py-12 text-[#5E7F73]">
            <p className="text-lg">📸 Upload your first meal to get started!</p>
            <p className="text-sm mt-2">Track your nutrition journey, one photo at a time</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {meals.map(meal => (
              <div 
                key={meal.id} 
                className="bg-white border-2 border-[#D9F1E3] rounded-2xl overflow-hidden hover:shadow-xl hover:border-[#2BAA66] transition-all duration-300 hover:-translate-y-1"
              >
                {/* Image Section */}
                {meal.image_url ? (
                  <div className="relative h-48 bg-gradient-to-br from-gray-50 to-gray-100">
                    <img 
                      src={meal.image_url} 
                      alt={meal.detected_food_name}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        e.currentTarget.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"%3E%3Crect fill="%23F1FBF6" width="200" height="200"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-family="system-ui" font-size="60" fill="%235E7F73"%3E🍽️%3C/text%3E%3C/svg%3E'
                      }}
                    />
                    {/* Score Badge */}
                    <div className="absolute top-3 right-3 bg-gradient-to-br from-[#2BAA66] to-[#27A05F] text-white font-bold px-3 py-1.5 rounded-full shadow-lg flex items-center gap-1">
                      <span className="text-sm">{meal.healthiness_score}</span>
                      <span className="text-xs opacity-75">/100</span>
                    </div>
                    {/* Category Badge */}
                    <div className="absolute bottom-3 left-3 bg-white/90 backdrop-blur-sm px-3 py-1 rounded-full shadow-md">
                      <span className="text-xs font-semibold text-[#0B3B29] capitalize">
                        {meal.food_category}
                      </span>
                    </div>
                  </div>
                ) : (
                  <div className="h-48 bg-gradient-to-br from-[#F1FBF6] to-[#D9F1E3] flex items-center justify-center">
                    <span className="text-6xl">🍽️</span>
                  </div>
                )}
                
                {/* Content Section */}
                <div className="p-4 space-y-2">
                  <h4 className="font-bold text-[#0B3B29] text-lg capitalize line-clamp-1">
                    {meal.detected_food_name}
                  </h4>
                  
                  <div className="flex items-center justify-between text-xs text-[#5E7F73]">
                    {meal.logged_at && (
                      <span className="flex items-center gap-1">
                        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        {new Date(meal.logged_at).toLocaleTimeString('en-US', { 
                          hour: 'numeric', 
                          minute: '2-digit',
                          hour12: true 
                        })}
                      </span>
                    )}
                    {meal.calories && (
                      <span className="font-medium text-[#2BAA66]">
                        {meal.calories} cal
                      </span>
                    )}
                  </div>

                  {/* Meal Type Tag */}
                  {meal.meal_type && (
                    <div className="pt-2">
                      <span className="inline-block bg-[#F1FBF6] text-[#2BAA66] text-xs font-semibold px-3 py-1 rounded-full capitalize">
                        {meal.meal_type}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </Section>

      <Section
        title="Add a Meal"
        subtitle="Take a photo or upload an image of your food"
      >
        <div className="space-y-4">
          {/* Upload Status Messages */}
          {uploading && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
              <p className="text-blue-700 font-semibold">Uploading and analyzing your meal...</p>
            </div>
          )}
          
          {uploadError && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
              <p className="text-red-700">{uploadError}</p>
            </div>
          )}

          {/* Upload Box - Clickable */}
          <button
            onClick={() => uploadRef.current?.click()}
            disabled={uploading}
            className="w-full bg-white border-4 border-[#2BAA66] rounded-2xl p-12 hover:bg-[#F1FBF6] transition-all cursor-pointer group disabled:opacity-50 disabled:cursor-not-allowed"
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
            disabled={uploading}
            className="w-full bg-[#2BAA66] text-white px-8 py-4 rounded-xl font-semibold text-lg hover:bg-[#27A05F] transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-1 flex items-center justify-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
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
      <button
        onClick={() => setIsChatOpen(true)}
        className="fixed bottom-6 right-6 bg-[#2BAA66] text-white p-4 rounded-full shadow-lg hover:bg-[#27A05F] hover:scale-110 transition-all z-30"
        aria-label="Open chat"
      >
        <MessageCircle size={24} />
      </button>

      {/* Chat Dialog */}
      <ChatDialog isOpen={isChatOpen} onClose={() => setIsChatOpen(false)} />
    </>
  )
}
