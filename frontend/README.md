# salescat-web

Frontend React + TypeScript de SalesCat. Login con API key, dashboard con KPIs y charts, tabla de clientes con drawer, carga de CSV y polling de jobs de categorización.

Para el quickstart end-to-end (incluyendo backend), ver el [README raíz](../README.md).

## Setup local rápido

```bash
npm install
cp .env.example .env  # apunta a http://localhost:8000 por default
npm run dev
```

Abrir http://localhost:5173. Te redirige a `/login` — pegar la `SALESCAT_API_KEY` que generaste para el backend.

## Scripts

```bash
npm run dev         # Vite dev server con HMR
npm run typecheck   # tsc --noEmit
npm run lint        # ESLint
npm run build       # tsc + vite build → dist/
npm run preview     # serve dist/ localmente
npm run format      # prettier
npm run gen:api     # genera src/api/schema.ts desde el OpenAPI del backend (requiere backend corriendo)
```

## Variables de entorno

Todas con prefijo `VITE_` (las únicas que Vite expone al bundle).

| Variable | Default | Descripción |
|---|---|---|
| `VITE_API_URL` | `http://localhost:8000` | URL base del backend, sin slash final |

En producción Vercel, setear `VITE_API_URL=https://<tu-dominio-railway>.up.railway.app` desde la UI del proyecto.

## Estructura

```
src/
├── api/
│   ├── client.ts                # fetch wrapper + ApiError + soporte de FormData
│   ├── types.ts                 # tipos manuales (mirroring de schemas backend)
│   ├── customers.ts             # fetchCustomers, fetchCustomerDetail, recategorizeMeeting
│   ├── metrics.ts               # fetchOverview, fetchSellerMetrics, fetchSellers, ...
│   └── uploads.ts               # uploadCsv (multipart)
│
├── auth/
│   ├── AuthContext.tsx          # provider con localStorage hydration + queryClient.clear() on logout
│   └── RequireAuth.tsx          # Navigate a /login si no hay key
│
├── components/
│   ├── ui/                      # primitivos shadcn (button, card, input, table, sheet, dialog, ...)
│   ├── layout/
│   │   ├── AppShell.tsx         # contenedor con sidebar + topbar + outlet
│   │   ├── Sidebar.tsx          # nav (Dashboard, Clientes, Carga CSV) — responsive con backdrop
│   │   └── Topbar.tsx           # menu hamburger (mobile) + theme toggle + logout
│   ├── filters/
│   │   └── GlobalFilters.tsx    # 5 controles (fechas, vendedor, industria con "Sin categorizar", estado)
│   ├── charts/
│   │   ├── SellerCloseRateBar.tsx
│   │   ├── IndustryBar.tsx
│   │   ├── DiscoveryChannelPie.tsx
│   │   └── ObjectionsList.tsx
│   ├── customers/
│   │   ├── CustomersTable.tsx          # TanStack Table v8: sort + paginación + skeleton
│   │   ├── CustomerDetailDrawer.tsx    # Sheet con tabs (Categorización / Transcripción / JSON crudo)
│   │   ├── CategorizationView.tsx      # render organizado de los 17 campos del schema
│   │   └── RecategorizeButton.tsx      # con Dialog de confirmación
│   ├── upload/
│   │   ├── CsvDropzone.tsx             # drag & drop manual (sin react-dropzone)
│   │   ├── IngestSummaryView.tsx       # stats + Alerts (errores, vendedores nuevos)
│   │   └── JobProgress.tsx             # useQuery con refetchInterval dinámico (para cuando completa)
│   ├── theme-provider.tsx              # next-themes wrapper
│   └── theme-toggle.tsx                # button con Moon/Sun icon
│
├── pages/
│   ├── LoginPage.tsx                   # form con probe de la key
│   ├── DashboardPage.tsx               # 6 KPIs + 4 charts
│   ├── CustomersPage.tsx               # filtros + search debounced + tabla + drawer
│   ├── CustomerDetailPage.tsx          # redirect → /customers?customer={id}
│   └── UploadPage.tsx                  # dropzone + post-upload actions + standalone "Categorizar pendientes"
│
├── hooks/
│   └── useMetricsFilters.ts            # lee/escribe URL params como source of truth
│
├── lib/
│   ├── format.ts                       # formatPercent, formatNumber (es-CL)
│   ├── labels.ts                       # INDUSTRY_LABELS, DISCOVERY_CHANNEL_LABELS + helpers humanize*
│   ├── query-client.ts                 # QueryClient con retry: false en 401/404
│   └── utils.ts                        # cn() helper de shadcn
│
├── providers.tsx                       # QueryClient + Theme + BrowserRouter + Auth + Toaster
├── router.tsx                          # rutas: /login + RequireAuth wrapping AppShell con outlet
├── main.tsx                            # bootstrap + StrictMode
├── index.css                           # Tailwind v4 @import + @theme inline + custom variants para data-state Radix
└── vite-env.d.ts                       # tipo de import.meta.env.VITE_API_URL
```

## Estado y URL

Filtros, paginación, sort, drawer abierto, search query — todo vive en `useSearchParams`. Es la fuente de verdad. Implicaciones:

- **URLs compartibles**: pegar `https://app/customers?seller_id=1&closed=true&customer=42` abre la tabla filtrada con el cliente 42 en el drawer.
- **Recargar mantiene contexto**: F5 no resetea estado.
- **Back/forward del browser** navegan entre estados de filtro.

`useMetricsFilters` parsea los params relevantes (`from`, `to`, `seller_id`, `industry`, `closed`, `uncategorized`) y expone setters que actualizan la URL.

## Cache y data fetching

`@tanstack/react-query` con queryKey conteniendo los filtros activos:

```ts
useQuery({
  queryKey: ["metrics", "by-seller", filters],
  queryFn: () => fetchSellerMetrics(filters),
});
```

Cambiar un filtro genera una nueva queryKey → refetch automático. La cache se mantiene entre páginas (volver al dashboard no refetchea inmediatamente).

`queryClient.clear()` se llama en `clearApiKey()` (logout) para evitar que datos cacheados de un usuario aparezcan tras un re-login.

## Theming

CSS variables en `index.css` mapeadas via `@theme inline`. Toggle claro/oscuro con `next-themes`. Las transiciones (200ms en `background-color`, `border-color`, `color`, `fill`, `stroke`) se aplican globalmente para que el cambio sea suave.

`@custom-variant` declarados en `index.css` para los `data-state` de Radix:

```css
@custom-variant data-active (&[data-state="active"]);
@custom-variant data-horizontal (&[data-orientation="horizontal"]);
/* ... */
```

Necesario porque shadcn v4 con Tailwind v4 usa esos shorthand y sin las custom variants el styling de tabs/sheets/etc. no aplica.
