import { useState, useEffect, useRef, useCallback } from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  useMap,
  GeoJSON,
} from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { Send, MapPin, AlertTriangle, Bot, User } from "lucide-react";
import colombiaGeoJson from "../data/colombia.geo.json";

// Fix para los iconos por defecto de Leaflet en Vite
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

delete (L.Icon.Default.prototype as unknown as { _getIconUrl?: string })
  ._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

interface MapMarker {
  id: string;
  lat: number;
  lng: number;
  label: string;
  description: string;
}

interface BoundaryStyle {
  color?: string;
  weight?: number;
  fillColor?: string;
  fillOpacity?: number;
}

interface MapState {
  center: [number, number];
  zoom: number;
  markers: MapMarker[];
  focus?: boolean;
  boundary?: GeoJSON.FeatureCollection | GeoJSON.Feature;
  boundaryStyle?: BoundaryStyle;
}

interface AIInstruction {
  action: string;
  data: MapState;
  message?: string;
  boundary?: GeoJSON.FeatureCollection | GeoJSON.Feature;
  boundaryStyle?: BoundaryStyle;
}

interface ChatMessage {
  id: string;
  type: "user" | "ai" | "system";
  content: string;
  timestamp: Date;
}

// Componente auxiliar para controlar la vista del mapa programáticamente
interface MapControllerProps {
  center: [number, number];
  zoom: number;
}

function MapController({ center, zoom }: MapControllerProps) {
  const map = useMap();
  useEffect(() => {
    if (center) map.flyTo(center, zoom);
  }, [center, zoom, map]);
  return null;
}

const AIMap = () => {
  const [mapState, setMapState] = useState<MapState>({
    center: [4.5709, -74.2973], // Centro de Colombia
    zoom: 6, // Zoom para ver todo el país
    markers: [],
  });

  const [activeBoundary, setActiveBoundary] = useState<
    GeoJSON.FeatureCollection | GeoJSON.Feature | null
  >(null);
  const [boundaryStyle, setBoundaryStyle] = useState<BoundaryStyle>({
    color: "#ef4444",
    weight: 3,
    fillColor: "#ef4444",
    fillOpacity: 0.15,
  });
  const [boundaryKey, setBoundaryKey] = useState(0); // Para forzar re-render del GeoJSON

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isConnected, setIsConnected] = useState(false);

  const ws = useRef<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const addMessage = useCallback(
    (type: ChatMessage["type"], content: string) => {
      const newMessage: ChatMessage = {
        id: crypto.randomUUID(),
        type,
        content,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, newMessage]);
    },
    [],
  );

  const handleAIInstruction = useCallback(
    (instruction: AIInstruction) => {
      switch (instruction.action) {
        case "UPDATE_SITUATION":
          setMapState((prevState) => ({
            ...prevState,
            markers: instruction.data.markers,
            center: instruction.data.focus
              ? instruction.data.center
              : prevState.center,
          }));
          if (instruction.message) {
            addMessage("ai", instruction.message);
          } else {
            addMessage(
              "ai",
              `Mapa actualizado: ${instruction.data.markers.length} marcadores`,
            );
          }
          break;

        case "FOCUS_AREA":
          // Actualizar centro y zoom
          setMapState((prevState) => ({
            ...prevState,
            center: instruction.data.center,
            zoom: instruction.data.zoom,
            markers: instruction.data.markers || prevState.markers,
          }));

          // Actualizar boundary si viene en la instrucción
          if (instruction.boundary) {
            setActiveBoundary(instruction.boundary);
            setBoundaryKey((prev) => prev + 1); // Forzar re-render
          }

          // Actualizar estilo del boundary si viene
          if (instruction.boundaryStyle) {
            setBoundaryStyle((prev) => ({
              ...prev,
              ...instruction.boundaryStyle,
            }));
          }

          if (instruction.message) {
            addMessage("ai", instruction.message);
          }
          break;

        case "CLEAR_BOUNDARY":
          setActiveBoundary(null);
          setMapState((prevState) => ({
            ...prevState,
            markers: prevState.markers,
            center: [4.5709, -74.2973],
            zoom: 6,
          }));
          if (instruction.message) {
            addMessage("ai", instruction.message);
          }
          break;

        case "EMERGENCY_ALERT":
          addMessage("ai", `ALERTA: ${instruction.message}`);
          break;

        default:
          if (instruction.message) {
            addMessage("ai", instruction.message);
          }
      }
    },
    [addMessage],
  );

  useEffect(() => {
    const wsUrl = import.meta.env.VITE_WS_URL || "ws://localhost:8082/ws";
    const socket = new WebSocket(wsUrl);
    ws.current = socket;

    socket.onopen = () => {
      setIsConnected(true);
      addMessage("system", "Conectado al servidor");
    };

    socket.onclose = () => {
      setIsConnected(false);
      addMessage("system", "Desconectado del servidor");
    };

    socket.onerror = () => {
      addMessage("system", "Error de conexión");
    };

    socket.onmessage = (event: MessageEvent) => {
      try {
        const response = JSON.parse(event.data as string) as AIInstruction;
        handleAIInstruction(response);
      } catch {
        addMessage("ai", event.data as string);
      }
    };

    return () => socket.close();
  }, [addMessage, handleAIInstruction]);

  const sendMessage = () => {
    if (!inputValue.trim() || !ws.current || !isConnected) return;

    addMessage("user", inputValue);
    ws.current.send(JSON.stringify({ message: inputValue }));
    setInputValue("");
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex h-screen w-full bg-background">
      {/* Mapa - Lado izquierdo */}
      <div className="flex-1 relative">
        <MapContainer
          center={mapState.center}
          zoom={mapState.zoom}
          className="h-full w-full"
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution="&copy; OpenStreetMap contributors"
          />

          {/* Resaltado de Colombia */}
          <GeoJSON
            data={colombiaGeoJson as GeoJSON.FeatureCollection}
            style={{
              color: "#3b82f6",
              weight: 2,
              fillColor: "#3b82f6",
              fillOpacity: 0.1,
            }}
          />

          {/* Boundary dinámico (ciudad, departamento, etc.) */}
          {activeBoundary && (
            <GeoJSON
              key={boundaryKey}
              data={activeBoundary}
              style={{
                color: boundaryStyle.color,
                weight: boundaryStyle.weight,
                fillColor: boundaryStyle.fillColor,
                fillOpacity: boundaryStyle.fillOpacity,
              }}
            />
          )}

          <MapController center={mapState.center} zoom={mapState.zoom} />
          {mapState.markers.map((marker) => (
            <Marker key={marker.id} position={[marker.lat, marker.lng]}>
              <Popup>
                <strong>{marker.label}</strong>
                <br />
                {marker.description}
              </Popup>
            </Marker>
          ))}
        </MapContainer>

        {/* Indicador de marcadores */}
        {mapState.markers.length > 0 && (
          <div className="absolute top-4 left-4 z-[1000] bg-card/90 backdrop-blur-sm px-3 py-2 rounded-lg shadow-lg border border-border flex items-center gap-2">
            <MapPin className="w-4 h-4 text-primary" />
            <span className="text-sm font-medium">
              {mapState.markers.length} marcadores
            </span>
          </div>
        )}
      </div>

      {/* Sidebar - Lado derecho */}
      <div className="w-96 border-l border-border flex flex-col bg-sidebar">
        {/* Header del sidebar */}
        <div className="p-4 border-b border-sidebar-border">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Bot className="w-5 h-5 text-sidebar-primary" />
              <h2 className="font-semibold text-sidebar-foreground">
                Asistente de Mapa
              </h2>
            </div>
            <div className="flex items-center gap-2">
              <div
                className={`w-2 h-2 rounded-full ${
                  isConnected ? "bg-green-500" : "bg-red-500"
                }`}
              />
              <span className="text-xs text-sidebar-foreground/70">
                {isConnected ? "Conectado" : "Desconectado"}
              </span>
            </div>
          </div>
        </div>

        {/* Área de mensajes */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-muted-foreground py-8">
              <Bot className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p className="text-sm">
                Envía un mensaje para interactuar con el mapa
              </p>
            </div>
          )}

          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex gap-3 ${
                msg.type === "user" ? "flex-row-reverse" : ""
              }`}
            >
              {msg.type !== "system" && (
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                    msg.type === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-sidebar-accent text-sidebar-accent-foreground"
                  }`}
                >
                  {msg.type === "user" ? (
                    <User className="w-4 h-4" />
                  ) : (
                    <Bot className="w-4 h-4" />
                  )}
                </div>
              )}

              <div
                className={`flex-1 ${msg.type === "user" ? "text-right" : ""}`}
              >
                {msg.type === "system" ? (
                  <div className="flex items-center justify-center gap-2 text-xs text-muted-foreground py-2">
                    <AlertTriangle className="w-3 h-3" />
                    {msg.content}
                  </div>
                ) : (
                  <div
                    className={`inline-block px-4 py-2 rounded-2xl max-w-[85%] ${
                      msg.type === "user"
                        ? "bg-primary text-primary-foreground rounded-br-md"
                        : "bg-sidebar-accent text-sidebar-accent-foreground rounded-bl-md"
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                  </div>
                )}
                <p className="text-[10px] text-muted-foreground mt-1 px-1">
                  {msg.timestamp.toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </p>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Input de mensaje */}
        <div className="p-4 border-t border-sidebar-border">
          <div className="flex gap-2">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Escribe un mensaje..."
              disabled={!isConnected}
              className="flex-1 px-4 py-2 rounded-full bg-input border border-border text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50 disabled:cursor-not-allowed text-sm"
            />
            <button
              onClick={sendMessage}
              disabled={!isConnected || !inputValue.trim()}
              className="w-10 h-10 rounded-full bg-primary text-primary-foreground flex items-center justify-center hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIMap;
