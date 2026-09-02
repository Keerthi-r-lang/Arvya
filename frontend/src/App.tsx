import { useEffect, useState } from "react";
import { getActivity, getCatalogSummary, getDemoMerchants, getProducts, login, uploadCatalog } from "./api/merchant";
import { approveRecommendation, generateOpportunities, getRecommendations, rejectRecommendation } from "./api/recommendations";
import { AppShell } from "./components/layout/AppShell";
import { DashboardPage } from "./pages/DashboardPage";
import { CatalogPage } from "./pages/CatalogPage";
import { LoginPage } from "./pages/LoginPage";
import { RecommendationsPage } from "./pages/RecommendationsPage";
import type { AuditLog, CatalogSummary, Merchant, Product, Recommendation } from "./types";

type Page = "dashboard" | "catalog" | "recommendations";
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
  const [theme, setTheme] = useState<Theme>(() => (localStorage.getItem("arvya_theme") as Theme) || "dark");

  const loadWorkspace = async () => { const [nextProducts, nextSummary, nextActivity, nextRecommendations] = await Promise.all([getProducts(), getCatalogSummary(), getActivity(), getRecommendations()]); setProducts(nextProducts); setSummary(nextSummary); setActivity(nextActivity); setRecommendations(nextRecommendations); };
  useEffect(() => { getDemoMerchants().then(setMerchants).catch((err) => setError(err.message)).finally(() => setLoading(false)); }, []);
  const handleLogin = async (merchantId: number) => { setLoading(true); setError(null); try { const result = await login(merchantId); localStorage.setItem("arvya_token", result.access_token); setMerchant(result.merchant); await loadWorkspace(); } catch (err) { setError(err instanceof Error ? err.message : "Could not sign in"); } finally { setLoading(false); } };
  const handleUpload = async (file: File) => { try { const result = await uploadCatalog(file); await loadWorkspace(); setMessage(`Imported ${result.imported_count} products${result.failed_count ? `; ${result.failed_count} rows skipped.` : "."}`); } catch (err) { setMessage(null); setError(err instanceof Error ? err.message : "Catalog import failed"); } };
  const handleGenerate = async () => { setAgentLoading(true); setError(null); try { await generateOpportunities(); await loadWorkspace(); setPage("recommendations"); } catch (err) { setError(err instanceof Error ? err.message : "Growth analysis failed"); } finally { setAgentLoading(false); } };
  const handleApprove = async (id: number) => { setAgentLoading(true); try { await approveRecommendation(id); await loadWorkspace(); } catch (err) { setError(err instanceof Error ? err.message : "Could not approve offer"); } finally { setAgentLoading(false); } };
  const handleReject = async (id: number) => { setAgentLoading(true); try { await rejectRecommendation(id); await loadWorkspace(); } catch (err) { setError(err instanceof Error ? err.message : "Could not reject offer"); } finally { setAgentLoading(false); } };
  const logout = () => { localStorage.removeItem("arvya_token"); setMerchant(null); setPage("dashboard"); setProducts([]); setSummary(null); setActivity([]); };
  const toggleTheme = () => setTheme((current) => { const next = current === "dark" ? "light" : "dark"; localStorage.setItem("arvya_theme", next); return next; });
  if (!merchant) return <LoginPage merchants={merchants} onLogin={handleLogin} loading={loading} error={error} theme={theme} onThemeToggle={toggleTheme} />;
  if (!summary) return <main className="grid min-h-screen place-items-center bg-slate-950 text-slate-300">Loading merchant workspace…</main>;
  return <AppShell merchant={merchant} activePage={page} onNavigate={(target) => { setPage(target); setMessage(null); }} onLogout={logout} theme={theme} onThemeToggle={toggleTheme}>{page === "dashboard" ? <DashboardPage merchant={merchant} summary={summary} activity={activity} onOpenCatalog={() => setPage("catalog")} onGenerate={handleGenerate} generating={agentLoading} /> : page === "catalog" ? <CatalogPage products={products} summary={summary} onUpload={handleUpload} onBack={() => setPage("dashboard")} message={message} /> : <RecommendationsPage recommendations={recommendations} loading={agentLoading} error={error} onGenerate={handleGenerate} onApprove={handleApprove} onReject={handleReject} />}</AppShell>;
}
