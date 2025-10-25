'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { ArrowRight } from 'lucide-react';
import { useEffect, useState } from 'react';

function ProcessTimeline() {
  const [activeStep, setActiveStep] = useState(0);

  const steps = [
    {
      num: '01',
      title: 'Define',
      desc: 'Start by setting precise campaign goals and identifying your target audience personas. Map out the competitive landscape to understand differentiation opportunities and market positioning.',
      visual: (
        <div className="space-y-3">
          <div className="p-3 rounded-lg border border-blue-200 bg-gradient-to-br from-blue-50 to-indigo-50 animate-in fade-in slide-in-from-bottom-2 duration-500" style={{ animationDelay: '0ms', animationFillMode: 'backwards' }}>
            <div className="text-[11px] font-semibold text-blue-600 mb-1.5">GOAL</div>
            <div className="text-[13px] text-slate-700">Increase B2B sign-ups by 40%</div>
          </div>
          <div className="p-3 rounded-lg border border-purple-200 bg-gradient-to-br from-purple-50 to-pink-50 animate-in fade-in slide-in-from-bottom-2 duration-500" style={{ animationDelay: '100ms', animationFillMode: 'backwards' }}>
            <div className="text-[11px] font-semibold text-purple-600 mb-1.5">AUDIENCE</div>
            <div className="text-[13px] text-slate-700">Marketing Directors, mid-market SaaS</div>
          </div>
          <div className="flex gap-2 animate-in fade-in slide-in-from-bottom-2 duration-500" style={{ animationDelay: '200ms', animationFillMode: 'backwards' }}>
            {['HubSpot', 'Marketo', 'ActiveCampaign'].map((comp, idx) => (
              <div key={comp} className="px-2.5 py-1 rounded-md bg-slate-100 border border-slate-200 text-[11px] font-medium text-slate-600 hover:scale-105 transition-transform duration-200">
                {comp}
              </div>
            ))}
          </div>
        </div>
      )
    },
    {
      num: '02',
      title: 'Collect',
      desc: 'Omnisearch automatically gathers real-time signals from 15+ platforms including search engines, social media, and forums. Each signal is tagged, attributed to its source, and processed for relevance.',
      visual: (
        <div className="space-y-2.5">
          {[
            { platform: 'Google', signals: 247, color: 'blue' },
            { platform: 'LinkedIn', signals: 183, color: 'indigo' },
            { platform: 'Reddit', signals: 156, color: 'orange' },
            { platform: 'Twitter', signals: 142, color: 'cyan' },
            { platform: 'YouTube', signals: 119, color: 'red' }
          ].map((item, i) => (
            <div key={item.platform} className="flex items-center gap-3 animate-in fade-in slide-in-from-left-2 duration-500" style={{ animationDelay: `${i * 80}ms`, animationFillMode: 'backwards' }}>
              <div className="w-20 text-[12px] font-medium text-slate-700">{item.platform}</div>
              <div className="flex-1 h-1.5 bg-slate-200 rounded-full overflow-hidden">
                <div
                  className={`h-full bg-gradient-to-r from-${item.color}-500 to-${item.color}-600 rounded-full animate-in slide-in-from-left-full duration-1000`}
                  style={{
                    width: `${(item.signals / 250) * 100}%`,
                    animationDelay: `${i * 80 + 200}ms`,
                    animationFillMode: 'backwards'
                  }}
                />
              </div>
              <div className="w-12 text-[11px] font-semibold text-slate-600">{item.signals}</div>
            </div>
          ))}
        </div>
      )
    },
    {
      num: '03',
      title: 'Analyze',
      desc: 'Multiple frontier AI models process the collected intelligence in parallel, each bringing unique analytical capabilities. They identify patterns, extract insights, and synthesize findings into actionable intelligence.',
      visual: (
        <div className="space-y-3">
          {[
            { agent: 'Claude 4.5', task: 'Competitor Analysis', color: 'from-indigo-500 to-purple-500' },
            { agent: 'GPT-4', task: 'Audience Insights', color: 'from-emerald-500 to-teal-500' },
            { agent: 'Gemini Pro', task: 'Creative Patterns', color: 'from-blue-500 to-cyan-500' }
          ].map((item, i) => (
            <div key={item.agent} className="p-3 rounded-lg border border-border bg-white hover:shadow-md transition-all duration-300 animate-in fade-in slide-in-from-bottom-2 duration-500" style={{ animationDelay: `${i * 100}ms`, animationFillMode: 'backwards' }}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-[12px] font-semibold text-slate-700">{item.agent}</span>
                <span className="text-[10px] text-emerald-600 font-medium animate-pulse">ANALYZING</span>
              </div>
              <div className="h-1.5 w-full bg-gradient-to-r rounded-full animate-pulse" style={{ backgroundImage: `linear-gradient(to right, ${item.color})` }} />
              <div className="text-[11px] text-muted-foreground mt-2">{item.task}</div>
            </div>
          ))}
        </div>
      )
    },
    {
      num: '04',
      title: 'Generate',
      desc: 'AI synthesizes all insights into a comprehensive 2-page strategic brief with complete citation trails. Every recommendation is backed by verifiable data and linked directly to source signals.',
      visual: (
        <div className="space-y-2.5">
          <div className="p-4 rounded-lg bg-gradient-to-br from-slate-50 to-slate-100 border border-slate-200 hover:shadow-md transition-all duration-300 animate-in fade-in slide-in-from-bottom-2 duration-500" style={{ animationDelay: '0ms', animationFillMode: 'backwards' }}>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="text-[12px] font-semibold text-slate-700">Positioning & Messaging</div>
                <div className="text-[10px] text-slate-600 font-medium">32 citations</div>
              </div>
              <div className="space-y-1.5">
                <div className="h-1.5 w-full bg-slate-300 rounded animate-in slide-in-from-left-full duration-700" style={{ animationDelay: '100ms', animationFillMode: 'backwards' }} />
                <div className="h-1.5 w-5/6 bg-slate-300 rounded animate-in slide-in-from-left-full duration-700" style={{ animationDelay: '200ms', animationFillMode: 'backwards' }} />
                <div className="h-1.5 w-4/5 bg-slate-300 rounded animate-in slide-in-from-left-full duration-700" style={{ animationDelay: '300ms', animationFillMode: 'backwards' }} />
              </div>
            </div>
          </div>
          <div className="p-4 rounded-lg bg-gradient-to-br from-amber-50 to-orange-50 border border-amber-200 hover:shadow-md transition-all duration-300 animate-in fade-in slide-in-from-bottom-2 duration-500" style={{ animationDelay: '150ms', animationFillMode: 'backwards' }}>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="text-[12px] font-semibold text-slate-700">Hook Strategy & Objections</div>
                <div className="text-[10px] text-slate-600 font-medium">28 citations</div>
              </div>
              <div className="space-y-1.5">
                <div className="h-1.5 w-full bg-amber-300 rounded animate-in slide-in-from-left-full duration-700" style={{ animationDelay: '250ms', animationFillMode: 'backwards' }} />
                <div className="h-1.5 w-3/4 bg-amber-300 rounded animate-in slide-in-from-left-full duration-700" style={{ animationDelay: '350ms', animationFillMode: 'backwards' }} />
              </div>
            </div>
          </div>
        </div>
      )
    },
    {
      num: '05',
      title: 'Execute',
      desc: 'Export your strategic brief in multiple formats for different stakeholders and use cases. Launch campaigns with full confidence knowing every decision is backed by transparent, verifiable intelligence.',
      visual: (
        <div className="space-y-3">
          <div className="flex flex-wrap gap-2">
            {['PDF', 'Markdown', 'JSON', 'CSV', 'DOCX'].map((format, idx) => (
              <div key={format} className="px-3 py-1.5 rounded-md bg-gradient-to-br from-emerald-100 to-teal-50 border border-emerald-200 text-[11px] font-semibold text-emerald-700 hover:scale-110 transition-transform duration-200 animate-in fade-in zoom-in duration-300" style={{ animationDelay: `${idx * 60}ms`, animationFillMode: 'backwards' }}>
                {format}
              </div>
            ))}
          </div>
          <div className="p-3 rounded-lg border border-green-200 bg-gradient-to-br from-green-50 to-emerald-50 hover:shadow-md transition-all duration-300 animate-in fade-in slide-in-from-bottom-2 duration-500" style={{ animationDelay: '300ms', animationFillMode: 'backwards' }}>
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] font-semibold text-green-700">READY TO LAUNCH</span>
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            </div>
            <div className="text-[12px] text-slate-700">94 inline citations • 8 min generation time</div>
          </div>
        </div>
      )
    },
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveStep((prev) => (prev + 1) % steps.length);
    }, 4500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="max-w-5xl mx-auto">
      {/* Steps Tabs */}
      <div className="flex border-b border-border mb-8">
        {steps.map((step, i) => (
          <button
            key={i}
            onClick={() => setActiveStep(i)}
            className={`flex-1 pb-4 px-4 transition-all duration-300 relative ${
              i === activeStep
                ? 'opacity-100'
                : 'opacity-50 hover:opacity-75'
            }`}
          >
            <div className="text-center space-y-1">
              <div className="text-[11px] font-medium text-muted-foreground tracking-wider">
                {step.num}
              </div>
              <div className="text-[14px] font-semibold tracking-tight">
                {step.title}
              </div>
            </div>
            {i === activeStep && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-foreground" />
            )}
          </button>
        ))}
      </div>

      {/* Active Step Content */}
      <div className="grid md:grid-cols-2 gap-8 items-start">
        <div className="space-y-4">
          <div>
            <h3 className="text-[24px] font-semibold tracking-tight mb-2">
              {steps[activeStep].title}
            </h3>
            <p className="text-[15px] text-muted-foreground leading-relaxed">
              {steps[activeStep].desc}
            </p>
          </div>
        </div>

        <div className="p-6 rounded-xl border border-border bg-slate-50">
          <div
            key={activeStep}
            className="animate-in fade-in slide-in-from-right-2 duration-500"
          >
            {steps[activeStep].visual}
          </div>
        </div>
      </div>

    </div>
  );
}

export default function LandingPage() {
  const [scrollY, setScrollY] = useState(0);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY);
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };

    window.addEventListener('scroll', handleScroll);
    window.addEventListener('mousemove', handleMouseMove);

    return () => {
      window.removeEventListener('scroll', handleScroll);
      window.removeEventListener('mousemove', handleMouseMove);
    };
  }, []);

  return (
    <div className="min-h-screen bg-white text-foreground">
      {/* Navigation */}
      <nav
        className="fixed top-0 w-full z-50 transition-all duration-300"
        style={{
          background: scrollY > 20 ? 'rgba(255, 255, 255, 0.8)' : 'rgba(255, 255, 255, 0.6)',
          backdropFilter: 'blur(12px) saturate(180%)',
          WebkitBackdropFilter: 'blur(12px) saturate(180%)',
          borderBottom: scrollY > 20 ? '1px solid rgba(0, 0, 0, 0.06)' : '1px solid rgba(0, 0, 0, 0.03)',
        }}
      >
        <div className="container mx-auto px-6 h-14 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 group">
            <div className="w-5 h-5 bg-foreground rounded transition-transform duration-200 group-hover:scale-105" />
            <span className="font-semibold text-[15px]">Fieldforge</span>
          </Link>

          <div className="hidden md:flex items-center gap-8">
            <Link href="#features" className="text-[13px] text-muted-foreground hover:text-foreground transition-colors">
              Features
            </Link>
            <Link href="#product" className="text-[13px] text-muted-foreground hover:text-foreground transition-colors">
              Product
            </Link>
            <Link href="#pricing" className="text-[13px] text-muted-foreground hover:text-foreground transition-colors">
              Pricing
            </Link>
          </div>

          <div className="flex items-center gap-3">
            <Link href="/auth/login">
              <Button variant="ghost" size="sm" className="text-[13px] h-8 !px-4">
                Sign In
              </Button>
            </Link>
            <Link href="/auth/register">
              <Button size="sm" className="text-[13px] h-8 !px-6 bg-foreground text-background hover:bg-foreground/90">
                Get Started
              </Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative min-h-[70vh] flex items-center justify-center px-6 pt-20 pb-32 overflow-hidden">
        {/* Background with mouse interaction */}
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(99,102,241,0.08),transparent_50%),radial-gradient(circle_at_70%_80%,rgba(14,165,233,0.08),transparent_50%)]" />
        <div
          className="absolute inset-0 opacity-50 transition-opacity duration-300"
          style={{
            background: `radial-gradient(circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(99,102,241,0.15), transparent 25%)`,
          }}
        />
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808008_1px,transparent_1px),linear-gradient(to_bottom,#80808008_1px,transparent_1px)] bg-[size:64px_64px]" />

        <div className="container mx-auto max-w-[920px] relative">
          <div className="space-y-7 text-center">
            <h1 className="text-[52px] md:text-[68px] font-semibold tracking-[-0.04em] leading-[1.2]">
              Intelligence-driven
              <br />
              campaign generation
            </h1>

            <p className="text-[17px] md:text-[19px] text-muted-foreground max-w-[680px] mx-auto leading-[1.6]">
              Transform campaign strategy from guesswork to evidence. Mine 15+ platforms, synthesize with AI agents, generate strategic briefs with receipts for every decision.
            </p>

            <div className="pt-3">
              <Link href="/auth/register">
                <Button className="h-9 !px-8 text-[13px] bg-foreground text-background hover:bg-foreground/90 shadow-lg hover:shadow-xl transition-all duration-200">
                  Start building free
                  <ArrowRight className="ml-2 h-3.5 w-3.5" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 px-6">
        <div className="container mx-auto max-w-[1100px]">
          <div className="text-center mb-16">
            <h2 className="text-[40px] md:text-[48px] font-semibold tracking-[-0.03em] leading-[1.2] mb-4">
              Evidence-backed campaigns
            </h2>
            <p className="text-[16px] text-muted-foreground max-w-[600px] mx-auto leading-[1.6]">
              Real-time intelligence from 15+ platforms with full citation trails
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
            {/* Card 1 - Platform Intelligence */}
            <div className="group p-8 rounded-xl border border-border bg-white hover:shadow-xl transition-all duration-300">
              <div className="space-y-4">
                {/* Platform Logos */}
                <div className="flex flex-wrap gap-2">
                  {['Google', 'Meta', 'LinkedIn', 'TikTok', 'YouTube', 'Reddit', 'Pinterest'].map((platform) => (
                    <div
                      key={platform}
                      className="px-3 py-1.5 rounded-md bg-gradient-to-br from-slate-100 to-slate-50 border border-slate-200 text-[11px] font-medium text-slate-700"
                    >
                      {platform}
                    </div>
                  ))}
                  <div className="px-3 py-1.5 rounded-md bg-gradient-to-br from-blue-100 to-blue-50 border border-blue-200 text-[11px] font-semibold text-blue-700">
                    +8 more
                  </div>
                </div>
                <div>
                  <h3 className="text-[18px] font-semibold mb-2">Omnisearch Intelligence</h3>
                  <p className="text-[14px] text-muted-foreground leading-[1.7]">
                    Mine real-time signals from 15+ platforms with automatic tagging and source attribution
                  </p>
                </div>
              </div>
            </div>

            {/* Card 2 - AI Analysis */}
            <div className="group p-8 rounded-xl border border-border bg-white hover:shadow-xl transition-all duration-300">
              <div className="space-y-4">
                <div className="space-y-2.5">
                  <div className="flex items-center gap-2">
                    <div className="h-1.5 flex-1 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full" />
                    <span className="text-[11px] font-medium text-slate-600">Claude 4.5</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="h-1.5 flex-1 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-full" />
                    <span className="text-[11px] font-medium text-slate-600">GPT-4</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="h-1.5 flex-1 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full" />
                    <span className="text-[11px] font-medium text-slate-600">Gemini Pro</span>
                  </div>
                </div>
                <div>
                  <h3 className="text-[18px] font-semibold mb-2">Multi-Agent Analysis</h3>
                  <p className="text-[14px] text-muted-foreground leading-[1.7]">
                    Multiple AI models analyze competitors, audiences, and trends in parallel
                  </p>
                </div>
              </div>
            </div>

            {/* Card 3 - Citations */}
            <div className="group p-8 rounded-xl border border-border bg-white hover:shadow-xl transition-all duration-300">
              <div className="space-y-4">
                <div className="space-y-2">
                  {[85, 60, 92, 75].map((width, i) => (
                    <div key={i} className="flex items-center gap-2">
                      <div
                        className="h-2 bg-gradient-to-r from-amber-400 to-orange-400 rounded-full"
                        style={{ width: `${width}%` }}
                      />
                      <svg className="w-3 h-3 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                      </svg>
                    </div>
                  ))}
                </div>
                <div>
                  <h3 className="text-[18px] font-semibold mb-2">Full Citation Trails</h3>
                  <p className="text-[14px] text-muted-foreground leading-[1.7]">
                    Every recommendation links directly to source signals for complete transparency
                  </p>
                </div>
              </div>
            </div>

            {/* Card 4 - Strategic Briefs */}
            <div className="group p-8 rounded-xl border border-border bg-white hover:shadow-xl transition-all duration-300">
              <div className="space-y-4">
                <div className="space-y-2">
                  <div className="p-3 rounded-lg bg-gradient-to-br from-slate-50 to-slate-100 border border-slate-200">
                    <div className="space-y-1.5">
                      <div className="h-2 w-full bg-slate-300 rounded" />
                      <div className="h-2 w-3/4 bg-slate-300 rounded" />
                      <div className="h-2 w-5/6 bg-slate-300 rounded" />
                    </div>
                  </div>
                  <div className="p-3 rounded-lg bg-gradient-to-br from-slate-50 to-slate-100 border border-slate-200">
                    <div className="space-y-1.5">
                      <div className="h-2 w-full bg-slate-300 rounded" />
                      <div className="h-2 w-4/5 bg-slate-300 rounded" />
                    </div>
                  </div>
                </div>
                <div>
                  <h3 className="text-[18px] font-semibold mb-2">2-Page Strategic Briefs</h3>
                  <p className="text-[14px] text-muted-foreground leading-[1.7]">
                    Dense, actionable briefs with positioning, messaging, and KPIs
                  </p>
                </div>
              </div>
            </div>

            {/* Card 5 - Export */}
            <div className="group p-8 rounded-xl border border-border bg-white hover:shadow-xl transition-all duration-300">
              <div className="space-y-4">
                <div className="flex flex-wrap gap-2">
                  {['PDF', 'MD', 'JSON', 'CSV', 'DOCX'].map((format) => (
                    <div
                      key={format}
                      className="px-3 py-1.5 rounded-md bg-gradient-to-br from-emerald-100 to-teal-50 border border-emerald-200 text-[11px] font-semibold text-emerald-700"
                    >
                      {format}
                    </div>
                  ))}
                </div>
                <div>
                  <h3 className="text-[18px] font-semibold mb-2">Export Everything</h3>
                  <p className="text-[14px] text-muted-foreground leading-[1.7]">
                    Multiple format exports with no vendor lock-in
                  </p>
                </div>
              </div>
            </div>

            {/* Card 6 - Real-time */}
            <div className="group p-8 rounded-xl border border-border bg-white hover:shadow-xl transition-all duration-300">
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <div className="relative">
                    <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
                    <div className="absolute inset-0 w-3 h-3 bg-green-500 rounded-full animate-ping" />
                  </div>
                  <span className="text-[12px] font-semibold text-green-700 uppercase tracking-wide">Live</span>
                </div>
                <div>
                  <h3 className="text-[18px] font-semibold mb-2">Real-Time Data</h3>
                  <p className="text-[14px] text-muted-foreground leading-[1.7]">
                    Current competitor and audience signals updated continuously
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Feature 1: Omnisearch Intelligence */}
      <section className="py-32 px-6 border-t border-border">
        <div className="container mx-auto max-w-[1100px]">
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <div className="space-y-6">
              <div className="inline-block px-3 py-1 rounded-full bg-blue-100 text-blue-700 text-[12px] font-semibold uppercase tracking-wide">
                Platform Intelligence
              </div>
              <h2 className="text-[40px] md:text-[48px] font-semibold tracking-[-0.03em] leading-[1.2]">
                Stop guessing. Start with evidence.
              </h2>
              <p className="text-[17px] text-muted-foreground leading-[1.7]">
                Fieldforge mines real-time intelligence from Google, Meta, LinkedIn, TikTok, YouTube, Reddit, and Pinterest. Every strategic recommendation comes with direct links to source signals. No more justifying campaigns with outdated playbooks.
              </p>
              <div className="space-y-4 pt-4">
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <svg className="w-3.5 h-3.5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div>
                    <h4 className="text-[15px] font-semibold mb-1">15+ Platform Coverage</h4>
                    <p className="text-[14px] text-muted-foreground leading-[1.6]">
                      Automated collection from social media, search engines, and content platforms with intelligent categorization
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <svg className="w-3.5 h-3.5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div>
                    <h4 className="text-[15px] font-semibold mb-1">Automatic Source Attribution</h4>
                    <p className="text-[14px] text-muted-foreground leading-[1.6]">
                      Every insight tagged with platform, timestamp, and direct link for instant verification
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <svg className="w-3.5 h-3.5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div>
                    <h4 className="text-[15px] font-semibold mb-1">Real-Time Updates</h4>
                    <p className="text-[14px] text-muted-foreground leading-[1.6]">
                      Continuous monitoring ensures you're working with current competitor and audience signals
                    </p>
                  </div>
                </div>
              </div>
            </div>
            <div className="relative">
              <div className="absolute -inset-4 bg-gradient-to-br from-blue-100/50 to-purple-100/50 rounded-2xl blur-2xl" />
              <div className="relative p-8 rounded-xl border border-border bg-white shadow-xl">
                <div className="space-y-3">
                  <div className="flex flex-wrap gap-2">
                    {['Google', 'Meta', 'LinkedIn', 'TikTok', 'YouTube', 'Reddit', 'Pinterest', 'Twitter', 'Instagram'].map((platform, i) => (
                      <div
                        key={platform}
                        className="px-3 py-2 rounded-lg bg-gradient-to-br from-slate-100 to-slate-50 border border-slate-200 text-[13px] font-medium text-slate-700 animate-in fade-in duration-700"
                        style={{ animationDelay: `${i * 100}ms`, animationFillMode: 'backwards' }}
                      >
                        {platform}
                      </div>
                    ))}
                    <div className="px-3 py-2 rounded-lg bg-gradient-to-br from-blue-100 to-blue-50 border border-blue-200 text-[13px] font-semibold text-blue-700">
                      +6 more
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Feature 2: Multi-Agent Analysis */}
      <section className="py-32 px-6 border-t border-border">
        <div className="container mx-auto max-w-[1100px]">
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <div className="space-y-6">
              <div className="inline-block px-3 py-1 rounded-full bg-purple-100 text-purple-700 text-[12px] font-semibold uppercase tracking-wide">
                AI Analysis
              </div>
              <h2 className="text-[40px] md:text-[48px] font-semibold tracking-[-0.03em] leading-[1.2]">
                Multi-agent intelligence synthesis
              </h2>
              <p className="text-[17px] text-muted-foreground leading-[1.7]">
                Claude Sonnet 4.5, GPT-4, and Gemini Pro analyze signals in parallel across competitors, audiences, messaging, and creative patterns. Independent review surfaces conflicting insights for comprehensive, unbiased strategic recommendations.
              </p>
              <div className="space-y-4 pt-4">
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-purple-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <svg className="w-3.5 h-3.5 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div>
                    <h4 className="text-[15px] font-semibold mb-1">Parallel Processing</h4>
                    <p className="text-[14px] text-muted-foreground leading-[1.6]">
                      Three leading AI models analyze your campaign simultaneously for faster, more comprehensive insights
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-purple-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <svg className="w-3.5 h-3.5 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div>
                    <h4 className="text-[15px] font-semibold mb-1">Cross-Verification</h4>
                    <p className="text-[14px] text-muted-foreground leading-[1.6]">
                      Independent agent reviews validate findings and surface disagreements for balanced perspective
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-purple-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <svg className="w-3.5 h-3.5 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div>
                    <h4 className="text-[15px] font-semibold mb-1">Comprehensive Coverage</h4>
                    <p className="text-[14px] text-muted-foreground leading-[1.6]">
                      Analyzes competitors, target audiences, messaging frameworks, and creative patterns
                    </p>
                  </div>
                </div>
              </div>
            </div>
            <div className="relative">
              <div className="absolute -inset-4 bg-gradient-to-br from-purple-100/50 to-pink-100/50 rounded-2xl blur-2xl" />
              <div className="relative p-8 rounded-xl border border-border bg-white shadow-xl space-y-4">
                {[
                  { name: 'Claude 4.5', color: 'from-indigo-500 to-purple-500', delay: 0 },
                  { name: 'GPT-4', color: 'from-emerald-500 to-teal-500', delay: 200 },
                  { name: 'Gemini Pro', color: 'from-blue-500 to-cyan-500', delay: 400 },
                ].map((ai) => (
                  <div key={ai.name} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-[13px] font-semibold text-slate-700">{ai.name}</span>
                      <span className="text-[12px] text-slate-500">Analyzing...</span>
                    </div>
                    <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                      <div
                        className={`h-full bg-gradient-to-r ${ai.color} rounded-full animate-in slide-in-from-left duration-1000`}
                        style={{ animationDelay: `${ai.delay}ms`, animationFillMode: 'backwards' }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Feature 3: Citation Trails */}
      <section className="py-32 px-6 border-t border-border">
        <div className="container mx-auto max-w-[1100px]">
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <div className="space-y-6">
              <div className="inline-block px-3 py-1 rounded-full bg-amber-100 text-amber-700 text-[12px] font-semibold uppercase tracking-wide">
                Transparency
              </div>
              <h2 className="text-[40px] md:text-[48px] font-semibold tracking-[-0.03em] leading-[1.2]">
                Every decision, fully receipted
              </h2>
              <p className="text-[17px] text-muted-foreground leading-[1.7]">
                Every strategic recommendation in your brief includes inline citations linking directly to source signals. Click through to verify, share with stakeholders, or dive deeper into the intelligence behind each decision.
              </p>
              <div className="space-y-4 pt-4">
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-amber-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <svg className="w-3.5 h-3.5 text-amber-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div>
                    <h4 className="text-[15px] font-semibold mb-1">Inline Citations</h4>
                    <p className="text-[14px] text-muted-foreground leading-[1.6]">
                      Every claim, insight, and recommendation tagged with direct source links
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-amber-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <svg className="w-3.5 h-3.5 text-amber-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div>
                    <h4 className="text-[15px] font-semibold mb-1">One-Click Verification</h4>
                    <p className="text-[14px] text-muted-foreground leading-[1.6]">
                      Instant access to original source material for stakeholder reviews
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-amber-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <svg className="w-3.5 h-3.5 text-amber-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div>
                    <h4 className="text-[15px] font-semibold mb-1">Full Audit Trail</h4>
                    <p className="text-[14px] text-muted-foreground leading-[1.6]">
                      Complete transparency from signal collection through final recommendations
                    </p>
                  </div>
                </div>
              </div>
            </div>
            <div className="relative">
              <div className="absolute -inset-4 bg-gradient-to-br from-amber-100/50 to-orange-100/50 rounded-2xl blur-2xl" />
              <div className="relative p-8 rounded-xl border border-border bg-white shadow-xl space-y-3">
                {[
                  { width: '85%', delay: 0 },
                  { width: '60%', delay: 150 },
                  { width: '92%', delay: 300 },
                  { width: '75%', delay: 450 },
                ].map((bar, i) => (
                  <div
                    key={i}
                    className="flex items-center gap-3 animate-in fade-in slide-in-from-left duration-700"
                    style={{ animationDelay: `${bar.delay}ms`, animationFillMode: 'backwards' }}
                  >
                    <div className="h-2.5 bg-gradient-to-r from-amber-400 to-orange-400 rounded-full" style={{ width: bar.width }} />
                    <svg className="w-4 h-4 text-amber-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                    </svg>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Feature 4: Strategic Briefs */}
      <section className="py-32 px-6 border-t border-border">
        <div className="container mx-auto max-w-[1100px]">
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <div className="space-y-6 order-2 md:order-1">
              <div className="inline-block px-3 py-1 rounded-full bg-slate-100 text-slate-700 text-[12px] font-semibold uppercase tracking-wide">
                Strategic Output
              </div>
              <h2 className="text-[40px] md:text-[48px] font-semibold tracking-[-0.03em] leading-[1.2]">
                Dense briefs, not bloated reports
              </h2>
              <p className="text-[17px] text-muted-foreground leading-[1.7]">
                Get actionable 2-page strategic briefs with positioning, messaging pillars, hook frameworks, objection handling, and KPIs. Each insight includes inline citations linking directly to source signals. Execute immediately, no thesis required.
              </p>
              <div className="space-y-4 pt-4">
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-slate-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <svg className="w-3.5 h-3.5 text-slate-700" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div>
                    <h4 className="text-[15px] font-semibold mb-1">2-Page Format</h4>
                    <p className="text-[14px] text-muted-foreground leading-[1.6]">
                      Concise, information-dense briefs that respect your time while delivering complete strategic guidance
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-slate-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <svg className="w-3.5 h-3.5 text-slate-700" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div>
                    <h4 className="text-[15px] font-semibold mb-1">Actionable Frameworks</h4>
                    <p className="text-[14px] text-muted-foreground leading-[1.6]">
                      Positioning statements, messaging pillars, hook frameworks, objection handling, and KPI targets ready to implement
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-slate-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <svg className="w-3.5 h-3.5 text-slate-700" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div>
                    <h4 className="text-[15px] font-semibold mb-1">Fully Cited</h4>
                    <p className="text-[14px] text-muted-foreground leading-[1.6]">
                      Every recommendation includes inline citations so you can verify and dive deeper into the intelligence
                    </p>
                  </div>
                </div>
              </div>
            </div>
            <div className="relative order-1 md:order-2">
              <div className="absolute -inset-4 bg-gradient-to-br from-slate-100/50 to-gray-100/50 rounded-2xl blur-2xl" />
              <div className="relative p-8 rounded-xl border border-border bg-white shadow-xl space-y-3">
                {[
                  { lines: 3, delay: 0 },
                  { lines: 2, delay: 200 },
                  { lines: 3, delay: 400 },
                ].map((section, i) => (
                  <div
                    key={i}
                    className="p-4 rounded-lg bg-gradient-to-br from-slate-50 to-slate-100 border border-slate-200 animate-in fade-in slide-in-from-bottom duration-700"
                    style={{ animationDelay: `${section.delay}ms`, animationFillMode: 'backwards' }}
                  >
                    <div className="space-y-2">
                      {[...Array(section.lines)].map((_, j) => (
                        <div
                          key={j}
                          className="h-2 bg-slate-300 rounded"
                          style={{ width: j === section.lines - 1 ? '70%' : '100%' }}
                        />
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Feature 5: Export */}
      <section className="py-32 px-6 border-t border-border">
        <div className="container mx-auto max-w-[1100px]">
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <div className="space-y-6">
              <div className="inline-block px-3 py-1 rounded-full bg-emerald-100 text-emerald-700 text-[12px] font-semibold uppercase tracking-wide">
                Export & Integration
              </div>
              <h2 className="text-[40px] md:text-[48px] font-semibold tracking-[-0.03em] leading-[1.2]">
                Export everything, own your data
              </h2>
              <p className="text-[17px] text-muted-foreground leading-[1.7]">
                Export your strategic briefs and all underlying intelligence in PDF, Markdown, JSON, CSV, DOCX, or HTML. No vendor lock-in. Your data, your formats, your workflow. Integrate with existing tools or keep it simple with clean exports.
              </p>
              <div className="space-y-4 pt-4">
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-emerald-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <svg className="w-3.5 h-3.5 text-emerald-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div>
                    <h4 className="text-[15px] font-semibold mb-1">Multiple Formats</h4>
                    <p className="text-[14px] text-muted-foreground leading-[1.6]">
                      Export to PDF for presentations, Markdown for docs, JSON for integrations, CSV for analysis
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-emerald-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <svg className="w-3.5 h-3.5 text-emerald-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div>
                    <h4 className="text-[15px] font-semibold mb-1">No Lock-In</h4>
                    <p className="text-[14px] text-muted-foreground leading-[1.6]">
                      Complete data portability means you can take your intelligence anywhere, anytime
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-emerald-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <svg className="w-3.5 h-3.5 text-emerald-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div>
                    <h4 className="text-[15px] font-semibold mb-1">Workflow Integration</h4>
                    <p className="text-[14px] text-muted-foreground leading-[1.6]">
                      Use JSON exports to build custom integrations with your existing marketing stack
                    </p>
                  </div>
                </div>
              </div>
            </div>
            <div className="relative">
              <div className="absolute -inset-4 bg-gradient-to-br from-emerald-100/50 to-teal-100/50 rounded-2xl blur-2xl" />
              <div className="relative p-8 rounded-xl border border-border bg-white shadow-xl">
                <div className="flex flex-wrap gap-3">
                  {[
                    { format: 'PDF', color: 'from-red-100 to-red-50 border-red-200 text-red-700', delay: 0 },
                    { format: 'Markdown', color: 'from-blue-100 to-blue-50 border-blue-200 text-blue-700', delay: 100 },
                    { format: 'JSON', color: 'from-yellow-100 to-yellow-50 border-yellow-200 text-yellow-700', delay: 200 },
                    { format: 'CSV', color: 'from-green-100 to-green-50 border-green-200 text-green-700', delay: 300 },
                    { format: 'DOCX', color: 'from-indigo-100 to-indigo-50 border-indigo-200 text-indigo-700', delay: 400 },
                    { format: 'HTML', color: 'from-purple-100 to-purple-50 border-purple-200 text-purple-700', delay: 500 },
                  ].map((item) => (
                    <div
                      key={item.format}
                      className={`px-4 py-3 rounded-lg bg-gradient-to-br ${item.color} border text-[13px] font-semibold animate-in fade-in zoom-in duration-500`}
                      style={{ animationDelay: `${item.delay}ms`, animationFillMode: 'backwards' }}
                    >
                      {item.format}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Feature 6: Real-Time Data */}
      <section className="py-32 px-6 border-t border-border">
        <div className="container mx-auto max-w-[1100px]">
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <div className="space-y-6 order-2 md:order-1">
              <div className="inline-block px-3 py-1 rounded-full bg-green-100 text-green-700 text-[12px] font-semibold uppercase tracking-wide">
                Live Intelligence
              </div>
              <h2 className="text-[40px] md:text-[48px] font-semibold tracking-[-0.03em] leading-[1.2]">
                Always current, never stale
              </h2>
              <p className="text-[17px] text-muted-foreground leading-[1.7]">
                Continuous monitoring ensures you're working with current competitor and audience signals. Market conditions change fast—your intelligence should keep up. Real-time updates mean you catch trends early and adjust strategy based on what's happening now, not last quarter.
              </p>
              <div className="space-y-4 pt-4">
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <svg className="w-3.5 h-3.5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div>
                    <h4 className="text-[15px] font-semibold mb-1">Continuous Monitoring</h4>
                    <p className="text-[14px] text-muted-foreground leading-[1.6]">
                      Automated collection runs 24/7 across all platforms to capture emerging trends and competitor moves
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <svg className="w-3.5 h-3.5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div>
                    <h4 className="text-[15px] font-semibold mb-1">Trend Detection</h4>
                    <p className="text-[14px] text-muted-foreground leading-[1.6]">
                      Catch emerging patterns early with AI-powered analysis of signal velocity and sentiment shifts
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <svg className="w-3.5 h-3.5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div>
                    <h4 className="text-[15px] font-semibold mb-1">Fresh Insights</h4>
                    <p className="text-[14px] text-muted-foreground leading-[1.6]">
                      Never base decisions on outdated information—intelligence updates reflect current market reality
                    </p>
                  </div>
                </div>
              </div>
            </div>
            <div className="relative order-1 md:order-2">
              <div className="absolute -inset-4 bg-gradient-to-br from-green-100/50 to-emerald-100/50 rounded-2xl blur-2xl" />
              <div className="relative p-8 rounded-xl border border-border bg-white shadow-xl">
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 rounded-lg bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200">
                    <div className="flex items-center gap-3">
                      <div className="relative">
                        <div className="w-4 h-4 bg-green-500 rounded-full animate-pulse" />
                        <div className="absolute inset-0 w-4 h-4 bg-green-500 rounded-full animate-ping" />
                      </div>
                      <div>
                        <div className="text-[13px] font-semibold text-green-700">System Status</div>
                        <div className="text-[11px] text-green-600">All platforms monitored</div>
                      </div>
                    </div>
                    <div className="text-[12px] font-semibold text-green-700 uppercase tracking-wide">Live</div>
                  </div>

                  {[
                    { platform: 'Google Trends', status: 'Updated 2m ago', delay: 0 },
                    { platform: 'Social Signals', status: 'Updated 5m ago', delay: 150 },
                    { platform: 'Competitor Activity', status: 'Updated 8m ago', delay: 300 },
                  ].map((item) => (
                    <div
                      key={item.platform}
                      className="flex items-center justify-between p-3 rounded-lg bg-slate-50 border border-slate-200 animate-in fade-in slide-in-from-right duration-700"
                      style={{ animationDelay: `${item.delay}ms`, animationFillMode: 'backwards' }}
                    >
                      <span className="text-[13px] font-medium text-slate-700">{item.platform}</span>
                      <span className="text-[11px] text-slate-500">{item.status}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Process Section - Interactive */}
      <section id="product" className="relative py-32 px-6 border-t border-border">
        <div className="container mx-auto max-w-[1200px] relative">
          <div className="text-center mb-20">
            <h2 className="text-[40px] md:text-[48px] font-semibold tracking-[-0.03em] leading-[1.2] mb-4">
              From zero to strategic brief
            </h2>
            <p className="text-[16px] text-muted-foreground max-w-[600px] mx-auto leading-[1.6]">
              A systematic process that transforms market signals into actionable campaign strategy
            </p>
          </div>

          <ProcessTimeline />
        </div>
      </section>

      {/* Use Cases Section */}
      <section className="py-32 px-6 border-t border-border">
        <div className="container mx-auto max-w-[1100px]">
          <div className="text-center mb-16">
            <h2 className="text-[40px] md:text-[48px] font-semibold tracking-[-0.03em] leading-[1.2] mb-4">
              Built for teams that need evidence
            </h2>
            <p className="text-[16px] text-muted-foreground max-w-[600px] mx-auto leading-[1.6]">
              Marketing professionals who value data-driven decisions
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {[
              {
                title: 'Performance Marketers',
                desc: 'Build campaigns backed by verifiable data to justify every budget decision. Track competitor positioning, audience sentiment, and messaging trends across 15+ platforms.',
                benefits: [
                  'Justify budget allocation with cited sources',
                  'Demonstrate ROI with transparent intelligence',
                  'Respond to market changes in real-time'
                ],
                gradient: 'from-blue-500/10 to-indigo-500/5',
                accent: 'from-blue-500 to-indigo-600',
              },
              {
                title: 'Strategy Consultants',
                desc: 'Deliver client recommendations with full citation trails and source attribution. Present strategic briefs that showcase deep market research in minutes instead of weeks.',
                benefits: [
                  'Generate evidence-backed client deliverables',
                  'Export professional PDFs with inline citations',
                  'Scale research capacity without hiring'
                ],
                gradient: 'from-purple-500/10 to-pink-500/5',
                accent: 'from-purple-500 to-pink-600',
              },
              {
                title: 'Growth Teams',
                desc: 'Launch with confidence on limited budgets by making high-conviction strategic decisions. Skip expensive agencies and get strategic briefs based on live market intelligence.',
                benefits: [
                  'Reduce campaign launch time from weeks to hours',
                  'Avoid costly positioning mistakes early',
                  'Compete with larger teams through AI leverage'
                ],
                gradient: 'from-teal-500/10 to-cyan-500/5',
                accent: 'from-teal-500 to-cyan-600',
              },
              {
                title: 'Product Marketing',
                desc: 'Position new products with intelligence from real customer conversations and competitor analysis. Craft messaging that resonates based on proven patterns, not assumptions.',
                benefits: [
                  'Discover winning messaging from competitor analysis',
                  'Identify objections before launch from forums',
                  'Validate positioning with market data'
                ],
                gradient: 'from-amber-500/10 to-orange-500/5',
                accent: 'from-amber-500 to-orange-600',
              },
            ].map((useCase, i) => (
              <div
                key={i}
                className="group relative overflow-hidden rounded-xl border border-border bg-white transition-all duration-500 hover:shadow-2xl cursor-default"
              >
                <div className={`absolute inset-0 bg-gradient-to-br ${useCase.gradient} opacity-0 group-hover:opacity-100 transition-opacity duration-500`} />

                <div className="relative p-8 space-y-5">
                  <div className={`h-1 w-12 bg-gradient-to-r ${useCase.accent} rounded-full transition-all duration-300 group-hover:w-20`} />

                  <div>
                    <h3 className="text-[20px] font-semibold mb-2">{useCase.title}</h3>
                    <p className="text-[14px] text-muted-foreground leading-[1.7]">{useCase.desc}</p>
                  </div>

                  <div className="space-y-2 pt-2">
                    {useCase.benefits.map((benefit, idx) => (
                      <div key={idx} className="flex items-start gap-2.5">
                        <div className={`w-1 h-1 rounded-full bg-gradient-to-r ${useCase.accent} mt-2 flex-shrink-0`} />
                        <span className="text-[13px] text-slate-700 leading-[1.6]">{benefit}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section id="pricing" className="relative py-32 px-6 overflow-hidden border-t border-border">
        <div className="absolute inset-0 bg-gradient-to-br from-slate-50 via-blue-50/30 to-purple-50/20" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_30%,rgba(99,102,241,0.08),transparent_50%),radial-gradient(circle_at_70%_70%,rgba(14,165,233,0.08),transparent_50%)]" />

        <div className="container mx-auto max-w-[800px] text-center relative">
          <div className="space-y-7">
            <h2 className="text-[48px] md:text-[56px] font-semibold tracking-[-0.04em] leading-[1.2]">
              Start building smarter campaigns today
            </h2>

            <p className="text-[17px] text-muted-foreground leading-[1.6] max-w-[600px] mx-auto">
              Free campaign included. No credit card required. Export everything.
            </p>

            <div className="pt-3">
              <Link href="/auth/register">
                <Button className="h-9 !px-8 text-[13px] font-medium bg-foreground text-background hover:bg-foreground/90 shadow-xl hover:shadow-2xl transition-all duration-300">
                  Get started free
                  <ArrowRight className="ml-2 h-3.5 w-3.5" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative py-16 px-6 border-t border-border">
        <div className="absolute inset-0 bg-gradient-to-b from-muted/10 to-background" />

        <div className="container mx-auto max-w-[1100px] relative">
          <div className="grid grid-cols-2 md:grid-cols-12 gap-10 mb-12">
            <div className="col-span-2 md:col-span-4 space-y-4">
              <Link href="/" className="flex items-center gap-2 group w-fit">
                <div className="w-5 h-5 bg-foreground rounded" />
                <span className="font-semibold text-[15px]">Fieldforge</span>
              </Link>
              <p className="text-[13px] text-muted-foreground leading-[1.6] max-w-[260px]">
                Intelligence-driven campaign generation with AI multi-agent analysis
              </p>
            </div>

            <div className="col-span-1 md:col-span-2">
              <h3 className="text-[12px] font-semibold mb-3 uppercase tracking-wide">Product</h3>
              <ul className="space-y-2.5">
                {[
                  { label: 'Features', href: '#features' },
                  { label: 'How it works', href: '#product' },
                  { label: 'Pricing', href: '#pricing' },
                  { label: 'Documentation', href: '/docs' },
                ].map((link) => (
                  <li key={link.href}>
                    <Link href={link.href} className="text-[13px] text-muted-foreground hover:text-foreground transition-colors">
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            <div className="col-span-1 md:col-span-2">
              <h3 className="text-[12px] font-semibold mb-3 uppercase tracking-wide">Company</h3>
              <ul className="space-y-2.5">
                {[
                  { label: 'About', href: '/about' },
                  { label: 'Blog', href: '/blog' },
                  { label: 'Careers', href: '/careers' },
                  { label: 'Contact', href: '/contact' },
                ].map((link) => (
                  <li key={link.href}>
                    <Link href={link.href} className="text-[13px] text-muted-foreground hover:text-foreground transition-colors">
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            <div className="col-span-1 md:col-span-2">
              <h3 className="text-[12px] font-semibold mb-3 uppercase tracking-wide">Resources</h3>
              <ul className="space-y-2.5">
                {[
                  { label: 'Guides', href: '/guides' },
                  { label: 'Help Center', href: '/help' },
                  { label: 'Changelog', href: '/changelog' },
                  { label: 'Status', href: '/status' },
                ].map((link) => (
                  <li key={link.href}>
                    <Link href={link.href} className="text-[13px] text-muted-foreground hover:text-foreground transition-colors">
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            <div className="col-span-1 md:col-span-2">
              <h3 className="text-[12px] font-semibold mb-3 uppercase tracking-wide">Legal</h3>
              <ul className="space-y-2.5">
                {[
                  { label: 'Privacy', href: '/privacy' },
                  { label: 'Terms', href: '/terms' },
                  { label: 'Security', href: '/security' },
                ].map((link) => (
                  <li key={link.href}>
                    <Link href={link.href} className="text-[13px] text-muted-foreground hover:text-foreground transition-colors">
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="pt-8 border-t border-border">
            <div className="flex flex-col md:flex-row items-center justify-between gap-4">
              <p className="text-[12px] text-muted-foreground">© 2025 Fieldforge, Inc. All rights reserved.</p>
              <div className="flex items-center gap-6 text-[12px] text-muted-foreground">
                <span>SOC 2 Compliant</span>
                <span>•</span>
                <span>256-bit Encryption</span>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
