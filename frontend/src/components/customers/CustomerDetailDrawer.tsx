import { useQuery } from "@tanstack/react-query";
import { AlertCircleIcon, MailIcon, PhoneIcon, UserIcon } from "lucide-react";
import { useState } from "react";

import { fetchCustomerDetail } from "@/api/customers";
import type { MeetingDetailResponse } from "@/api/types";
import { CategorizationView } from "@/components/customers/CategorizationView";
import { RecategorizeButton } from "@/components/customers/RecategorizeButton";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

interface CustomerDetailDrawerProps {
  customerId: number | null;
  onOpenChange: (open: boolean) => void;
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("es-CL", {
    day: "2-digit",
    month: "long",
    year: "numeric",
  });
}

export function CustomerDetailDrawer({
  customerId,
  onOpenChange,
}: CustomerDetailDrawerProps) {
  const open = customerId !== null;
  const { data, isLoading, error } = useQuery({
    queryKey: ["customer", customerId],
    queryFn: () => fetchCustomerDetail(customerId!),
    enabled: open,
  });

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="w-full overflow-y-auto [scrollbar-gutter:stable] sm:max-w-2xl">
        <SheetHeader className="space-y-1">
          <SheetTitle className="font-heading">
            {data ? data.name : isLoading ? "Cargando..." : "Cliente"}
          </SheetTitle>
          {data ? (
            <SheetDescription>
              Vendido por <strong>{data.seller.name}</strong>
            </SheetDescription>
          ) : null}
        </SheetHeader>

        <div className="px-4 pb-6 space-y-6">
          {isLoading ? <DetailSkeleton /> : null}

          {error ? (
            <Alert variant="destructive">
              <AlertCircleIcon />
              <AlertTitle>No se pudo cargar el cliente</AlertTitle>
              <AlertDescription>
                {error instanceof Error ? error.message : "Error desconocido"}
              </AlertDescription>
            </Alert>
          ) : null}

          {data ? (
            <>
              <ContactInfo
                email={data.email}
                phone={data.phone}
                createdAt={data.created_at}
              />
              <MeetingsList meetings={data.meetings} customerId={data.id} />
            </>
          ) : null}
        </div>
      </SheetContent>
    </Sheet>
  );
}

function ContactInfo({
  email,
  phone,
  createdAt,
}: {
  email: string | null;
  phone: string | null;
  createdAt: string;
}) {
  return (
    <section className="space-y-2 rounded-lg border bg-card p-4 text-sm">
      <h3 className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
        Contacto
      </h3>
      <div className="flex items-center gap-2">
        <MailIcon className="h-4 w-4 text-muted-foreground" />
        <span>{email ?? "—"}</span>
      </div>
      <div className="flex items-center gap-2">
        <PhoneIcon className="h-4 w-4 text-muted-foreground" />
        <span>{phone ?? "—"}</span>
      </div>
      <div className="flex items-center gap-2 text-xs text-muted-foreground">
        <UserIcon className="h-3 w-3" />
        <span>
          Creado el {new Date(createdAt).toLocaleDateString("es-CL")}
        </span>
      </div>
    </section>
  );
}

function MeetingsList({
  meetings,
  customerId,
}: {
  meetings: MeetingDetailResponse[];
  customerId: number;
}) {
  if (meetings.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        Este cliente no tiene reuniones registradas.
      </p>
    );
  }

  return (
    <section className="space-y-3">
      <h3 className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
        Reuniones ({meetings.length})
      </h3>
      {meetings.map((meeting) => (
        <MeetingCard key={meeting.id} meeting={meeting} customerId={customerId} />
      ))}
    </section>
  );
}

function MeetingCard({
  meeting,
  customerId,
}: {
  meeting: MeetingDetailResponse;
  customerId: number;
}) {
  const [tab, setTab] = useState("summary");

  return (
    <div className="space-y-3 rounded-lg border bg-card p-4">
      <header className="flex flex-wrap items-center justify-between gap-2">
        <div className="space-y-0.5">
          <p className="font-medium">{formatDate(meeting.meeting_date)}</p>
          <div className="flex items-center gap-2">
            <Badge variant={meeting.closed ? "default" : "secondary"}>
              {meeting.closed ? "Cerrada" : "Abierta"}
            </Badge>
            {meeting.categorization === null ? (
              <Badge variant="outline">Sin categorizar</Badge>
            ) : null}
          </div>
        </div>
        <RecategorizeButton
          meetingId={meeting.id}
          customerId={customerId}
          hasExisting={meeting.categorization !== null}
        />
      </header>

      <Tabs value={tab} onValueChange={setTab}>
        <TabsList className="w-full overflow-hidden">
          <TabsTrigger value="summary" disabled={meeting.categorization === null}>
            Categorización
          </TabsTrigger>
          <TabsTrigger value="transcript">Transcripción</TabsTrigger>
          <TabsTrigger value="raw" disabled={meeting.categorization === null}>
            JSON crudo
          </TabsTrigger>
        </TabsList>

        <TabsContent value="summary" className="pt-3">
          {meeting.categorization ? (
            <CategorizationView categorization={meeting.categorization} />
          ) : (
            <p className="text-sm text-muted-foreground">
              Esta reunión todavía no fue categorizada.
            </p>
          )}
        </TabsContent>

        <TabsContent value="transcript" className="pt-3">
          <p className="whitespace-pre-wrap text-sm leading-relaxed">
            {meeting.transcript}
          </p>
        </TabsContent>

        <TabsContent value="raw" className="pt-3">
          {meeting.categorization ? (
            <pre className="max-h-96 overflow-auto rounded-md bg-muted p-3 text-xs">
              {JSON.stringify(meeting.categorization, null, 2)}
            </pre>
          ) : null}
        </TabsContent>
      </Tabs>
    </div>
  );
}

function DetailSkeleton() {
  return (
    <div className="space-y-4">
      <Skeleton className="h-24 w-full" />
      <Skeleton className="h-72 w-full" />
    </div>
  );
}
