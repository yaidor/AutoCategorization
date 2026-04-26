import { useQuery } from "@tanstack/react-query";

import { fetchObjections } from "@/api/metrics";
import type { MetricsFilters } from "@/api/types";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export function ObjectionsList({ filters }: { filters: MetricsFilters }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ["metrics", "objections", filters],
    queryFn: () => fetchObjections(filters, 10),
  });

  const maxFreq = data && data.length > 0 ? data[0].frequency_pct : 1;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="font-heading text-lg">Top objeciones</CardTitle>
        <CardDescription>Frecuencia entre reuniones con objeción registrada</CardDescription>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-2">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-8 animate-pulse rounded bg-muted" />
            ))}
          </div>
        ) : null}
        {error ? (
          <p className="text-sm text-destructive">No se pudieron cargar los datos.</p>
        ) : null}
        {data && data.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            No se detectaron objeciones en las transcripciones.
          </p>
        ) : null}
        {data && data.length > 0 ? (
          <ul className="space-y-3">
            {data.map((row) => (
              <li key={row.objection} className="space-y-1">
                <div className="flex items-baseline justify-between gap-2 text-sm">
                  <span className="truncate">{row.objection}</span>
                  <span className="font-medium tabular-nums">
                    {row.count} · {row.frequency_pct.toFixed(0)}%
                  </span>
                </div>
                <div className="h-1.5 w-full rounded-full bg-muted">
                  <div
                    className="h-full rounded-full bg-primary"
                    style={{ width: `${(row.frequency_pct / maxFreq) * 100}%` }}
                  />
                </div>
              </li>
            ))}
          </ul>
        ) : null}
      </CardContent>
    </Card>
  );
}
