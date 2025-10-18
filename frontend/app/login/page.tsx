'use client'

import { useState } from 'react'
import { supabase } from '@/lib/client'
import { useRouter } from 'next/navigation'

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isLogin, setIsLogin] = useState(true)
  const [message, setMessage] = useState('')

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault()
    setMessage('')

    if (isLogin) {
      const { error } = await supabase.auth.signInWithPassword({ email, password })
      if (error) {
        setMessage(error.message)
      } else {
        setMessage('Login successful!')
        // Optionally redirect to home after login
        setTimeout(() => router.push('/'), 1000)
      }
    } else {
      const { error } = await supabase.auth.signUp({ email, password })
      if (error) {
        setMessage(error.message)
      } else {
        setMessage('Check your email for confirmation link!')
      }
    }
  }

  return (
    <main className="min-h-screen bg-[#F1FBF6] flex items-center justify-center px-6">
      <div className="bg-white border border-[#D9F1E3] rounded-2xl shadow-md w-full max-w-sm p-8 space-y-6">
        <h1 className="text-2xl font-bold text-center text-[#0B3B29]">
          {isLogin ? 'Sign in' : 'Create account'}
        </h1>

        <form onSubmit={handleAuth} className="space-y-4">
          <div>
            <label className="block text-sm text-[#5E7F73] mb-1">Email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full border border-[#D9F1E3] rounded-lg px-3 py-2 outline-none focus:border-[#2BAA66]"
            />
          </div>

          <div>
            <label className="block text-sm text-[#5E7F73] mb-1">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full border border-[#D9F1E3] rounded-lg px-3 py-2 outline-none focus:border-[#2BAA66]"
            />
          </div>

          {message && <p className="text-sm text-center text-red-600">{message}</p>}

          <button
            type="submit"
            className="w-full bg-[#2BAA66] text-white py-2.5 rounded-lg font-semibold hover:bg-[#27A05F] transition-all"
          >
            {isLogin ? 'Sign in' : 'Sign up'}
          </button>
        </form>

        <p className="text-center text-sm text-[#5E7F73]">
          {isLogin ? "Don't have an account?" : 'Already have an account?'}{' '}
          <button
            type="button"
            onClick={() => setIsLogin(!isLogin)}
            className="text-[#2BAA66] font-semibold underline"
          >
            {isLogin ? 'Sign up' : 'Sign in'}
          </button>
        </p>
      </div>
    </main>
  )
}
