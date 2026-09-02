import { useEffect, useState } from "react";
import { getActivity, getCatalogSummary, getDemoMerchants, getProducts, login, uploadCatalog } from "./api/merchant";
import { approveRecommendation, generateOpportunities, getRecommendations, rejectRecommendation } from "./api/recommendations";
import { checkoutOffer, searchApprovedOffers } from "./api/shopping";
import { AppShell } from "./components/layout/AppShell";
import { DashboardPage } from "./pages/DashboardPage";
import { CatalogPage } from "./pages/CatalogPage";
import { LoginPage } from "./pages/LoginPage";
import { RecommendationsPage } from "./pages/RecommendationsPage";
import { ShoppingPage } from "./pages/ShoppingPage";
import type { AuditLog, CatalogSummary, Merchant, PaymentLink, Product, Recommendation, ShoppingOffer, ShoppingSearchResponse } from "./types";

type Page = "dashboard" | "catalog" | "recommendations" | "shopping";
type Theme = "dark" | "light";

export default function App() {
  const [merchants, setMerchants] = useState<Merchant[]>([]);
  const [merchant, setMerchant] = useState<Merchant | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [summary, setSummary] = useState<CatalogSummary | null>(null);
  const [activity, setActivity] = useState<AuditLog[]>([]);
  const [page, setPage] = useState<Page>("dashboard");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [agentLoading, setAgentLoading] = useState(false);
  const [shoppingResult, setShoppingResult] = useState<ShoppingSearchResponse | null>(null);
  const [shoppingLoading, setShoppingLoading] = useState(false);
  const [theme, setTheme] = useState<Theme>(() => (localStorage.getItem("arvya_theme") as Theme) || "dark");

  const loadWorkspace = async () => { const [nextProducts, nextSummary, nextActivity, nextRecommendations] = await Promise.all([getProducts(), getCatalogSummary(), getActivity(), getRecommendations()]); setProducts(nextProducts); setSummary(nextSummary); setActivity(nextActivity); setRecommendations(nextRecommendations); };
  useEffect(() => { getDemoMerchants().then(setMerchants).catch((err) => setError(err.message)).finally(() => setLoading(false)); }, []);
  const handleLogin = async (merchantId: number) => { setLoading(true); setError(null); try { const result = await login(merchantId); localStorage.setItem("arvya_token", result.access_token); setMerchant(result.merchant); await loadWorkspace(); } catch (err) { setError(err instanceof Error ? err.message : "Could not sign in"); } finally { setLoading(false); } };
  const handleUpload = async (file: File) => { try { const result = await uploadCatalog(file); await loadWorkspace(); setMessage(`Imported ${result.imported_count} products${result.failed_count ? `; ${result.failed_count} rows skipped.` : "."}`); } catch (err) { setMessage(null); setError(err instanceof Error ? err.message : "Catalog import failed"); } };
  const handleGenerate = async () => { setAgentLoading(true); setError(null); try { await generateOpportunities(); await loadWorkspace(); setPage("recommendations"); } catch (err) { setError(err instanceof Error ? err.message : "Growth analysis failed"); } finally { setAgentLoading(false); } };
  const handleApprove = async (id: number, proposedPricePaise?: number) => { setAgentLoading(true); try { await approveRecommendation(id, proposedPricePaise); await loadWorkspace(); } catch (err) { setError(err instanceof Error ? err.message : "Could not approve offer"); } finally { setAgentLoading(false); } };
  const handleReject = async (id: number) => { setAgentLoading(true); try { await rejectRecommendation(id); await loadWorkspace(); } catch (err) { setError(err instanceof Error ? err.message : "Could not reject offer"); } finally { setAgentLoading(false); } };
  const handleShoppingSearch = async (query: string, budget: string) => { setShoppingLoading(true); setError(null); try { setShoppingResult(await searchApprovedOffers(query, budget)); } catch (err) { setError(err instanceof Error ? err.message : "Could not compare approved offers"); } finally { setShoppingLoading(false); } };
  const handleCheckout = async (offer: ShoppingOffer, name: string, email: string): Promise<PaymentLink | undefined> => { setShoppingLoading(true); setError(null); try { return await checkoutOffer(offer.recommendation_id, name, email, offer.coupon_code); } catch (err) { setError(err instanceof Error ? err.message : "Could not create checkout"); return undefined; } finally { setShoppingLoading(false); } };
  const logout = () => { localStorage.removeItem("arvya_token"); setMerchant(null); setPage("dashboard"); setProducts([]); setSummary(null); setActivity([]); };
  const toggleTheme = () => setTheme((current) => { const next = current === "dark" ? "light" : "dark"; localStorage.setItem("arvya_theme", next); return next; });
  if (!merchant) return <LoginPage merchants={merchants} onLogin={handleLogin} loading={loading} error={error} theme={theme} onThemeToggle={toggleTheme} />;
  if (!summary) return <main className="grid min-h-screen place-items-center bg-slate-950 text-slate-300">Loading merchant workspace…</main>;
  return <AppShell merchant={merchant} activePage={page} onNavigate={(target) => { setPage(target); setMessage(null); setError(null); }} onLogout={logout} theme={theme} onThemeToggle={toggleTheme}>{page === "dashboard" ? <DashboardPage merchant={merchant} summary={summary} activity={activity} onOpenCatalog={() => setPage("catalog")} onGenerate={handleGenerate} generating={agentLoading} /> : page === "catalog" ? <CatalogPage products={products} summary={summary} onUpload={handleUpload} onBack={() => setPage("dashboard")} message={message} /> : page === "recommendations" ? <RecommendationsPage recommendations={recommendations} loading={agentLoading} error={error} onGenerate={handleGenerate} onApprove={handleApprove} onReject={handleReject} /> : <ShoppingPage result={shoppingResult} searching={shoppingLoading} error={error} onSearch={handleShoppingSearch} onCheckout={handleCheckout} />}</AppShell>;
}
