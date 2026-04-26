import { api } from "@/api/client";
import type {
  CategorizationFull,
  CustomerDetailResponse,
  CustomerListPage,
  CustomerSort,
  MetricsFilters,
} from "@/api/types";

export interface ListCustomersParams extends MetricsFilters {
  skip?: number;
  limit?: number;
  sort?: CustomerSort;
  search?: string;
}

function buildQuery(params: ListCustomersParams): string {
  const qs = new URLSearchParams();
  if (params.skip !== undefined) qs.set("skip", String(params.skip));
  if (params.limit !== undefined) qs.set("limit", String(params.limit));
  if (params.sort) qs.set("sort", params.sort);
  if (params.search) qs.set("search", params.search);
  if (params.from) qs.set("from", params.from);
  if (params.to) qs.set("to", params.to);
  if (params.seller_id !== undefined) qs.set("seller_id", String(params.seller_id));
  if (params.industry) qs.set("industry", params.industry);
  if (params.closed !== undefined) qs.set("closed", String(params.closed));
  if (params.uncategorized !== undefined) {
    qs.set("uncategorized", String(params.uncategorized));
  }
  const s = qs.toString();
  return s ? `?${s}` : "";
}

export const fetchCustomers = (params: ListCustomersParams) =>
  api.get<CustomerListPage>(`/api/v1/customers${buildQuery(params)}`);

export const fetchCustomerDetail = (id: number) =>
  api.get<CustomerDetailResponse>(`/api/v1/customers/${id}`);

export const recategorizeMeeting = (meetingId: number) =>
  api.post<CategorizationFull>(`/api/v1/meetings/${meetingId}/categorize?force=true`);
