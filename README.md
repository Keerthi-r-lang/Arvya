# Arvya Growth Agent

Day 1 foundation for an AI merchant growth and agentic-commerce platform.

## Run locally

1. In `backend`, create a virtual environment and install `requirements.txt`.
2. Copy `.env.example` to `.env`. For real payment-link testing, add Razorpay **Test Mode** values for `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET`; without them Arvya runs an explicitly labelled demo checkout.
3. Start the API with `uvicorn app.main:app --reload --port 8000`.
4. In `frontend`, install packages with `npm.cmd install` and start with `npm.cmd run dev`.

The application seeds three demo merchants and catalogs when the backend first starts.

## Day 3 demo flow

1. Sign in as a merchant and generate growth opportunities.
2. Approve a bundle or upsell in **Growth opportunities**.
3. Open **Shopping agent** and search for a relevant customer need.
4. Select a merchant-approved offer to apply the merchant coupon and create a payment link.
