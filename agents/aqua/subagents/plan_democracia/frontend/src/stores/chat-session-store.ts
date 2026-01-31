import { create } from "zustand";

interface ChatSessionState {
  sessionId: string | null;
  setSessionId: (id: string) => void;
  clearSession: () => void;
  hasSession: () => boolean;
}

export const useChatSessionStore = create<ChatSessionState>()((set, get) => ({
  sessionId: null,

  setSessionId: (id: string) => set({ sessionId: id }),

  clearSession: () => set({ sessionId: null }),

  hasSession: () => get().sessionId !== null,
}));

// Helpers para usar fuera de componentes React
export const getChatSessionId = () => useChatSessionStore.getState().sessionId;
export const setChatSessionId = (id: string) =>
  useChatSessionStore.getState().setSessionId(id);
export const clearChatSession = () =>
  useChatSessionStore.getState().clearSession();
