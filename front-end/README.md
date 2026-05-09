# Cheburek Shop Frontend

React 18 storefront built with Vite, TypeScript, Redux Toolkit, SCSS modules, and npm.

## Requirements

- Node.js `20.19+` or `22.12+`
- npm

## Environment

Create a local env file:

```bash
cp .env.example .env
```

Variables:

- `VITE_API_BASE_URL`: backend API base URL, default `http://localhost:8091/api/v1`
- `VITE_DEV_SERVER_HOST`: dev server host, default `127.0.0.1`
- `VITE_DEV_SERVER_PORT`: dev server port, default `5178`

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

Default local URL:

```text
http://localhost:5178
```

## Integration Notes

- API calls use `src/api/api.ts`.
- Keep `VITE_API_BASE_URL` aligned with the backend port.
- If the browser reports CORS errors, add the frontend origin to backend `APP_CONFIG__CORS__ALLOWED_ORIGINS`.
- The app stores bearer tokens in `localStorage` and sends session cookies for cart and language flows.

## Troubleshooting

- Build fails after dependency changes: run `npm ci` to refresh `node_modules` from `package-lock.json`.
- Dev server port is busy: set `VITE_DEV_SERVER_PORT` in `.env`.
- API calls fail locally: verify the backend health endpoint at `http://localhost:8091/health`.
