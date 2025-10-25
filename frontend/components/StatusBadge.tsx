"use client"

import * as React from "react"
import { cn } from "@/lib/utils"

const statusStyles: Record<string, string> = {
  draft:
    "bg-secondary/50 text-secondary-foreground border-secondary dark:bg-secondary/30",
  collecting_signals:
    "bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-950/50 dark:text-blue-400 dark:border-blue-900",
  analyzing:
    "bg-purple-50 text-purple-700 border-purple-200 dark:bg-purple-950/50 dark:text-purple-400 dark:border-purple-900",
  ready:
    "bg-green-50 text-green-700 border-green-200 dark:bg-green-950/50 dark:text-green-400 dark:border-green-900",
  failed:
    "bg-destructive/10 text-destructive border-destructive/20 dark:bg-destructive/20 dark:border-destructive/30",
  completed:
    "bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/50 dark:text-emerald-400 dark:border-emerald-900",
  pending:
    "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/50 dark:text-amber-400 dark:border-amber-900",
}

export interface StatusBadgeProps
  extends React.HTMLAttributes<HTMLSpanElement> {
  status: string
}

export function StatusBadge({
  className,
  status,
  children,
  ...props
}: StatusBadgeProps) {
  const baseClasses = "inline-flex items-center justify-center rounded-full border px-2.5 py-1 text-xs font-medium w-fit whitespace-nowrap shrink-0 transition-colors"
  const statusClass = statusStyles[status] || statusStyles.draft

  return (
    <span
      className={cn(baseClasses, statusClass, className)}
      {...props}
    >
      {children || (status && status.replace(/_/g, " ").toUpperCase())}
    </span>
  )
}
