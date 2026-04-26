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

import { ApiError } from "@/api/client";
import { fetchOverview } from "@/api/metrics";
import type { OverviewResponse } from "@/api/types";
import { useAuth } from "@/auth/AuthContext";
import { DiscoveryChannelPie } from "@/components/charts/DiscoveryChannelPie";
import { IndustryBar } from "@/components/charts/IndustryBar";
import { ObjectionsList } from "@/components/charts/ObjectionsList";
import { SellerCloseRateBar } from "@/components/charts/SellerCloseRateBar";
import { GlobalFilters } from "@/components/filters/GlobalFilters";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useMetricsFilters } from "@/hooks/useMetricsFilters";
import { formatNumber, formatPercent } from "@/lib/format";
import { humanizeChannel, humanizeIndustry } from "@/lib/labels";

export function DashboardPage() {
  const { clearApiKey } = useAuth();
  const { filters } = useMetricsFilters();
  const overview = useQuery({
    queryKey: ["metrics", "overview", filters],
    queryFn: () => fetchOverview(filters),
  });

  return (
    <div className="space-y-6">
      <header>
        <h1 className="font-heading text-3xl font-semibold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">Vista general de las reuniones de ventas.</p>
      </header>

      <GlobalFilters />

      {overview.isLoading ? <SkeletonGrid /> : null}
      {overview.error ? (
        <DashboardError error={overview.error} onLogout={clearApiKey} />
      ) : null}
      {overview.data ? <KPIGrid data={overview.data} /> : null}

      <div className="grid gap-4 lg:grid-cols-2">
        <SellerCloseRateBar filters={filters} />
        <IndustryBar filters={filters} />
        <DiscoveryChannelPie filters={filters} />
        <ObjectionsList filters={filters} />
      </div>
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
        value={humanizeIndustry(data.top_industry)}
        description="con más reuniones"
        icon={SparklesIcon}
      />
      <KPICard
        title="Canal principal"
        value={humanizeChannel(data.top_discovery_channel)}
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
