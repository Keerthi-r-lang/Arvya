# 2.5-Minute Judge Demo

## Setup before the judges arrive

1. Start backend, frontend, and ngrok.
2. Keep Razorpay Dashboard in **Test Mode** open in a second browser tab.
3. Confirm the webhook points to the active public backend URL.
4. Use **Glow Naturals** for the primary story. Its catalog makes the bundle easy to understand.

## Talk track

### 0:00–0:20 — the problem

“Merchants have product data but not an accountable way to turn it into targeted offers. Arvya is not a chatbot: it is a governed growth workflow.”

### 0:20–0:55 — agentic reasoning

Sign in to Glow Naturals and run **Generate growth opportunities**. Open the **Agent reasoning trace** and say:

“The orchestrator delegates catalog analysis, bundle discovery, upsell identification, campaign drafting, and impact estimation. Each action records its tools and reasoning.”

Expand a recommendation’s evidence and assumptions.

### 0:55–1:20 — human control

Point out the margin-safe offer price, evidence, confidence, and assumptions. Adjust the offer price if desired, then approve it.

“The agent cannot publish or charge. The merchant must explicitly approve, edit, or reject every financial recommendation.”

### 1:20–1:50 — customer value

Open **Shopping agent**. Search `skincare routine with sunscreen`, show the merchant comparison and coupon, then create the payment link.

“The customer agent compares only merchant-approved offers and validates coupon eligibility before checkout.”

### 1:50–2:15 — Razorpay proof

Open the Razorpay Test Mode payment link and complete the test payment. Return to Arvya, refresh if needed, and open **Payment links**.

“A payment link being created is not proof of payment. Razorpay sends a signed webhook; Arvya verifies it, deduplicates it, and reconciles this ledger.”

### 2:15–2:30 — auditability close

Open **Audit trail** and point to the customer checkout, merchant approval, and Razorpay webhook event.

“That gives merchants a defensible answer to who proposed, approved, and executed every action.”

## Backup path

If a public tunnel or webhook delivery is unavailable during a venue demo, show an already verified `paid` payment row and its audit event, then use the architecture diagram to explain signature verification and deduplication. Do not manually fabricate a `paid` state.
