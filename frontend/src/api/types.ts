export interface IngestError {
  row: number;
  field: string | null;
  message: string;
}

export interface IngestSummary {
  total_rows: number;
  inserted: number;
  skipped_duplicates: number;
  errors: IngestError[];
  new_sellers: string[];
}

export interface JobError {
  meeting_id: number;
  error: string;
}

export type JobStatus = "queued" | "running" | "completed" | "failed";

export interface JobResponse {
  id: number;
  status: JobStatus;
  total: number;
  completed: number;
  failed: number;
  cached: number;
  errors: JobError[];
  created_at: string;
  updated_at: string;
}

export interface OverviewResponse {
  total_meetings: number;
  closed_meetings: number;
  close_rate: number;
  avg_sentiment: number | null;
  avg_close_probability: number | null;
  top_industry: string | null;
  top_discovery_channel: string | null;
}

export interface SellerMetric {
  seller_id: number;
  seller_name: string;
  total_meetings: number;
  closed_meetings: number;
  close_rate: number;
  avg_sentiment: number;
  avg_interest_level: number;
  avg_close_probability: number;
}

export interface IndustryMetric {
  industry: string;
  total_meetings: number;
  closed_meetings: number;
  close_rate: number;
  avg_close_probability: number;
}

export interface ObjectionMetric {
  objection: string;
  count: number;
  frequency_pct: number;
}

export interface DiscoveryChannelMetric {
  discovery_channel: string;
  total_meetings: number;
  closed_meetings: number;
  close_rate: number;
}

export interface SellerOption {
  id: number;
  name: string;
}

export interface MetricsFilters {
  from?: string;
  to?: string;
  seller_id?: number;
  industry?: string;
  closed?: boolean;
}
