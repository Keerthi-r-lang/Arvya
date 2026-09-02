import { api } from "./client";
import type { AgentRun, Recommendation } from "../types";

export const generateOpportunities = () => api<AgentRun>("/agent-runs", { method: "POST", body: JSON.stringify({ analysis_types: ["bundle", "upsell", "campaign"], max_recommendations: 3 }) });
export const getRecommendations = () => api<Recommendation[]>("/recommendations");
export const approveRecommendation = (id: number, proposed_price_paise?: number) => api<Recommendation>(`/recommendations/${id}/approve`, { method: "POST", body: JSON.stringify({ proposed_price_paise, note: "Approved from merchant workspace" }) });
export const rejectRecommendation = (id: number) => api<Recommendation>(`/recommendations/${id}/reject`, { method: "POST", body: JSON.stringify({ reason: "Merchant chose not to use this offer." }) });
