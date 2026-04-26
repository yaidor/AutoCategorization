import { useQuery } from "@tanstack/react-query";
import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts";

import { fetchIndustryMetrics } from "@/api/metrics";
import type { MetricsFilters } from "@/api/types";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart";
import { formatPercent } from "@/lib/format";
import { humanizeIndustry } from "@/lib/labels";

const chartConfig = {
  close_rate: {
    label: "Tasa de cierre",
    color: "var(--chart-2)",
  },
} satisfies ChartConfig;

export function IndustryBar({ filters }: { filters: MetricsFilters }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ["metrics", "by-industry", filters],
    queryFn: () => fetchIndustryMetrics(filters),
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle className="font-heading text-lg">Cierre por industria</CardTitle>
        <CardDescription>Ordenado por volumen</CardDescription>
      </CardHeader>
      <CardContent>
        {isLoading ? <div className="h-72 w-full animate-pulse rounded-md bg-muted" /> : null}
        {error ? (
          <p className="text-sm text-destructive">No se pudieron cargar los datos.</p>
        ) : null}
        {data && data.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            Sin datos para los filtros activos.
          </p>
        ) : null}
        {data && data.length > 0 ? (
          <ChartContainer config={chartConfig} className="h-72 w-full">
            <BarChart data={data} layout="vertical" margin={{ left: 8, right: 24 }}>
              <CartesianGrid horizontal={false} />
              <YAxis
                dataKey="industry"
                type="category"
                tickLine={false}
                axisLine={false}
                width={150}
                tickFormatter={(value) => humanizeIndustry(value)}
              />
              <XAxis
                type="number"
                domain={[0, 1]}
                tickFormatter={(v) => formatPercent(v, 0)}
              />
              <ChartTooltip
                content={
                  <ChartTooltipContent
                    labelFormatter={(label) => humanizeIndustry(String(label))}
                    formatter={(value) => formatPercent(Number(value))}
                  />
                }
              />
              <Bar dataKey="close_rate" fill="var(--color-close_rate)" radius={4} />
            </BarChart>
          </ChartContainer>
        ) : null}
      </CardContent>
    </Card>
  );
}
