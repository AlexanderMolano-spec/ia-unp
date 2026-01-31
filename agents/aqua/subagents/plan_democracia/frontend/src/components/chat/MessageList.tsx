import { useRef, useEffect } from "react";
import { BarChart3, Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ChatMessage } from "@/components/ChatMessage";
import { TypingIndicator } from "./TypingIndicator";
import { cn } from "@/lib/utils";
import type { Message, ActiveInsights } from "@/types/chat";

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
  activeInsights: ActiveInsights;
  showInsightsPanel: boolean;
  onSelectInsights: (message: Message) => void;
  hasInsights: (message: Message) => boolean;
}

export function MessageList({
  messages,
  isLoading,
  activeInsights,
  showInsightsPanel,
  onSelectInsights,
  hasInsights,
}: MessageListProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const getInsightsLabel = (message: Message): string => {
    const parts: string[] = [];
    if (message.chart) parts.push("datos");
    if (message.sources?.length) {
      const count = message.sources.length;
      parts.push(`${count} fuente${count > 1 ? "s" : ""}`);
    }
    return `Ver ${parts.join(" y ")}`;
  };

  const isInsightsActive = (message: Message): boolean => {
    return (
      activeInsights.sources === message.sources &&
      activeInsights.chart === message.chart &&
      showInsightsPanel
    );
  };

  return (
    <ScrollArea className="flex-1 overflow-hidden" viewportRef={scrollRef}>
      <div className="mx-auto max-w-3xl px-2 sm:px-0">
        {messages.map((message) => (
          <div key={message.id}>
            <ChatMessage message={message} />

            {/* Action buttons for assistant messages */}
            {message.role === "assistant" && message.id !== "welcome" && (
              <div className="flex justify-start px-2 sm:px-4 pb-2 gap-1 flex-wrap">
                {hasInsights(message) && (
                  <Button
                    variant="ghost"
                    size="sm"
                    className={cn(
                      "ml-9 sm:ml-11 gap-1.5 sm:gap-2 text-[11px] sm:text-xs text-muted-foreground hover:text-foreground h-8 px-2 sm:px-3",
                      isInsightsActive(message) && "bg-accent"
                    )}
                    onClick={() => onSelectInsights(message)}
                  >
                    <BarChart3 className="h-3.5 w-3.5" />
                    <span className="hidden xs:inline">{getInsightsLabel(message)}</span>
                    <span className="xs:hidden">Ver</span>
                  </Button>
                )}
                <Button
                  variant="ghost"
                  size="sm"
                  className={cn(
                    "gap-1.5 sm:gap-2 text-[11px] sm:text-xs text-muted-foreground hover:text-foreground h-8 px-2 sm:px-3",
                    !hasInsights(message) && "ml-9 sm:ml-11"
                  )}
                  onClick={() => {
                    // TODO: Implementar descarga de PDF
                    console.log("Descargar informe:", message.id);
                  }}
                >
                  <Download className="h-3.5 w-3.5" />
                  <span className="hidden xs:inline">Descargar informe</span>
                  <span className="xs:hidden">PDF</span>
                </Button>
              </div>
            )}
          </div>
        ))}

        {isLoading && <TypingIndicator />}
      </div>
    </ScrollArea>
  );
}
