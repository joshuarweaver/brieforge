'use client';

import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import Link from 'next/link';
import { toast } from 'sonner';

export default function RegisterPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { register } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    if (password.length < 6) {
      toast.error('Password must be at least 6 characters');
      return;
    }

    setIsLoading(true);

    try {
      await register({ email, password });
      toast.success('Account created successfully!');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to create account');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen grid md:grid-cols-2">
      {/* Left Column - Value Prop & Feature Blocks */}
      <div className="hidden md:flex flex-col px-8 lg:px-12 bg-slate-50 border-r border-border py-12">
        <div className="w-full space-y-16">
          {/* Top Section - Logo & Heading */}
          <div>
            <Link href="/" className="flex items-center gap-3 group w-fit mb-8">
              <div className="w-7 h-7 bg-foreground rounded" />
              <span className="font-semibold text-[18px]">Fieldforge</span>
            </Link>
            <div className="max-w-[50%]">
              <h1 className="text-[32px] font-semibold tracking-[-0.03em] leading-[1.2] mb-3">
                Intelligence-driven campaign strategy
              </h1>
              <p className="text-[15px] text-muted-foreground leading-[1.6]">
                Stop guessing. Generate evidence-backed strategic briefs with AI-powered intelligence from 15+ platforms.
              </p>
            </div>
          </div>

          {/* Feature Blocks */}
          <div className="grid grid-cols-2 gap-3">
            {/* Block 1 - Omnisearch */}
            <div className="p-4 rounded-xl border border-border bg-white hover:shadow-lg transition-all duration-300">
              <div className="space-y-3">
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <div className="px-2 py-0.5 rounded-md bg-blue-100 border border-blue-200 text-[10px] font-semibold text-blue-700">
                      Google
                    </div>
                    <div className="px-2 py-0.5 rounded-md bg-indigo-100 border border-indigo-200 text-[10px] font-semibold text-indigo-700">
                      LinkedIn
                    </div>
                    <div className="px-2 py-0.5 rounded-md bg-orange-100 border border-orange-200 text-[10px] font-semibold text-orange-700">
                      Reddit
                    </div>
                  </div>
                </div>
                <div>
                  <h3 className="text-[16px] font-semibold mb-1">Omnisearch Intelligence</h3>
                  <p className="text-[13px] text-muted-foreground leading-[1.6]">
                    Mine real-time signals from 15+ platforms with automatic tagging and source attribution
                  </p>
                </div>
              </div>
            </div>

            {/* Block 2 - AI Analysis */}
            <div className="p-6 rounded-xl border border-border bg-white hover:shadow-lg transition-all duration-300">
              <div className="space-y-3">
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <div className="h-1 flex-1 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full" />
                    <span className="text-[10px] font-medium text-slate-600">Claude 4.5</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="h-1 flex-1 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-full" />
                    <span className="text-[10px] font-medium text-slate-600">GPT-4</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="h-1 flex-1 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full" />
                    <span className="text-[10px] font-medium text-slate-600">Gemini Pro</span>
                  </div>
                </div>
                <div>
                  <h3 className="text-[16px] font-semibold mb-1">Multi-Agent Analysis</h3>
                  <p className="text-[13px] text-muted-foreground leading-[1.6]">
                    Multiple AI models analyze competitors, audiences, and trends in parallel
                  </p>
                </div>
              </div>
            </div>

            {/* Block 3 - Citations */}
            <div className="p-6 rounded-xl border border-border bg-white hover:shadow-lg transition-all duration-300">
              <div className="space-y-3">
                <div className="space-y-1.5">
                  {[85, 60, 92, 75].map((width, i) => (
                    <div key={i} className="flex items-center gap-2">
                      <div
                        className="h-1.5 bg-gradient-to-r from-amber-400 to-orange-400 rounded-full"
                        style={{ width: `${width}%` }}
                      />
                      <svg className="w-3 h-3 text-amber-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                      </svg>
                    </div>
                  ))}
                </div>
                <div>
                  <h3 className="text-[16px] font-semibold mb-1">Full Citation Trails</h3>
                  <p className="text-[13px] text-muted-foreground leading-[1.6]">
                    Every recommendation links directly to source signals for complete transparency
                  </p>
                </div>
              </div>
            </div>

            {/* Block 4 - Strategic Briefs */}
            <div className="p-6 rounded-xl border border-border bg-white hover:shadow-lg transition-all duration-300">
              <div className="space-y-3">
                <div className="space-y-1.5">
                  <div className="p-2 rounded-lg bg-gradient-to-br from-slate-50 to-slate-100 border border-slate-200">
                    <div className="space-y-1">
                      <div className="h-1 w-full bg-slate-300 rounded" />
                      <div className="h-1 w-3/4 bg-slate-300 rounded" />
                    </div>
                  </div>
                </div>
                <div>
                  <h3 className="text-[16px] font-semibold mb-1">2-Page Strategic Briefs</h3>
                  <p className="text-[13px] text-muted-foreground leading-[1.6]">
                    Dense, actionable briefs with positioning, messaging, and KPIs
                  </p>
                </div>
              </div>
            </div>

            {/* Block 5 - Export */}
            <div className="p-6 rounded-xl border border-border bg-white hover:shadow-lg transition-all duration-300">
              <div className="space-y-3">
                <div className="flex flex-wrap gap-1.5">
                  {['PDF', 'MD', 'JSON'].map((format) => (
                    <div
                      key={format}
                      className="px-2 py-0.5 rounded-md bg-gradient-to-br from-emerald-100 to-teal-50 border border-emerald-200 text-[10px] font-semibold text-emerald-700"
                    >
                      {format}
                    </div>
                  ))}
                </div>
                <div>
                  <h3 className="text-[16px] font-semibold mb-1">Export Everything</h3>
                  <p className="text-[13px] text-muted-foreground leading-[1.6]">
                    Download briefs in multiple formats with zero vendor lock-in
                  </p>
                </div>
              </div>
            </div>

            {/* Block 6 - Real-Time Data */}
            <div className="p-6 rounded-xl border border-border bg-white hover:shadow-lg transition-all duration-300">
              <div className="space-y-3">
                <div className="flex items-center justify-between p-2 rounded-lg bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                    <div className="text-[10px] font-semibold text-green-700">LIVE</div>
                  </div>
                </div>
                <div>
                  <h3 className="text-[16px] font-semibold mb-1">Always Current</h3>
                  <p className="text-[13px] text-muted-foreground leading-[1.6]">
                    Continuous monitoring ensures intelligence is never stale
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Right Column - Register Form */}
      <div className="flex items-center justify-center p-8 md:p-12 bg-white">
        <div className="w-full max-w-md space-y-8">
          <div>
            <h2 className="text-[28px] font-semibold tracking-tight mb-2">Create your account</h2>
            <p className="text-[14px] text-muted-foreground">
              Start building evidence-backed campaigns today
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-2">
              <Label htmlFor="email" className="text-[13px] font-medium">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={isLoading}
                className="h-9"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password" className="text-[13px] font-medium">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={isLoading}
                className="h-9"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirmPassword" className="text-[13px] font-medium">Confirm Password</Label>
              <Input
                id="confirmPassword"
                type="password"
                placeholder="••••••••"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                disabled={isLoading}
                className="h-9"
              />
            </div>

            <Button type="submit" className="w-full h-9 text-[13px] font-medium bg-foreground text-background hover:bg-foreground/90" disabled={isLoading}>
              {isLoading ? 'Creating account...' : 'Create account'}
            </Button>

            <p className="text-[13px] text-center text-muted-foreground">
              Already have an account?{' '}
              <Link href="/auth/login" className="text-foreground hover:underline font-medium">
                Sign in
              </Link>
            </p>
          </form>
        </div>
      </div>
    </div>
  );
}
