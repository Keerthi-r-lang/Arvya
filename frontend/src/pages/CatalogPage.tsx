import { ArrowLeft, CheckCircle2 } from "lucide-react";
import { CatalogUpload } from "../components/catalog/CatalogUpload";
import { ProductTable } from "../components/catalog/ProductTable";
import type { CatalogSummary, Product } from "../types";

export function CatalogPage({ products, summary, onUpload, onBack, message }: { products: Product[]; summary: CatalogSummary; onUpload: (file: File) => Promise<void>; onBack: () => void; message: string | null }) {
  return <div className="space-y-7"><div><button onClick={onBack} className="mb-4 flex items-center gap-2 text-sm text-slate-400 hover:text-white"><ArrowLeft size={16} /> Back to overview</button><h2 className="text-3xl font-semibold tracking-tight">Catalog health</h2><p className="mt-2 text-slate-400">Clean product data makes growth recommendations safer and more useful.</p></div>{message && <div className="flex items-center gap-2 rounded-xl border border-emerald-400/20 bg-emerald-400/10 p-4 text-sm text-emerald-200"><CheckCircle2 size={18} />{message}</div>}<section className="grid gap-4 md:grid-cols-3"><HealthItem label="Products ready" value={`${summary.active_products} / ${summary.total_products}`} description="Active catalog products" /><HealthItem label="Margin coverage" value={`${summary.total_products - summary.missing_cost_data} / ${summary.total_products}`} description="Products with cost data" /><HealthItem label="Inventory warnings" value={summary.out_of_stock} description="Products currently out of stock" /></section><CatalogUpload onUpload={onUpload} /><ProductTable products={products} /></div>;
}

function HealthItem({ label, value, description }: { label: string; value: string | number; description: string }) { return <article className="rounded-xl border border-white/10 bg-slate-900/70 p-5"><p className="text-sm text-slate-400">{label}</p><p className="mt-2 text-2xl font-semibold">{value}</p><p className="mt-1 text-xs text-slate-500">{description}</p></article>; }

