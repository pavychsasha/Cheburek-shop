# Cheburek Shop Frontend

React 18 storefront built with Vite, TypeScript, Redux Toolkit, SCSS modules, and npm.

## Requirements

- Node.js `20.19+` or `22.12+`
- npm

## Environment

The root setup script creates `front-end/.env` and keeps it aligned with the backend:

```bash
../setup.sh
```

Default local-domain URL:

```text
http://app.local.cheburek-shop.com:5178
```

Localhost fallback:

```text
http://localhost:5178
```

Variables:

- `VITE_API_BASE_URL`: backend API base URL
- `VITE_DEV_SERVER_HOST`: dev server bind host
- `VITE_DEV_SERVER_PORT`: dev server port
- `VITE_DEV_ALLOWED_HOSTS`: comma-separated Vite host allowlist

`front-end/.env` is local-only and ignored by Git. Keep real local values out of commits.

## Commands

```bash
npm ci
npm run dev
npm run lint
npm run typecheck
npm run build
npm run preview
npm audit
```

## Integration Notes

- API calls use `src/api/api.ts`.
- Keep `VITE_API_BASE_URL` aligned with the backend port and hostname.
- If the browser reports CORS errors, add the frontend origin to backend `APP_CONFIG__CORS__ALLOWED_ORIGINS`.
- The app stores bearer tokens in `localStorage` and sends session cookies for cart and language flows.

## Troubleshooting

- Build fails after dependency changes: run `npm ci` to refresh `node_modules` from `package-lock.json`.
- Dev server port is busy: set `VITE_DEV_SERVER_PORT` in `.env`.
- Local-domain page is blocked by Vite: confirm `VITE_DEV_ALLOWED_HOSTS` includes `app.local.cheburek-shop.com`.
- API calls fail locally: verify the backend health endpoint at `http://api.local.cheburek-shop.com:8091/health`.
- Local-domain URLs do not resolve: run root `./setup.sh` and add the printed hosts entry.
