import { ScrollArea } from "@/components/ui/scroll-area";
import { SourceCard, type Source } from "@/components/SourceCard";
import { BookOpen, X } from "lucide-react";
import { Button } from "@/components/ui/button";

interface SourcesPanelProps {
  sources: Source[];
  onClose?: () => void;
}

export function SourcesPanel({ sources, onClose }: SourcesPanelProps) {
  if (sources.length === 0) return null;

  return (
    <div className="flex h-full w-80 flex-col border-l bg-background">
      <div className="flex items-center justify-between border-b px-4 py-3">
        <div className="flex items-center gap-2">
          <BookOpen className="h-4 w-4 text-muted-foreground" />
          <h2 className="text-sm font-semibold">Fuentes</h2>
          <span className="rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground">
            {sources.length}
          </span>
        </div>
        {onClose && (
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 lg:hidden"
            onClick={onClose}
          >
            <X className="h-4 w-4" />
          </Button>
        )}
      </div>
      <ScrollArea className="flex-1">
        <div className="flex flex-col gap-3 p-4">
          {sources.map((source) => (
            <SourceCard key={source.id} source={source} />
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}
