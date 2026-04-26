import { useQuery } from "@tanstack/react-query";
import { FilterIcon, XIcon } from "lucide-react";

import { fetchSellers } from "@/api/metrics";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useMetricsFilters } from "@/hooks/useMetricsFilters";
import { INDUSTRY_LABELS } from "@/lib/labels";

const SELECT_CLASSES =
  "h-9 w-full rounded-md border bg-background px-3 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring [&>option]:bg-card [&>option]:text-foreground";

export function GlobalFilters() {
  const { filters, setFilter, clearFilters, hasActiveFilters } = useMetricsFilters();
  const sellersQuery = useQuery({
    queryKey: ["sellers", "list"],
    queryFn: fetchSellers,
  });

  return (
    <section className="rounded-lg border bg-card p-4">
      <div className="mb-3 flex items-center gap-2">
        <FilterIcon className="h-4 w-4 text-muted-foreground" />
        <span className="text-sm font-medium">Filtros</span>
        {hasActiveFilters ? (
          <Button
            variant="ghost"
            size="sm"
            onClick={clearFilters}
            className="ml-auto h-7"
          >
            <XIcon className="h-3 w-3" /> Limpiar
          </Button>
        ) : null}
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        <div className="space-y-1.5">
          <Label htmlFor="from">Desde</Label>
          <Input
            id="from"
            type="date"
            value={filters.from ?? ""}
            onChange={(e) => setFilter("from", e.target.value || undefined)}
          />
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="to">Hasta</Label>
          <Input
            id="to"
            type="date"
            value={filters.to ?? ""}
            onChange={(e) => setFilter("to", e.target.value || undefined)}
          />
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="seller">Vendedor</Label>
          <select
            id="seller"
            className={SELECT_CLASSES}
            value={filters.seller_id ?? ""}
            onChange={(e) =>
              setFilter("seller_id", e.target.value ? Number(e.target.value) : undefined)
            }
            disabled={sellersQuery.isLoading}
          >
            <option value="">Todos</option>
            {sellersQuery.data?.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="industry">Industria</Label>
          <select
            id="industry"
            className={SELECT_CLASSES}
            value={filters.industry ?? ""}
            onChange={(e) => setFilter("industry", e.target.value || undefined)}
          >
            <option value="">Todas</option>
            {Object.entries(INDUSTRY_LABELS).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="closed">Estado</Label>
          <select
            id="closed"
            className={SELECT_CLASSES}
            value={filters.closed === undefined ? "" : String(filters.closed)}
            onChange={(e) => {
              const v = e.target.value;
              setFilter("closed", v === "" ? undefined : v === "true");
            }}
          >
            <option value="">Todas</option>
            <option value="true">Cerradas</option>
            <option value="false">Abiertas</option>
          </select>
        </div>
      </div>
    </section>
  );
}
