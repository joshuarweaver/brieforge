"use client"

import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { Skeleton } from "@/components/ui/skeleton"
import { cn } from "@/lib/utils"
import { Loader2 } from "lucide-react"

const loadingScreenVariants = cva("flex items-center justify-center", {
  variants: {
    variant: {
      fullPage: "min-h-screen w-full bg-background",
      inline: "w-full py-8",
      card: "w-full p-6 rounded-lg border bg-card",
    },
  },
  defaultVariants: {
    variant: "inline",
  },
})

export interface LoadingScreenProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof loadingScreenVariants> {
  text?: string
  showSpinner?: boolean
  showSkeleton?: boolean
}

export function LoadingScreen({
  className,
  variant,
  text = "Loading...",
  showSpinner = true,
  showSkeleton = false,
  ...props
}: LoadingScreenProps) {
  return (
    <div
      className={cn(loadingScreenVariants({ variant }), className)}
      role="status"
      aria-live="polite"
      aria-label={text}
      {...props}
    >
      {showSkeleton ? (
        <div className="w-full max-w-2xl space-y-4">
          <Skeleton className="h-8 w-3/4" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-5/6" />
          <div className="grid grid-cols-2 gap-4 mt-6">
            <Skeleton className="h-24" />
            <Skeleton className="h-24" />
          </div>
          <Skeleton className="h-32 w-full mt-4" />
        </div>
      ) : (
        <div className="flex flex-col items-center gap-3">
          {showSpinner && (
            <Loader2 className="size-8 animate-spin text-primary" />
          )}
          <p className="text-sm text-muted-foreground">{text}</p>
        </div>
      )}
    </div>
  )
}
