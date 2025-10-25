import React from 'react';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import {
  Linkedin,
  Facebook,
  Instagram,
  Youtube,
  Search,
} from 'lucide-react';

interface ChannelBadgeProps {
  channelId: string;
  channelName: string;
  className?: string;
  showIcon?: boolean;
}

const channelIcons: Record<string, React.ReactNode> = {
  linkedin: <Linkedin className="h-3 w-3" />,
  facebook: <Facebook className="h-3 w-3" />,
  instagram: <Instagram className="h-3 w-3" />,
  tiktok: <span className="text-xs font-bold">TT</span>,
  youtube: <Youtube className="h-3 w-3" />,
  pinterest: <span className="text-xs font-bold">P</span>,
  google_ads: <Search className="h-3 w-3" />,
};

export function ChannelBadge({ channelId, channelName, className, showIcon = true }: ChannelBadgeProps) {
  const icon = channelIcons[channelId] || null;

  return (
    <Badge variant="secondary" className={cn('gap-1.5', className)}>
      {showIcon && icon}
      {channelName}
    </Badge>
  );
}
