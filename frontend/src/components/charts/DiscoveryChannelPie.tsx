import { useQuery } from "@tanstack/react-query";
import { Cell, Pie, PieChart } from "recharts";

import { fetchDiscoveryChannels } from "@/api/metrics";
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
  ChartLegend,
  ChartLegendContent,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart";
import { humanizeChannel } from "@/lib/labels";

const PIE_COLORS = [
  "var(--chart-1)",
  "var(--chart-2)",
  "var(--chart-3)",
  "var(--chart-4)",
  "var(--chart-5)",
];

export function DiscoveryChannelPie({ filters }: { filters: MetricsFilters }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ["metrics", "discovery-channels", filters],
    queryFn: () => fetchDiscoveryChannels(filters),
  });

  const chartConfig: ChartConfig = (data ?? []).reduce<ChartConfig>((acc, item, i) => {
    acc[item.discovery_channel] = {
      label: humanizeChannel(item.discovery_channel),
      color: PIE_COLORS[i % PIE_COLORS.length],
    };
    return acc;
  }, {});

  return (
    <Card>
      <CardHeader>
        <CardTitle className="font-heading text-lg">Canales de descubrimiento</CardTitle>
        <CardDescription>Cómo nos descubrieron los clientes</CardDescription>
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
          <ChartContainer config={chartConfig} className="mx-auto h-72 w-full">
            <PieChart>
              <ChartTooltip
                content={
                  <ChartTooltipContent
                    nameKey="discovery_channel"
                    labelFormatter={(label) => humanizeChannel(String(label))}
                  />
                }
              />
              <Pie
                data={data}
                dataKey="total_meetings"
                nameKey="discovery_channel"
                cy="44%"
                outerRadius={80}
                strokeWidth={2}
              >
                {data.map((item, i) => (
                  <Cell
                    key={item.discovery_channel}
                    fill={PIE_COLORS[i % PIE_COLORS.length]}
                  />
                ))}
              </Pie>
              <ChartLegend
                content={
                  <ChartLegendContent
                    nameKey="discovery_channel"
                    className="flex-wrap gap-x-3 gap-y-1"
                  />
                }
                verticalAlign="bottom"
              />
            </PieChart>
          </ChartContainer>
        ) : null}
      </CardContent>
    </Card>
  );
}
