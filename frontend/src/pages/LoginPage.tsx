import { AlertCircleIcon } from "lucide-react";
import { useState, type FormEvent } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";

import { ApiError, api } from "@/api/client";
import { useAuth } from "@/auth/AuthContext";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface LocationState {
  from?: string;
}

export function LoginPage() {
  const { setApiKey, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [keyInput, setKeyInput] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  if (isAuthenticated) {
    const target = (location.state as LocationState | null)?.from ?? "/";
    return <Navigate to={target} replace />;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    const trimmed = keyInput.trim();
    if (!trimmed) {
      setError("Pega tu API key.");
      return;
    }
    setPending(true);
    try {
      await api.get("/api/v1/metrics/overview", { apiKey: trimmed });
      setApiKey(trimmed);
      const target = (location.state as LocationState | null)?.from ?? "/";
      navigate(target, { replace: true });
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        setError("API key inválida.");
      } else if (err instanceof ApiError) {
        setError(`Error ${err.status}: ${err.detail}`);
      } else {
        setError("No se pudo conectar al backend.");
      }
    } finally {
      setPending(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-background p-4">
      <Card className="w-full max-w-sm">
        <CardHeader>
          <CardTitle className="text-xl">SalesCat</CardTitle>
          <CardDescription>Pega tu API key para entrar.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="apiKey">API key</Label>
              <Input
                id="apiKey"
                type="password"
                value={keyInput}
                onChange={(e) => setKeyInput(e.target.value)}
                placeholder="X-API-Key"
                autoComplete="off"
                autoFocus
                disabled={pending}
              />
            </div>
            {error ? (
              <Alert variant="destructive">
                <AlertCircleIcon className="h-4 w-4" />
                <AlertTitle>No se pudo entrar</AlertTitle>
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            ) : null}
            <Button type="submit" disabled={pending} className="w-full">
              {pending ? "Verificando..." : "Entrar"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </main>
  );
}
