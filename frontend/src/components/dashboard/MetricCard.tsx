import type { ReactNode } from "react";

export function MetricCard({ label, value, detail, icon }: { label: string; value: string | number; detail: string; icon: ReactNode }) {
  return <article className="rounded-2xl border border-white/10 bg-slate-900/80 p-5 shadow-xl shadow-slate-950/20"><div className="mb-5 flex items-start justify-between"><p className="text-sm text-slate-400">{label}</p><div className="rounded-lg bg-violet-500/10 p-2 text-violet-300">{icon}</div></div><p className="text-3xl font-semibold tracking-tight">{value}</p><p className="mt-2 text-xs text-slate-500">{detail}</p></article>;
}

