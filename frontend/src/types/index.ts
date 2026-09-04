export type Merchant = {
  id: number;
  name: string;
  email: string;
  industry: string;
  currency: string;
};

export type Product = {
  id: number;
  merchant_id: number;
  sku: string;
  name: string;
  category: string;
  price_paise: number;
  cost_paise: number | null;
  inventory_count: number;
  status: string;
};

export type CatalogSummary = {
  total_products: number;
  active_products: number;
  categories: number;
  missing_cost_data: number;
  out_of_stock: number;
  average_price_paise: number;
};

export type AuditLog = {
  id: number;
  actor_type: string;
  actor_id: string;
  event_type: string;
  entity_type: string;
  entity_id: string;
  detail: string;
  created_at: string;
};

export type RecommendationItem = {
  product_id: number;
  role: string;
  original_price_paise: number;
  proposed_price_paise: number | null;
  quantity: number;
};

export type Recommendation = {
  id: number;
  agent_run_id: number;
  type: "bundle" | "upsell" | "campaign";
  status: "pending_approval" | "approved" | "rejected";
  title: string;
  rationale: string;
  evidence_json: { signals?: string[]; products?: string[]; [key: string]: unknown };
  action_payload_json: { original_price_paise?: number; proposed_price_paise?: number; discount_percent?: number; campaign_copy?: string; [key: string]: unknown };
  impact_json: { estimated_monthly_revenue_uplift_inr: number; estimated_incremental_orders: number; confidence_range: string; assumptions: string[] };
  confidence_score: number;
  approved_at: string | null;
  rejected_reason: string | null;
  created_at: string;
  items: RecommendationItem[];
};

export type AgentRun = {
  id: number;
  merchant_id: number;
  status: string;
  trigger_type: string;
  model_provider: string;
  started_at: string;
  completed_at: string | null;
};

export type AgentAction = {
  id: number;
  agent_run_id: number;
  recommendation_id: number | null;
  agent_name: string;
  action_type: string;
  status: string;
  input_summary_json: Record<string, unknown>;
  output_summary_json: Record<string, unknown>;
  tools_used_json: string[];
  reasoning_summary: string;
  started_at: string;
  completed_at: string;
};

export type ShoppingOffer = {
  recommendation_id: number;
  merchant_id: number;
  merchant_name: string;
  merchant_industry: string;
  title: string;
  type: string;
  products: string[];
  original_price_paise: number | null;
  offer_price_paise: number;
  coupon_code: string | null;
  coupon_discount_paise: number;
  final_price_paise: number;
  relevance_score: number;
  explanation: string;
  confidence_score: number;
};

export type ShoppingSearchResponse = {
  query: string;
  recommendation_summary: string;
  offers: ShoppingOffer[];
};

export type PaymentLink = {
  id: number;
  recommendation_id: number;
  amount_paise: number;
  currency: string;
  status: string;
  provider: string;
  short_url: string | null;
  coupon_code: string | null;
  customer_email: string;
  failure_reason: string | null;
  created_at: string;
};

export type CommerceMetrics = {
  actual_paid_revenue_paise: number;
  payment_links_created: number;
  paid_links: number;
  approved_offers: number;
  estimated_monthly_uplift_inr: number;
};

export type DashboardOverview = {
  merchant: { id: number; name: string; industry: string };
  catalog: CatalogSummary;
  growth_agent_status: string;
  commerce_metrics: CommerceMetrics;
};

export type ScoreComponent = { label: string; score: number; weight: number; detail: string };
export type DecisionEvent = { step: number; title: string; detail: string; actor: string; status: string };
export type AuditReference = { id: number; event_type: string; detail: string; created_at: string };
export type Guardrail = { name: string; status: "passed" | "blocked" | "review" | "neutral"; detail: string };
export type DecisionCenter = { recommendation_id: number; title: string; recommendation_type: string; approval_status: string; confidence_score: number; confidence_formula: string; confidence_components: ScoreComponent[]; risk_score: number; risk_level: "low" | "medium" | "high"; risk_reasons: string[]; guardrails: Guardrail[]; why_selected: string[]; why_rejected: string[]; evidence_sources: string[]; original_price_paise: number; offer_price_paise: number; coupon_code: string | null; coupon_discount_paise: number; final_price_paise: number; margin_after_discount_percent: number | null; expected_monthly_uplift_inr: number; expected_incremental_orders: number; assumptions: string[]; decision_trace: DecisionEvent[]; audit_references: AuditReference[] };
export type CommerceSimulation = { simulation_id: string; mode: string; safety_notice: string; decision: DecisionCenter; events: DecisionEvent[]; audit_references: AuditReference[] };
