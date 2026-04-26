import { api } from "@/api/client";
import type { IngestSummary } from "@/api/types";

export async function uploadCsv(file: File): Promise<IngestSummary> {
  const formData = new FormData();
  formData.append("file", file);
  return api.post<IngestSummary>("/api/v1/uploads/csv", formData);
}
