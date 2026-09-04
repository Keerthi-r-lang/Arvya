import { api } from "./client";
import type { CommerceSimulation, DecisionCenter } from "../types";

export const getDecisionCenter = () => api<DecisionCenter>("/decision-center");
export const runCommerceSimulation = () => api<CommerceSimulation>("/commerce-simulations", { method: "POST" });
