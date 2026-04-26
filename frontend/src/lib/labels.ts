export const INDUSTRY_LABELS: Record<string, string> = {
  financial_services: "Servicios financieros",
  healthcare: "Salud",
  retail_ecommerce: "Retail / E-commerce",
  education: "Educación",
  logistics: "Logística",
  hospitality: "Hospitalidad",
  real_estate: "Bienes raíces",
  saas_tech: "SaaS / Tecnología",
  legal: "Legal",
  marketing: "Marketing",
  manufacturing: "Manufactura",
  nonprofit: "Sin fines de lucro",
  other: "Otro",
};

export const DISCOVERY_CHANNEL_LABELS: Record<string, string> = {
  conference: "Conferencia",
  referral: "Referido",
  google_search: "Búsqueda Google",
  linkedin: "LinkedIn",
  podcast: "Podcast",
  webinar: "Webinar",
  forum: "Foro",
  trade_fair: "Feria comercial",
  other: "Otro",
};

export function humanizeIndustry(value: string | null | undefined): string {
  if (!value) return "—";
  return INDUSTRY_LABELS[value] ?? value;
}

export function humanizeChannel(value: string | null | undefined): string {
  if (!value) return "—";
  return DISCOVERY_CHANNEL_LABELS[value] ?? value;
}
