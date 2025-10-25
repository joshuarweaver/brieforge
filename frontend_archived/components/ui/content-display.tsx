import React from 'react';
import { cn } from '@/lib/utils';

interface ContentDisplayProps {
  content: any;
  className?: string;
}

export function ContentDisplay({ content, className }: ContentDisplayProps) {
  // If content is a string, display it directly
  if (typeof content === 'string') {
    return (
      <div className={cn('prose prose-sm max-w-none', className)}>
        <p className="whitespace-pre-wrap">{content}</p>
      </div>
    );
  }

  // If content is an object with specific fields, format them nicely
  if (typeof content === 'object' && content !== null) {
    // Check for common strategic brief structure
    if ('executive_summary' in content || 'recommendations' in content) {
      return (
        <div className={cn('space-y-6', className)}>
          {content.executive_summary && (
            <div>
              <h3 className="font-semibold text-lg mb-2">Executive Summary</h3>
              <p className="text-muted-foreground whitespace-pre-wrap">
                {content.executive_summary}
              </p>
            </div>
          )}
          {content.key_insights && Array.isArray(content.key_insights) && (
            <div>
              <h3 className="font-semibold text-lg mb-2">Key Insights</h3>
              <ul className="list-disc list-inside space-y-1 text-muted-foreground">
                {content.key_insights.map((insight: string, idx: number) => (
                  <li key={idx}>{insight}</li>
                ))}
              </ul>
            </div>
          )}
          {content.recommendations && Array.isArray(content.recommendations) && (
            <div>
              <h3 className="font-semibold text-lg mb-2">Recommendations</h3>
              <ul className="list-disc list-inside space-y-1 text-muted-foreground">
                {content.recommendations.map((rec: string, idx: number) => (
                  <li key={idx}>{rec}</li>
                ))}
              </ul>
            </div>
          )}
          {content.audience_insights && (
            <div>
              <h3 className="font-semibold text-lg mb-2">Audience Insights</h3>
              <p className="text-muted-foreground whitespace-pre-wrap">
                {typeof content.audience_insights === 'string'
                  ? content.audience_insights
                  : JSON.stringify(content.audience_insights, null, 2)}
              </p>
            </div>
          )}
          {content.messaging && (
            <div>
              <h3 className="font-semibold text-lg mb-2">Messaging</h3>
              <p className="text-muted-foreground whitespace-pre-wrap">
                {typeof content.messaging === 'string'
                  ? content.messaging
                  : JSON.stringify(content.messaging, null, 2)}
              </p>
            </div>
          )}
        </div>
      );
    }

    // For analysis insights
    if ('trends' in content || 'patterns' in content || 'insights' in content) {
      return (
        <div className={cn('space-y-6', className)}>
          {content.insights && (
            <div>
              <h3 className="font-semibold text-lg mb-2">Insights</h3>
              {Array.isArray(content.insights) ? (
                <ul className="list-disc list-inside space-y-1 text-muted-foreground">
                  {content.insights.map((insight: any, idx: number) => (
                    <li key={idx}>
                      {typeof insight === 'string' ? insight : JSON.stringify(insight)}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-muted-foreground whitespace-pre-wrap">
                  {typeof content.insights === 'string'
                    ? content.insights
                    : JSON.stringify(content.insights, null, 2)}
                </p>
              )}
            </div>
          )}
          {content.trends && (
            <div>
              <h3 className="font-semibold text-lg mb-2">Trends</h3>
              {Array.isArray(content.trends) ? (
                <ul className="list-disc list-inside space-y-1 text-muted-foreground">
                  {content.trends.map((trend: any, idx: number) => (
                    <li key={idx}>
                      {typeof trend === 'string' ? trend : JSON.stringify(trend)}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-muted-foreground">{content.trends}</p>
              )}
            </div>
          )}
          {content.patterns && (
            <div>
              <h3 className="font-semibold text-lg mb-2">Patterns</h3>
              {Array.isArray(content.patterns) ? (
                <ul className="list-disc list-inside space-y-1 text-muted-foreground">
                  {content.patterns.map((pattern: any, idx: number) => (
                    <li key={idx}>
                      {typeof pattern === 'string' ? pattern : JSON.stringify(pattern)}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-muted-foreground">{content.patterns}</p>
              )}
            </div>
          )}
        </div>
      );
    }
  }

  // Fallback to formatted JSON
  return (
    <pre className={cn('text-xs bg-muted p-4 rounded overflow-auto max-h-96 text-foreground', className)}>
      {JSON.stringify(content, null, 2)}
    </pre>
  );
}
