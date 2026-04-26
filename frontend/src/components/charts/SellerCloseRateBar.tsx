import { useQuery } from "@tanstack/react-query";
import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts";

import { fetchSellerMetrics } from "@/api/metrics";
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

const chartConfig = {
  close_rate: {
    label: "Tasa de cierre",
    color: "var(--chart-1)",
  },
} satisfies ChartConfig;

export function SellerCloseRateBar({ filters }: { filters: MetricsFilters }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ["metrics", "by-seller", filters],
    queryFn: () => fetchSellerMetrics(filters),
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle className="font-heading text-lg">Cierre por vendedor</CardTitle>
        <CardDescription>Tasa de cierre por seller</CardDescription>
      </CardHeader>
      <CardContent>
        {isLoading ? <ChartSkeleton /> : null}
        {error ? <ChartError /> : null}
        {data && data.length === 0 ? <ChartEmpty /> : null}
        {data && data.length > 0 ? (
          <ChartContainer config={chartConfig} className="h-72 w-full">
            <BarChart data={data} layout="vertical" margin={{ left: 8, right: 24 }}>
              <CartesianGrid horizontal={false} />
              <YAxis
                dataKey="seller_name"
                type="category"
                tickLine={false}
                axisLine={false}
                width={70}
              />
              <XAxis
                type="number"
                domain={[0, 1]}
                tickFormatter={(v) => formatPercent(v, 0)}
              />
              <ChartTooltip
                content={
                  <ChartTooltipContent
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

function ChartSkeleton() {
  return <div className="h-72 w-full animate-pulse rounded-md bg-muted" />;
}

function ChartError() {
  return (
    <p className="text-sm text-destructive">No se pudieron cargar los datos.</p>
  );
}

function ChartEmpty() {
  return <p className="text-sm text-muted-foreground">Sin datos para los filtros activos.</p>;
}
