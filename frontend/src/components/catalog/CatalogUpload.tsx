import { Upload } from "lucide-react";
import { useRef, useState } from "react";

export function CatalogUpload({ onUpload }: { onUpload: (file: File) => Promise<void> }) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [loading, setLoading] = useState(false);
  const chooseFile = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setLoading(true);
    try { await onUpload(file); } finally { setLoading(false); event.target.value = ""; }
  };
  return <div className="rounded-2xl border border-dashed border-violet-400/40 bg-violet-500/5 p-6 text-center"><Upload className="mx-auto mb-3 text-violet-300" size={25} /><h3 className="font-medium">Import your catalog</h3><p className="mx-auto mt-2 max-w-md text-sm text-slate-400">Upload a UTF-8 CSV with sku, name, category, price_inr, cost_inr, inventory_count, and status.</p><input ref={inputRef} onChange={chooseFile} className="hidden" type="file" accept=".csv" /><button disabled={loading} onClick={() => inputRef.current?.click()} className="mt-5 rounded-lg bg-violet-500 px-4 py-2 text-sm font-medium hover:bg-violet-400 disabled:opacity-60">{loading ? "Importing…" : "Choose CSV file"}</button></div>;
}

