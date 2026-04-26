import { FileTextIcon, UploadCloudIcon, XIcon } from "lucide-react";
import { useCallback, useRef, useState, type DragEvent, type KeyboardEvent } from "react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const MAX_BYTES = 5 * 1024 * 1024;

interface CsvDropzoneProps {
  file: File | null;
  onFileChange: (file: File | null) => void;
  disabled?: boolean;
}

function validate(file: File): string | null {
  if (!file.name.toLowerCase().endsWith(".csv")) {
    return "Solo se aceptan archivos .csv";
  }
  if (file.size > MAX_BYTES) {
    return `Archivo demasiado grande (max ${MAX_BYTES / 1024 / 1024} MB)`;
  }
  return null;
}

export function CsvDropzone({ file, onFileChange, disabled }: CsvDropzoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback(
    (selected: File) => {
      const err = validate(selected);
      if (err) {
        setError(err);
        return;
      }
      setError(null);
      onFileChange(selected);
    },
    [onFileChange],
  );

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setIsDragging(false);
    if (disabled) return;
    const dropped = event.dataTransfer.files[0];
    if (dropped) handleFile(dropped);
  }

  function handleKey(event: KeyboardEvent<HTMLDivElement>) {
    if (disabled) return;
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      inputRef.current?.click();
    }
  }

  if (file) {
    return (
      <div className="flex items-center gap-3 rounded-lg border bg-card p-4">
        <FileTextIcon className="h-8 w-8 text-muted-foreground" />
        <div className="flex-1 min-w-0">
          <p className="font-medium truncate">{file.name}</p>
          <p className="text-sm text-muted-foreground">
            {(file.size / 1024).toFixed(1)} KB
          </p>
        </div>
        <Button
          variant="ghost"
          size="icon"
          onClick={() => onFileChange(null)}
          disabled={disabled}
          aria-label="Quitar archivo"
        >
          <XIcon className="h-4 w-4" />
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <div
        className={cn(
          "rounded-lg border-2 border-dashed p-8 text-center",
          isDragging ? "border-primary bg-primary/5" : "border-border",
          disabled
            ? "opacity-50 cursor-not-allowed"
            : "cursor-pointer hover:border-primary/50 focus-visible:border-primary focus-visible:outline-none",
        )}
        onClick={() => !disabled && inputRef.current?.click()}
        onDragEnter={(e) => {
          e.preventDefault();
          if (!disabled) setIsDragging(true);
        }}
        onDragOver={(e) => e.preventDefault()}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onKeyDown={handleKey}
        role="button"
        tabIndex={disabled ? -1 : 0}
        aria-disabled={disabled}
        aria-label="Seleccionar archivo CSV"
      >
        <UploadCloudIcon className="mx-auto h-10 w-10 text-muted-foreground" />
        <p className="mt-2 font-medium">Arrastra un CSV o haz clic para seleccionar</p>
        <p className="text-sm text-muted-foreground mt-1">
          Headers esperados: Nombre, Correo, Teléfono, Fecha, Vendedor, closed, Transcripción
        </p>
        <input
          ref={inputRef}
          type="file"
          accept=".csv,text/csv"
          className="hidden"
          onChange={(event) => {
            const selected = event.target.files?.[0];
            if (selected) handleFile(selected);
            event.target.value = "";
          }}
          disabled={disabled}
        />
      </div>
      {error ? (
        <p className="text-sm text-destructive" role="alert">
          {error}
        </p>
      ) : null}
    </div>
  );
}
