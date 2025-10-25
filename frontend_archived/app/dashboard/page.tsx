'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api';
import {
  Campaign,
  DashboardAnalytics,
  CampaignStatusResponse,
  IntelligenceQualityResponse,
  LLMUsageResponse,
  CompetitorsResponse,
  AudiencesResponse,
  ChannelsResponse
} from '@/lib/types';
import { Button } from '@/components/ui/button';
import { StatusBadge } from '@/components/StatusBadge';
import { LoadingScreen } from '@/components/LoadingScreen';
import Link from 'next/link';
import { Plus, ArrowRight } from 'lucide-react';
import { format } from 'date-fns';
import { Bar, BarChart, XAxis, YAxis, Pie, PieChart, Area, AreaChart, CartesianGrid } from 'recharts';
import { ChartContainer, ChartTooltip, ChartTooltipContent } from '@/components/ui/chart';

export default function DashboardPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/auth/login');
    }
  }, [user, isLoading, router]);

  const { data: campaigns, isLoading: campaignsLoading } = useQuery({
    queryKey: ['campaigns'],
    queryFn: async () => {
      const response = await api.get<Campaign[]>('/campaigns');
      return response.data;
    },
    enabled: !!user,
  });

  const { data: analytics, isLoading: analyticsLoading } = useQuery({
    queryKey: ['dashboard-analytics'],
    queryFn: async () => {
      const response = await api.get<DashboardAnalytics>('/analytics/dashboard');
      return response.data;
    },
    enabled: !!user,
  });

  const { data: campaignStatus } = useQuery({
    queryKey: ['campaign-status'],
    queryFn: async () => {
      const response = await api.get<CampaignStatusResponse>('/analytics/campaign-status');
      return response.data;
    },
    enabled: !!user,
  });

  const { data: intelligenceQuality } = useQuery({
    queryKey: ['intelligence-quality'],
    queryFn: async () => {
      const response = await api.get<IntelligenceQualityResponse>('/analytics/intelligence-quality');
      return response.data;
    },
    enabled: !!user,
  });

  const { data: llmUsage } = useQuery({
    queryKey: ['llm-usage'],
    queryFn: async () => {
      const response = await api.get<LLMUsageResponse>('/analytics/llm-usage');
      return response.data;
    },
    enabled: !!user,
  });

  const { data: competitors } = useQuery({
    queryKey: ['competitors'],
    queryFn: async () => {
      const response = await api.get<CompetitorsResponse>('/analytics/competitors');
      return response.data;
    },
    enabled: !!user,
  });

  const { data: audiences } = useQuery({
    queryKey: ['audiences'],
    queryFn: async () => {
      const response = await api.get<AudiencesResponse>('/analytics/audiences');
      return response.data;
    },
    enabled: !!user,
  });

  const { data: channels } = useQuery({
    queryKey: ['channels'],
    queryFn: async () => {
      const response = await api.get<ChannelsResponse>('/analytics/channels');
      return response.data;
    },
    enabled: !!user,
  });

  if (isLoading || !user) {
    return <LoadingScreen variant="fullPage" text="Loading dashboard..." />;
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="border-b border-border bg-white">
        <div className="container mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-8">
            <Link href="/" className="flex items-center gap-2 group">
              <div className="w-5 h-5 bg-foreground rounded" />
              <span className="font-semibold text-[15px]">Fieldforge</span>
            </Link>
            <div className="flex items-center gap-1">
              <div className="px-2 py-1 text-[13px] text-muted-foreground">
                {user.email}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/campaigns/new">
              <Button className="h-8 px-8 text-[13px] font-medium bg-foreground text-background hover:bg-foreground/90">
                <Plus className="h-4 w-4 mr-1.5" />
                New Campaign
              </Button>
            </Link>
            <Link href="/settings">
              <Button variant="ghost" className="h-8 px-4 text-[13px]">
                Settings
              </Button>
            </Link>
            <Button variant="ghost" className="h-8 px-4 text-[13px]" onClick={() => router.push('/auth/login')}>
              Logout
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-12 max-w-[1200px]">
        {/* Header with New Campaign Button */}
        <div className="flex justify-between items-center mb-8 pt-4">
          <h1 className="text-[40px] font-semibold tracking-[-0.03em]">Dashboard</h1>
          <Link href="/campaigns/new">
            <Button className="h-8 px-8 text-[13px] font-medium bg-foreground text-background hover:bg-foreground/90">
              <Plus className="h-4 w-4 mr-1.5" />
              New Campaign
            </Button>
          </Link>
        </div>

        {/* Stats Bar */}
        {analyticsLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="p-6 rounded-xl border border-border bg-white animate-pulse">
                <div className="space-y-3">
                  <div className="h-4 bg-slate-200 rounded w-24" />
                  <div className="h-10 bg-slate-200 rounded w-16" />
                  <div className="h-3 bg-slate-200 rounded w-20" />
                </div>
              </div>
            ))}
          </div>
        ) : analytics ? (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="p-6 rounded-xl border border-border bg-white hover:shadow-lg transition-all duration-300">
              <div className="space-y-3">
                <div className="text-[13px] text-muted-foreground font-medium">Total Campaigns</div>
                <div className="text-[32px] font-semibold tracking-tight">{analytics.stats.total_campaigns}</div>
                <div className="flex items-center gap-2 text-[12px]">
                  <div className={analytics.stats.campaigns_growth >= 0 ? "text-emerald-600 font-medium" : "text-red-600 font-medium"}>
                    {analytics.stats.campaigns_growth >= 0 ? '+' : ''}{analytics.stats.campaigns_growth}%
                  </div>
                  <div className="text-muted-foreground">vs last month</div>
                </div>
              </div>
            </div>

            <div className="p-6 rounded-xl border border-border bg-white hover:shadow-lg transition-all duration-300">
              <div className="space-y-3">
                <div className="text-[13px] text-muted-foreground font-medium">Signals Collected</div>
                <div className="text-[32px] font-semibold tracking-tight">{analytics.stats.total_signals}</div>
                <div className="flex items-center gap-2 text-[12px]">
                  <div className={analytics.stats.signals_growth >= 0 ? "text-emerald-600 font-medium" : "text-red-600 font-medium"}>
                    {analytics.stats.signals_growth >= 0 ? '+' : ''}{analytics.stats.signals_growth}%
                  </div>
                  <div className="text-muted-foreground">vs last month</div>
                </div>
              </div>
            </div>

            <div className="p-6 rounded-xl border border-border bg-white hover:shadow-lg transition-all duration-300">
              <div className="space-y-3">
                <div className="text-[13px] text-muted-foreground font-medium">AI Analyses</div>
                <div className="text-[32px] font-semibold tracking-tight">{analytics.stats.total_analyses}</div>
                <div className="flex items-center gap-2 text-[12px]">
                  <div className={analytics.stats.analyses_growth >= 0 ? "text-emerald-600 font-medium" : "text-red-600 font-medium"}>
                    {analytics.stats.analyses_growth >= 0 ? '+' : ''}{analytics.stats.analyses_growth}%
                  </div>
                  <div className="text-muted-foreground">vs last month</div>
                </div>
              </div>
            </div>

            <div className="p-6 rounded-xl border border-border bg-white hover:shadow-lg transition-all duration-300">
              <div className="space-y-3">
                <div className="text-[13px] text-muted-foreground font-medium">Briefs Generated</div>
                <div className="text-[32px] font-semibold tracking-tight">{analytics.stats.total_briefs}</div>
                <div className="flex items-center gap-2 text-[12px]">
                  <div className={analytics.stats.briefs_growth >= 0 ? "text-emerald-600 font-medium" : "text-red-600 font-medium"}>
                    {analytics.stats.briefs_growth >= 0 ? '+' : ''}{analytics.stats.briefs_growth}%
                  </div>
                  <div className="text-muted-foreground">vs last month</div>
                </div>
              </div>
            </div>
          </div>
        ) : null}

        {/* Charts Section */}
        {analyticsLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
            {[1, 2].map((i) => (
              <div key={i} className="p-8 rounded-xl border border-border bg-white animate-pulse">
                <div className="space-y-4">
                  <div className="h-6 bg-slate-200 rounded w-40" />
                  <div className="h-32 bg-slate-100 rounded" />
                </div>
              </div>
            ))}
          </div>
        ) : null}

        {/* Analytics Widgets Row 1 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          {/* Campaign Status */}
          <div className="p-6 rounded-xl border border-border bg-white hover:shadow-lg transition-all duration-300">
            <h3 className="text-[16px] font-semibold tracking-tight mb-4">Campaign Status</h3>
            {campaignStatus && campaignStatus.statuses.length > 0 ? (
              <ChartContainer
                config={{ count: { label: "Campaigns", color: "hsl(var(--chart-1))" } }}
                className="h-[180px]"
              >
                <BarChart
                  data={campaignStatus.statuses.map(s => ({
                    status: s.status.replace('_', ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' '),
                    count: s.count
                  }))}
                  layout="horizontal"
                >
                  <XAxis type="number" />
                  <YAxis dataKey="status" type="category" width={90} className="text-xs" />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Bar dataKey="count" fill="hsl(var(--chart-1))" radius={4} />
                </BarChart>
              </ChartContainer>
            ) : (
              <div className="h-[180px] flex items-center justify-center text-[13px] text-muted-foreground">
                No data
              </div>
            )}
          </div>

          {/* Signal Sources */}
          <div className="p-6 rounded-xl border border-border bg-white hover:shadow-lg transition-all duration-300">
            <h3 className="text-[16px] font-semibold tracking-tight mb-4">Signal Sources</h3>
            {analytics && analytics.signal_sources.length > 0 ? (
              <ChartContainer
                config={{ count: { label: "Signals", color: "hsl(var(--chart-2))" } }}
                className="h-[180px]"
              >
                <BarChart data={analytics.signal_sources.slice(0, 5)} layout="horizontal">
                  <XAxis type="number" />
                  <YAxis dataKey="source" type="category" width={70} className="text-xs" />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Bar dataKey="count" fill="hsl(var(--chart-2))" radius={4} />
                </BarChart>
              </ChartContainer>
            ) : (
              <div className="h-[180px] flex items-center justify-center text-[13px] text-muted-foreground">
                No signal data
              </div>
            )}
          </div>

          {/* Signal Quality */}
          <div className="p-6 rounded-xl border border-border bg-white hover:shadow-lg transition-all duration-300">
            <h3 className="text-[16px] font-semibold tracking-tight mb-4">Signal Quality</h3>
            {intelligenceQuality ? (
              <div className="grid grid-cols-1 gap-4">
                <div className="text-center p-3 rounded-lg bg-slate-50">
                  <div className="text-[28px] font-semibold tracking-tight">{intelligenceQuality.avg_relevance.toFixed(2)}</div>
                  <div className="text-[12px] text-muted-foreground">Avg Relevance</div>
                </div>
                <div className="text-center p-3 rounded-lg bg-slate-50">
                  <div className="text-[28px] font-semibold tracking-tight">{intelligenceQuality.high_quality_percentage.toFixed(0)}%</div>
                  <div className="text-[12px] text-muted-foreground">High Quality</div>
                </div>
                <div className="text-center p-3 rounded-lg bg-slate-50">
                  <div className="text-[28px] font-semibold tracking-tight">{intelligenceQuality.avg_per_campaign.toFixed(0)}</div>
                  <div className="text-[12px] text-muted-foreground">Per Campaign</div>
                </div>
              </div>
            ) : (
              <div className="h-[180px] flex items-center justify-center text-[13px] text-muted-foreground">
                No quality data
              </div>
            )}
          </div>
        </div>

        {/* Analytics Widgets Row 2 - 4 Column Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          {/* Top Competitors */}
          <div className="p-6 rounded-xl border border-border bg-white">
            <h3 className="text-[16px] font-semibold tracking-tight mb-4">Competitors</h3>
            {competitors && competitors.competitors.length > 0 ? (
              <div className="space-y-2">
                {competitors.competitors.slice(0, 4).map((comp, i) => (
                  <div key={i} className="flex justify-between p-2 rounded-lg bg-slate-50">
                    <span className="text-[13px] font-medium truncate">{comp.name}</span>
                    <span className="text-[12px] text-muted-foreground">{comp.count}</span>
                  </div>
                ))}
              </div>
            ) : (<div className="text-[13px] text-muted-foreground">No data</div>)}
          </div>

          {/* Top Audiences */}
          <div className="p-6 rounded-xl border border-border bg-white">
            <h3 className="text-[16px] font-semibold tracking-tight mb-4">Audiences</h3>
            {audiences && audiences.audiences.length > 0 ? (
              <div className="space-y-2">
                {audiences.audiences.slice(0, 4).map((aud, i) => (
                  <div key={i} className="flex justify-between p-2 rounded-lg bg-slate-50">
                    <span className="text-[13px] font-medium truncate">{aud.name}</span>
                    <span className="text-[12px] text-muted-foreground">{aud.count}</span>
                  </div>
                ))}
              </div>
            ) : (<div className="text-[13px] text-muted-foreground">No data</div>)}
          </div>

          {/* Channels */}
          <div className="p-6 rounded-xl border border-border bg-white">
            <h3 className="text-[16px] font-semibold tracking-tight mb-4">Channels</h3>
            {channels && channels.channels.length > 0 ? (
              <div className="space-y-2">
                {channels.channels.slice(0, 4).map((ch, i) => (
                  <div key={i} className="flex justify-between p-2 rounded-lg bg-slate-50">
                    <span className="text-[13px] font-medium capitalize">{ch.name}</span>
                    <span className="text-[12px] text-muted-foreground">{ch.count}</span>
                  </div>
                ))}
              </div>
            ) : (<div className="text-[13px] text-muted-foreground">No data</div>)}
          </div>

          {/* LLM Usage */}
          <div className="p-6 rounded-xl border border-border bg-white">
            <h3 className="text-[16px] font-semibold tracking-tight mb-4">LLM Tokens</h3>
            {llmUsage && llmUsage.providers.length > 0 ? (
              <div className="space-y-2">
                {llmUsage.providers.map((p, i) => (
                  <div key={i} className="flex justify-between p-2 rounded-lg bg-slate-50">
                    <span className="text-[13px] font-medium">{p.provider}</span>
                    <span className="text-[12px] text-muted-foreground">{(p.tokens / 1000).toFixed(0)}K</span>
                  </div>
                ))}
                <div className="pt-2 mt-2 border-t border-border text-center">
                  <span className="text-[11px] text-muted-foreground">Total: {(llmUsage.total_tokens / 1000).toFixed(0)}K</span>
                </div>
              </div>
            ) : (<div className="text-[13px] text-muted-foreground">No data</div>)}
          </div>
        </div>

        {/* Campaigns Section */}
        <div className="pt-12 mb-8">
          <h2 className="text-[32px] font-semibold tracking-[-0.03em]">Your Campaigns</h2>
        </div>

        {/* Campaign Grid */}
        {campaignsLoading ? (
          <LoadingScreen variant="inline" text="Loading campaigns..." />
        ) : campaigns && campaigns.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {campaigns.map((campaign) => (
              <Link key={campaign.id} href={`/campaigns/${campaign.id}`}>
                <div className="group p-6 rounded-xl border border-border bg-white hover:shadow-xl transition-all duration-300 cursor-pointer">
                  <div className="space-y-4">
                    <div className="flex justify-between items-start">
                      <h3 className="text-[18px] font-semibold tracking-tight line-clamp-1">{campaign.name}</h3>
                      <StatusBadge status={campaign.status} />
                    </div>

                    <p className="text-[14px] text-muted-foreground leading-[1.6] line-clamp-2">
                      {campaign.brief.goal}
                    </p>

                    <div className="space-y-2.5 pt-2">
                      <div>
                        <div className="text-[12px] font-medium text-slate-700 mb-1">Audiences</div>
                        <div className="text-[13px] text-muted-foreground">
                          {campaign.brief.audiences.slice(0, 2).join(', ')}
                          {campaign.brief.audiences.length > 2 && ` +${campaign.brief.audiences.length - 2} more`}
                        </div>
                      </div>

                      <div>
                        <div className="text-[12px] font-medium text-slate-700 mb-1">Channels</div>
                        <div className="flex flex-wrap gap-1.5">
                          {campaign.brief.channels.slice(0, 3).map((channel) => (
                            <div key={channel} className="px-2 py-0.5 rounded-md bg-slate-100 border border-slate-200 text-[11px] font-medium text-slate-600">
                              {channel}
                            </div>
                          ))}
                          {campaign.brief.channels.length > 3 && (
                            <div className="px-2 py-0.5 rounded-md bg-slate-100 border border-slate-200 text-[11px] font-medium text-slate-600">
                              +{campaign.brief.channels.length - 3}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center justify-between pt-2 border-t border-border">
                      <div className="text-[12px] text-muted-foreground">
                        {format(new Date(campaign.created_at), 'MMM d, yyyy')}
                      </div>
                      <ArrowRight className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-24 px-6 rounded-xl border border-border bg-slate-50">
            <div className="max-w-md text-center space-y-6">
              <div className="w-16 h-16 mx-auto rounded-full bg-slate-200 flex items-center justify-center">
                <Plus className="h-8 w-8 text-slate-600" />
              </div>
              <div>
                <h3 className="text-[20px] font-semibold tracking-tight mb-2">No campaigns yet</h3>
                <p className="text-[14px] text-muted-foreground leading-[1.6]">
                  Create your first intelligence-backed campaign to get started
                </p>
              </div>
              <Button
                onClick={() => router.push('/campaigns/new')}
                className="h-9 !px-8 text-[13px] bg-foreground text-background hover:bg-foreground/90"
              >
                <Plus className="h-4 w-4 mr-2" />
                Create First Campaign
              </Button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
