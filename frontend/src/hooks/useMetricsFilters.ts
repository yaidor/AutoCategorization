import { useSearchParams } from "react-router-dom";

import type { MetricsFilters } from "@/api/types";

type FilterKey = keyof MetricsFilters;
type FilterValue<K extends FilterKey> = MetricsFilters[K];

export function useMetricsFilters() {
  const [searchParams, setSearchParams] = useSearchParams();

  const filters: MetricsFilters = {};
  const from = searchParams.get("from");
  const to = searchParams.get("to");
  const sellerId = searchParams.get("seller_id");
  const industry = searchParams.get("industry");
  const closed = searchParams.get("closed");
  const uncategorized = searchParams.get("uncategorized");

  if (from) filters.from = from;
  if (to) filters.to = to;
  if (sellerId) filters.seller_id = Number(sellerId);
  if (industry) filters.industry = industry;
  if (closed !== null) filters.closed = closed === "true";
  if (uncategorized !== null) filters.uncategorized = uncategorized === "true";

  function setFilter<K extends FilterKey>(key: K, value: FilterValue<K> | undefined) {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      if (value === undefined || value === null || value === "") {
        next.delete(key);
      } else {
        next.set(key, String(value));
      }
      return next;
    });
  }

  function clearFilters() {
    setSearchParams(new URLSearchParams());
  }

  const hasActiveFilters = Object.keys(filters).length > 0;

  return { filters, setFilter, clearFilters, hasActiveFilters };
}
