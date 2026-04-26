import { useMutation, useQueryClient } from "@tanstack/react-query";
import { RefreshCwIcon } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { ApiError } from "@/api/client";
import { recategorizeMeeting } from "@/api/customers";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

interface RecategorizeButtonProps {
  meetingId: number;
  customerId: number;
  hasExisting: boolean;
}

export function RecategorizeButton({
  meetingId,
  customerId,
  hasExisting,
}: RecategorizeButtonProps) {
  const [open, setOpen] = useState(false);
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: () => recategorizeMeeting(meetingId),
    onSuccess: () => {
      toast.success("Reunión re-categorizada", {
        description: `La categorización del meeting #${meetingId} se actualizó.`,
      });
      queryClient.invalidateQueries({ queryKey: ["customer", customerId] });
      queryClient.invalidateQueries({ queryKey: ["customers"] });
      queryClient.invalidateQueries({ queryKey: ["metrics"] });
      setOpen(false);
    },
    onError: (err) => {
      const detail =
        err instanceof ApiError ? err.detail : err instanceof Error ? err.message : "Error";
      toast.error("No se pudo re-categorizar", { description: detail });
    },
  });

  return (
    <>
      <Button
        variant="outline"
        size="sm"
        onClick={() => setOpen(true)}
        disabled={mutation.isPending}
      >
        <RefreshCwIcon className="h-3.5 w-3.5" />
        {hasExisting ? "Re-categorizar" : "Categorizar"}
      </Button>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {hasExisting ? "Re-categorizar reunión" : "Categorizar reunión"}
            </DialogTitle>
            <DialogDescription>
              {hasExisting
                ? "Esto eliminará la categorización actual y llamará al LLM de nuevo. Consume tokens y puede demorar 1–3 segundos."
                : "Se llamará al LLM para categorizar la transcripción. Consume tokens y puede demorar 1–3 segundos."}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setOpen(false)}
              disabled={mutation.isPending}
            >
              Cancelar
            </Button>
            <Button onClick={() => mutation.mutate()} disabled={mutation.isPending}>
              {mutation.isPending ? "Procesando..." : "Confirmar"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
