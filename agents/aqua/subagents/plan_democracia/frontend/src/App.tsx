import {
  useState,
  useRef,
  useEffect,
  type FormEvent,
  type KeyboardEvent,
} from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ChatMessage, type Message } from "@/components/ChatMessage";
import { InsightsPanel } from "@/components/InsightsPanel";
import type { Source } from "@/components/SourceCard";
import type { ChartData } from "@/components/ChartDisplay";
import { Bot, SendHorizonal, Loader2, BarChart3, Download } from "lucide-react";
import { cn } from "@/lib/utils";
import logoUnidad from "@/assets/logo_unidad_gris.svg";
import "./App.css";
import { Input } from "./components/ui/input";
import { useApiKeyStore } from "@/stores/api-key-store";
import { useAuthStore } from "./stores";

const INITIAL_MESSAGES: Message[] = [
  {
    id: "welcome",
    content:
      "¡Hola! Soy tu asistente del Plan Democracia. Estoy aquí para ayudarte con información sobre participación ciudadana, procesos democráticos y tus derechos. ¿En qué puedo ayudarte hoy?",
    role: "assistant",
    timestamp: new Date(),
  },
];

interface ActiveInsights {
  sources: Source[];
  chart?: ChartData;
}

function App() {
  const [messages, setMessages] = useState<Message[]>(INITIAL_MESSAGES);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [activeInsights, setActiveInsights] = useState<ActiveInsights>({
    sources: [],
  });
  const [showInsightsPanel, setShowInsightsPanel] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const { apiKey, setApiKey } = useApiKeyStore();
  const { getUserId, getUserIdentity, getUserArea, getServicios } =
    useAuthStore();

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSelectInsights = (message: Message) => {
    setActiveInsights({
      sources: message.sources || [],
      chart: message.chart,
    });
    setShowInsightsPanel(true);
  };

  const hasInsights = (message: Message) => {
    return (message.sources && message.sources.length > 0) || message.chart;
  };

  const handleSubmit = async (e?: FormEvent) => {
    e?.preventDefault();

    const trimmedInput = input.trim();
    if (!trimmedInput || isLoading) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      content: trimmedInput,
      role: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    // Cerrar sidebar y limpiar insights mientras se espera la respuesta
    setShowInsightsPanel(false);
    setActiveInsights({ sources: [] });

    // Preparar payload con datos del usuario
    const payload = {
      message: trimmedInput,
      user: {
        ...getUserIdentity(),
        ...getUserArea(),
        id_busuario: getUserId(),
        servicios: getServicios(),
      },
      input_mode: "text",
    };

    // Debug: imprimir payload antes de enviar
    console.log("[handleSubmit] Payload a enviar:", payload);

    try {
      // Descomentar cuando tengas el endpoint listo:
      // const response = await apiService.post("/chat", payload);
      // console.log("[handleSubmit] Respuesta:", response.data);

      // Por ahora simular respuesta
      await new Promise((resolve) => setTimeout(resolve, 1500));
      // Ejemplo de respuesta con fuentes y datos estadísticos
      const mockSources: Source[] = [
        {
          id: "src-1",
          title: "Constitución Política de Colombia - Artículo 40",
          url: "https://www.constitucioncolombia.com/titulo-2/capitulo-1/articulo-40",
          description:
            "Derechos fundamentales de participación ciudadana y mecanismos de democracia directa.",
          type: "web",
        },
        {
          id: "src-2",
          title: "Registraduría Nacional - Mecanismos de Participación",
          url: "https://www.registraduria.gov.co/mecanismos-de-participacion",
          description:
            "Información oficial sobre los mecanismos de participación ciudadana en Colombia.",
          type: "web",
        },
        {
          id: "src-3",
          title: "Ley 134 de 1994 - Mecanismos de Participación Ciudadana",
          url: "https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=330",
          description:
            "Marco legal que regula los mecanismos de participación del pueblo.",
          type: "document",
        },
      ];

      const mockChart: ChartData = {
        id: "chart-1",
        title: "Participación por mecanismo (2020-2024)",
        description: "Número de iniciativas ciudadanas por tipo",
        type: "bar",
        data: [
          { label: "Consulta Popular", value: 45 },
          { label: "Referendo", value: 12 },
          { label: "Revocatoria", value: 28 },
          { label: "Cabildo Abierto", value: 156 },
          { label: "Iniciativa Legislativa", value: 8 },
        ],
      };

      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        content:
          "Los mecanismos de participación ciudadana en Colombia incluyen: el voto, el plebiscito, el referendo, la consulta popular, el cabildo abierto, la iniciativa legislativa y la revocatoria del mandato. Estos están consagrados en la Constitución Política y regulados por la Ley 134 de 1994.\n\nEn los últimos años, el cabildo abierto ha sido el mecanismo más utilizado, seguido por las consultas populares y las revocatorias de mandato.",
        role: "assistant",
        timestamp: new Date(),
        sources: mockSources,
        chart: mockChart,
      };
      setMessages((prev) => [...prev, assistantMessage]);

      // Mostrar automáticamente el panel si hay insights
      setActiveInsights({
        sources: mockSources,
        chart: mockChart,
      });
      setShowInsightsPanel(true);
    } catch (error) {
      console.error("[handleSubmit] Error:", error);
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
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const insightsCount =
    activeInsights.sources.length + (activeInsights.chart ? 1 : 0);

  return (
    <div className="flex h-screen flex-col bg-background">
      {/* Header */}
      <header className="flex items-center justify-between border-b px-6 py-4">
        <div className="flex items-center gap-3">
          <img src={logoUnidad} alt="Logo Unidad" className="h-10 w-auto" />
          <div>
            <h1 className="text-lg font-semibold">Plan Democracia</h1>
            <p className="text-sm text-muted-foreground">
              Asistente de participación ciudadana
            </p>
          </div>
        </div>
        {import.meta.env.DEV && (
          <div>
            <Input
              placeholder="Ingresa tu API Key de Gemini"
              value={apiKey || ""}
              onChange={(e) => setApiKey(e.target.value)}
            />
          </div>
        )}
        {insightsCount > 0 && (
          <Button
            variant="outline"
            size="sm"
            className="gap-2 lg:hidden"
            onClick={() => setShowInsightsPanel(!showInsightsPanel)}
          >
            <BarChart3 className="h-4 w-4" />
            Ver datos ({insightsCount})
          </Button>
        )}
      </header>

      {/* Loading Bar */}
      <div className="relative h-1 w-full overflow-hidden bg-transparent">
        <div
          className={cn(
            "absolute inset-0 bg-primary/20 transition-opacity duration-300",
            isLoading ? "opacity-100" : "opacity-0",
          )}
        />
        <div
          className={cn(
            "absolute inset-y-0 left-0 w-1/3 bg-primary transition-opacity duration-300",
            isLoading ? "opacity-100 animate-loading-bar" : "opacity-0",
          )}
        />
      </div>

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Chat Area */}
        <div className="flex flex-1 flex-col overflow-hidden">
          <ScrollArea
            className="flex-1 overflow-hidden"
            viewportRef={scrollRef}
          >
            <div className="mx-auto max-w-3xl">
              {messages.map((message) => (
                <div key={message.id}>
                  <ChatMessage message={message} />
                  {message.role === "assistant" && message.id !== "welcome" && (
                    <div className="flex justify-start px-4 pb-2 gap-1 flex-wrap">
                      {hasInsights(message) && (
                        <Button
                          variant="ghost"
                          size="sm"
                          className={cn(
                            "ml-11 gap-2 text-xs text-muted-foreground hover:text-foreground",
                            activeInsights.sources === message.sources &&
                              activeInsights.chart === message.chart &&
                              showInsightsPanel &&
                              "bg-accent",
                          )}
                          onClick={() => handleSelectInsights(message)}
                        >
                          <BarChart3 className="h-3.5 w-3.5" />
                          Ver {message.chart ? "datos" : ""}{" "}
                          {message.chart && message.sources?.length ? "y " : ""}
                          {message.sources?.length
                            ? `${message.sources.length} fuente${message.sources.length > 1 ? "s" : ""}`
                            : ""}
                        </Button>
                      )}
                      <Button
                        variant="ghost"
                        size="sm"
                        className={cn(
                          "gap-2 text-xs text-muted-foreground hover:text-foreground",
                          !hasInsights(message) && "ml-11",
                        )}
                        onClick={() => {
                          // TODO: Implementar descarga de PDF
                          console.log("Descargar informe:", message.id);
                        }}
                      >
                        <Download className="h-3.5 w-3.5" />
                        Descargar informe
                      </Button>
                    </div>
                  )}
                </div>
              ))}
              {isLoading && (
                <div className="flex gap-3 p-4">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-muted">
                    <Bot className="h-4 w-4 text-muted-foreground" />
                  </div>
                  <div className="flex items-center gap-2 rounded-2xl rounded-tl-sm bg-muted px-4 py-2.5">
                    <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">
                      Escribiendo...
                    </span>
                  </div>
                </div>
              )}
            </div>
          </ScrollArea>

          {/* Input Area */}
          <div className="border-t bg-background p-4">
            <form
              onSubmit={handleSubmit}
              className="mx-auto flex max-w-3xl gap-3"
            >
              <Textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Escribe tu mensaje..."
                className="min-h-[52px] max-h-[200px] resize-none"
                rows={1}
                disabled={isLoading}
              />
              <Button
                type="submit"
                size="icon"
                className="h-[52px] w-[52px] shrink-0"
                disabled={!input.trim() || isLoading}
              >
                <SendHorizonal className="h-5 w-5" />
                <span className="sr-only">Enviar mensaje</span>
              </Button>
            </form>
            <p className="mx-auto mt-2 max-w-3xl text-center text-xs text-muted-foreground">
              Presiona Enter para enviar, Shift+Enter para nueva línea
            </p>
          </div>
        </div>

        {/* Insights Panel - Desktop */}
        <div
          className={cn(
            "hidden lg:block transition-all duration-300 ease-in-out overflow-hidden",
            showInsightsPanel && insightsCount > 0
              ? "w-[360px] opacity-100"
              : "w-0 opacity-0",
          )}
        >
          <InsightsPanel
            sources={activeInsights.sources}
            chart={activeInsights.chart}
            onClose={() => setShowInsightsPanel(false)}
          />
        </div>

        {/* Mobile Insights Panel Overlay */}
        <div
          className={cn(
            "fixed inset-0 z-50 lg:hidden transition-opacity duration-300 ease-in-out",
            showInsightsPanel && insightsCount > 0
              ? "opacity-100 pointer-events-auto"
              : "opacity-0 pointer-events-none",
          )}
        >
          <div
            className="absolute inset-0 bg-black/50"
            onClick={() => setShowInsightsPanel(false)}
          />
          <div
            className={cn(
              "absolute right-0 top-0 h-full transition-transform duration-300 ease-in-out",
              showInsightsPanel && insightsCount > 0
                ? "translate-x-0"
                : "translate-x-full",
            )}
          >
            <InsightsPanel
              sources={activeInsights.sources}
              chart={activeInsights.chart}
              onClose={() => setShowInsightsPanel(false)}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
