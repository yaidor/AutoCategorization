import { useQuery } from "@tanstack/react-query";
import { AlertTriangleIcon, CheckCircle2Icon, Loader2Icon } from "lucide-react";

import { api } from "@/api/client";
import type { JobError, JobResponse, JobStatus } from "@/api/types";
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

type ErrorKind = "tpd" | "tpm" | "rpd" | "rpm" | "validation" | "auth" | "other";

interface ErrorClassification {
  kind: ErrorKind;
  sample: string;
}

function classifyErrors(errors: JobError[]): ErrorClassification {
  if (errors.length === 0) return { kind: "other", sample: "" };
  const text = errors[0].error;
  const lower = text.toLowerCase();
  if (lower.includes("tokens per day") || lower.includes("(tpd)")) {
    return { kind: "tpd", sample: text };
  }
  if (lower.includes("requests per day") || lower.includes("(rpd)")) {
    return { kind: "rpd", sample: text };
  }
  if (lower.includes("tokens per minute") || lower.includes("(tpm)")) {
    return { kind: "tpm", sample: text };
  }
  if (lower.includes("requests per minute") || lower.includes("(rpm)")) {
    return { kind: "rpm", sample: text };
  }
  if (lower.includes("schema") || lower.includes("validationerror")) {
    return { kind: "validation", sample: text };
  }
  if (lower.includes("401") || lower.includes("unauthorized") || lower.includes("invalid api key")) {
    return { kind: "auth", sample: text };
  }
  return { kind: "other", sample: text };
}

const ERROR_HEADLINES: Record<ErrorKind, string> = {
  tpd: "Cuota diaria de tokens del LLM agotada",
  rpd: "Cuota diaria de requests al LLM agotada",
  tpm: "Rate limit por minuto del LLM excedido",
  rpm: "Rate limit de requests por minuto del LLM",
  validation: "El LLM devolvió respuestas con formato inválido",
  auth: "Error de autenticación con el proveedor LLM",
  other: "Algunas reuniones fallaron",
};

const ERROR_GUIDANCE: Record<ErrorKind, string> = {
  tpd: "Groq tiene un límite diario de tokens (TPD) que ya consumiste. El contador se resetea cada 24h. Mientras tanto, no es posible procesar más reuniones con este provider. Alternativas: esperar al reset, pasar a un plan paid de Groq, o sumar otro provider (Anthropic / OpenAI) como fallback.",
  rpd: "Groq tiene un límite diario de cantidad de requests (RPD) que ya alcanzaste. Espera al reset diario o cambia de plan/provider.",
  tpm: "Excediste los tokens permitidos en el último minuto. Espera 1-2 minutos y vuelve a ejecutar la categorización — el cache solo procesa las reuniones pendientes.",
  rpm: "Demasiados requests por minuto al LLM. Espera 1-2 minutos y reintenta.",
  validation: "El LLM produjo JSON que no cumple el schema esperado. Esto suele ser transitorio — reintenta. Si persiste en las mismas reuniones, puede ser un problema con el prompt o transcripciones inusuales.",
  auth: "La API key del LLM está vacía o inválida. Verifica `SALESCAT_LLM_API_KEY` en las variables de entorno del backend.",
  other: "Revisa el detalle de los errores abajo.",
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
  const showFailures = !isRunning && data.failed > 0;
  const classification = showFailures ? classifyErrors(data.errors) : null;
  const variant = data.status === "failed" ? "destructive" : "default";

  return (
    <div className="space-y-3">
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
      </Alert>

      {classification ? (
        <Alert variant="destructive">
          <AlertTriangleIcon />
          <AlertTitle>{ERROR_HEADLINES[classification.kind]}</AlertTitle>
          <AlertDescription className="space-y-2 text-sm">
            <p>{ERROR_GUIDANCE[classification.kind]}</p>
            <details className="text-xs">
              <summary className="cursor-pointer font-medium">
                Detalle ({data.errors.length} {data.errors.length === 1 ? "error" : "errores"})
              </summary>
              <ul className="mt-2 max-h-48 space-y-1 overflow-y-auto rounded border p-2">
                {data.errors.slice(0, 10).map((err, i) => (
                  <li key={i}>
                    <span className="font-medium">meeting #{err.meeting_id}:</span>{" "}
                    <span className="break-words">{err.error}</span>
                  </li>
                ))}
                {data.errors.length > 10 ? (
                  <li className="text-muted-foreground">
                    … {data.errors.length - 10} errores más
                  </li>
                ) : null}
              </ul>
            </details>
          </AlertDescription>
        </Alert>
      ) : null}
    </div>
  );
}
