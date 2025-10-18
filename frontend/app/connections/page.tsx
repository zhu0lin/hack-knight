'use client'

import { useEffect, useState } from 'react'
import { supabase } from '@/lib/client'
import { useRouter } from 'next/navigation'
import { GhostButton } from '@/components/Buttons'
import { UserPlus, Users, Search, UserCheck, UserX } from 'lucide-react'

type Connection = {
  id: string
  user_id: string
  friend_id: string
  status: 'pending' | 'accepted' | 'blocked'
  created_at: string
  friend: {
    id: string
    full_name: string
    email: string
  }[]
}

type PendingRequest = {
  id: string
  user_id: string
  friend_id: string
  created_at: string
  requester: {
    id: string
    full_name: string
    email: string
  }[]
}

export default function ConnectionsPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [connections, setConnections] = useState<Connection[]>([])
  const [pendingRequests, setPendingRequests] = useState<PendingRequest[]>([])
  const [searchEmail, setSearchEmail] = useState('')
  const [searchResults, setSearchResults] = useState<any[]>([])
  const [searching, setSearching] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    loadConnections()
  }, [])

  const loadConnections = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser()
      if (!user) {
        setLoading(false)
        return
      }

      // Load accepted connections
      const { data: connectionsData } = await supabase
        .from('user_connections')
        .select(`
          id,
          user_id,
          friend_id,
          status,
          created_at,
          friend:friend_id (
            id,
            full_name,
            email
          )
        `)
        .eq('user_id', user.id)
        .eq('status', 'accepted')

      // Load pending requests (where user is the recipient)
      const { data: pendingData } = await supabase
        .from('user_connections')
        .select(`
          id,
          user_id,
          friend_id,
          created_at,
          requester:user_id (
            id,
            full_name,
            email
          )
        `)
        .eq('friend_id', user.id)
        .eq('status', 'pending')

      setConnections(connectionsData || [])
      setPendingRequests(pendingData || [])
      setLoading(false)
    } catch (error) {
      console.error('Error loading connections:', error)
      setMessage('Failed to load connections')
      setLoading(false)
    }
  }

  const searchUsers = async () => {
    if (!searchEmail.trim()) return

    setSearching(true)
    try {
      const { data: { user } } = await supabase.auth.getUser()
      if (!user) {
        setMessage('No user session')
        setSearching(false)
        return
      }

      // Search for users by email (excluding current user)
      const { data, error } = await supabase
        .from('users')
        .select('id, full_name, email')
        .ilike('email', `%${searchEmail}%`)
        .neq('id', user.id)

      if (error) throw error

      setSearchResults(data || [])
    } catch (error) {
      console.error('Search error:', error)
      setMessage('Failed to search users')
    } finally {
      setSearching(false)
    }
  }

  const sendConnectionRequest = async (friendId: string) => {
    try {
      const { data: { user } } = await supabase.auth.getUser()
      if (!user) {
        setMessage('No user session')
        return
      }

      const { error } = await supabase
        .from('user_connections')
        .insert({
          user_id: user.id,
          friend_id: friendId,
          status: 'pending'
        })

      if (error) throw error

      setMessage('Connection request sent!')
      setTimeout(() => setMessage(''), 3000)
      loadConnections() // Refresh to show updated state
    } catch (error) {
      console.error('Send request error:', error)
      setMessage('Failed to send connection request')
    }
  }

  const acceptConnection = async (connectionId: string) => {
    try {
      const { error } = await supabase
        .from('user_connections')
        .update({ status: 'accepted' })
        .eq('id', connectionId)

      if (error) throw error

      setMessage('Connection accepted!')
      setTimeout(() => setMessage(''), 3000)
      loadConnections()
    } catch (error) {
      console.error('Accept error:', error)
      setMessage('Failed to accept connection')
    }
  }

  const rejectConnection = async (connectionId: string) => {
    try {
      const { error } = await supabase
        .from('user_connections')
        .delete()
        .eq('id', connectionId)

      if (error) throw error

      setMessage('Connection rejected')
      setTimeout(() => setMessage(''), 3000)
      loadConnections()
    } catch (error) {
      console.error('Reject error:', error)
      setMessage('Failed to reject connection')
    }
  }

  const removeConnection = async (connectionId: string) => {
    try {
      const { error } = await supabase
        .from('user_connections')
        .delete()
        .eq('id', connectionId)

      if (error) throw error

      setMessage('Connection removed')
      setTimeout(() => setMessage(''), 3000)
      loadConnections()
    } catch (error) {
      console.error('Remove error:', error)
      setMessage('Failed to remove connection')
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
      <div className="bg-white border border-[#D9F1E3] rounded-2xl shadow-md w-full max-w-4xl p-8 space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold text-[#0B3B29]">Connections</h1>
          <GhostButton onClick={() => router.push('/')}>← Back to Home</GhostButton>
        </div>

        {message && (
          <p className={`text-sm text-center ${message.includes('success') || message.includes('sent') || message.includes('accepted') ? 'text-green-600' : 'text-red-600'}`}>
            {message}
          </p>
        )}

        {/* Search for New Connections */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-[#0B3B29]">Find Friends</h2>
          <div className="flex gap-2">
            <input
              type="email"
              value={searchEmail}
              onChange={(e) => setSearchEmail(e.target.value)}
              placeholder="Search by email..."
              className="flex-1 border border-[#D9F1E3] rounded-lg px-3 py-2 outline-none focus:border-[#2BAA66]"
            />
            <button
              onClick={searchUsers}
              disabled={searching || !searchEmail.trim()}
              className="bg-[#2BAA66] text-white px-4 py-2 rounded-lg font-semibold hover:bg-[#27A05F] transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <Search size={18} />
              {searching ? 'Searching...' : 'Search'}
            </button>
          </div>

          {/* Search Results */}
          {searchResults.length > 0 && (
            <div className="space-y-2">
              <h3 className="font-semibold text-[#0B3B29]">Search Results</h3>
              {searchResults.map((user) => (
                <div key={user.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-semibold text-[#0B3B29]">{user.full_name || 'No name'}</p>
                    <p className="text-sm text-[#5E7F73]">{user.email}</p>
                  </div>
                  <button
                    onClick={() => sendConnectionRequest(user.id)}
                    className="bg-[#2BAA66] text-white px-3 py-1 rounded-lg text-sm hover:bg-[#27A05F] transition-all flex items-center gap-1"
                  >
                    <UserPlus size={16} />
                    Connect
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Pending Requests */}
        {pendingRequests.length > 0 && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-[#0B3B29]">Pending Requests</h2>
            <div className="space-y-3">
              {pendingRequests.map((request) => (
                <div key={request.id} className="flex items-center justify-between p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <div>
                    <p className="font-semibold text-[#0B3B29]">{request.requester[0]?.full_name || 'No name'}</p>
                    <p className="text-sm text-[#5E7F73]">{request.requester[0]?.email}</p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => acceptConnection(request.id)}
                      className="bg-green-600 text-white px-3 py-1 rounded-lg text-sm hover:bg-green-700 transition-all flex items-center gap-1"
                    >
                      <UserCheck size={16} />
                      Accept
                    </button>
                    <button
                      onClick={() => rejectConnection(request.id)}
                      className="bg-red-600 text-white px-3 py-1 rounded-lg text-sm hover:bg-red-700 transition-all flex items-center gap-1"
                    >
                      <UserX size={16} />
                      Reject
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Your Connections */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-[#0B3B29]">Your Connections</h2>
          {connections.length === 0 ? (
            <p className="text-[#5E7F73] text-center py-8">No connections yet. Search for friends to get started!</p>
          ) : (
            <div className="space-y-3">
              {connections.map((connection) => (
                <div key={connection.id} className="flex items-center justify-between p-4 bg-green-50 border border-green-200 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-[#2BAA66] rounded-full flex items-center justify-center">
                      <Users className="text-white" size={20} />
                    </div>
                    <div>
                    <p className="font-semibold text-[#0B3B29]">{connection.friend[0]?.full_name || 'No name'}</p>
                    <p className="text-sm text-[#5E7F73]">{connection.friend[0]?.email}</p>
                    </div>
                  </div>
                  <button
                    onClick={() => removeConnection(connection.id)}
                    className="text-red-600 hover:text-red-800 transition-colors"
                  >
                    <UserX size={20} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </main>
  )
}
