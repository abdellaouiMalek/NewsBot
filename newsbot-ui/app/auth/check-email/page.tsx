import Link from "next/link"
import { Brain } from "lucide-react"

export default function CheckEmailPage() {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="flex items-center justify-center gap-2 mb-8">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center">
            <Brain className="w-6 h-6 text-primary-foreground" />
          </div>
          <span className="text-2xl font-bold">NewsBot AI</span>
        </div>

        {/* Message Card */}
        <div className="bg-card border border-border rounded-lg p-8 text-center">
          <h1 className="text-2xl font-bold mb-2">Check Your Email</h1>
          <p className="text-muted-foreground mb-6">
            We've sent you a confirmation link. Please click it to verify your email and activate your account.
          </p>

          <div className="bg-accent/10 border border-accent/20 rounded-lg p-4 mb-6">
            <p className="text-sm text-accent">
              If you don't see the email in your inbox, please check your spam folder.
            </p>
          </div>

          <Link
            href="/auth/login"
            className="inline-block px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors font-medium"
          >
            Back to Login
          </Link>
        </div>
      </div>
    </div>
  )
}
