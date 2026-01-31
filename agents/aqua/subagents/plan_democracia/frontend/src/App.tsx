import { useState } from "react";
import { cn } from "@/lib/utils";

// Layout components
import { Header, Sidebar } from "@/components/layout";

// Chat components
import { ChatInput, MessageList } from "@/components/chat";
import { InsightsPanel } from "@/components/InsightsPanel";
import { LoadingBar } from "@/components/ui/loading-bar";

// Hooks and constants
import { useChat } from "@/hooks/useChat";
import { MOCK_CHAT_HISTORY } from "@/constants/chat";

// Styles
import "./App.css";

function App() {
  const [showSidebar, setShowSidebar] = useState(false);

  const {
    messages,
    isLoading,
    activeInsights,
    showInsightsPanel,
    sendMessage,
    selectInsights,
    closeInsightsPanel,
    resetChat,
    hasInsights,
    insightsCount,
  } = useChat();

  const handleNewChat = () => {
    resetChat();
    setShowSidebar(false);
  };

  const handleSelectChat = (chatId: string) => {
    // TODO: Cargar chat del historial (IndexedDB)
    console.log("Cargar chat:", chatId);
  };

  const toggleInsightsPanel = () => {
    if (showInsightsPanel) {
      closeInsightsPanel();
    } else if (insightsCount > 0) {
      // Reopen with current insights
    }
  };

  return (
    <div className="flex h-screen flex-col bg-background">
      {/* Header */}
      <Header
        onMenuClick={() => setShowSidebar(!showSidebar)}
        insightsCount={insightsCount}
        onInsightsClick={toggleInsightsPanel}
      />

      {/* Sidebar */}
      <Sidebar
        isOpen={showSidebar}
        onClose={() => setShowSidebar(false)}
        onNewChat={handleNewChat}
        chatHistory={MOCK_CHAT_HISTORY}
        onSelectChat={handleSelectChat}
      />

      {/* Loading Bar */}
      <LoadingBar isLoading={isLoading} />

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Chat Area */}
        <div className="flex flex-1 flex-col overflow-hidden">
          <MessageList
            messages={messages}
            isLoading={isLoading}
            activeInsights={activeInsights}
            showInsightsPanel={showInsightsPanel}
            onSelectInsights={selectInsights}
            hasInsights={hasInsights}
          />
          <ChatInput onSendMessage={sendMessage} isLoading={isLoading} />
        </div>

        {/* Insights Panel - Desktop */}
        <div
          className={cn(
            "hidden lg:block transition-all duration-300 ease-in-out overflow-hidden",
            showInsightsPanel && insightsCount > 0
              ? "w-[360px] opacity-100"
              : "w-0 opacity-0"
          )}
        >
          <InsightsPanel
            sources={activeInsights.sources}
            chart={activeInsights.chart}
            onClose={closeInsightsPanel}
          />
        </div>

        {/* Mobile Insights Panel Overlay */}
        <div
          className={cn(
            "fixed inset-0 z-50 lg:hidden transition-opacity duration-300 ease-in-out",
            showInsightsPanel && insightsCount > 0
              ? "opacity-100 pointer-events-auto"
              : "opacity-0 pointer-events-none"
          )}
        >
          <div
            className="absolute inset-0 bg-black/50"
            onClick={closeInsightsPanel}
          />
          <div
            className={cn(
              "absolute right-0 top-0 h-full transition-transform duration-300 ease-in-out",
              showInsightsPanel && insightsCount > 0
                ? "translate-x-0"
                : "translate-x-full"
            )}
          >
            <InsightsPanel
              sources={activeInsights.sources}
              chart={activeInsights.chart}
              onClose={closeInsightsPanel}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
