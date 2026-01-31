import type { Message, ChatHistoryItem, Source, ChartData } from "@/types/chat";

export const WELCOME_MESSAGE: Message = {
  id: "welcome",
  content:
    "¡Hola! Soy tu asistente del Plan Democracia. Estoy aquí para ayudarte con información sobre participación ciudadana, procesos democráticos y tus derechos. ¿En qué puedo ayudarte hoy?",
  role: "assistant",
  timestamp: new Date(),
};

export const INITIAL_MESSAGES: Message[] = [WELCOME_MESSAGE];

// Mock data para desarrollo (eliminar cuando se conecte al backend)
export const MOCK_CHAT_HISTORY: ChatHistoryItem[] = [
  { id: "1", title: "Mecanismos de participación", date: "Hoy" },
  { id: "2", title: "Derechos ciudadanos", date: "Ayer" },
  { id: "3", title: "Consulta popular", date: "23 Ene" },
];

export const MOCK_SOURCES: Source[] = [
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

export const MOCK_CHART: ChartData = {
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
