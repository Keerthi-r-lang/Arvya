import { api } from "./client";
import type { AuditLog, CatalogSummary, Merchant, Product } from "../types";

export const getDemoMerchants = () => api<Merchant[]>("/auth/merchants");
export const login = (merchant_id: number) => api<{ access_token: string; merchant: Merchant }>("/auth/login", { method: "POST", body: JSON.stringify({ merchant_id }) });
export const getProducts = () => api<Product[]>("/catalog/products");
export const getCatalogSummary = () => api<CatalogSummary>("/catalog/summary");
export const getActivity = () => api<AuditLog[]>("/dashboard/recent-activity");
export const uploadCatalog = (file: File) => {
  const body = new FormData();
  body.append("file", file);
  return api<{ imported_count: number; failed_count: number; warnings: string[] }>("/catalog/upload", { method: "POST", body });
};

