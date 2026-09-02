import { api } from "./client";
import type { PaymentLink } from "../types";

export const getPaymentLinks = () => api<PaymentLink[]>("/payment-links");
export const retryPaymentLink = (id: number) => api<PaymentLink>(`/payment-links/${id}/retry`, { method: "POST" });
