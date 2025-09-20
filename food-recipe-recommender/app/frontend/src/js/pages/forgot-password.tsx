import { AuthLayout } from '../components/auth-layout'
import { Button } from '../components/button'
import { Field, Label } from '../components/fieldset'
import { Heading } from '../components/heading'
import { Input } from '../components/input'
import { Strong, Text, TextLink } from '../components/text'
import { useState } from 'react'

export default function ForgotPassword() {
  const [sent, setSent] = useState(false)
  const [devToken, setDevToken] = useState<string | null>(null)
  const [email, setEmail] = useState('')

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const res = await fetch('/api/forgot-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ email })
    })
    const result = await res.json()
    setSent(true)
    if (result.devResetToken) setDevToken(result.devResetToken)
  }

  return (
    <AuthLayout>
      <form onSubmit={handleSubmit} className="grid w-full max-w-sm grid-cols-1 gap-8">
        <Heading>Forgot your password?</Heading>
        <Text>Enter your email to receive a reset link.</Text>
        <Field>
          <Label>Email</Label>
          <Input type="email" name="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </Field>
        <Button type="submit" className="w-full">Send reset link</Button>
        {sent && (
          <div className="space-y-2">
            <Text>
              We’ve sent a reset link if the email exists.{' '}
              <TextLink href="/login"><Strong>Back to login</Strong></TextLink>
            </Text>
            {devToken && (
              <Text>
                Dev shortcut: <TextLink href={`/reset-password?token=${encodeURIComponent(devToken)}`}><Strong>Reset now</Strong></TextLink>
              </Text>
            )}
          </div>
        )}
      </form>
    </AuthLayout>
  )
}

