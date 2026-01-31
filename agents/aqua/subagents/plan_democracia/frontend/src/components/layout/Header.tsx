import { useState } from "react";
import { Menu, BarChart3, Key, Settings } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useApiKeyStore } from "@/stores/api-key-store";
import { cn } from "@/lib/utils";
import logoUnidad from "@/assets/logo_unidad_gris.svg";

interface HeaderProps {
  onMenuClick: () => void;
  insightsCount: number;
  onInsightsClick: () => void;
}

export function Header({
  onMenuClick,
  insightsCount,
  onInsightsClick,
}: HeaderProps) {
  const { apiKey, setApiKey } = useApiKeyStore();
  const [showApiKeyInput, setShowApiKeyInput] = useState(false);

  return (
    <header className="relative flex items-center justify-between border-b px-2 py-2 sm:px-4 sm:py-3">
      {/* Left - Menu button */}
      <div className="flex items-center gap-1 sm:gap-2 shrink-0">
        <Button variant="ghost" size="icon" onClick={onMenuClick} className="h-9 w-9 sm:h-10 sm:w-10">
          <Menu className="h-5 w-5" />
        </Button>
      </div>

      {/* Center - Title */}
      <div className="flex items-center gap-2 sm:gap-3 flex-1 justify-center min-w-0">
        <img
          src={logoUnidad}
          alt="Logo Unidad"
          className="h-6 sm:h-8 w-auto shrink-0"
        />
        <div className="text-center min-w-0">
          <h1 className="text-sm sm:text-lg font-semibold truncate">Plan Democracia</h1>
          <p className="text-[10px] sm:text-xs text-muted-foreground hidden sm:block">
            Asistente de participación ciudadana
          </p>
        </div>
      </div>

      {/* Right - Actions */}
      <div className="flex items-center gap-1 sm:gap-2 shrink-0">
        {/* API Key - Dev only */}
        {import.meta.env.DEV && (
          <>
            {/* Mobile: Icon button to toggle input */}
            <Button
              variant="ghost"
              size="icon"
              className={cn(
                "h-9 w-9 sm:hidden",
                apiKey && "text-green-600"
              )}
              onClick={() => setShowApiKeyInput(!showApiKeyInput)}
            >
              <Key className="h-4 w-4" />
            </Button>

            {/* Desktop: Always visible input */}
            <div className="hidden sm:flex items-center gap-2">
              <Label htmlFor="apikey" className="text-xs whitespace-nowrap">
                GEMINI API KEY
              </Label>
              <Input
                id="apikey"
                type="password"
                placeholder="API Key"
                value={apiKey || ""}
                onChange={(e) => setApiKey(e.target.value)}
                className="w-[120px] md:w-[150px] h-8 text-xs"
              />
            </div>
          </>
        )}

        {/* Insights button */}
        {insightsCount > 0 && (
          <Button
            variant="outline"
            size="icon"
            className="h-9 w-9 sm:h-auto sm:w-auto sm:px-3 sm:py-1.5 lg:hidden"
            onClick={onInsightsClick}
          >
            <BarChart3 className="h-4 w-4 sm:mr-2" />
            <span className="hidden sm:inline text-sm">
              Ver datos ({insightsCount})
            </span>
          </Button>
        )}
      </div>

      {/* Mobile API Key Input - Expandable */}
      {import.meta.env.DEV && showApiKeyInput && (
        <div className="absolute top-full left-0 right-0 bg-background border-b p-3 sm:hidden z-50 animate-in slide-in-from-top-2">
          <div className="flex items-center gap-2">
            <Label htmlFor="apikey-mobile" className="text-xs whitespace-nowrap">
              GEMINI API KEY
            </Label>
            <Input
              id="apikey-mobile"
              type="password"
              placeholder="Ingresa tu API Key"
              value={apiKey || ""}
              onChange={(e) => setApiKey(e.target.value)}
              className="flex-1 h-8 text-xs"
              autoFocus
            />
          </div>
        </div>
      )}
    </header>
  );
}
