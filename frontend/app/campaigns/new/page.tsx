'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useMutation } from '@tanstack/react-query';
import api from '@/lib/api';
import { CampaignCreate } from '@/lib/types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Stepper } from '@/components/ui/stepper';
import { ChannelBadge } from '@/components/ui/channel-badge';
import { toast } from 'sonner';
import { ArrowLeft, ArrowRight, Check, X } from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';

const CHANNELS = [
  { id: 'linkedin', name: 'LinkedIn' },
  { id: 'facebook', name: 'Facebook' },
  { id: 'instagram', name: 'Instagram' },
  { id: 'tiktok', name: 'TikTok' },
  { id: 'youtube', name: 'YouTube' },
  { id: 'pinterest', name: 'Pinterest' },
  { id: 'google_ads', name: 'Google Ads' },
];

const BUDGET_BANDS = [
  '<$5k/month',
  '$5k-$10k',
  '$10k-$25k',
  '$25k-$50k',
  '$50k-$100k',
  '$100k+',
];

export default function NewCampaignPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);

  // Form state
  const [name, setName] = useState('');
  const [goal, setGoal] = useState('');
  const [audiences, setAudiences] = useState<string[]>([]);
  const [audienceInput, setAudienceInput] = useState('');
  const [offer, setOffer] = useState('');
  const [competitors, setCompetitors] = useState<string[]>([]);
  const [competitorInput, setCompetitorInput] = useState('');
  const [channels, setChannels] = useState<string[]>([]);
  const [budgetBand, setBudgetBand] = useState('');
  const [voiceConstraints, setVoiceConstraints] = useState('');

  const createCampaignMutation = useMutation({
    mutationFn: async (data: CampaignCreate) => {
      const response = await api.post('/campaigns', data);
      return response.data;
    },
    onSuccess: (data) => {
      toast.success('Campaign created successfully!');
      router.push(`/campaigns/${data.id}`);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create campaign');
    },
  });

  const addAudience = () => {
    if (audienceInput.trim() && !audiences.includes(audienceInput.trim())) {
      setAudiences([...audiences, audienceInput.trim()]);
      setAudienceInput('');
    }
  };

  const removeAudience = (audience: string) => {
    setAudiences(audiences.filter(a => a !== audience));
  };

  const addCompetitor = () => {
    if (competitorInput.trim() && !competitors.includes(competitorInput.trim())) {
      setCompetitors([...competitors, competitorInput.trim()]);
      setCompetitorInput('');
    }
  };

  const removeCompetitor = (competitor: string) => {
    setCompetitors(competitors.filter(c => c !== competitor));
  };

  const toggleChannel = (channelId: string) => {
    if (channels.includes(channelId)) {
      setChannels(channels.filter(c => c !== channelId));
    } else {
      setChannels([...channels, channelId]);
    }
  };

  const canProceed = () => {
    if (step === 1) return name.trim() && goal.trim();
    if (step === 2) return audiences.length > 0 && offer.trim();
    if (step === 3) return channels.length > 0 && budgetBand;
    return false;
  };

  const handleSubmit = () => {
    createCampaignMutation.mutate({
      name,
      brief: {
        goal,
        audiences,
        offer,
        competitors,
        channels,
        budget_band: budgetBand,
        voice_constraints: voiceConstraints || undefined,
      },
    });
  };

  const steps = [
    { label: 'Basic Info' },
    { label: 'Audiences' },
    { label: 'Channels' },
    { label: 'Review' },
  ];

  return (
    <div className="min-h-screen bg-muted py-8">
      <div className="container mx-auto px-4 max-w-3xl">
        <div className="mb-8">
          <Button variant="ghost" onClick={() => router.push('/dashboard')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Dashboard
          </Button>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-3xl">Create New Campaign</CardTitle>
            <CardDescription>
              Step {step} of 4 - Build your intelligence-backed campaign
            </CardDescription>

            {/* Progress Stepper */}
            <Stepper steps={steps} currentStep={step} className="pt-4" />
          </CardHeader>

          <CardContent className="space-y-6 pt-6">
            {/* Step 1: Basic Info */}
            {step === 1 && (
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Campaign Name *</Label>
                  <Input
                    id="name"
                    placeholder="Q1 2025 Lead Generation"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="goal">Campaign Goal *</Label>
                  <Textarea
                    id="goal"
                    placeholder="Increase B2B SaaS signups by 30% through targeted LinkedIn and Google Ads campaigns"
                    value={goal}
                    onChange={(e) => setGoal(e.target.value)}
                    rows={4}
                  />
                  <p className="text-sm text-muted-foreground">
                    Be specific about what you want to achieve
                  </p>
                </div>
              </div>
            )}

            {/* Step 2: Audiences & Offer */}
            {step === 2 && (
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="audienceInput">Target Audiences *</Label>
                  <div className="flex gap-2">
                    <Input
                      id="audienceInput"
                      placeholder="e.g., Marketing Directors"
                      value={audienceInput}
                      onChange={(e) => setAudienceInput(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addAudience())}
                    />
                    <Button type="button" onClick={addAudience}>Add</Button>
                  </div>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {audiences.map((audience) => (
                      <Badge key={audience} variant="secondary" className="px-3 py-1">
                        {audience}
                        <X
                          className="h-3 w-3 ml-2 cursor-pointer"
                          onClick={() => removeAudience(audience)}
                        />
                      </Badge>
                    ))}
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="offer">Offer/Product Description *</Label>
                  <Textarea
                    id="offer"
                    placeholder="AI-powered campaign intelligence platform that transforms market signals into strategic briefs"
                    value={offer}
                    onChange={(e) => setOffer(e.target.value)}
                    rows={4}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="competitorInput">Competitors (Optional)</Label>
                  <div className="flex gap-2">
                    <Input
                      id="competitorInput"
                      placeholder="e.g., HubSpot"
                      value={competitorInput}
                      onChange={(e) => setCompetitorInput(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addCompetitor())}
                    />
                    <Button type="button" onClick={addCompetitor}>Add</Button>
                  </div>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {competitors.map((competitor) => (
                      <Badge key={competitor} variant="outline" className="px-3 py-1">
                        {competitor}
                        <X
                          className="h-3 w-3 ml-2 cursor-pointer"
                          onClick={() => removeCompetitor(competitor)}
                        />
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Step 3: Channels & Budget */}
            {step === 3 && (
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label>Select Channels *</Label>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                    {CHANNELS.map((channel) => (
                      <Card
                        key={channel.id}
                        className={`cursor-pointer transition-all ${
                          channels.includes(channel.id)
                            ? 'ring-2 ring-primary bg-primary/5'
                            : 'hover:bg-muted'
                        }`}
                        onClick={() => toggleChannel(channel.id)}
                      >
                        <CardContent className="p-4 flex items-center gap-3">
                          <ChannelBadge
                            channelId={channel.id}
                            channelName={channel.name}
                            className="flex-1"
                          />
                          {channels.includes(channel.id) && (
                            <Check className="h-4 w-4 text-primary" />
                          )}
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="budget">Budget Band *</Label>
                  <Select value={budgetBand} onValueChange={setBudgetBand}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select budget range" />
                    </SelectTrigger>
                    <SelectContent>
                      {BUDGET_BANDS.map((band) => (
                        <SelectItem key={band} value={band}>
                          {band}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="voice">Voice Constraints (Optional)</Label>
                  <Textarea
                    id="voice"
                    placeholder="Professional but approachable, data-driven, avoid jargon"
                    value={voiceConstraints}
                    onChange={(e) => setVoiceConstraints(e.target.value)}
                    rows={3}
                  />
                </div>
              </div>
            )}

            {/* Step 4: Review */}
            {step === 4 && (
              <div className="space-y-4">
                <h3 className="text-xl font-semibold mb-4">Review Your Campaign</h3>

                <div className="space-y-3">
                  <div>
                    <span className="font-semibold">Name:</span> {name}
                  </div>
                  <div>
                    <span className="font-semibold">Goal:</span> {goal}
                  </div>
                  <div>
                    <span className="font-semibold">Audiences:</span>{' '}
                    {audiences.join(', ')}
                  </div>
                  <div>
                    <span className="font-semibold">Offer:</span> {offer}
                  </div>
                  {competitors.length > 0 && (
                    <div>
                      <span className="font-semibold">Competitors:</span>{' '}
                      {competitors.join(', ')}
                    </div>
                  )}
                  <div>
                    <span className="font-semibold">Channels:</span>{' '}
                    <div className="flex flex-wrap gap-2 mt-1">
                      {channels.map((channelId) => {
                        const channel = CHANNELS.find((c) => c.id === channelId);
                        return channel ? (
                          <ChannelBadge
                            key={channelId}
                            channelId={channel.id}
                            channelName={channel.name}
                          />
                        ) : null;
                      })}
                    </div>
                  </div>
                  <div>
                    <span className="font-semibold">Budget:</span> {budgetBand}
                  </div>
                  {voiceConstraints && (
                    <div>
                      <span className="font-semibold">Voice:</span> {voiceConstraints}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Navigation Buttons */}
            <div className="flex justify-between pt-6 border-t">
              <Button
                variant="outline"
                onClick={() => setStep(Math.max(1, step - 1))}
                disabled={step === 1}
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Previous
              </Button>

              {step < 4 ? (
                <Button
                  onClick={() => setStep(step + 1)}
                  disabled={!canProceed()}
                >
                  Next
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              ) : (
                <Button
                  onClick={handleSubmit}
                  disabled={createCampaignMutation.isPending}
                >
                  {createCampaignMutation.isPending ? 'Creating...' : 'Create Campaign'}
                  <Check className="h-4 w-4 ml-2" />
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
