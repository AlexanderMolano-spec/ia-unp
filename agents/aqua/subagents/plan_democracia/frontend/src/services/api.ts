import axios from "axios";
import type { AxiosError, InternalAxiosRequestConfig } from "axios";
import { getApiKey, getChatSessionId, setChatSessionId } from "@/stores";
import { getUserId, getUserIdentity, getUserArea } from "@/stores";

// Crear instancia de axios
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Interceptor de request - agrega API key y datos del usuario
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Agregar API Key solo en desarrollo
    if (import.meta.env.DEV) {
      const apiKey = getApiKey();
      if (apiKey) {
        config.headers["GEMINI_API_KEY"] = apiKey;
      }
    }

    // Agregar session de chat (se obtiene del response del primer mensaje)
    const chatSessionId = getChatSessionId();
    if (chatSessionId) {
      config.headers["X-Session-Id"] = chatSessionId;
    }

    // Agregar ID de usuario
    const userId = getUserId();
    if (userId) {
      config.headers["X-User-Id"] = userId;
    }

    // Debug: imprimir request antes de enviar (solo en desarrollo)
    if (import.meta.env.DEV) {
      console.log("[API Request]", {
        method: config.method?.toUpperCase(),
        url: config.url,
        baseURL: config.baseURL,
        fullURL: `${config.baseURL}${config.url}`,
        headers: config.headers,
        data: config.data,
        userIdentity: getUserIdentity(),
        userArea: getUserArea(),
      });
    }

    return config;
  },
  (error: AxiosError) => {
    console.error("[API Request Error]", error);
    return Promise.reject(error);
  },
);

// Interceptor de response
api.interceptors.response.use(
  (response) => {
    // Capturar session_id del response headers
    const sessionId = response.headers["x-session-id"];
    if (sessionId) {
      setChatSessionId(sessionId);
      if (import.meta.env.DEV) {
        console.log("[API] Session ID guardado:", sessionId);
      }
    }

    if (import.meta.env.DEV) {
      console.log("[API Response]", {
        status: response.status,
        headers: response.headers,
        data: response.data,
      });
    }
    return response;
  },
  (error: AxiosError) => {
    if (import.meta.env.DEV) {
      console.error("[API Response Error]", {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message,
      });
    }
    return Promise.reject(error);
  },
);

// Métodos de la API
export const apiService = {
  get: <T>(url: string, params?: object) => api.get<T>(url, { params }),

  post: <T>(url: string, data?: object) => api.post<T>(url, data),

  put: <T>(url: string, data?: object) => api.put<T>(url, data),

  patch: <T>(url: string, data?: object) => api.patch<T>(url, data),

  delete: <T>(url: string) => api.delete<T>(url),
};

export default api;
