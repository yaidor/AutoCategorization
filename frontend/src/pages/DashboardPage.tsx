import { useQuery } from "@tanstack/react-query";
import {
  AlertCircleIcon,
  BarChart3Icon,
  CalendarCheckIcon,
  MessageSquareIcon,
  PercentIcon,
  RouteIcon,
  SparklesIcon,
  type LucideIcon,
} from "lucide-react";
import { type ReactNode } from "react";

import { ApiError, api } from "@/api/client";
import { useAuth } from "@/auth/AuthContext";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { formatNumber, formatPercent } from "@/lib/format";

interface OverviewResponse {
  total_meetings: number;
  closed_meetings: number;
  close_rate: number;
  avg_sentiment: number | null;
  avg_close_probability: number | null;
  top_industry: string | null;
  top_discovery_channel: string | null;
}

export function DashboardPage() {
  const { clearApiKey } = useAuth();
  const { data, isLoading, error } = useQuery({
    queryKey: ["metrics", "overview"],
    queryFn: () => api.get<OverviewResponse>("/api/v1/metrics/overview"),
  });

  return (
    <div className="space-y-6">
      <header>
        <h1 className="font-heading text-3xl font-semibold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">Vista general de las reuniones de ventas.</p>
      </header>

      {isLoading ? <SkeletonGrid /> : null}

      {error ? <DashboardError error={error} onLogout={clearApiKey} /> : null}

      {data ? <KPIGrid data={data} /> : null}
    </div>
  );
}

function KPIGrid({ data }: { data: OverviewResponse }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <KPICard
        title="Total reuniones"
        value={formatNumber(data.total_meetings)}
        description={`${formatNumber(data.closed_meetings)} cerradas`}
        icon={CalendarCheckIcon}
      />
      <KPICard
        title="Tasa de cierre"
        value={formatPercent(data.close_rate)}
        description="del total de reuniones"
        icon={PercentIcon}
      />
      <KPICard
        title="Sentimiento promedio"
        value={data.avg_sentiment !== null ? formatNumber(data.avg_sentiment, 2) : "—"}
        description="rango -1 a +1"
        icon={MessageSquareIcon}
      />
      <KPICard
        title="Probabilidad de cierre"
        value={
          data.avg_close_probability !== null
            ? formatPercent(data.avg_close_probability)
            : "—"
        }
        description="proyección promedio del LLM"
        icon={BarChart3Icon}
      />
      <KPICard
        title="Industria principal"
        value={data.top_industry ?? "—"}
        description="con más reuniones"
        icon={SparklesIcon}
      />
      <KPICard
        title="Canal principal"
        value={data.top_discovery_channel ?? "—"}
        description="cómo nos descubrieron"
        icon={RouteIcon}
      />
    </div>
  );
}

function KPICard({
  title,
  value,
  description,
  icon: Icon,
}: {
  title: string;
  value: string;
  description: string;
  icon: LucideIcon;
}) {
  return (
    <Card>
      <CardHeader>
        <CardDescription className="flex items-center gap-2">
          <Icon className="h-4 w-4" />
          {title}
        </CardDescription>
        <CardTitle className="font-heading text-2xl break-words">{value}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-xs text-muted-foreground">{description}</p>
      </CardContent>
    </Card>
  );
}

function SkeletonGrid() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {Array.from({ length: 6 }).map((_, i) => (
        <Card key={i}>
          <CardHeader>
            <CardDescription>
              <span className="inline-block h-3 w-24 animate-pulse rounded bg-muted" />
            </CardDescription>
            <CardTitle>
              <span className="inline-block h-7 w-20 animate-pulse rounded bg-muted" />
            </CardTitle>
          </CardHeader>
          <CardContent>
            <span className="inline-block h-3 w-32 animate-pulse rounded bg-muted" />
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

function DashboardError({
  error,
  onLogout,
}: {
  error: unknown;
  onLogout: () => void;
}): ReactNode {
  if (error instanceof ApiError && error.status === 401) {
    return (
      <Alert variant="destructive">
        <AlertCircleIcon className="h-4 w-4" />
        <AlertTitle>Sesión expirada</AlertTitle>
        <AlertDescription className="space-y-2">
          <p>Tu API key ya no es válida.</p>
          <Button variant="outline" size="sm" onClick={onLogout}>
            Volver al login
          </Button>
        </AlertDescription>
      </Alert>
    );
  }
  const message = error instanceof Error ? error.message : "Error desconocido";
  return (
    <Alert variant="destructive">
      <AlertCircleIcon className="h-4 w-4" />
      <AlertTitle>No se pudieron cargar las métricas</AlertTitle>
      <AlertDescription>{message}</AlertDescription>
    </Alert>
  );
}
