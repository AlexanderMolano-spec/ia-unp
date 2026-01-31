import { Menu, BarChart3 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useApiKeyStore } from "@/stores/api-key-store";
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

  return (
    <header className="flex items-center justify-between border-b px-4 py-3">
      {/* Left - Menu button */}
      <div className="flex items-center gap-2 w-[200px]">
        <Button variant="ghost" size="icon" onClick={onMenuClick}>
          <Menu className="h-5 w-5" />
        </Button>
      </div>

      {/* Center - Title */}
      <div className="flex items-center gap-3 flex-1 justify-center">
        <img src={logoUnidad} alt="Logo Unidad" className="h-8 w-auto" />
        <div className="text-center">
          <h1 className="text-lg font-semibold">Plan Democracia</h1>
          <p className="text-xs text-muted-foreground">
            Asistente de participación ciudadana
          </p>
        </div>
      </div>

      {/* Right - API Key (dev) & Insights button */}
      <div className="flex items-center gap-2 w-[200px] justify-end">
        {import.meta.env.DEV && (
          <div className="flex items-center gap-2">
            <Label htmlFor="apikey" className="text-xs whitespace-nowrap">
              GEMINI API KEY
            </Label>
            <Input
              id="apikey"
              type="password"
              placeholder="API Key"
              value={apiKey || ""}
              onChange={(e) => setApiKey(e.target.value)}
              className="w-[150px] h-8 text-xs"
            />
          </div>
        )}
        {insightsCount > 0 && (
          <Button
            variant="outline"
            size="sm"
            className="gap-2 lg:hidden"
            onClick={onInsightsClick}
          >
            <BarChart3 className="h-4 w-4" />
            Ver datos ({insightsCount})
          </Button>
        )}
      </div>
    </header>
  );
}
