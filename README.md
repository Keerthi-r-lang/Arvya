# Arvya Growth Agent

Arvya is a governed AI-commerce workspace: agents propose merchant growth offers, merchants approve them, customers discover the approved offers, and Razorpay Test Mode closes the payment loop.

## Run locally

1. In `backend`, create a virtual environment and install `requirements.txt`.
2. Create `backend/.env` locally and add Razorpay **Test Mode** values for `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`, and `RAZORPAY_WEBHOOK_SECRET`. Never commit API secrets or place them in `.env.example`; without the API keys Arvya runs an explicitly labelled demo checkout.
3. Start the API with `uvicorn app.main:app --reload --port 8000`.
4. In `frontend`, install packages with `npm.cmd install` and start with `npm.cmd run dev`.

The application seeds three demo merchants and catalogs when the backend first starts.

## Demo flow

1. Sign in as a merchant and generate growth opportunities.
2. Approve a bundle or upsell in **Growth opportunities**.
3. Open **Shopping agent** and search for a relevant customer need.
4. Select a merchant-approved offer to apply the merchant coupon and create a payment link.
5. Complete the Razorpay Test Mode payment, then use **Payment links** to show the reconciled status and **Audit trail** to show the verified event.

## Razorpay webhook setup

Payment-link creation confirms only that a checkout URL exists. A webhook is the trusted server-to-server event that confirms the eventual payment result.

1. Give the backend a public HTTPS URL while demoing locally (for example, using your preferred secure tunnel).
2. In the Razorpay Test Mode dashboard, create a webhook targeting `https://YOUR-PUBLIC-URL/api/v1/webhooks/razorpay`.
3. Subscribe to `payment_link.paid`, `payment_link.partially_paid`, and `payment_link.cancelled`.
4. Copy that webhook secret into `backend/.env` as `RAZORPAY_WEBHOOK_SECRET` and restart the backend.

Arvya verifies the raw webhook signature, deduplicates the Razorpay event ID, records an audit entry, and then updates the merchant payment ledger. The endpoint is intentionally public but does not accept unsigned events.
