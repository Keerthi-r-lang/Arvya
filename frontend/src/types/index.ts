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

