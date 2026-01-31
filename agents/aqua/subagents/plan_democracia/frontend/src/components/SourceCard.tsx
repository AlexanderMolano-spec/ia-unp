import { useState } from "react";
import { ExternalLink, Globe, FileText } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";

export interface Source {
  id: string;
  title: string;
  url: string;
  description?: string;
  type?: "web" | "document" | "other";
  previewImage?: string;
}

interface SourceCardProps {
  source: Source;
}

export function SourceCard({ source }: SourceCardProps) {
  const Icon = source.type === "document" ? FileText : Globe;
  const [imageLoaded, setImageLoaded] = useState(false);
  const [imageError, setImageError] = useState(false);

  // Generar URL de preview usando un servicio gratuito
  const getPreviewUrl = () => {
    if (source.previewImage) return source.previewImage;
    if (source.type === "document") return null;
    // Usar microlink para obtener screenshot
    return `https://api.microlink.io/?url=${encodeURIComponent(source.url)}&screenshot=true&meta=false&embed=screenshot.url`;
  };

  const previewUrl = getPreviewUrl();

  return (
    <a
      href={source.url}
      target="_blank"
      rel="noopener noreferrer"
      className="block w-full rounded-lg border bg-card transition-all hover:bg-accent hover:shadow-sm group overflow-hidden"
    >
      {/* Preview Image */}
      {previewUrl && !imageError && (
        <div className="relative w-full h-24 bg-muted overflow-hidden">
          {!imageLoaded && (
            <Skeleton className="absolute inset-0 w-full h-full" />
          )}
          <img
            src={previewUrl}
            alt={`Preview de ${source.title}`}
            className={`w-full h-full object-cover object-top transition-opacity duration-300 ${
              imageLoaded ? "opacity-100" : "opacity-0"
            }`}
            onLoad={() => setImageLoaded(true)}
            onError={() => setImageError(true)}
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent" />
        </div>
      )}

      {/* Content */}
      <div className="p-3">
        <div className="flex items-start gap-3 w-full overflow-hidden">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-muted">
            <Icon className="h-4 w-4 text-muted-foreground" />
          </div>
          <div className="flex-1 min-w-0 overflow-hidden">
            <div className="flex items-start justify-between gap-2">
              <p className="text-sm font-medium leading-tight line-clamp-2 break-words">
                {source.title}
              </p>
              <ExternalLink className="h-3.5 w-3.5 shrink-0 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100 mt-0.5" />
            </div>
            <p className="text-xs text-muted-foreground mt-1 truncate">
              {new URL(source.url).hostname}
            </p>
            {source.description && (
              <p className="text-xs text-muted-foreground mt-1 line-clamp-2 break-words">
                {source.description}
              </p>
            )}
          </div>
        </div>
      </div>
    </a>
  );
}
