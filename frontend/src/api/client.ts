const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const STORAGE_KEY = "salescat:apiKey";

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly detail: string,
  ) {
    super(detail);
    this.name = "ApiError";
  }
}

function readStoredKey(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(STORAGE_KEY);
}

interface RequestOptions extends Omit<RequestInit, "body"> {
  body?: unknown;
  apiKey?: string | null;
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { apiKey, body, headers: extraHeaders, ...init } = options;
  const effectiveKey = apiKey === undefined ? readStoredKey() : apiKey;

  const headers = new Headers(extraHeaders);
  if (body !== undefined && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  if (effectiveKey) {
    headers.set("X-API-Key", effectiveKey);
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    let detail = `HTTP ${response.status}`;
    try {
      const errBody = (await response.json()) as { detail?: string };
      if (errBody?.detail) detail = errBody.detail;
    } catch {
      // body no es JSON, usamos el status default
    }
    throw new ApiError(response.status, detail);
  }

  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

export const api = {
  get: <T>(path: string, options: RequestOptions = {}) =>
    request<T>(path, { ...options, method: "GET" }),
  post: <T>(path: string, body?: unknown, options: RequestOptions = {}) =>
    request<T>(path, { ...options, method: "POST", body }),
};
