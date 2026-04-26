import { useQuery } from "@tanstack/react-query";
import { AlertTriangleIcon, CheckCircle2Icon, Loader2Icon } from "lucide-react";

import { api } from "@/api/client";
import type { JobResponse, JobStatus } from "@/api/types";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

interface JobProgressProps {
  jobId: number;
}

const STATUS_LABELS: Record<JobStatus, string> = {
  queued: "en cola",
  running: "corriendo",
  completed: "completado",
  failed: "falló",
};

export function JobProgress({ jobId }: JobProgressProps) {
  const { data, error } = useQuery({
    queryKey: ["job", jobId],
    queryFn: () => api.get<JobResponse>(`/api/v1/jobs/${jobId}`),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === "completed" || status === "failed" ? false : 2000;
    },
  });

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertTriangleIcon />
        <AlertTitle>Error consultando job #{jobId}</AlertTitle>
        <AlertDescription>
          {error instanceof Error ? error.message : "Error desconocido"}
        </AlertDescription>
      </Alert>
    );
  }

  if (!data) {
    return (
      <Alert>
        <Loader2Icon className="animate-spin" />
        <AlertTitle>Conectando con job #{jobId}…</AlertTitle>
      </Alert>
    );
  }

  const isRunning = data.status === "queued" || data.status === "running";
  const variant = data.status === "failed" ? "destructive" : "default";

  return (
    <Alert variant={variant}>
      {isRunning ? (
        <Loader2Icon className="animate-spin" />
      ) : data.status === "completed" ? (
        <CheckCircle2Icon />
      ) : (
        <AlertTriangleIcon />
      )}
      <AlertTitle>
        Job #{data.id}: {STATUS_LABELS[data.status]} — {data.completed}/{data.total}
        {data.failed > 0 ? ` · ${data.failed} fallaron` : ""}
      </AlertTitle>
      {data.status === "completed" && data.failed > 0 ? (
        <AlertDescription className="mt-2 text-sm">
          {data.failed} reuniones fallaron — probable rate limit del LLM. Vuelve a
          ejecutar la categorización para reintentar las pendientes.
        </AlertDescription>
      ) : null}
    </Alert>
  );
}
