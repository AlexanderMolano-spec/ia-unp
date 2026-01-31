import { Plus, MessageSquare, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import type { ChatHistoryItem } from "@/types/chat";

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  onNewChat: () => void;
  chatHistory: ChatHistoryItem[];
  onSelectChat: (chatId: string) => void;
}

export function Sidebar({
  isOpen,
  onClose,
  onNewChat,
  chatHistory,
  onSelectChat,
}: SidebarProps) {
  const handleNewChat = () => {
    onNewChat();
    onClose();
  };

  const handleSelectChat = (chatId: string) => {
    onSelectChat(chatId);
    onClose();
  };

  return (
    <div
      className={cn(
        "fixed inset-0 z-40 transition-opacity duration-300",
        isOpen
          ? "opacity-100 pointer-events-auto"
          : "opacity-0 pointer-events-none"
      )}
    >
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />

      {/* Sidebar Panel */}
      <aside
        className={cn(
          "absolute left-0 top-0 h-full w-[85vw] max-w-[320px] sm:w-[280px] bg-background border-r transition-transform duration-300 flex flex-col shadow-xl",
          isOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-3 sm:p-4 border-b">
          <h2 className="font-semibold text-base sm:text-lg">Historial</h2>
          <Button variant="ghost" size="icon" onClick={onClose} className="h-9 w-9">
            <X className="h-5 w-5" />
          </Button>
        </div>

        {/* New Chat Button */}
        <div className="p-2 sm:p-3">
          <Button
            onClick={handleNewChat}
            className="w-full gap-2 h-11 sm:h-10"
            variant="outline"
          >
            <Plus className="h-4 w-4" />
            Nuevo chat
          </Button>
        </div>

        {/* Chat History */}
        <ScrollArea className="flex-1 px-2 sm:px-3">
          <div className="space-y-1 pb-4">
            {chatHistory.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-8">
                No hay conversaciones
              </p>
            ) : (
              chatHistory.map((chat) => (
                <button
                  key={chat.id}
                  className="w-full flex items-center gap-3 px-3 py-3 sm:py-2.5 rounded-lg hover:bg-muted active:bg-muted/80 text-left transition-colors"
                  onClick={() => handleSelectChat(chat.id)}
                >
                  <MessageSquare className="h-4 w-4 text-muted-foreground shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm truncate">{chat.title}</p>
                    <p className="text-xs text-muted-foreground">{chat.date}</p>
                  </div>
                </button>
              ))
            )}
          </div>
        </ScrollArea>
      </aside>
    </div>
  );
}
