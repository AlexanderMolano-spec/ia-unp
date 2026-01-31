import type { Source } from "@/components/SourceCard";
import type { ChartData } from "@/components/ChartDisplay";

export interface Message {
  id: string;
  content: string;
  role: "user" | "assistant";
  timestamp: Date;
  sources?: Source[];
  chart?: ChartData;
}

export interface ChatHistoryItem {
  id: string;
  title: string;
  date: string;
}

export interface ActiveInsights {
  sources: Source[];
  chart?: ChartData;
}

export type { Source, ChartData };
