"use client";

import { useEffect, useState, DragEvent, useCallback } from "react";
import { deals } from "@/lib/api";
import Modal from "@/components/ui/Modal";
import {
  Handshake,
  Loader2,
  Search,
  Plus,
  Pencil,
  LayoutGrid,
  List,
  GripVertical,
  CalendarDays,
  User,
  Banknote,
} from "lucide-react";

// ─── Types ───

interface Deal {
  id: string;
  title: string;
  contact_name?: string;
  value: number;
  stage: string;
  status: string;
  expected_close_date?: string;
  notes?: string;
  created_at: string;
}

type ViewMode = "board" | "table";

// ─── Stage Configuration ───

interface StageConfig {
  key: string;
  label: string;
  badgeColor: string;
  borderColor: string;
  headerBg: string;
  headerText: string;
  dotColor: string;
}

const STAGES: StageConfig[] = [
  {
    key: "new",
    label: "اكتشاف",
    badgeColor: "bg-blue-100 text-blue-700",
    borderColor: "border-blue-500",
    headerBg: "bg-blue-50",
    headerText: "text-blue-700",
    dotColor: "bg-blue-500",
  },
  {
    key: "proposal",
    label: "عرض سعر",
    badgeColor: "bg-purple-100 text-purple-700",
    borderColor: "border-purple-500",
    headerBg: "bg-purple-50",
    headerText: "text-purple-700",
    dotColor: "bg-purple-500",
  },
  {
    key: "negotiation",
    label: "تفاوض",
    badgeColor: "bg-yellow-100 text-yellow-700",
    borderColor: "border-yellow-500",
    headerBg: "bg-yellow-50",
    headerText: "text-yellow-700",
    dotColor: "bg-yellow-500",
  },
  {
    key: "closed_won",
    label: "مكتسب",
    badgeColor: "bg-green-100 text-green-700",
    borderColor: "border-green-500",
    headerBg: "bg-green-50",
    headerText: "text-green-700",
    dotColor: "bg-green-500",
  },
  {
    key: "closed_lost",
    label: "مفقود",
    badgeColor: "bg-red-100 text-red-700",
    borderColor: "border-red-500",
    headerBg: "bg-red-50",
    headerText: "text-red-700",
    dotColor: "bg-red-500",
  },
];

const stageMap: Record<string, StageConfig> = {};
for (const s of STAGES) {
  stageMap[s.key] = s;
}

// ─── Empty Form ───

const emptyForm = {
  title: "",
  contact_name: "",
  value: "",
  stage: "new",
  expected_close_date: "",
  notes: "",
};

// ─── Helper: resolve stage key from deal ───

function resolveStageKey(deal: Deal): string {
  if (stageMap[deal.stage]) return deal.stage;
  if (stageMap[deal.status]) return deal.status;
  return "new";
}

// ─── Helper: format currency ───

function formatSAR(value: number): string {
  return value.toLocaleString("ar-SA") + " ر.س";
}

// ──────────────────────────────────────────────
// COMPONENT
// ──────────────────────────────────────────────

export default function DealsPage() {
  const [data, setData] = useState<Deal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [viewMode, setViewMode] = useState<ViewMode>("board");
  const [modalOpen, setModalOpen] = useState(false);
  const [editingDeal, setEditingDeal] = useState<Deal | null>(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);

  // Drag & drop state
  const [draggedDealId, setDraggedDealId] = useState<string | null>(null);
  const [dragOverColumn, setDragOverColumn] = useState<string | null>(null);

  // ─── Data Fetching ───

  const fetchDeals = useCallback(() => {
    setLoading(true);
    deals
      .list()
      .then((res: any) => setData(res.items || res.deals || res || []))
      .catch((err: any) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    fetchDeals();
  }, [fetchDeals]);

  // ─── Filtered data ───

  const filtered = data.filter(
    (d) =>
      d.title?.includes(search) ||
      d.contact_name?.includes(search)
  );

  // ─── Modal Handlers ───

  const openCreate = () => {
    setEditingDeal(null);
    setForm(emptyForm);
    setModalOpen(true);
  };

  const openEdit = (deal: Deal) => {
    setEditingDeal(deal);
    setForm({
      title: deal.title || "",
      contact_name: deal.contact_name || "",
      value: deal.value?.toString() || "",
      stage: resolveStageKey(deal),
      expected_close_date: deal.expected_close_date || "",
      notes: deal.notes || "",
    });
    setModalOpen(true);
  };

  const handleSave = async () => {
    if (!form.title.trim()) return;
    setSaving(true);
    try {
      const payload = {
        ...form,
        value: parseFloat(form.value) || 0,
      };
      if (editingDeal) {
        await deals.update(editingDeal.id, payload);
      } else {
        await deals.create(payload);
      }
      setModalOpen(false);
      fetchDeals();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const updateField = (field: string, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  // ─── Drag & Drop Handlers ───

  const handleDragStart = (e: DragEvent<HTMLDivElement>, dealId: string) => {
    e.dataTransfer.setData("text/plain", dealId);
    e.dataTransfer.effectAllowed = "move";
    setDraggedDealId(dealId);
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>, stageKey: string) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
    setDragOverColumn(stageKey);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    const relatedTarget = e.relatedTarget as HTMLElement | null;
    const currentTarget = e.currentTarget as HTMLElement;
    if (relatedTarget && currentTarget.contains(relatedTarget)) {
      return;
    }
    setDragOverColumn(null);
  };

  const handleDrop = async (e: DragEvent<HTMLDivElement>, newStage: string) => {
    e.preventDefault();
    setDragOverColumn(null);
    const dealId = e.dataTransfer.getData("text/plain");
    setDraggedDealId(null);

    if (!dealId) return;

    const deal = data.find((d) => d.id === dealId);
    if (!deal) return;

    const currentStage = resolveStageKey(deal);
    if (currentStage === newStage) return;

    // Optimistic update
    setData((prev) =>
      prev.map((d) =>
        d.id === dealId ? { ...d, stage: newStage, status: newStage } : d
      )
    );

    try {
      await deals.update(dealId, { stage: newStage });
    } catch (err: any) {
      // Revert on error
      setData((prev) =>
        prev.map((d) =>
          d.id === dealId ? { ...d, stage: currentStage, status: currentStage } : d
        )
      );
      setError(err.message);
    }
  };

  const handleDragEnd = () => {
    setDraggedDealId(null);
    setDragOverColumn(null);
  };

  // ─── Loading State ───

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-[#0FAF9A]" />
      </div>
    );
  }

  // ─── Error State (no data) ───

  if (error && data.length === 0) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 text-sm">
        {error}
      </div>
    );
  }

  // ─── Render ───

  return (
    <div dir="rtl">
      {/* ─── Header Bar ─── */}
      <div className="mb-4 flex items-center justify-between gap-4 flex-wrap">
        {/* Search */}
        <div className="relative max-w-sm flex-1 min-w-[200px]">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="بحث في الصفقات..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pr-9 pl-4 py-2.5 bg-white border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-[#0FAF9A] focus:border-[#0FAF9A] outline-none"
          />
        </div>

        <div className="flex items-center gap-3">
          {/* View Toggle */}
          <div className="flex items-center bg-white border border-gray-300 rounded-lg overflow-hidden">
            <button
              onClick={() => setViewMode("board")}
              className={`flex items-center gap-1.5 px-3 py-2 text-sm font-medium transition ${
                viewMode === "board"
                  ? "bg-[#0FAF9A] text-white"
                  : "text-gray-600 hover:bg-gray-50"
              }`}
              title="عرض اللوحة"
            >
              <LayoutGrid className="w-4 h-4" />
              <span className="hidden sm:inline">لوحة</span>
            </button>
            <button
              onClick={() => setViewMode("table")}
              className={`flex items-center gap-1.5 px-3 py-2 text-sm font-medium transition ${
                viewMode === "table"
                  ? "bg-[#0FAF9A] text-white"
                  : "text-gray-600 hover:bg-gray-50"
              }`}
              title="عرض الجدول"
            >
              <List className="w-4 h-4" />
              <span className="hidden sm:inline">جدول</span>
            </button>
          </div>

          {/* Add Deal Button */}
          <button
            onClick={openCreate}
            className="bg-[#0FAF9A] hover:bg-[#0d9e8b] text-white px-4 py-2.5 rounded-lg text-sm font-medium transition flex items-center gap-2 shrink-0"
          >
            <Plus className="w-4 h-4" />
            إضافة صفقة
          </button>
        </div>
      </div>

      {/* ─── Inline Error Banner ─── */}
      {error && data.length > 0 && (
        <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm flex items-center justify-between">
          <span>{error}</span>
          <button
            onClick={() => setError("")}
            className="text-red-500 hover:text-red-700 text-xs font-medium"
          >
            إغلاق
          </button>
        </div>
      )}

      {/* ─── Board View ─── */}
      {viewMode === "board" && (
        <div className="flex gap-4 overflow-x-auto pb-4" style={{ direction: "rtl" }}>
          {STAGES.map((stage) => {
            const columnDeals = filtered.filter(
              (d) => resolveStageKey(d) === stage.key
            );
            const totalValue = columnDeals.reduce(
              (sum, d) => sum + (d.value || 0),
              0
            );
            const isOver = dragOverColumn === stage.key;

            return (
              <div
                key={stage.key}
                className={`flex-shrink-0 w-72 flex flex-col rounded-xl border transition-colors ${
                  isOver
                    ? "border-[#0FAF9A] bg-[#0FAF9A]/5 shadow-md"
                    : "border-gray-200 bg-gray-50/50"
                }`}
                onDragOver={(e) => handleDragOver(e, stage.key)}
                onDragLeave={handleDragLeave}
                onDrop={(e) => handleDrop(e, stage.key)}
              >
                {/* Column Header */}
                <div
                  className={`px-4 py-3 rounded-t-xl ${stage.headerBg} border-b border-gray-200`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div
                        className={`w-2.5 h-2.5 rounded-full ${stage.dotColor}`}
                      />
                      <span
                        className={`text-sm font-bold ${stage.headerText}`}
                      >
                        {stage.label}
                      </span>
                      <span className="text-xs text-gray-500 bg-white/80 px-1.5 py-0.5 rounded-full font-medium">
                        {columnDeals.length}
                      </span>
                    </div>
                  </div>
                  <div className="mt-1 text-xs text-gray-500 font-medium">
                    {formatSAR(totalValue)}
                  </div>
                </div>

                {/* Column Body */}
                <div className="flex-1 p-2 space-y-2 min-h-[120px]">
                  {columnDeals.length === 0 && (
                    <div className="flex items-center justify-center h-24 text-gray-400 text-xs">
                      لا توجد صفقات
                    </div>
                  )}
                  {columnDeals.map((deal) => {
                    const isDragging = draggedDealId === deal.id;
                    return (
                      <div
                        key={deal.id}
                        draggable
                        onDragStart={(e) => handleDragStart(e, deal.id)}
                        onDragEnd={handleDragEnd}
                        className={`bg-white rounded-lg border border-gray-200 p-3 cursor-grab active:cursor-grabbing transition-all hover:shadow-md group border-r-4 ${stage.borderColor} ${
                          isDragging
                            ? "opacity-40 scale-95 shadow-none"
                            : "opacity-100"
                        }`}
                      >
                        {/* Card Header */}
                        <div className="flex items-start justify-between gap-2 mb-2">
                          <div className="flex items-center gap-1.5 min-w-0">
                            <GripVertical className="w-3.5 h-3.5 text-gray-300 group-hover:text-gray-500 flex-shrink-0 transition" />
                            <h4 className="text-sm font-semibold text-gray-900 truncate">
                              {deal.title}
                            </h4>
                          </div>
                          <button
                            onClick={() => openEdit(deal)}
                            className="p-1 text-gray-400 hover:text-[#0FAF9A] hover:bg-[#0FAF9A]/10 rounded transition opacity-0 group-hover:opacity-100 flex-shrink-0"
                          >
                            <Pencil className="w-3.5 h-3.5" />
                          </button>
                        </div>

                        {/* Card Details */}
                        <div className="space-y-1.5">
                          {deal.contact_name && (
                            <div className="flex items-center gap-1.5 text-xs text-gray-500">
                              <User className="w-3 h-3 flex-shrink-0" />
                              <span className="truncate">
                                {deal.contact_name}
                              </span>
                            </div>
                          )}
                          <div className="flex items-center gap-1.5 text-xs font-semibold text-gray-800">
                            <Banknote className="w-3 h-3 flex-shrink-0 text-[#0FAF9A]" />
                            <span>{formatSAR(deal.value || 0)}</span>
                          </div>
                          {deal.expected_close_date && (
                            <div className="flex items-center gap-1.5 text-xs text-gray-400">
                              <CalendarDays className="w-3 h-3 flex-shrink-0" />
                              <span>
                                {new Date(
                                  deal.expected_close_date
                                ).toLocaleDateString("ar-SA")}
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* ─── Table View ─── */}
      {viewMode === "table" && (
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-200">
                  <th className="text-right px-4 py-3 font-semibold text-gray-600">
                    العنوان
                  </th>
                  <th className="text-right px-4 py-3 font-semibold text-gray-600">
                    العميل
                  </th>
                  <th className="text-right px-4 py-3 font-semibold text-gray-600">
                    القيمة
                  </th>
                  <th className="text-right px-4 py-3 font-semibold text-gray-600">
                    المرحلة
                  </th>
                  <th className="text-right px-4 py-3 font-semibold text-gray-600">
                    تاريخ الإغلاق
                  </th>
                  <th className="text-right px-4 py-3 font-semibold text-gray-600">
                    تاريخ الإنشاء
                  </th>
                  <th className="text-right px-4 py-3 font-semibold text-gray-600 w-10"></th>
                </tr>
              </thead>
              <tbody>
                {filtered.length === 0 ? (
                  <tr>
                    <td
                      colSpan={7}
                      className="text-center py-10 text-gray-400"
                    >
                      <Handshake className="w-8 h-8 mx-auto mb-2 opacity-50" />
                      لا توجد صفقات
                    </td>
                  </tr>
                ) : (
                  filtered.map((deal) => {
                    const stageKey = resolveStageKey(deal);
                    const stage = stageMap[stageKey] || STAGES[0];
                    return (
                      <tr
                        key={deal.id}
                        className="border-b border-gray-100 hover:bg-gray-50 transition"
                      >
                        <td className="px-4 py-3 font-medium text-gray-900">
                          {deal.title}
                        </td>
                        <td className="px-4 py-3 text-gray-600">
                          {deal.contact_name || "-"}
                        </td>
                        <td className="px-4 py-3 text-gray-900 font-medium">
                          {formatSAR(deal.value || 0)}
                        </td>
                        <td className="px-4 py-3">
                          <span
                            className={`inline-block px-2.5 py-1 rounded-full text-xs font-medium ${stage.badgeColor}`}
                          >
                            {stage.label}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-gray-500 text-xs">
                          {deal.expected_close_date
                            ? new Date(
                                deal.expected_close_date
                              ).toLocaleDateString("ar-SA")
                            : "-"}
                        </td>
                        <td className="px-4 py-3 text-gray-500 text-xs">
                          {new Date(deal.created_at).toLocaleDateString(
                            "ar-SA"
                          )}
                        </td>
                        <td className="px-4 py-3">
                          <button
                            onClick={() => openEdit(deal)}
                            className="p-1.5 text-gray-400 hover:text-[#0FAF9A] hover:bg-[#0FAF9A]/10 rounded-lg transition"
                          >
                            <Pencil className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ─── Create / Edit Modal ─── */}
      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editingDeal ? "تعديل الصفقة" : "إضافة صفقة جديدة"}
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              عنوان الصفقة *
            </label>
            <input
              type="text"
              value={form.title}
              onChange={(e) => updateField("title", e.target.value)}
              placeholder="مشروع تطوير الموقع"
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-[#0FAF9A] focus:border-[#0FAF9A] outline-none"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                اسم العميل
              </label>
              <input
                type="text"
                value={form.contact_name}
                onChange={(e) => updateField("contact_name", e.target.value)}
                placeholder="أحمد محمد"
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-[#0FAF9A] focus:border-[#0FAF9A] outline-none"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                القيمة (ر.س)
              </label>
              <input
                type="number"
                dir="ltr"
                value={form.value}
                onChange={(e) => updateField("value", e.target.value)}
                placeholder="50000"
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-[#0FAF9A] focus:border-[#0FAF9A] outline-none"
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                المرحلة
              </label>
              <select
                value={form.stage}
                onChange={(e) => updateField("stage", e.target.value)}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-[#0FAF9A] focus:border-[#0FAF9A] outline-none"
              >
                {STAGES.map((s) => (
                  <option key={s.key} value={s.key}>
                    {s.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                تاريخ الإغلاق المتوقع
              </label>
              <input
                type="date"
                dir="ltr"
                value={form.expected_close_date}
                onChange={(e) =>
                  updateField("expected_close_date", e.target.value)
                }
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-[#0FAF9A] focus:border-[#0FAF9A] outline-none"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              ملاحظات
            </label>
            <textarea
              value={form.notes}
              onChange={(e) => updateField("notes", e.target.value)}
              rows={3}
              placeholder="ملاحظات إضافية..."
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-[#0FAF9A] focus:border-[#0FAF9A] outline-none resize-none"
            />
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button
              onClick={() => setModalOpen(false)}
              className="px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-100 rounded-lg transition"
            >
              إلغاء
            </button>
            <button
              onClick={handleSave}
              disabled={saving || !form.title.trim()}
              className="bg-[#0FAF9A] hover:bg-[#0d9e8b] text-white px-5 py-2.5 rounded-lg text-sm font-medium transition disabled:opacity-50 flex items-center gap-2"
            >
              {saving && <Loader2 className="w-4 h-4 animate-spin" />}
              {editingDeal ? "حفظ التعديلات" : "إضافة"}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
