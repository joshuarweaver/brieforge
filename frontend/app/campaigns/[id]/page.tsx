'use client';

import { useParams, useRouter } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';
import { Campaign, Signal, SignalAnalysis, StrategicBrief } from '@/lib/types';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { StatusBadge } from '@/components/ui/status-badge';
import { LoadingScreen } from '@/components/ui/loading-screen';
import { ContentDisplay } from '@/components/ui/content-display';
import { ArrowLeft, TrendingUp, Brain, FileText, Users, Play } from 'lucide-react';
import { toast } from 'sonner';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useState } from 'react';
import { format } from 'date-fns';

export default function CampaignDetailPage() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const campaignId = params.id as string;

  const [collectSignalsOpen, setCollectSignalsOpen] = useState(false);
  const [analyzeOpen, setAnalyzeOpen] = useState(false);
  const [generateBriefOpen, setGenerateBriefOpen] = useState(false);

  // Fetch campaign
  const { data: campaign, isLoading } = useQuery({
    queryKey: ['campaign', campaignId],
    queryFn: async () => {
      const response = await api.get<Campaign>(`/campaigns/${campaignId}`);
      return response.data;
    },
  });

  // Fetch signals
  const { data: signals } = useQuery({
    queryKey: ['signals', campaignId],
    queryFn: async () => {
      const response = await api.get<Signal[]>(`/campaigns/${campaignId}/signals`);
      return response.data;
    },
    enabled: !!campaign,
  });

  // Fetch analyses
  const { data: analyses } = useQuery({
    queryKey: ['analyses', campaignId],
    queryFn: async () => {
      const response = await api.get<SignalAnalysis[]>(`/campaigns/${campaignId}/signal-analyses`);
      return response.data;
    },
    enabled: !!campaign,
  });

  // Fetch briefs
  const { data: briefs } = useQuery({
    queryKey: ['briefs', campaignId],
    queryFn: async () => {
      const response = await api.get<StrategicBrief[]>(`/campaigns/${campaignId}/strategic-briefs`);
      return response.data;
    },
    enabled: !!campaign,
  });

  // Collect signals mutation
  const collectSignalsMutation = useMutation({
    mutationFn: async () => {
      const response = await api.post(`/campaigns/${campaignId}/signals/collect`, {
        max_queries_per_cartridge: 10,
      });
      return response.data;
    },
    onSuccess: () => {
      toast.success('Signal collection started!');
      queryClient.invalidateQueries({ queryKey: ['signals', campaignId] });
      setCollectSignalsOpen(false);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to collect signals');
    },
  });

  // Analyze mutation
  const analyzeMutation = useMutation({
    mutationFn: async (data: { analysis_type: string; llm_provider: string }) => {
      const response = await api.post(`/campaigns/${campaignId}/analyze`, {
        analysis_type: data.analysis_type,
        llm_provider: data.llm_provider,
        min_relevance: 0.0,
        async_mode: true,
      });
      return response.data;
    },
    onSuccess: () => {
      toast.success('Analysis started!');
      queryClient.invalidateQueries({ queryKey: ['analyses', campaignId] });
      setAnalyzeOpen(false);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to start analysis');
    },
  });

  // Generate brief mutation
  const generateBriefMutation = useMutation({
    mutationFn: async (llmProvider: string) => {
      const response = await api.post(`/campaigns/${campaignId}/strategic-brief`, {
        llm_provider: llmProvider,
        async_mode: true,
      });
      return response.data;
    },
    onSuccess: () => {
      toast.success('Strategic brief generation started!');
      queryClient.invalidateQueries({ queryKey: ['briefs', campaignId] });
      setGenerateBriefOpen(false);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to generate brief');
    },
  });

  if (isLoading) {
    return <LoadingScreen message="Loading campaign..." />;
  }

  if (!campaign) {
    return <div className="min-h-screen flex items-center justify-center">Campaign not found</div>;
  }

  return (
    <div className="min-h-screen bg-muted">
      {/* Header */}
      <header className="bg-card border-b border-border">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center gap-4 mb-4">
            <Button variant="ghost" onClick={() => router.push('/dashboard')}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Dashboard
            </Button>
          </div>

          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold mb-2">{campaign.name}</h1>
              <div className="flex gap-2 items-center">
                <StatusBadge status={campaign.status} />
                <span className="text-sm text-muted-foreground">
                  Updated {format(new Date(campaign.updated_at), 'MMM d, yyyy')}
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="signals">
              Signals {signals && `(${signals.length})`}
            </TabsTrigger>
            <TabsTrigger value="analyses">
              Analyses {analyses && `(${analyses.length})`}
            </TabsTrigger>
            <TabsTrigger value="brief">Strategic Brief</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Campaign Brief</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <span className="font-semibold">Goal:</span>
                  <p className="text-muted-foreground mt-1">{campaign.brief.goal}</p>
                </div>
                <div>
                  <span className="font-semibold">Offer:</span>
                  <p className="text-muted-foreground mt-1">{campaign.brief.offer}</p>
                </div>
                <div>
                  <span className="font-semibold">Audiences:</span>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {campaign.brief.audiences.map((audience) => (
                      <Badge key={audience} variant="secondary">{audience}</Badge>
                    ))}
                  </div>
                </div>
                <div>
                  <span className="font-semibold">Channels:</span>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {campaign.brief.channels.map((channel) => (
                      <Badge key={channel} variant="outline">{channel}</Badge>
                    ))}
                  </div>
                </div>
                <div>
                  <span className="font-semibold">Budget:</span> {campaign.brief.budget_band}
                </div>
                {campaign.brief.competitors && campaign.brief.competitors.length > 0 && (
                  <div>
                    <span className="font-semibold">Competitors:</span> {campaign.brief.competitors.join(', ')}
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
                <CardDescription>Run intelligence operations on your campaign</CardDescription>
              </CardHeader>
              <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Dialog open={collectSignalsOpen} onOpenChange={setCollectSignalsOpen}>
                  <DialogTrigger asChild>
                    <Button className="w-full h-24 flex-col gap-2">
                      <TrendingUp className="h-6 w-6" />
                      Collect Signals
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Collect Signals</DialogTitle>
                      <DialogDescription>
                        Gather intelligence from 15+ sources across all platforms
                      </DialogDescription>
                    </DialogHeader>
                    <div className="py-4">
                      <p className="text-sm text-muted-foreground mb-4">
                        This will collect signals from Google, Meta, LinkedIn, TikTok, YouTube, Reddit, and Pinterest.
                      </p>
                      <Button
                        onClick={() => collectSignalsMutation.mutate()}
                        disabled={collectSignalsMutation.isPending}
                        className="w-full"
                      >
                        {collectSignalsMutation.isPending ? 'Starting...' : 'Start Collection'}
                      </Button>
                    </div>
                  </DialogContent>
                </Dialog>

                <Dialog open={analyzeOpen} onOpenChange={setAnalyzeOpen}>
                  <DialogTrigger asChild>
                    <Button className="w-full h-24 flex-col gap-2" variant="outline">
                      <Brain className="h-6 w-6" />
                      Run Analysis
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Run Analysis</DialogTitle>
                      <DialogDescription>
                        Use AI to analyze collected signals
                      </DialogDescription>
                    </DialogHeader>
                    <AnalysisForm onSubmit={(data) => analyzeMutation.mutate(data)} isPending={analyzeMutation.isPending} />
                  </DialogContent>
                </Dialog>

                <Dialog open={generateBriefOpen} onOpenChange={setGenerateBriefOpen}>
                  <DialogTrigger asChild>
                    <Button className="w-full h-24 flex-col gap-2" variant="outline">
                      <FileText className="h-6 w-6" />
                      Generate Brief
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Generate Strategic Brief</DialogTitle>
                      <DialogDescription>
                        Create a comprehensive 2-page strategy document
                      </DialogDescription>
                    </DialogHeader>
                    <BriefForm onSubmit={(provider) => generateBriefMutation.mutate(provider)} isPending={generateBriefMutation.isPending} />
                  </DialogContent>
                </Dialog>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Signals Tab */}
          <TabsContent value="signals">
            <Card>
              <CardHeader>
                <CardTitle>Collected Signals</CardTitle>
                <CardDescription>
                  Intelligence gathered from across the web
                </CardDescription>
              </CardHeader>
              <CardContent>
                {signals && signals.length > 0 ? (
                  <div className="space-y-4">
                    {signals.slice(0, 10).map((signal) => (
                      <div key={signal.id} className="border-b pb-4 last:border-0">
                        <div className="flex justify-between items-start mb-2">
                          <div className="flex gap-2">
                            <Badge>{signal.source}</Badge>
                            <Badge variant="outline">{signal.search_method}</Badge>
                          </div>
                          <span className="text-sm font-semibold">
                            {(signal.relevance_score * 100).toFixed(0)}% relevant
                          </span>
                        </div>
                        <p className="text-sm font-medium">{signal.query}</p>
                        <p className="text-sm text-muted-foreground mt-1">
                          {signal.evidence.length} evidence items
                        </p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-center text-muted-foreground py-8">
                    No signals collected yet. Click "Collect Signals" to start.
                  </p>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Analyses Tab */}
          <TabsContent value="analyses">
            <Card>
              <CardHeader>
                <CardTitle>Signal Analyses</CardTitle>
                <CardDescription>
                  AI-powered insights from your collected signals
                </CardDescription>
              </CardHeader>
              <CardContent>
                {analyses && analyses.length > 0 ? (
                  <div className="space-y-4">
                    {analyses.map((analysis) => (
                      <Card key={analysis.id}>
                        <CardHeader>
                          <div className="flex justify-between items-start">
                            <div>
                              <CardTitle className="text-lg">{analysis.analysis_type}</CardTitle>
                              <CardDescription>
                                {analysis.llm_provider} • {analysis.llm_model}
                              </CardDescription>
                            </div>
                            <StatusBadge status={analysis.status} />
                          </div>
                        </CardHeader>
                        {analysis.insights && (
                          <CardContent>
                            <ContentDisplay content={analysis.insights} />
                          </CardContent>
                        )}
                      </Card>
                    ))}
                  </div>
                ) : (
                  <p className="text-center text-muted-foreground py-8">
                    No analyses yet. Click "Run Analysis" to start.
                  </p>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Brief Tab */}
          <TabsContent value="brief">
            <Card>
              <CardHeader>
                <CardTitle>Strategic Brief</CardTitle>
                <CardDescription>
                  Your AI-generated 2-page strategy document
                </CardDescription>
              </CardHeader>
              <CardContent>
                {briefs && briefs.length > 0 ? (
                  <div className="space-y-4">
                    {briefs.map((brief) => (
                      <Card key={brief.id}>
                        <CardHeader>
                          <div className="flex justify-between items-start">
                            <div>
                              <CardTitle className="text-lg">Version {brief.version}</CardTitle>
                              <CardDescription>
                                {brief.llm_provider} • {brief.llm_model}
                              </CardDescription>
                            </div>
                            <StatusBadge status={brief.status} />
                          </div>
                        </CardHeader>
                        {brief.content && (
                          <CardContent>
                            <ContentDisplay content={brief.content} />
                          </CardContent>
                        )}
                      </Card>
                    ))}
                  </div>
                ) : (
                  <p className="text-center text-muted-foreground py-8">
                    No strategic brief yet. Click "Generate Brief" to create one.
                  </p>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}

function AnalysisForm({ onSubmit, isPending }: { onSubmit: (data: any) => void; isPending: boolean }) {
  const [analysisType, setAnalysisType] = useState('comprehensive');
  const [llmProvider, setLlmProvider] = useState('claude');

  return (
    <div className="space-y-4 py-4">
      <div className="space-y-2">
        <Label>Analysis Type</Label>
        <Select value={analysisType} onValueChange={setAnalysisType}>
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="comprehensive">Comprehensive</SelectItem>
            <SelectItem value="competitor">Competitor Analysis</SelectItem>
            <SelectItem value="audience">Audience Insights</SelectItem>
            <SelectItem value="messaging">Messaging Patterns</SelectItem>
            <SelectItem value="creative">Creative Recommendations</SelectItem>
            <SelectItem value="trends">Market Trends</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <Label>LLM Provider</Label>
        <Select value={llmProvider} onValueChange={setLlmProvider}>
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="claude">Claude (Sonnet 4.5)</SelectItem>
            <SelectItem value="openai">OpenAI (GPT-4)</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Button
        onClick={() => onSubmit({ analysis_type: analysisType, llm_provider: llmProvider })}
        disabled={isPending}
        className="w-full"
      >
        {isPending ? 'Starting...' : 'Run Analysis'}
      </Button>
    </div>
  );
}

function BriefForm({ onSubmit, isPending }: { onSubmit: (provider: string) => void; isPending: boolean }) {
  const [llmProvider, setLlmProvider] = useState('claude');

  return (
    <div className="space-y-4 py-4">
      <div className="space-y-2">
        <Label>LLM Provider</Label>
        <Select value={llmProvider} onValueChange={setLlmProvider}>
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="claude">Claude (Sonnet 4.5)</SelectItem>
            <SelectItem value="openai">OpenAI (GPT-4)</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Button
        onClick={() => onSubmit(llmProvider)}
        disabled={isPending}
        className="w-full"
      >
        {isPending ? 'Generating...' : 'Generate Strategic Brief'}
      </Button>
    </div>
  );
}
