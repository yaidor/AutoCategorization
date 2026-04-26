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

export interface CategorizationFull {
  id: number;
  meeting_id: number;
  provider: string;
  model: string;
  prompt_version: string;
  industry: string;
  use_case: string;
  interest_level: number;
  sentiment: number;
  urgency: string;
  volume_amount: number | null;
  volume_period: string | null;
  discovery_channel: string;
  integration_required: boolean;
  systems_mentioned: string[];
  main_objection: string | null;
  competitors_mentioned: string[];
  personalization_concern: string;
  data_sensitivity: string;
  close_probability: number;
  customer_segment: string;
  key_topics: string[];
  summary_es: string;
  cached: boolean;
  created_at: string;
}

export interface CustomerListItem {
  customer_id: number;
  customer_name: string;
  customer_email: string | null;
  customer_phone: string | null;
  seller_id: number;
  seller_name: string;
  meeting_id: number;
  meeting_date: string;
  closed: boolean;
  industry: string | null;
  close_probability: number | null;
  has_categorization: boolean;
}

export interface CustomerListPage {
  items: CustomerListItem[];
  total: number;
  skip: number;
  limit: number;
}

export interface SellerSummary {
  id: number;
  name: string;
}

export interface MeetingDetailResponse {
  id: number;
  meeting_date: string;
  closed: boolean;
  transcript: string;
  transcript_hash: string;
  created_at: string;
  categorization: CategorizationFull | null;
}

export interface CustomerDetailResponse {
  id: number;
  name: string;
  email: string | null;
  phone: string | null;
  created_at: string;
  seller: SellerSummary;
  meetings: MeetingDetailResponse[];
}

export type CustomerSort =
  | "meeting_date_desc"
  | "meeting_date_asc"
  | "customer_name_asc"
  | "customer_name_desc";
