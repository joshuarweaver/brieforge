import React from 'react';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface StatusBadgeProps {
  status: string;
  className?: string;
}

const statusConfig: Record<string, { className: string; label: string }> = {
  completed: {
    className: 'bg-green-500 hover:bg-green-600 text-white',
    label: 'Completed',
  },
  failed: {
    className: 'bg-destructive hover:bg-destructive/90 text-white',
    label: 'Failed',
  },
  pending: {
    className: 'bg-muted hover:bg-muted/90 text-muted-foreground',
    label: 'Pending',
  },
  processing: {
    className: 'bg-primary hover:bg-primary/90 text-primary-foreground',
    label: 'Processing',
  },
  active: {
    className: 'bg-primary hover:bg-primary/90 text-primary-foreground',
    label: 'Active',
  },
  draft: {
    className: 'bg-muted hover:bg-muted/90 text-muted-foreground',
    label: 'Draft',
  },
  ready: {
    className: 'bg-green-500 hover:bg-green-600 text-white',
    label: 'Ready',
  },
  collecting_signals: {
    className: 'bg-primary hover:bg-primary/90 text-primary-foreground',
    label: 'Collecting Signals',
  },
  analyzing: {
    className: 'bg-primary hover:bg-primary/90 text-primary-foreground',
    label: 'Analyzing',
  },
};

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const normalizedStatus = status?.toLowerCase() || 'pending';
  const config = statusConfig[normalizedStatus] || {
    className: 'bg-secondary hover:bg-secondary/90 text-secondary-foreground',
    label: status || 'Unknown',
  };

  return (
    <Badge className={cn(config.className, className)}>
      {config.label}
    </Badge>
  );
}
