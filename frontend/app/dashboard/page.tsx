'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api';
import { Campaign } from '@/lib/types';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { StatusBadge } from '@/components/StatusBadge';
import { LoadingScreen } from '@/components/LoadingScreen';
import { EmptyState } from '@/components/EmptyState';
import Link from 'next/link';
import { Plus, BarChart, FileText, Users, TrendingUp } from 'lucide-react';
import { format } from 'date-fns';

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

  if (isLoading || !user) {
    return <LoadingScreen variant="fullPage" text="Loading dashboard..." />;
  }

  return (
    <div className="min-h-screen bg-muted">
      {/* Header */}
      <header className="bg-card border-b border-border">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <h1 className="text-2xl font-bold text-foreground">BrieForge</h1>
            <Badge variant="outline">{user.email}</Badge>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/settings">
              <Button variant="ghost">Settings</Button>
            </Link>
            <Button variant="ghost" onClick={() => router.push('/auth/login')}>
              Logout
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Stats Bar */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Campaigns</CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{campaigns?.length || 0}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Signals Collected</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">-</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Analyses Run</CardTitle>
              <BarChart className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">-</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Briefs Generated</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">-</div>
            </CardContent>
          </Card>
        </div>

        {/* Campaigns Section */}
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-3xl font-bold">Your Campaigns</h2>
          <Link href="/campaigns/new">
            <Button size="lg">
              <Plus className="h-5 w-5 mr-2" />
              New Campaign
            </Button>
          </Link>
        </div>

        {/* Campaign Grid */}
        {campaignsLoading ? (
          <LoadingScreen variant="inline" text="Loading campaigns..." />
        ) : campaigns && campaigns.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {campaigns.map((campaign) => (
              <Card key={campaign.id} className="hover:shadow-lg transition-shadow cursor-pointer">
                <Link href={`/campaigns/${campaign.id}`}>
                  <CardHeader>
                    <div className="flex justify-between items-start mb-2">
                      <CardTitle className="text-xl">{campaign.name}</CardTitle>
                      <StatusBadge status={campaign.status} />
                    </div>
                    <CardDescription className="line-clamp-2">
                      {campaign.brief.goal}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2 text-sm">
                      <div>
                        <span className="font-semibold">Audiences:</span>{' '}
                        {campaign.brief.audiences.slice(0, 2).join(', ')}
                        {campaign.brief.audiences.length > 2 && ' +more'}
                      </div>
                      <div>
                        <span className="font-semibold">Channels:</span>{' '}
                        {campaign.brief.channels.slice(0, 3).join(', ')}
                        {campaign.brief.channels.length > 3 && ' +more'}
                      </div>
                      <div className="text-xs text-muted-foreground pt-2">
                        Created {format(new Date(campaign.created_at), 'MMM d, yyyy')}
                      </div>
                    </div>
                  </CardContent>
                </Link>
              </Card>
            ))}
          </div>
        ) : (
          <Card className="bg-card">
            <CardContent className="p-0">
              <EmptyState
                icon={<FileText />}
                title="No campaigns yet"
                description="Create your first intelligence-backed campaign to get started"
                action={{
                  label: "Create First Campaign",
                  onClick: () => router.push('/campaigns/new')
                }}
              />
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}
