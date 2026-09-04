# Deployment Path

ngrok is correct for a local Test Mode demo, but it is intentionally temporary. For the final submission or a production-style walkthrough, deploy the backend to a stable HTTPS domain and configure Razorpay once against that domain.

## Included Render Blueprint

This repository now includes [`render.yaml`](../render.yaml). It defines an `arvya-api` Docker web service and a managed `arvya-db` PostgreSQL database. In Render, create a **Blueprint** from the GitHub repository, enter the requested secrets, and deploy. Render will give the backend a stable `https://...onrender.com` address.

Set `FRONTEND_ORIGIN` to the final frontend address. After deployment, set Razorpay’s Test Mode webhook URL to:

```text
https://YOUR-RENDER-SERVICE/api/v1/webhooks/razorpay
```

The backend accepts Render's common `postgres://` or `postgresql://` connection strings and normalizes them for the bundled psycopg driver.

## Recommended simple topology

| Layer | Suggested host | Notes |
|---|---|---|
| React/Vite frontend | Vercel or Netlify | Set `VITE_API_URL` to the backend API URL. |
| FastAPI backend | Render, Railway, or Fly.io | Expose HTTPS; keep one stable URL for webhooks. |
| Database | Managed PostgreSQL | Replace local SQLite for durability and concurrent access. |
| Payments | Razorpay Test Mode, then Live Mode | Keep Test and Live secrets fully separate. |

## Backend environment variables

```env
DATABASE_URL=postgresql+psycopg://...
JWT_SECRET=long-random-production-secret
FRONTEND_ORIGIN=https://your-frontend-domain
RAZORPAY_KEY_ID=rzp_test_... or rzp_live_...
RAZORPAY_KEY_SECRET=...
RAZORPAY_WEBHOOK_SECRET=...
```

## Deployment order

1. Deploy the FastAPI backend and run database migrations/initialization.
2. Deploy the frontend with `VITE_API_URL=https://YOUR-BACKEND/api/v1`.
3. Add the frontend URL to `FRONTEND_ORIGIN` and redeploy backend.
4. Configure Razorpay’s webhook URL as `https://YOUR-BACKEND/api/v1/webhooks/razorpay`.
5. Make a Test Mode payment and verify `paid` in Arvya before switching any credential to Live Mode.

## Important production hardening

- Move from SQLite to Postgres.
- Replace demo login with Razorpay-compatible merchant authentication / OAuth or an identity provider.
- Persist the webhook payload separately with retention rules, alert on unmatched events, and enforce idempotency at the database transaction boundary.
- Store all secrets in host-managed secret storage; never put them in GitHub or the frontend bundle.
