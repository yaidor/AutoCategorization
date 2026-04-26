import { useMutation } from "@tanstack/react-query";
import { SparklesIcon } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { api } from "@/api/client";
import type { IngestSummary, JobResponse } from "@/api/types";
import { uploadCsv } from "@/api/uploads";
import { CsvDropzone } from "@/components/upload/CsvDropzone";
import { IngestSummaryView } from "@/components/upload/IngestSummaryView";
import { JobProgress } from "@/components/upload/JobProgress";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [summary, setSummary] = useState<IngestSummary | null>(null);
  const [activeJobId, setActiveJobId] = useState<number | null>(null);

  const uploadMutation = useMutation({
    mutationFn: (selected: File) => uploadCsv(selected),
    onSuccess: (data) => {
      setSummary(data);
      toast.success(`${data.inserted} filas insertadas`, {
        description:
          data.skipped_duplicates > 0
            ? `${data.skipped_duplicates} duplicadas omitidas`
            : undefined,
      });
    },
    onError: (err) => {
      toast.error("Error al subir CSV", {
        description: err instanceof Error ? err.message : "Error desconocido",
      });
    },
  });

  const categorizeMutation = useMutation({
    mutationFn: () => api.post<JobResponse>("/api/v1/meetings/batch-categorize"),
    onSuccess: (job) => {
      setActiveJobId(job.id);
      if (job.total === 0) {
        toast.info("No hay reuniones pendientes de categorizar");
      } else {
        toast.success(`Categorización iniciada (job #${job.id})`, {
          description: `${job.total} reuniones por procesar`,
        });
      }
    },
    onError: (err) => {
      toast.error("Error al iniciar categorización", {
        description: err instanceof Error ? err.message : "Error desconocido",
      });
    },
  });

  function handleFileChange(next: File | null) {
    setFile(next);
    setSummary(null);
    setActiveJobId(null);
  }

  function reset() {
    setFile(null);
    setSummary(null);
    setActiveJobId(null);
  }

  const showStandaloneRetry = !file && !summary;

  return (
    <div className="space-y-6">
      <header>
        <h1 className="font-heading text-3xl font-semibold tracking-tight">Carga CSV</h1>
        <p className="text-muted-foreground">
          Sube un CSV de reuniones para ingestar y categorizar.
        </p>
      </header>

      <CsvDropzone
        file={file}
        onFileChange={handleFileChange}
        disabled={uploadMutation.isPending}
      />

      {file && !summary ? (
        <Button
          onClick={() => uploadMutation.mutate(file)}
          disabled={uploadMutation.isPending}
        >
          {uploadMutation.isPending ? "Subiendo..." : "Cargar CSV"}
        </Button>
      ) : null}

      {summary ? (
        <>
          <IngestSummaryView summary={summary} />
          <div className="flex flex-wrap gap-2">
            {summary.inserted > 0 && activeJobId === null ? (
              <Button
                onClick={() => categorizeMutation.mutate()}
                disabled={categorizeMutation.isPending}
              >
                {categorizeMutation.isPending
                  ? "Iniciando..."
                  : "Categorizar reuniones nuevas"}
              </Button>
            ) : null}
            <Button variant="outline" onClick={reset}>
              Cargar otro CSV
            </Button>
          </div>
        </>
      ) : null}

      {showStandaloneRetry ? (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 font-heading text-lg">
              <SparklesIcon className="h-4 w-4" />
              Categorizar reuniones pendientes
            </CardTitle>
            <CardDescription>
              Procesa las reuniones que aún no tienen categorización (típicamente las
              que fallaron por rate limit del LLM en intentos anteriores). El cache
              evita reprocesar las que ya están al día.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button
              onClick={() => categorizeMutation.mutate()}
              disabled={categorizeMutation.isPending}
            >
              {categorizeMutation.isPending
                ? "Iniciando..."
                : "Categorizar pendientes"}
            </Button>
          </CardContent>
        </Card>
      ) : null}

      {activeJobId !== null ? <JobProgress jobId={activeJobId} /> : null}
    </div>
  );
}
