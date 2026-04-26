import { api } from "@/api/client";
import type {
  DiscoveryChannelMetric,
  IndustryMetric,
  MetricsFilters,
  ObjectionMetric,
  OverviewResponse,
  SellerMetric,
  SellerOption,
} from "@/api/types";

function buildQuery(filters: MetricsFilters): string {
  const params = new URLSearchParams();
  if (filters.from) params.set("from", filters.from);
  if (filters.to) params.set("to", filters.to);
  if (filters.seller_id !== undefined) params.set("seller_id", String(filters.seller_id));
  if (filters.industry) params.set("industry", filters.industry);
  if (filters.closed !== undefined) params.set("closed", String(filters.closed));
  if (filters.uncategorized !== undefined) {
    params.set("uncategorized", String(filters.uncategorized));
  }
  const qs = params.toString();
  return qs ? `?${qs}` : "";
}

export const fetchOverview = (filters: MetricsFilters) =>
  api.get<OverviewResponse>(`/api/v1/metrics/overview${buildQuery(filters)}`);

export const fetchSellerMetrics = (filters: MetricsFilters) =>
  api.get<SellerMetric[]>(`/api/v1/metrics/by-seller${buildQuery(filters)}`);

export const fetchIndustryMetrics = (filters: MetricsFilters) =>
  api.get<IndustryMetric[]>(`/api/v1/metrics/by-industry${buildQuery(filters)}`);

export const fetchObjections = (filters: MetricsFilters, limit = 10) => {
  const params = new URLSearchParams(buildQuery(filters).slice(1));
  params.set("limit", String(limit));
  const qs = params.toString();
  return api.get<ObjectionMetric[]>(
    `/api/v1/metrics/objections${qs ? `?${qs}` : ""}`,
  );
};

export const fetchDiscoveryChannels = (filters: MetricsFilters) =>
  api.get<DiscoveryChannelMetric[]>(
    `/api/v1/metrics/discovery-channels${buildQuery(filters)}`,
  );

export const fetchSellers = () => api.get<SellerOption[]>("/api/v1/sellers");
