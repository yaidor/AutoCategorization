import { LogOutIcon, MenuIcon } from "lucide-react";

import { useAuth } from "@/auth/AuthContext";
import { ThemeToggle } from "@/components/theme-toggle";
import { Button } from "@/components/ui/button";

interface TopbarProps {
  onMenuClick: () => void;
}

export function Topbar({ onMenuClick }: TopbarProps) {
  const { clearApiKey } = useAuth();

  return (
    <header className="fixed top-0 right-0 left-0 z-30 flex h-14 items-center gap-2 border-b bg-background px-4 md:left-60">
      <Button
        variant="ghost"
        size="icon"
        className="md:hidden"
        onClick={onMenuClick}
        aria-label="Abrir menú"
      >
        <MenuIcon className="h-4 w-4" />
      </Button>
      <div className="flex-1" />
      <ThemeToggle />
      <Button variant="ghost" size="icon" onClick={clearApiKey} aria-label="Cerrar sesión">
        <LogOutIcon className="h-4 w-4" />
      </Button>
    </header>
  );
}
