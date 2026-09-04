# Razorpay Buildathon Submission Narrative

## One-line pitch

Arvya is a governed AI-commerce layer that converts a merchant catalog into explainable, merchant-approved offers and proves each payment outcome through Razorpay-signed events.

## Problem

Small and mid-sized merchants have catalog, inventory, and margin data, but struggle to turn it into relevant cross-sell and upsell offers. Generic AI assistants can suggest ideas but do not solve approval, price control, payment execution, or accountability.

## Solution

Arvya uses a specialist-agent workflow to propose bundle, upsell, and campaign opportunities. Campaign drafts have their own control center with evidence, copy, and approval/rejection states; no campaign is auto-sent. The system keeps recommendations separate from execution: the merchant approves every offer before it can appear to a customer or generate a payment link. The Customer Shopping Agent then compares approved offers and applies eligible coupons. Razorpay payment links and signed webhooks close the loop.

## Differentiation

1. **Governed agentic commerce:** AI is constrained by merchant approval and server-side price rules.
2. **Two-sided value:** merchant growth and customer savings are connected through one approved-offer marketplace.
3. **Proof, not optimism:** Razorpay webhooks turn a created link into a verified payment outcome.
4. **Inspectable reasoning:** every agent action, recommendation evidence, assumption, decision, and payment state is auditable.

## Judging-criteria map

| Criterion | Arvya evidence |
|---|---|
| Agentic reasoning | Specialist workflow and visible agent reasoning trace. |
| Explainability | Product signals, confidence, impact assumptions, and campaign draft per recommendation. |
| Human-in-the-loop | Merchant approval, rejection, and safe final-price edit before checkout. |
| Razorpay integration | Test Mode payment links and verified payment-link webhooks. |
| Reliability | Idempotent checkout, webhook HMAC validation, event deduplication, safe retry, unmatched-event isolation. |
| Business value | Merchant revenue uplift opportunities plus customer coupon comparison. |

## Demo data

The app includes skincare, coffee, and fitness merchants to demonstrate that the workflow is catalog-driven rather than tuned to one product category.
