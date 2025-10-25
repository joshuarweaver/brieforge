'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useMutation } from '@tanstack/react-query';
import api from '@/lib/api';
import { CampaignCreate } from '@/lib/types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Stepper } from '@/components/ui/stepper';
import { toast } from 'sonner';
import { ArrowLeft, ArrowRight, Check, X, Sparkles, Lightbulb } from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

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

  // AI-generated suggestions state
  const [goalSuggestions, setGoalSuggestions] = useState<string[]>([]);
  const [audienceSuggestions, setAudienceSuggestions] = useState<string[]>([]);
  const [competitorSuggestions, setCompetitorSuggestions] = useState<string[]>([]);
  const [voiceSuggestions, setVoiceSuggestions] = useState<string[]>([]);
  const [isGeneratingGoals, setIsGeneratingGoals] = useState(false);
  const [isGeneratingAudiences, setIsGeneratingAudiences] = useState(false);
  const [isGeneratingCompetitors, setIsGeneratingCompetitors] = useState(false);
  const [isGeneratingVoice, setIsGeneratingVoice] = useState(false);

  // AI Generation Functions
  const generateGoalSuggestions = async (campaignName: string) => {
    if (!campaignName.trim()) return;

    setIsGeneratingGoals(true);
    try {
      const response = await api.post('/ai/suggest-goals', {
        campaign_name: campaignName
      });
      setGoalSuggestions(response.data.suggestions || []);
    } catch (error) {
      console.error('Failed to generate goal suggestions:', error);
      // Fallback suggestions
      setGoalSuggestions([
        `Increase qualified leads through ${campaignName}`,
        `Drive brand awareness for ${campaignName}`,
        `Generate pipeline revenue with ${campaignName}`,
      ]);
    } finally {
      setIsGeneratingGoals(false);
    }
  };

  const generateAudienceSuggestions = async (offerText: string, goalText: string) => {
    if (!offerText.trim()) return;

    setIsGeneratingAudiences(true);
    try {
      const response = await api.post('/ai/suggest-audiences', {
        offer: offerText,
        goal: goalText
      });
      setAudienceSuggestions(response.data.suggestions || []);
    } catch (error) {
      console.error('Failed to generate audience suggestions:', error);
      setAudienceSuggestions([]);
    } finally {
      setIsGeneratingAudiences(false);
    }
  };

  const generateCompetitorSuggestions = async (offerText: string) => {
    if (!offerText.trim()) return;

    setIsGeneratingCompetitors(true);
    try {
      const response = await api.post('/ai/suggest-competitors', {
        offer: offerText
      });
      setCompetitorSuggestions(response.data.suggestions || []);
    } catch (error) {
      console.error('Failed to generate competitor suggestions:', error);
      setCompetitorSuggestions([]);
    } finally {
      setIsGeneratingCompetitors(false);
    }
  };

  const generateVoiceSuggestions = async (channelsList: string[], offerText: string) => {
    if (channelsList.length === 0) return;

    setIsGeneratingVoice(true);
    try {
      const response = await api.post('/ai/suggest-voice', {
        channels: channelsList,
        offer: offerText
      });
      setVoiceSuggestions(response.data.suggestions || []);
    } catch (error) {
      console.error('Failed to generate voice suggestions:', error);
      setVoiceSuggestions([]);
    } finally {
      setIsGeneratingVoice(false);
    }
  };

  // Trigger AI suggestions when relevant fields change
  useEffect(() => {
    if (name && name.length > 3) {
      const timer = setTimeout(() => {
        generateGoalSuggestions(name);
      }, 500); // Debounce
      return () => clearTimeout(timer);
    }
  }, [name]);

  useEffect(() => {
    if (offer && offer.length > 10) {
      const timer = setTimeout(() => {
        generateAudienceSuggestions(offer, goal);
        generateCompetitorSuggestions(offer);
      }, 800); // Debounce
      return () => clearTimeout(timer);
    }
  }, [offer, goal]);

  useEffect(() => {
    if (channels.length > 0 && offer) {
      const timer = setTimeout(() => {
        generateVoiceSuggestions(channels, offer);
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [channels, offer]);

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
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="border-b border-border bg-white">
        <div className="container mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-8">
            <button onClick={() => router.push('/dashboard')} className="flex items-center gap-2 group">
              <div className="w-5 h-5 bg-foreground rounded transition-transform duration-200 group-hover:scale-105" />
              <span className="font-semibold text-[15px]">Fieldforge</span>
            </button>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.push('/dashboard')}
            className="text-[13px]"
          >
            <ArrowLeft className="h-3.5 w-3.5 mr-2" />
            Back to Dashboard
          </Button>
        </div>
      </header>

      <div className="container mx-auto px-6 py-12 max-w-[920px]">
        <div className="space-y-8">
          {/* Header Section */}
          <div className="space-y-4">
            <h1 className="text-[40px] md:text-[48px] font-semibold tracking-[-0.03em] leading-[1.2]">
              Create New Campaign
            </h1>
            <p className="text-[16px] text-muted-foreground leading-[1.6]">
              Step {step} of 4 - Build your intelligence-backed campaign
            </p>

            {/* Progress Stepper */}
            <Stepper steps={steps} currentStep={step} className="pt-6" />
          </div>

          {/* Main Card */}
          <div className="p-8 rounded-xl border border-border bg-white shadow-lg">

            <div className="space-y-6">
            {/* Step 1: Basic Info */}
            {step === 1 && (
              <div className="space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="name" className="text-[14px] font-medium">Campaign Name *</Label>
                  <Input
                    id="name"
                    placeholder="Q1 2025 Lead Generation"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="text-[14px]"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="goal" className="text-[14px] font-medium">Campaign Goal *</Label>
                  <Textarea
                    id="goal"
                    placeholder="Increase B2B SaaS signups by 30% through targeted LinkedIn and Google Ads campaigns"
                    value={goal}
                    onChange={(e) => setGoal(e.target.value)}
                    rows={4}
                    className="text-[14px]"
                  />

                  {/* AI Suggestions - Show only when campaign name is filled and goal is empty */}
                  {name && !goal && (
                    <div className="mt-2 p-4 rounded-lg border border-blue-200 bg-blue-50/50 space-y-2 animate-in fade-in slide-in-from-top-2 duration-300">
                      <div className="flex items-center gap-2 text-[13px] font-medium text-blue-900 mb-3">
                        <Sparkles className={`h-4 w-4 text-blue-600 ${isGeneratingGoals ? 'animate-spin' : ''}`} />
                        {isGeneratingGoals ? 'AI is analyzing your campaign...' : 'AI-Suggested Goals'}
                      </div>
                      {isGeneratingGoals ? (
                        <div className="flex items-center justify-center py-8">
                          <div className="animate-pulse text-[13px] text-blue-700">Generating intelligent suggestions...</div>
                        </div>
                      ) : goalSuggestions.length > 0 ? (
                        goalSuggestions.map((suggestion, idx) => (
                          <button
                            key={idx}
                            type="button"
                            onClick={() => setGoal(suggestion)}
                            className="w-full text-left p-3 rounded-md bg-white border border-blue-100 hover:border-blue-300 hover:bg-blue-50 transition-all text-[13px] leading-[1.6]"
                          >
                            {suggestion}
                          </button>
                        ))
                      ) : (
                        <div className="text-[13px] text-blue-700 py-4">Type more details in the campaign name to get AI suggestions</div>
                      )}
                    </div>
                  )}

                  <p className="text-[13px] text-muted-foreground leading-[1.6]">
                    Be specific about what you want to achieve
                  </p>
                </div>
              </div>
            )}

            {/* Step 2: Audiences & Offer */}
            {step === 2 && (
              <div className="space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="audienceInput" className="text-[14px] font-medium">Target Audiences *</Label>
                  <div className="flex gap-2">
                    <Input
                      id="audienceInput"
                      placeholder="e.g., Marketing Directors"
                      value={audienceInput}
                      onChange={(e) => setAudienceInput(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addAudience())}
                      className="text-[14px]"
                    />
                    <Button type="button" size="sm" onClick={addAudience} className="px-6 text-[13px]">Add</Button>
                  </div>

                  {/* AI Suggestions - Show only when offer is filled */}
                  {offer && (
                    <div className="mt-2 p-4 rounded-lg border border-blue-200 bg-blue-50/50 space-y-2 animate-in fade-in slide-in-from-top-2 duration-300">
                      <div className="flex items-center gap-2 text-[13px] font-medium text-blue-900 mb-3">
                        <Sparkles className={`h-4 w-4 text-blue-600 ${isGeneratingAudiences ? 'animate-spin' : ''}`} />
                        {isGeneratingAudiences ? 'AI is analyzing your offer...' : 'AI-Suggested Audiences based on your offer'}
                      </div>
                      {isGeneratingAudiences ? (
                        <div className="flex items-center justify-center py-6">
                          <div className="animate-pulse text-[13px] text-blue-700">Generating audience insights...</div>
                        </div>
                      ) : audienceSuggestions.length > 0 ? (
                        <div className="flex flex-wrap gap-2">
                          {audienceSuggestions.map((suggestion, idx) => (
                            <button
                              key={idx}
                              type="button"
                              onClick={() => {
                                if (!audiences.includes(suggestion)) {
                                  setAudiences([...audiences, suggestion]);
                                }
                              }}
                              disabled={audiences.includes(suggestion)}
                              className="px-3 py-2 rounded-md bg-white border border-blue-100 hover:border-blue-300 hover:bg-blue-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all text-[13px]"
                            >
                              + {suggestion}
                            </button>
                          ))}
                        </div>
                      ) : (
                        <div className="text-[13px] text-blue-700 py-4">Add more details to your offer to get AI audience suggestions</div>
                      )}
                    </div>
                  )}

                  <div className="flex flex-wrap gap-2 mt-2">
                    {audiences.map((audience) => (
                      <Badge key={audience} variant="secondary" className="px-3 py-1.5 text-[13px]">
                        {audience}
                        <X
                          className="h-3.5 w-3.5 ml-2 cursor-pointer"
                          onClick={() => removeAudience(audience)}
                        />
                      </Badge>
                    ))}
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="offer" className="text-[14px] font-medium">Offer/Product Description *</Label>
                  <Textarea
                    id="offer"
                    placeholder="AI-powered campaign intelligence platform that transforms market signals into strategic briefs"
                    value={offer}
                    onChange={(e) => setOffer(e.target.value)}
                    rows={4}
                    className="text-[14px]"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="competitorInput" className="text-[14px] font-medium">Competitors (Optional)</Label>
                  <div className="flex gap-2">
                    <Input
                      id="competitorInput"
                      placeholder="e.g., HubSpot"
                      value={competitorInput}
                      onChange={(e) => setCompetitorInput(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addCompetitor())}
                      className="text-[14px]"
                    />
                    <Button type="button" size="sm" onClick={addCompetitor} className="px-6 text-[13px]">Add</Button>
                  </div>

                  {/* AI Suggestions - Show only when offer is filled */}
                  {offer && (
                    <div className="mt-2 p-4 rounded-lg border border-blue-200 bg-blue-50/50 space-y-2 animate-in fade-in slide-in-from-top-2 duration-300">
                      <div className="flex items-center gap-2 text-[13px] font-medium text-blue-900 mb-3">
                        <Sparkles className={`h-4 w-4 text-blue-600 ${isGeneratingCompetitors ? 'animate-spin' : ''}`} />
                        {isGeneratingCompetitors ? 'AI is researching competitors...' : 'AI-Suggested Competitors based on your offer'}
                      </div>
                      {isGeneratingCompetitors ? (
                        <div className="flex items-center justify-center py-6">
                          <div className="animate-pulse text-[13px] text-blue-700">Analyzing competitive landscape...</div>
                        </div>
                      ) : competitorSuggestions.length > 0 ? (
                        <div className="flex flex-wrap gap-2">
                          {competitorSuggestions.map((suggestion, idx) => (
                            <button
                              key={idx}
                              type="button"
                              onClick={() => {
                                if (!competitors.includes(suggestion)) {
                                  setCompetitors([...competitors, suggestion]);
                                }
                              }}
                              disabled={competitors.includes(suggestion)}
                              className="px-3 py-2 rounded-md bg-white border border-blue-100 hover:border-blue-300 hover:bg-blue-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all text-[13px]"
                            >
                              + {suggestion}
                            </button>
                          ))}
                        </div>
                      ) : (
                        <div className="text-[13px] text-blue-700 py-4">Add more details to get AI competitor suggestions</div>
                      )}
                    </div>
                  )}

                  <div className="flex flex-wrap gap-2 mt-2">
                    {competitors.map((competitor) => (
                      <Badge key={competitor} variant="outline" className="px-3 py-1.5 text-[13px]">
                        {competitor}
                        <X
                          className="h-3.5 w-3.5 ml-2 cursor-pointer"
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
              <div className="space-y-6">
                <div className="space-y-2">
                  <Label className="text-[14px] font-medium">Select Channels *</Label>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                    {CHANNELS.map((channel) => (
                      <div
                        key={channel.id}
                        className={`p-4 rounded-lg border transition-all duration-200 cursor-pointer ${
                          channels.includes(channel.id)
                            ? 'border-foreground bg-slate-50 shadow-sm'
                            : 'border-border hover:bg-slate-50 hover:border-slate-300'
                        }`}
                        onClick={() => toggleChannel(channel.id)}
                      >
                        <div className="flex items-center justify-between gap-3">
                          <span className="text-[13px] font-medium">{channel.name}</span>
                          {channels.includes(channel.id) && (
                            <Check className="h-4 w-4 text-foreground flex-shrink-0" />
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="budget" className="text-[14px] font-medium">Budget Band *</Label>
                  <Select value={budgetBand} onValueChange={setBudgetBand}>
                    <SelectTrigger className="text-[14px]">
                      <SelectValue placeholder="Select budget range" />
                    </SelectTrigger>
                    <SelectContent>
                      {BUDGET_BANDS.map((band) => (
                        <SelectItem key={band} value={band} className="text-[14px]">
                          {band}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="voice" className="text-[14px] font-medium">Voice Constraints (Optional)</Label>
                  <Textarea
                    id="voice"
                    placeholder="Professional but approachable, data-driven, avoid jargon"
                    value={voiceConstraints}
                    onChange={(e) => setVoiceConstraints(e.target.value)}
                    rows={3}
                    className="text-[14px]"
                  />

                  {/* AI Suggestions - Show only when channels are selected and voice is empty */}
                  {channels.length > 0 && !voiceConstraints && (
                    <div className="mt-2 p-4 rounded-lg border border-blue-200 bg-blue-50/50 space-y-2 animate-in fade-in slide-in-from-top-2 duration-300">
                      <div className="flex items-center gap-2 text-[13px] font-medium text-blue-900 mb-3">
                        <Sparkles className={`h-4 w-4 text-blue-600 ${isGeneratingVoice ? 'animate-spin' : ''}`} />
                        {isGeneratingVoice ? 'AI is crafting voice recommendations...' : 'AI-Suggested Voice & Tone for your channels'}
                      </div>
                      {isGeneratingVoice ? (
                        <div className="flex items-center justify-center py-8">
                          <div className="animate-pulse text-[13px] text-blue-700">Analyzing channel best practices...</div>
                        </div>
                      ) : voiceSuggestions.length > 0 ? (
                        voiceSuggestions.map((suggestion, idx) => (
                          <button
                            key={idx}
                            type="button"
                            onClick={() => setVoiceConstraints(suggestion)}
                            className="w-full text-left p-3 rounded-md bg-white border border-blue-100 hover:border-blue-300 hover:bg-blue-50 transition-all text-[13px] leading-[1.6]"
                          >
                            {suggestion}
                          </button>
                        ))
                      ) : (
                        <div className="text-[13px] text-blue-700 py-4">Select channels to get AI voice suggestions</div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Step 4: Review */}
            {step === 4 && (
              <div className="space-y-6">
                <h3 className="text-[24px] font-semibold tracking-tight">Review Your Campaign</h3>

                <div className="space-y-4">
                  <div className="p-4 rounded-lg bg-slate-50 border border-border">
                    <div className="text-[13px] font-medium text-muted-foreground mb-1">Campaign Name</div>
                    <div className="text-[15px] font-medium">{name}</div>
                  </div>

                  <div className="p-4 rounded-lg bg-slate-50 border border-border">
                    <div className="text-[13px] font-medium text-muted-foreground mb-1">Goal</div>
                    <div className="text-[15px] leading-[1.6]">{goal}</div>
                  </div>

                  <div className="p-4 rounded-lg bg-slate-50 border border-border">
                    <div className="text-[13px] font-medium text-muted-foreground mb-2">Target Audiences</div>
                    <div className="flex flex-wrap gap-2">
                      {audiences.map((audience) => (
                        <Badge key={audience} variant="secondary" className="px-3 py-1.5 text-[13px]">
                          {audience}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  <div className="p-4 rounded-lg bg-slate-50 border border-border">
                    <div className="text-[13px] font-medium text-muted-foreground mb-1">Offer</div>
                    <div className="text-[15px] leading-[1.6]">{offer}</div>
                  </div>

                  {competitors.length > 0 && (
                    <div className="p-4 rounded-lg bg-slate-50 border border-border">
                      <div className="text-[13px] font-medium text-muted-foreground mb-2">Competitors</div>
                      <div className="flex flex-wrap gap-2">
                        {competitors.map((competitor) => (
                          <Badge key={competitor} variant="outline" className="px-3 py-1.5 text-[13px]">
                            {competitor}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="p-4 rounded-lg bg-slate-50 border border-border">
                    <div className="text-[13px] font-medium text-muted-foreground mb-2">Channels</div>
                    <div className="flex flex-wrap gap-2">
                      {channels.map((channelId) => {
                        const channel = CHANNELS.find((c) => c.id === channelId);
                        return channel ? (
                          <div key={channelId} className="px-3 py-1.5 rounded-md bg-white border border-slate-200 text-[13px] font-medium">
                            {channel.name}
                          </div>
                        ) : null;
                      })}
                    </div>
                  </div>

                  <div className="p-4 rounded-lg bg-slate-50 border border-border">
                    <div className="text-[13px] font-medium text-muted-foreground mb-1">Budget Band</div>
                    <div className="text-[15px] font-medium">{budgetBand}</div>
                  </div>

                  {voiceConstraints && (
                    <div className="p-4 rounded-lg bg-slate-50 border border-border">
                      <div className="text-[13px] font-medium text-muted-foreground mb-1">Voice Constraints</div>
                      <div className="text-[15px] leading-[1.6]">{voiceConstraints}</div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Navigation Buttons */}
            <div className="flex justify-between pt-6 border-t border-border">
              <Button
                variant="outline"
                onClick={() => setStep(Math.max(1, step - 1))}
                disabled={step === 1}
                className="h-7 px-6 text-[13px]"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Previous
              </Button>

              {step < 4 ? (
                <Button
                  onClick={() => setStep(step + 1)}
                  disabled={!canProceed()}
                  className="h-7 px-8 text-[13px] bg-foreground text-background hover:bg-foreground/90"
                >
                  Next
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              ) : (
                <Button
                  onClick={handleSubmit}
                  disabled={createCampaignMutation.isPending}
                  className="h-7 px-8 text-[13px] bg-foreground text-background hover:bg-foreground/90"
                >
                  {createCampaignMutation.isPending ? 'Creating...' : 'Create Campaign'}
                  <Check className="h-4 w-4 ml-2" />
                </Button>
              )}
            </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
