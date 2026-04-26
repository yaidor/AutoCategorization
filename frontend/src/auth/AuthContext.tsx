import { useQueryClient } from "@tanstack/react-query";
import { createContext, useCallback, useContext, useState, type ReactNode } from "react";

import { STORAGE_KEY } from "@/api/client";

interface AuthContextValue {
  apiKey: string | null;
  isAuthenticated: boolean;
  setApiKey: (key: string) => void;
  clearApiKey: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

function readInitialKey(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(STORAGE_KEY);
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();
  const [apiKey, setKeyState] = useState<string | null>(readInitialKey);

  const setApiKey = useCallback((key: string) => {
    window.localStorage.setItem(STORAGE_KEY, key);
    setKeyState(key);
  }, []);

  const clearApiKey = useCallback(() => {
    window.localStorage.removeItem(STORAGE_KEY);
    setKeyState(null);
    queryClient.clear();
  }, [queryClient]);

  const value: AuthContextValue = {
    apiKey,
    isAuthenticated: apiKey !== null,
    setApiKey,
    clearApiKey,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (ctx === null) {
    throw new Error("useAuth debe usarse dentro de <AuthProvider>");
  }
  return ctx;
}
