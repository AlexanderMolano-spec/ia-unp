import { useState, useRef, type FormEvent, type KeyboardEvent } from "react";
import { SendHorizonal } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

export function ChatInput({ onSendMessage, isLoading }: ChatInputProps) {
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e?: FormEvent) => {
    e?.preventDefault();
    const trimmedInput = input.trim();
    if (!trimmedInput || isLoading) return;

    onSendMessage(trimmedInput);
    setInput("");
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="border-t bg-background p-2 sm:p-4">
      <form onSubmit={handleSubmit} className="mx-auto flex max-w-3xl gap-2 sm:gap-3">
        <Textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Escribe tu mensaje..."
          className="min-h-[44px] sm:min-h-[52px] max-h-[120px] sm:max-h-[200px] resize-none text-sm sm:text-base"
          rows={1}
          disabled={isLoading}
        />
        <Button
          type="submit"
          size="icon"
          className="h-[44px] w-[44px] sm:h-[52px] sm:w-[52px] shrink-0"
          disabled={!input.trim() || isLoading}
        >
          <SendHorizonal className="h-4 w-4 sm:h-5 sm:w-5" />
          <span className="sr-only">Enviar mensaje</span>
        </Button>
      </form>
      <p className="mx-auto mt-1.5 sm:mt-2 max-w-3xl text-center text-[10px] sm:text-xs text-muted-foreground hidden sm:block">
        Presiona Enter para enviar, Shift+Enter para nueva línea
      </p>
    </div>
  );
}
