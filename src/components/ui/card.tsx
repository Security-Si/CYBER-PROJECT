import * as React from "react";
import { cn } from "@/lib/cn";

export function Card({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "rounded-2xl border bg-card text-card-foreground shadow-[0_18px_45px_rgba(15,23,42,0.10)]",
        className
      )}
      {...props}
    />
  );
}

