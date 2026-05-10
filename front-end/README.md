# Cheburek Shop Frontend

React 18 storefront and admin CMS built with Vite, TypeScript, Redux Toolkit, SCSS modules, Recharts, and npm.

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
http://app.local.cheburek-shop.com
```

Admin local-domain URL:

```text
http://admin.local.cheburek-shop.com
```

Localhost fallback:

```text
http://localhost:5178
```

Variables:

- `VITE_API_BASE_URL`: backend API base URL
- `VITE_DEV_SERVER_HOST`: dev server bind host
- `VITE_DEV_SERVER_PORT`: dev server port
- `VITE_DEV_ALLOWED_HOSTS`: comma-separated Vite host allowlist, including storefront and admin local domains

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
- Prices are stored by the backend in base UAH and displayed through public currency settings from `/settings/public`.
- The storefront currency selector persists the selected display currency in browser local storage.
- Keep `VITE_API_BASE_URL` aligned with the backend hostname. The default local-domain URL uses the root local proxy at `http://api.local.cheburek-shop.com/api/v1`.
- When the app is opened through `localhost`, API calls fall back to the localhost backend if the configured API URL points at the preferred local API domain.
- The storefront renders on the storefront local domain and localhost. The admin portal renders only on the admin local domain.
- Admin tokens are stored in `sessionStorage` and are cleared on unauthorized or forbidden API responses.
- Admin access is enforced by backend superuser checks; frontend route selection is only a rendering concern.
- Product images are uploaded through admin media APIs and displayed from backend `/media/...` URLs backed by MinIO.
- The admin CMS includes dashboard charts, products with image upload/preview, translation tabs, orders, users, currency settings, and product language settings.
- Product-language drafts are generated from the English fallback and are meant to be reviewed in the CMS before publishing as final localized copy.
- The storefront ships baseline SEO metadata, canonical URLs, Open Graph/Twitter metadata, and restaurant structured data. The admin host sets `noindex,nofollow`.
- Product-specific SEO requires stable product detail routes plus server-side rendering or prerendering in a later production hardening pass.
- If the browser reports CORS errors, add the frontend origin to backend `APP_CONFIG__CORS__ALLOWED_ORIGINS`.
- The app stores bearer tokens in `localStorage` and sends session cookies for cart and language flows.

## Troubleshooting

- Build fails after dependency changes: run `npm ci` to refresh `node_modules` from `package-lock.json`.
- Dev server port is busy: set `VITE_DEV_SERVER_PORT` in `.env`.
- Local-domain page is blocked by Vite: confirm `VITE_DEV_ALLOWED_HOSTS` includes the storefront and admin local domains.
- API calls fail locally: verify the backend health endpoint at `http://api.local.cheburek-shop.com/health`.
- Product images do not load: verify the backend health endpoint reports MinIO as healthy and rerun the root migration helper.
- Currency values look stale: refresh the page after saving admin currency settings.
- Product language tabs look stale: reload Admin Settings, save the language list, run product translation backfill, then refresh Products.
- Local-domain URLs do not resolve: run root `./setup.sh` and add the printed hosts entry.
- Admin portal shows the login page but login fails: rerun root `./setup.sh`, then rerun the backend admin bootstrap command from the root README.
