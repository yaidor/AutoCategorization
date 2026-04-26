import type { CategorizationFull } from "@/api/types";
import { Badge } from "@/components/ui/badge";
import { formatPercent } from "@/lib/format";
import { humanizeChannel, humanizeIndustry } from "@/lib/labels";

const URGENCY_LABELS: Record<string, string> = {
  low: "Baja",
  medium: "Media",
  high: "Alta",
};

const SEGMENT_LABELS: Record<string, string> = {
  smb: "SMB",
  midmarket: "Mid-market",
  enterprise: "Enterprise",
  unknown: "Desconocido",
};

const VOLUME_PERIOD_LABELS: Record<string, string> = {
  daily: "diario",
  weekly: "semanal",
  monthly: "mensual",
};

const USE_CASE_LABELS: Record<string, string> = {
  customer_support: "Soporte al cliente",
  technical_support: "Soporte técnico",
  sales_inquiries: "Consultas de ventas",
  bookings_reservations: "Reservas",
  logistics_tracking: "Seguimiento logístico",
  internal_ops: "Operaciones internas",
  other: "Otro",
};

const LEVEL_LABELS: Record<string, string> = {
  low: "Baja",
  medium: "Media",
  high: "Alta",
};

function humanize(map: Record<string, string>, value: string | null): string {
  if (!value) return "—";
  return map[value] ?? value;
}

interface CategorizationViewProps {
  categorization: CategorizationFull;
}

export function CategorizationView({ categorization: c }: CategorizationViewProps) {
  return (
    <div className="space-y-6 text-sm">
      <Section title="Resumen del LLM">
        <p className="leading-relaxed">{c.summary_es}</p>
      </Section>

      <Section title="Clasificación">
        <Field label="Industria" value={humanizeIndustry(c.industry)} />
        <Field label="Caso de uso" value={humanize(USE_CASE_LABELS, c.use_case)} />
        <Field label="Segmento" value={humanize(SEGMENT_LABELS, c.customer_segment)} />
        <Field label="Canal de descubrimiento" value={humanizeChannel(c.discovery_channel)} />
      </Section>

      <Section title="Señales de venta">
        <Field
          label="Probabilidad de cierre"
          value={formatPercent(c.close_probability)}
        />
        <Field label="Nivel de interés" value={`${c.interest_level} / 5`} />
        <Field label="Sentimiento" value={c.sentiment.toFixed(2)} />
        <Field label="Urgencia" value={humanize(URGENCY_LABELS, c.urgency)} />
      </Section>

      <Section title="Volumen estimado">
        {c.volume_amount !== null ? (
          <p>
            {c.volume_amount.toLocaleString("es-CL")} interacciones{" "}
            {c.volume_period ? humanize(VOLUME_PERIOD_LABELS, c.volume_period) : ""}
          </p>
        ) : (
          <p className="text-muted-foreground">Sin estimación</p>
        )}
      </Section>

      <Section title="Integración y datos">
        <Field
          label="Requiere integración"
          value={c.integration_required ? "Sí" : "No"}
        />
        <Field
          label="Sensibilidad de datos"
          value={humanize(LEVEL_LABELS, c.data_sensitivity)}
        />
        <Field
          label="Concern de personalización"
          value={humanize(LEVEL_LABELS, c.personalization_concern)}
        />
        <ChipsField label="Sistemas mencionados" values={c.systems_mentioned} />
        <ChipsField label="Competidores mencionados" values={c.competitors_mentioned} />
      </Section>

      <Section title="Tópicos clave">
        <ChipsField label="" values={c.key_topics} />
      </Section>

      {c.main_objection ? (
        <Section title="Objeción principal">
          <p className="leading-relaxed">{c.main_objection}</p>
        </Section>
      ) : null}

      <Section title="Provenance">
        <Field label="Provider" value={c.provider} />
        <Field label="Modelo" value={c.model} />
        <Field label="Versión de prompt" value={c.prompt_version} />
        <Field
          label="Categorizado el"
          value={new Date(c.created_at).toLocaleString("es-CL")}
        />
      </Section>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="space-y-2">
      <h3 className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
        {title}
      </h3>
      <div className="space-y-1.5">{children}</div>
    </section>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div className="grid grid-cols-[160px_1fr] gap-2">
      <span className="text-muted-foreground">{label}</span>
      <span>{value}</span>
    </div>
  );
}

function ChipsField({ label, values }: { label: string; values: string[] }) {
  if (values.length === 0) {
    return label ? (
      <div className="grid grid-cols-[160px_1fr] gap-2">
        <span className="text-muted-foreground">{label}</span>
        <span className="text-muted-foreground">—</span>
      </div>
    ) : (
      <p className="text-muted-foreground">—</p>
    );
  }
  return (
    <div className={label ? "grid grid-cols-[160px_1fr] gap-2" : ""}>
      {label ? <span className="text-muted-foreground">{label}</span> : null}
      <div className="flex flex-wrap gap-1.5">
        {values.map((v) => (
          <Badge key={v} variant="secondary" className="text-xs font-normal">
            {v}
          </Badge>
        ))}
      </div>
    </div>
  );
}
