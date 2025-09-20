import { AuthLayout } from '../components/auth-layout'
import { Button } from '../components/button'
import { Field, Label } from '../components/fieldset'
import { Heading } from '../components/heading'
import { Input } from '../components/input'
import { Strong, Text, TextLink } from '../components/text'
import { useEffect, useState } from 'react'

export default function ResetPassword() {
  const [token, setToken] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [done, setDone] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    setToken(params.get('token') || '')
  }, [])

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError(null)
    if (!token) {
      setError('Missing token.')
      return
    }
    if (password.length < 6) {
      setError('Password must be at least 6 characters.')
      return
    }
    if (password !== confirm) {
      setError('Passwords do not match.')
      return
    }
    const res = await fetch('/api/reset-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ token, password })
    })
    const result = await res.json()
    if (result.success) {
      setDone(true)
    } else {
      setError(result.message || 'Reset failed')
    }
  }

  return (
    <AuthLayout>
      <form onSubmit={handleSubmit} className="grid w-full max-w-sm grid-cols-1 gap-8">
        <Heading>Reset your password</Heading>
        {!done ? (
          <>
            <Field>
              <Label>New Password</Label>
              <Input type="password" name="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
            </Field>
            <Field>
              <Label>Confirm Password</Label>
              <Input type="password" name="confirm" value={confirm} onChange={(e) => setConfirm(e.target.value)} required />
            </Field>
            {error && <Text className="text-red-600">{error}</Text>}
            <Button type="submit" className="w-full">Reset Password</Button>
            <Text>
              Remembered it? <TextLink href="/login"><Strong>Back to login</Strong></TextLink>
            </Text>
          </>
        ) : (
          <>
            <Text>Your password has been reset successfully.</Text>
            <Button href="/login" className="w-full">Go to Login</Button>
          </>
        )}
      </form>
    </AuthLayout>
  )
}
