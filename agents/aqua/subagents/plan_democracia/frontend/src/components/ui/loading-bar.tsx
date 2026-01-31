import { cn } from "@/lib/utils";

interface LoadingBarProps {
  isLoading: boolean;
}

export function LoadingBar({ isLoading }: LoadingBarProps) {
  return (
    <div className="relative h-1 w-full overflow-hidden bg-transparent">
      <div
        className={cn(
          "absolute inset-0 bg-primary/20 transition-opacity duration-300",
          isLoading ? "opacity-100" : "opacity-0"
        )}
      />
      <div
        className={cn(
          "absolute inset-y-0 left-0 w-1/3 bg-primary transition-opacity duration-300",
          isLoading ? "opacity-100 animate-loading-bar" : "opacity-0"
        )}
      />
    </div>
  );
}
