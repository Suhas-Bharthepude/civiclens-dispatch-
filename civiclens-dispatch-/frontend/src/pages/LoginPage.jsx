import { useState } from 'react'
import { Siren, AlertTriangle, Loader2 } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { cn } from '../lib/cn'

const INPUT_CLASS = cn(
  'w-full px-3 py-2.5 text-body rounded-lg',
  'bg-surface-2 border border-border',
  'text-text-primary placeholder:text-text-muted',
  'focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent/30',
  'disabled:opacity-50 transition-colors',
)

const LoginPage = () => {
  const [username, setUsername] = useState('dispatcher')
  const [password, setPassword] = useState('dispatch123')
  const [error,    setError]    = useState(null)
  const [loading,  setLoading]  = useState(false)

  const { login } = useAuth()

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!username.trim() || !password.trim()) {
      setError('Username and password are required')
      return
    }
    setLoading(true)
    setError(null)
    try {
      await login(username.trim(), password)
    } catch (err) {
      setError(err.message || 'Login failed — check your credentials')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-6">
      <div className="w-full max-w-sm">

        {/* Card */}
        <div className="bg-surface border border-border rounded-xl p-8 flex flex-col gap-6">

          {/* Branding */}
          <div className="flex flex-col items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-accent flex items-center justify-center">
              <Siren size={24} className="text-accent-fg" />
            </div>
            <div className="text-center">
              <h1 className="text-display text-text-primary">CivicLens Dispatch</h1>
              <p className="text-body text-text-muted mt-1">AI-Powered Incident Management</p>
            </div>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">

            {error && (
              <div
                role="alert"
                className="flex items-start gap-2 px-3 py-2.5 rounded-lg bg-red-950/60 border border-red-800 text-red-300 text-body"
              >
                <AlertTriangle size={15} className="flex-shrink-0 mt-0.5" />
                {error}
              </div>
            )}

            <div className="flex flex-col gap-1.5">
              <label htmlFor="username" className="text-caption text-text-muted uppercase tracking-widest">
                Username
              </label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={e => setUsername(e.target.value)}
                placeholder="Enter your username"
                autoComplete="username"
                autoFocus
                disabled={loading}
                className={INPUT_CLASS}
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="password" className="text-caption text-text-muted uppercase tracking-widest">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="Enter your password"
                autoComplete="current-password"
                disabled={loading}
                className={INPUT_CLASS}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className={cn(
                'flex items-center justify-center gap-2 h-10 w-full rounded-lg mt-1',
                'bg-accent text-accent-fg font-medium text-body',
                'hover:bg-amber-400 transition-colors',
                'disabled:opacity-50 disabled:pointer-events-none',
              )}
            >
              {loading ? (
                <><Loader2 size={15} className="animate-spin" /> Signing in…</>
              ) : (
                'Sign In'
              )}
            </button>

          </form>

          <p className="text-caption text-text-muted text-center">
            For life-threatening emergencies always call 911
          </p>
        </div>
      </div>
    </div>
  )
}

export default LoginPage
