import { api } from "./client";
import type { PaymentLink, ShoppingSearchResponse } from "../types";

export const searchApprovedOffers = (query: string, budgetInr?: string) => api<ShoppingSearchResponse>("/shopping/search", { method: "POST", body: JSON.stringify({ query, budget_paise: budgetInr ? Math.round(Number(budgetInr) * 100) : undefined }) });
export const checkoutOffer = (recommendationId: number, customerName: string, customerEmail: string, couponCode?: string | null) => api<PaymentLink>(`/shopping/offers/${recommendationId}/checkout`, { method: "POST", body: JSON.stringify({ customer_name: customerName, customer_email: customerEmail, coupon_code: couponCode }) });
