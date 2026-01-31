import { useState, useCallback } from "react";
import type { Message, ActiveInsights } from "@/types/chat";
import { useAuthStore, clearChatSession } from "@/stores";
import {
  INITIAL_MESSAGES,
  MOCK_SOURCES,
  MOCK_CHART,
} from "@/constants/chat";

interface UseChatReturn {
  messages: Message[];
  isLoading: boolean;
  activeInsights: ActiveInsights;
  showInsightsPanel: boolean;
  sendMessage: (content: string) => Promise<void>;
  selectInsights: (message: Message) => void;
  closeInsightsPanel: () => void;
  resetChat: () => void;
  hasInsights: (message: Message) => boolean;
  insightsCount: number;
}

export function useChat(): UseChatReturn {
  const [messages, setMessages] = useState<Message[]>(INITIAL_MESSAGES);
  const [isLoading, setIsLoading] = useState(false);
  const [activeInsights, setActiveInsights] = useState<ActiveInsights>({
    sources: [],
  });
  const [showInsightsPanel, setShowInsightsPanel] = useState(false);

  const { getUserId, getUserIdentity, getUserArea, getServicios } =
    useAuthStore();

  const hasInsights = useCallback((message: Message): boolean => {
    return (message.sources && message.sources.length > 0) || !!message.chart;
  }, []);

  const insightsCount =
    activeInsights.sources.length + (activeInsights.chart ? 1 : 0);

  const selectInsights = useCallback((message: Message) => {
    setActiveInsights({
      sources: message.sources || [],
      chart: message.chart,
    });
    setShowInsightsPanel(true);
  }, []);

  const closeInsightsPanel = useCallback(() => {
    setShowInsightsPanel(false);
  }, []);

  const resetChat = useCallback(() => {
    setMessages(INITIAL_MESSAGES);
    setActiveInsights({ sources: [] });
    setShowInsightsPanel(false);
    clearChatSession();
  }, []);

  const sendMessage = useCallback(
    async (content: string) => {
      const trimmedContent = content.trim();
      if (!trimmedContent || isLoading) return;

      const userMessage: Message = {
        id: `user-${Date.now()}`,
        content: trimmedContent,
        role: "user",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);
      setShowInsightsPanel(false);
      setActiveInsights({ sources: [] });

      // Preparar payload con datos del usuario
      const payload = {
        message: trimmedContent,
        user: {
          ...getUserIdentity(),
          ...getUserArea(),
          id_busuario: getUserId(),
          servicios: getServicios(),
        },
        input_mode: "text",
      };

      if (import.meta.env.DEV) {
        console.log("[useChat] Payload a enviar:", payload);
      }

      try {
        // TODO: Descomentar cuando tengas el endpoint listo:
        // const response = await apiService.post("/chat", payload);
        // console.log("[useChat] Respuesta:", response.data);

        // Por ahora simular respuesta
        await new Promise((resolve) => setTimeout(resolve, 1500));

        const assistantMessage: Message = {
          id: `assistant-${Date.now()}`,
          content:
            "Los mecanismos de participación ciudadana en Colombia incluyen: el voto, el plebiscito, el referendo, la consulta popular, el cabildo abierto, la iniciativa legislativa y la revocatoria del mandato. Estos están consagrados en la Constitución Política y regulados por la Ley 134 de 1994.\n\nEn los últimos años, el cabildo abierto ha sido el mecanismo más utilizado, seguido por las consultas populares y las revocatorias de mandato.",
          role: "assistant",
          timestamp: new Date(),
          sources: MOCK_SOURCES,
          chart: MOCK_CHART,
        };

        setMessages((prev) => [...prev, assistantMessage]);
        setActiveInsights({
          sources: MOCK_SOURCES,
          chart: MOCK_CHART,
        });
        setShowInsightsPanel(true);
      } catch (error) {
        console.error("[useChat] Error:", error);
        const errorMessage: Message = {
          id: `error-${Date.now()}`,
          content:
            "Lo siento, ocurrió un error al procesar tu mensaje. Por favor intenta de nuevo.",
          role: "assistant",
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      } finally {
        setIsLoading(false);
      }
    },
    [isLoading, getUserId, getUserIdentity, getUserArea, getServicios]
  );

  return {
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
  };
}
