import { BarChart3, BookOpenCheck, Boxes, CreditCard, LayoutDashboard, Moon, Search, Sparkles, Sun } from "lucide-react";
import type { Merchant } from "../../types";

type Props = { merchant: Merchant; activePage: "dashboard" | "catalog" | "recommendations" | "shopping" | "payments" | "audit"; onNavigate: (page: "dashboard" | "catalog" | "recommendations" | "shopping" | "payments" | "audit") => void; onLogout: () => void; theme: "dark" | "light"; onThemeToggle: () => void; children: React.ReactNode };

export function AppShell({ merchant, activePage, onNavigate, onLogout, theme, onThemeToggle, children }: Props) {
  return <div className={`min-h-screen bg-slate-950 text-slate-100 ${theme === "light" ? "theme-light" : ""}`}>
    <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-white/10 bg-slate-950 p-5 lg:block">
      <div className="mb-10 flex items-center gap-3"><div className="grid h-9 w-9 place-items-center rounded-xl bg-violet-500"><Sparkles size={19} /></div><div><p className="font-semibold">Arvya</p><p className="text-xs text-slate-400">Growth Agent</p></div></div>
      <nav className="space-y-2">
        <Nav icon={<LayoutDashboard size={18} />} label="Overview" active={activePage === "dashboard"} onClick={() => onNavigate("dashboard")} />
        <Nav icon={<Boxes size={18} />} label="Catalog" active={activePage === "catalog"} onClick={() => onNavigate("catalog")} />
        <Nav icon={<Sparkles size={18} />} label="Growth opportunities" active={activePage === "recommendations"} onClick={() => onNavigate("recommendations")} />
        <Nav icon={<Search size={18} />} label="Shopping agent" active={activePage === "shopping"} onClick={() => onNavigate("shopping")} />
        <Nav icon={<CreditCard size={18} />} label="Payment links" active={activePage === "payments"} onClick={() => onNavigate("payments")} />
        <Nav icon={<BarChart3 size={18} />} label="Campaigns" muted />
        <Nav icon={<BookOpenCheck size={18} />} label="Audit trail" active={activePage === "audit"} onClick={() => onNavigate("audit")} />
      </nav>
      <p className="absolute bottom-6 text-xs text-slate-500">Buildathon MVP · Trusted commerce</p>
    </aside>
    <main className="lg:ml-64">
      <header className="flex h-20 items-center justify-between border-b border-white/10 px-6 lg:px-10"><div><p className="text-sm text-slate-400">Merchant workspace</p><h1 className="font-semibold">{merchant.name}</h1></div><div className="flex items-center gap-3"><span className="hidden rounded-full border border-emerald-400/30 bg-emerald-400/10 px-3 py-1 text-xs font-medium text-emerald-300 sm:inline">Demo mode</span><button aria-label="Toggle color theme" onClick={onThemeToggle} className="grid h-9 w-9 place-items-center rounded-lg border border-white/10 text-slate-400 hover:bg-white/5 hover:text-white">{theme === "dark" ? <Sun size={17} /> : <Moon size={17} />}</button><button onClick={onLogout} className="text-sm text-slate-400 hover:text-white">Sign out</button></div></header>
      <section className="mx-auto max-w-7xl p-6 lg:p-10">{children}</section>
    </main>
  </div>;
}

function Nav({ icon, label, active, muted, onClick }: { icon: React.ReactNode; label: string; active?: boolean; muted?: boolean; onClick?: () => void }) {
  return <button disabled={muted} onClick={onClick} className={`flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm ${active ? "bg-violet-500 text-white" : muted ? "cursor-not-allowed text-slate-600" : "text-slate-400 hover:bg-white/5 hover:text-white"}`}>{icon}{label}{muted && <span className="ml-auto text-[10px]">Soon</span>}</button>;
}
