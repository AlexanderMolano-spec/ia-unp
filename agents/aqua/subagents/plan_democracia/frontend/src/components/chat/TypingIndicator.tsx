import { Bot, Loader2 } from "lucide-react";

export function TypingIndicator() {
  return (
    <div className="flex gap-3 p-4">
      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-muted">
        <Bot className="h-4 w-4 text-muted-foreground" />
      </div>
      <div className="flex items-center gap-2 rounded-2xl rounded-tl-sm bg-muted px-4 py-2.5">
        <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
        <span className="text-sm text-muted-foreground">Escribiendo...</span>
      </div>
    </div>
  );
}
