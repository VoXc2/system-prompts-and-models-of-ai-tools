"use client";

import { useCallback, useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

type Tab = "unified" | "maps" | "ai" | "file";

type Capabilities = {
  google_places: boolean;
  serpapi: boolean;
  google_cse: boolean;
  bing: boolean;
  sources: string[];
};

const SOURCE_LABELS: Record<string, string> = {
  maps: "خرائط Google (Places)",
  serp_google: "بحث Google (SerpAPI)",
  serp_maps: "خرائط Google (SerpAPI)",
  google_cse: "بحث مخصص (CSE)",
  bing: "Bing",
  linkedin_signals: "إشارات LinkedIn (بحث عام)",
};

export function LeadGeneratorView() {
  const [tab, setTab] = useState<Tab>("unified");
  const [caps, setCaps] = useState<Capabilities | null>(null);

  const [query, setQuery] = useState("عيادة أسنان");
  const [city, setCity] = useState("الرياض");
  const [sector, setSector] = useState("الصحة");
  const [maxPer, setMaxPer] = useState(12);
  const [sources, setSources] = useState<string[]>(["maps", "serp_google", "linkedin_signals"]);

  const [aiSector, setAiSector] = useState("تقنية المعلومات");
  const [count, setCount] = useState(10);

  const [leads, setLeads] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [meta, setMeta] = useState<Record<string, unknown> | null>(null);

  const [selected, setSelected] = useState<Record<string, unknown> | null>(null);
  const [pipelineRunning, setPipelineRunning] = useState<string | null>(null);
  const [pipelineResult, setPipelineResult] = useState<Record<string, unknown> | null>(null);

  const loadCaps = useCallback(async () => {
    try {
      const r = await fetch(`${API}/api/v1/lead-intelligence/capabilities`);
      if (r.ok) setCaps(await r.json());
    } catch {
      setCaps(null);
    }
  }, []);

  useEffect(() => {
    loadCaps();
  }, [loadCaps]);

  const runUnified = async () => {
    setLoading(true);
    setError(null);
    setMeta(null);
    setLeads([]);
    try {
      const r = await fetch(`${API}/api/v1/lead-intelligence/unified-search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query,
          city,
          sector,
          sources,
          max_per_source: maxPer,
        }),
      });
      const data = await r.json();
      if (!r.ok) throw new Error((data as { detail?: string }).detail || r.statusText);
      setMeta(data as Record<string, unknown>);
      setLeads((data as { prospects?: Record<string, unknown>[] }).prospects || []);
    } catch (e) {
      setError(e instanceof Error ? e.message : "فشل الطلب");
    } finally {
      setLoading(false);
    }
  };

  const runMaps = async () => {
    setLoading(true);
    setError(null);
    setMeta(null);
    setLeads([]);
    try {
      const r = await fetch(`${API}/api/v1/prospector/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query,
          city,
          sector: "maps",
          max_results: maxPer,
        }),
      });
      const data = await r.json();
      if (!r.ok) throw new Error((data as { detail?: string }).detail || r.statusText);
      setLeads((data as { prospects?: Record<string, unknown>[] }).prospects || []);
      setMeta({ total_found: (data as { total_found?: number }).total_found });
    } catch (e) {
      setError(e instanceof Error ? e.message : "فشل الطلب");
    } finally {
      setLoading(false);
    }
  };

  const runAiSector = async () => {
    setLoading(true);
    setError(null);
    setMeta(null);
    setLeads([]);
    try {
      const r = await fetch(
        `${API}/api/v1/dealix/generate-leads?sector=${encodeURIComponent(aiSector)}&city=${encodeURIComponent(city)}&count=${count}`,
        { method: "POST" }
      );
      const data = await r.json();
      if (!r.ok) throw new Error("تعذر توليد القائمة");
      const list = (data as { leads?: Record<string, unknown>[] }).leads || [];
      setLeads(list);
      setMeta({ mode: "ai_sector", count: list.length });
    } catch {
      setLeads(
        Array.from({ length: Math.min(count, 5) }, (_, i) => ({
          company_name: `مثال ${aiSector} ${i + 1}`,
          city,
          urgency: ["high", "medium", "low"][i % 3],
          pain_point: "— وضع تجريبي بدون خادم",
          source: "demo_fallback",
        }))
      );
      setError("الخادم غير متاح — عُرضت عيّنة محلية.");
    } finally {
      setLoading(false);
    }
  };

  const runUpload = async (file: File | null) => {
    if (!file) return;
    setLoading(true);
    setError(null);
    setMeta(null);
    setLeads([]);
    const fd = new FormData();
    fd.append("file", file);
    try {
      const r = await fetch(`${API}/api/v1/lead-intelligence/ingest-csv`, {
        method: "POST",
        body: fd,
      });
      const data = await r.json();
      if (!r.ok) throw new Error((data as { detail?: string }).detail || r.statusText);
      setLeads((data as { prospects?: Record<string, unknown>[] }).prospects || []);
      setMeta({ warnings: (data as { warnings?: string[] }).warnings, filename: file.name });
    } catch (e) {
      setError(e instanceof Error ? e.message : "فشل الرفع");
    } finally {
      setLoading(false);
    }
  };

  const runPipeline = async (lead: Record<string, unknown>) => {
    const name = String(lead.company_name || lead.name || "شركة");
    const phoneDigits = String(lead.phone ?? "").replace(/\D/g, "");
    if (phoneDigits.length < 9) {
      setPipelineResult({
        notice: "لا يوجد رقم هاتف موثوق لهذا السجل — أضف هاتفاً أو استورد CSV يحتوي أرقاماً قبل تشغيل المسار الكامل.",
      });
      return;
    }
    setPipelineRunning(name);
    try {
      const res = await fetch(`${API}/api/v1/dealix/full-power`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          company_name: name,
          contact_name: "المدير التنفيذي",
          contact_phone: phoneDigits,
          contact_title: "المدير التنفيذي",
          website: lead.website || "",
        }),
      });
      if (res.ok) setPipelineResult((await res.json()) as Record<string, unknown>);
      else setPipelineResult({ notice: "تعذر إكمال الـ pipeline" });
    } catch {
      setPipelineResult({ notice: "تعذر الاتصال بالخادم" });
    } finally {
      setPipelineRunning(null);
    }
  };

  const toggleSource = (s: string) => {
    setSources((prev) => (prev.includes(s) ? prev.filter((x) => x !== s) : [...prev, s]));
  };

  const displayName = (row: Record<string, unknown>) =>
    String(row.company_name || row.name || row.title || "—");

  return (
    <div className="min-h-screen bg-[#0a0a0f] p-4 text-slate-100 md:p-6">
      <div className="mx-auto max-w-6xl">
        <header className="mb-6 border-b border-white/10 pb-4">
          <h2 className="text-xl font-black text-amber-400 md:text-2xl">مولّد واستخبارات الليدات</h2>
          <p className="mt-1 text-sm text-slate-500">
            دمج خرائط Google، بحث الويب (SerpAPI / CSE / Bing)، وإشارات LinkedIn من نتائج بحث عامة، مع استيراد
            CSV — بدون كشط غير مصرّح به.
          </p>
          {caps && (
            <div className="mt-3 flex flex-wrap gap-2 text-[11px]">
              {(["google_places", "serpapi", "google_cse", "bing"] as const).map((k) => (
                <span
                  key={k}
                  className={`rounded-full px-2 py-0.5 ${
                    caps[k] ? "bg-teal-500/20 text-teal-300" : "bg-white/5 text-slate-500"
                  }`}
                >
                  {k}: {caps[k] ? "مفعّل" : "غير مفعّل"}
                </span>
              ))}
            </div>
          )}
        </header>

        <div className="mb-6 flex flex-wrap gap-2">
          {(
            [
              ["unified", "محرك موحّد"],
              ["maps", "خرائط مباشرة"],
              ["ai", "AI قطاعي"],
              ["file", "استيراد ملف"],
            ] as const
          ).map(([id, label]) => (
            <button
              key={id}
              type="button"
              onClick={() => setTab(id)}
              className={`rounded-xl px-4 py-2 text-sm font-semibold transition ${
                tab === id ? "bg-amber-500 text-slate-950" : "bg-white/5 text-slate-400 hover:bg-white/10"
              }`}
            >
              {label}
            </button>
          ))}
        </div>

        {tab === "unified" && (
          <div className="mb-8 space-y-4 rounded-2xl border border-white/10 bg-white/[0.03] p-4 md:p-6">
            <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
              <label className="text-xs text-slate-500">
                البحث / النشاط
                <input
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="mt-1 w-full rounded-lg border border-white/10 bg-black/30 px-3 py-2 text-sm"
                />
              </label>
              <label className="text-xs text-slate-500">
                المدينة
                <input
                  value={city}
                  onChange={(e) => setCity(e.target.value)}
                  className="mt-1 w-full rounded-lg border border-white/10 bg-black/30 px-3 py-2 text-sm"
                />
              </label>
              <label className="text-xs text-slate-500">
                قطاع (لإشارات LinkedIn)
                <input
                  value={sector}
                  onChange={(e) => setSector(e.target.value)}
                  className="mt-1 w-full rounded-lg border border-white/10 bg-black/30 px-3 py-2 text-sm"
                />
              </label>
              <label className="text-xs text-slate-500">
                حد أقصى لكل مصدر
                <input
                  type="number"
                  min={1}
                  max={40}
                  value={maxPer}
                  onChange={(e) => setMaxPer(Number(e.target.value))}
                  className="mt-1 w-full rounded-lg border border-white/10 bg-black/30 px-3 py-2 text-sm"
                />
              </label>
            </div>
            <div>
              <p className="mb-2 text-xs font-semibold text-slate-400">المصادر</p>
              <div className="flex flex-wrap gap-2">
                {(caps?.sources || ["maps", "serp_google", "serp_maps", "google_cse", "bing", "linkedin_signals"]).map(
                  (s) => (
                    <button
                      key={s}
                      type="button"
                      onClick={() => toggleSource(s)}
                      className={`rounded-lg px-3 py-1.5 text-xs ${
                        sources.includes(s)
                          ? "bg-teal-600/40 text-teal-100 ring-1 ring-teal-500/50"
                          : "bg-white/5 text-slate-500"
                      }`}
                    >
                      {SOURCE_LABELS[s] || s}
                    </button>
                  )
                )}
              </div>
            </div>
            <button
              type="button"
              disabled={loading || sources.length === 0}
              onClick={runUnified}
              className="rounded-xl bg-gradient-to-l from-amber-500 to-orange-600 px-8 py-3 font-bold text-slate-950 disabled:opacity-50"
            >
              {loading ? "جاري الدمج…" : "تشغيل البحث الموحّد"}
            </button>
          </div>
        )}

        {tab === "maps" && (
          <div className="mb-8 space-y-4 rounded-2xl border border-white/10 bg-white/[0.03] p-4">
            <p className="text-sm text-slate-400">بحث Places مباشر (هاتف مطلوب للتصفية).</p>
            <button
              type="button"
              disabled={loading}
              onClick={runMaps}
              className="rounded-xl bg-teal-600 px-6 py-2.5 font-bold text-white"
            >
              {loading ? "…" : "بحث خرائط"}
            </button>
          </div>
        )}

        {tab === "ai" && (
          <div className="mb-8 flex flex-wrap items-end gap-3 rounded-2xl border border-white/10 bg-white/[0.03] p-4">
            <label className="text-xs text-slate-500">
              القطاع
              <select
                value={aiSector}
                onChange={(e) => setAiSector(e.target.value)}
                className="mt-1 block rounded-lg border border-white/10 bg-black/30 px-3 py-2 text-sm"
              >
                {["تقنية المعلومات", "العقارات", "الصحة", "التعليم", "التجزئة", "المقاولات"].map((s) => (
                  <option key={s}>{s}</option>
                ))}
              </select>
            </label>
            <label className="text-xs text-slate-500">
              العدد
              <select
                value={count}
                onChange={(e) => setCount(Number(e.target.value))}
                className="mt-1 block rounded-lg border border-white/10 bg-black/30 px-3 py-2 text-sm"
              >
                {[5, 10, 20, 50].map((n) => (
                  <option key={n} value={n}>
                    {n}
                  </option>
                ))}
              </select>
            </label>
            <button
              type="button"
              disabled={loading}
              onClick={runAiSector}
              className="rounded-xl bg-amber-500 px-6 py-2.5 font-bold text-slate-950"
            >
              توليد AI
            </button>
          </div>
        )}

        {tab === "file" && (
          <div className="mb-8 rounded-2xl border border-dashed border-teal-500/40 bg-teal-950/20 p-6">
            <p className="mb-3 text-sm text-slate-400">
              CSV بفاصلة أو فاصلة منقوطة — أعمدة مثل: اسم الشركة، هاتف، موقع، مدينة، قطاع.
            </p>
            <input
              type="file"
              accept=".csv,.txt"
              onChange={(e) => runUpload(e.target.files?.[0] || null)}
              className="text-sm"
            />
          </div>
        )}

        {error && <p className="mb-4 text-sm text-red-400">{error}</p>}

        {meta && (
          <pre className="mb-4 max-h-32 overflow-auto rounded-lg bg-black/40 p-3 text-[11px] text-slate-500">
            {JSON.stringify(meta, null, 2)}
          </pre>
        )}

        <div className="grid gap-6 lg:grid-cols-[1fr_380px]">
          {leads.length > 0 && (
            <div className="max-h-[560px] space-y-2 overflow-y-auto">
              <p className="text-sm font-semibold text-slate-400">النتائج: {leads.length}</p>
              {leads.map((lead, i) => (
                <button
                  key={String(lead.id || i)}
                  type="button"
                  onClick={() => setSelected(lead)}
                  className={`w-full rounded-xl border px-4 py-3 text-right transition ${
                    selected === lead ? "border-amber-500 bg-amber-950/20" : "border-white/10 bg-white/[0.04]"
                  }`}
                >
                  <div className="flex justify-between gap-2">
                    <span className="font-bold text-white">{displayName(lead)}</span>
                    <span className="text-[10px] text-teal-400">{String(lead.source || "—")}</span>
                  </div>
                  {(String(lead.phone ?? "").length > 0 || String(lead.snippet ?? "").length > 0) && (
                    <p className="mt-1 line-clamp-2 text-xs text-slate-500">
                      {String(lead.phone ?? "")}{" "}
                      {lead.snippet != null && String(lead.snippet).length > 0
                        ? `— ${String(lead.snippet).slice(0, 120)}`
                        : ""}
                    </p>
                  )}
                </button>
              ))}
            </div>
          )}

          {(selected != null || pipelineResult != null) && (
            <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
              {selected && (
                <div className="mb-4">
                  <h3 className="font-bold text-amber-400">{displayName(selected)}</h3>
                  <dl className="mt-3 space-y-2 text-sm">
                    {Object.entries(selected)
                      .filter(([k]) => !["id"].includes(k))
                      .slice(0, 14)
                      .map(([k, v]) => (
                        <div key={k}>
                          <dt className="text-[10px] uppercase text-slate-500">{k}</dt>
                          <dd className="text-slate-300">{typeof v === "object" ? JSON.stringify(v) : String(v)}</dd>
                        </div>
                      ))}
                  </dl>
                  <button
                    type="button"
                    disabled={!!pipelineRunning}
                    onClick={() => runPipeline(selected)}
                    className="mt-4 w-full rounded-lg bg-amber-500 py-2 text-sm font-bold text-slate-950"
                  >
                    {pipelineRunning ? "…" : "تشغيل Pipeline كامل"}
                  </button>
                </div>
              )}
              {pipelineResult && (
                <div>
                  <h4 className="text-sm font-bold text-emerald-400">نتيجة Pipeline</h4>
                  <pre className="mt-2 max-h-64 overflow-auto text-[10px] text-slate-500">
                    {JSON.stringify(pipelineResult, null, 2).slice(0, 4000)}
                  </pre>
                  <button
                    type="button"
                    onClick={() => setPipelineResult(null)}
                    className="mt-2 text-xs text-teal-400"
                  >
                    إغلاق
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

        <p className="mt-8 text-center text-[11px] text-slate-600">
          الاستخدام يخضع لسياسات Google، SerpAPI، Bing، وخصوصية الأفراد. إشارات LinkedIn مأخوذة من نتائج بحث عامة
          وليست استخراجاً من داخل المنصة.
        </p>
      </div>
    </div>
  );
}
