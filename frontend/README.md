# salescat-web

Frontend React + TypeScript + Tailwind de SalesCat.

## Setup

```bash
npm install
cp .env.example .env
npm run dev
```

Abre http://localhost:5173.

## Scripts

```bash
npm run dev         # servidor Vite
npm run build       # type-check + build de producción a dist/
npm run preview     # servir dist/ localmente
npm run lint        # ESLint
npm run typecheck   # tsc --noEmit
npm run format      # Prettier
```

## Estructura

```
src/
  pages/         # Dashboard, Customers, CustomerDetail, Upload
  components/    # charts/, filters/, table/, ui/
  api/           # cliente tipado generado desde OpenAPI
  hooks/         # react-query hooks
  lib/           # utils, formateo
  types/
  App.tsx        # root component
  main.tsx       # entrypoint
  index.css      # Tailwind directives
```
