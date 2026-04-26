import { AlertTriangleIcon, CheckCircle2Icon, InfoIcon } from "lucide-react";

import type { IngestSummary } from "@/api/types";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { cn } from "@/lib/utils";

interface IngestSummaryViewProps {
  summary: IngestSummary;
}

export function IngestSummaryView({ summary }: IngestSummaryViewProps) {
  return (
    <div className="space-y-4">
      <div className="grid gap-3 sm:grid-cols-3">
        <Stat label="Total filas" value={summary.total_rows} />
        <Stat label="Insertadas" value={summary.inserted} variant="success" />
        <Stat
          label="Duplicadas (omitidas)"
          value={summary.skipped_duplicates}
          variant="muted"
        />
      </div>

      {summary.new_sellers.length > 0 ? (
        <Alert>
          <InfoIcon />
          <AlertTitle>Vendedores nuevos detectados</AlertTitle>
          <AlertDescription>{summary.new_sellers.join(", ")}</AlertDescription>
        </Alert>
      ) : null}

      {summary.errors.length > 0 ? (
        <Alert variant="destructive">
          <AlertTriangleIcon />
          <AlertTitle>{summary.errors.length} errores de validación</AlertTitle>
          <AlertDescription>
            <ul className="mt-2 max-h-40 space-y-1 overflow-y-auto text-sm">
              {summary.errors.map((err, i) => (
                <li key={i}>
                  Fila {err.row}
                  {err.field ? ` · ${err.field}` : ""}: {err.message}
                </li>
              ))}
            </ul>
          </AlertDescription>
        </Alert>
      ) : (
        <Alert>
          <CheckCircle2Icon />
          <AlertTitle>Sin errores de validación</AlertTitle>
          <AlertDescription>Todas las filas válidas fueron procesadas.</AlertDescription>
        </Alert>
      )}
    </div>
  );
}

function Stat({
  label,
  value,
  variant,
}: {
  label: string;
  value: number;
  variant?: "success" | "muted";
}) {
  return (
    <div className="rounded-lg border bg-card p-4">
      <p className="text-sm text-muted-foreground">{label}</p>
      <p
        className={cn(
          "text-2xl font-semibold",
          variant === "success" && "text-emerald-600 dark:text-emerald-400",
          variant === "muted" && "text-muted-foreground",
        )}
      >
        {value}
      </p>
    </div>
  );
}
