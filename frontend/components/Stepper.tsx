"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { Check } from "lucide-react"

export interface Step {
  label: string
  description?: string
}

export interface StepperProps {
  steps: Step[]
  currentStep: number
  className?: string
}

export function Stepper({ steps, currentStep, className }: StepperProps) {
  return (
    <nav
      aria-label="Progress"
      className={cn("w-full", className)}
      role="navigation"
    >
      <ol className="flex items-center w-full">
        {steps.map((step, index) => {
          const stepNumber = index + 1
          const isCompleted = stepNumber < currentStep
          const isCurrent = stepNumber === currentStep
          const isUpcoming = stepNumber > currentStep

          return (
            <li
              key={index}
              className={cn(
                "flex items-center",
                index !== steps.length - 1 && "flex-1"
              )}
            >
              <div className="flex flex-col items-center gap-2">
                {/* Step Circle */}
                <div
                  className={cn(
                    "flex items-center justify-center size-10 rounded-full border-2 transition-colors",
                    isCompleted &&
                      "bg-primary border-primary text-primary-foreground",
                    isCurrent &&
                      "border-primary bg-background text-primary font-semibold",
                    isUpcoming &&
                      "border-muted bg-background text-muted-foreground"
                  )}
                  aria-current={isCurrent ? "step" : undefined}
                  aria-label={`Step ${stepNumber}: ${step.label}${
                    isCompleted ? " - Completed" : ""
                  }${isCurrent ? " - Current" : ""}${
                    isUpcoming ? " - Upcoming" : ""
                  }`}
                >
                  {isCompleted ? (
                    <Check className="size-5" aria-hidden="true" />
                  ) : (
                    <span className="text-sm">{stepNumber}</span>
                  )}
                </div>

                {/* Step Label */}
                <div className="flex flex-col items-center text-center min-w-[80px] max-w-[120px]">
                  <span
                    className={cn(
                      "text-xs font-medium transition-colors",
                      isCurrent && "text-foreground",
                      (isCompleted || isUpcoming) && "text-muted-foreground"
                    )}
                  >
                    {step.label}
                  </span>
                  {step.description && (
                    <span className="text-[10px] text-muted-foreground mt-0.5 hidden sm:block">
                      {step.description}
                    </span>
                  )}
                </div>
              </div>

              {/* Connector Line */}
              {index !== steps.length - 1 && (
                <div
                  className="flex-1 h-[2px] mx-2 -mt-14"
                  aria-hidden="true"
                >
                  <div
                    className={cn(
                      "h-full transition-colors",
                      isCompleted ? "bg-primary" : "bg-muted"
                    )}
                  />
                </div>
              )}
            </li>
          )
        })}
      </ol>
    </nav>
  )
}
