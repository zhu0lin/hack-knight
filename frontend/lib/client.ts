import { createBrowserClient } from '@supabase/ssr'

// Provide default values to prevent build/runtime errors
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://placeholder.supabase.co'
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'placeholder-key'

// Check if environment variables are properly configured
if (typeof window !== 'undefined' && supabaseUrl === 'https://placeholder.supabase.co') {
  console.error('⚠️ Supabase environment variables are not configured!')
  console.error('Please set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY')
}

export const supabase = createBrowserClient(supabaseUrl, supabaseAnonKey)