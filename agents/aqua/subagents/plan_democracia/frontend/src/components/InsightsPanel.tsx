import { ScrollArea } from "@/components/ui/scroll-area";
import { SourceCard, type Source } from "@/components/SourceCard";
import { ChartDisplay, type ChartData } from "@/components/ChartDisplay";
import { BookOpen, BarChart3, X, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";

interface InsightsPanelProps {
  sources: Source[];
  chart?: ChartData;
  onClose?: () => void;
}

export function InsightsPanel({ sources, chart, onClose }: InsightsPanelProps) {
  const hasContent = sources.length > 0 || chart;

  if (!hasContent) return null;

  return (
    <div className="flex h-full w-[360px] max-w-[360px] flex-col border-l bg-background overflow-hidden">
      {/* Header */}
      <div className="flex shrink-0 items-center justify-between border-b px-4 py-3">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-muted-foreground" />
          <h2 className="text-sm font-semibold">Información adicional</h2>
        </div>
        {onClose && (
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={onClose}
          >
            <X className="h-4 w-4" />
          </Button>
        )}
      </div>

      {/* Content */}
      <div className="flex-1 min-h-0 overflow-hidden">
        <ScrollArea className="h-full w-full">
          <div className="w-[89%] flex flex-col gap-4 p-3">
            {/* Chart Section */}
            {chart && (
              <div className="w-full flex flex-col gap-2 overflow-hidden">
                <div className="flex items-center gap-2">
                  <BarChart3 className="h-4 w-4 text-muted-foreground" />
                  <h3 className="text-sm font-medium">Estadísticas</h3>
                </div>
                <ChartDisplay chart={chart} />
              </div>
            )}

            {/* Separator */}
            {chart && sources.length > 0 && <Separator />}

            {/* Sources Section */}
            {sources.length > 0 && (
              <div className="w-full flex flex-col gap-2">
                <div className="flex items-center gap-2">
                  <BookOpen className="h-4 w-4 text-muted-foreground" />
                  <h3 className="text-sm font-medium">Fuentes</h3>
                  <span className="rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground">
                    {sources.length}
                  </span>
                </div>
                <div className="flex flex-col gap-2">
                  {sources.map((source) => (
                    <SourceCard key={source.id} source={source} />
                  ))}
                </div>
              </div>
            )}
          </div>
        </ScrollArea>
      </div>
    </div>
  );
}
