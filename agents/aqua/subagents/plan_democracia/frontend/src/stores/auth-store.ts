import { create } from "zustand";

export interface Servicio {
  url: string;
  rol: string;
  id_rol: number;
}

export interface User {
  username: string;
  nombres: string;
  dependencia: string;
  grupo: string;
  id_busuario: string;
  servicios: Servicio[];
}

export interface AuthState {
  session_id: string | null;
  expiresAt: number | null;
  user: User | null;
}

export interface UserIdentity {
  username: string | null;
  nombres: string | null;
}

export interface UserArea {
  dependencia: string | null;
  grupo: string | null;
}

interface AuthStore extends AuthState {
  loadFromStorage: () => void;
  clearAuth: () => void;
  isAuthenticated: () => boolean;
  isSessionExpired: () => boolean;
  getUser: () => User | null;
  getSessionId: () => string | null;
  getUserIdentity: () => UserIdentity;
  getUserArea: () => UserArea;
  getUserId: () => string | null;
  getServicios: () => Servicio[];
  hasServicio: (url: string) => boolean;
  hasRol: (idRol: number) => boolean;
}

const initialState: AuthState = {
  session_id: null,
  expiresAt: null,
  user: null,
};

// Lee el auth_state del localStorage
const loadAuthFromStorage = (): AuthState => {
  // Verificar si estamos en el navegador
  if (typeof window === "undefined") return initialState;

  try {
    const stored = localStorage.getItem("auth_state");
    if (!stored) return initialState;

    // Sanitizar el JSON: reemplazar espacios especiales y normalizar
    const sanitized = stored
      .replace(/[\u00A0\u2000-\u200B\u202F\u205F\u3000]/g, " ") // Non-breaking spaces
      .replace(/[\r\n\t]/g, " ") // Saltos de línea y tabs
      .replace(/\s+/g, " "); // Múltiples espacios a uno solo

    const parsed = JSON.parse(sanitized);

    return {
      session_id: parsed.session_id ?? null,
      expiresAt: parsed.expiresAt ?? null,
      user: parsed.user ?? null,
    };
  } catch (error) {
    console.error("[auth-store] Error parsing auth_state:", error);
    return initialState;
  }
};

export const useAuthStore = create<AuthStore>()((set, get) => ({
  // Carga inicial desde localStorage
  ...loadAuthFromStorage(),

  loadFromStorage: () => {
    const auth = loadAuthFromStorage();
    set(auth);
  },

  clearAuth: () => {
    localStorage.removeItem("auth_state");
    set(initialState);
  },

  isAuthenticated: () => {
    const state = get();
    return (
      state.session_id !== null &&
      state.user !== null &&
      !get().isSessionExpired()
    );
  },

  isSessionExpired: () => {
    const expiresAt = get().expiresAt;
    if (!expiresAt) return true;
    return Date.now() > expiresAt;
  },

  getUser: () => get().user,

  getSessionId: () => get().session_id,

  getUserIdentity: () => ({
    username: get().user?.username ?? null,
    nombres: get().user?.nombres ?? null,
  }),

  getUserArea: () => ({
    dependencia: get().user?.dependencia ?? null,
    grupo: get().user?.grupo ?? null,
  }),

  getUserId: () => get().user?.id_busuario ?? null,

  getServicios: () => get().user?.servicios ?? [],

  hasServicio: (url: string) => {
    const servicios = get().user?.servicios ?? [];
    return servicios.some((s) => s.url === url);
  },

  hasRol: (idRol: number) => {
    const servicios = get().user?.servicios ?? [];
    return servicios.some((s) => s.id_rol === idRol);
  },
}));

// Helpers para usar fuera de componentes React
export const getAuth = () => useAuthStore.getState();
export const getUser = () => useAuthStore.getState().user;
export const getSessionId = () => useAuthStore.getState().session_id;
export const getUserIdentity = () => useAuthStore.getState().getUserIdentity();
export const getUserArea = () => useAuthStore.getState().getUserArea();
export const getUserId = () => useAuthStore.getState().getUserId();
export const getServicios = () => useAuthStore.getState().user?.servicios ?? [];
export const isAuthenticated = () => useAuthStore.getState().isAuthenticated();
export const loadAuthFromLocalStorage = () =>
  useAuthStore.getState().loadFromStorage();
