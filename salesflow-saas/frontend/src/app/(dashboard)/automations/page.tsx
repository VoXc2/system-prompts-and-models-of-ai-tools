"use client";

import { useEffect, useState } from "react";
import { sequences } from "@/lib/api";
import {
  Zap, Play, Pause, Plus, Clock, Users, MessageSquare,
  Loader2, X, ChevronLeft, Mail, Phone, Bell,
  RefreshCw, Calendar, UserPlus, ArrowLeft, Check, Trash2,
} from "lucide-react";

interface Sequence {
  id: string;
  name: string;
  trigger_type?: string;
  status?: string;
  is_active?: boolean;
  enrolled_count?: number;
  steps?: any[];
  created_at?: string;
}

const TEMPLATES = [
  {
    name: "متابعة العميل الجديد",
    icon: UserPlus,
    color: "text-green-600 bg-green-50",
    trigger: "new_lead",
    description: "تابع العملاء الجدد تلقائياً",
    steps: [
      { delay: "0h", action: "whatsapp", message: "مرحباً {name}! شكراً لتواصلك معنا. كيف نقدر نخدمك؟" },
      { delay: "72h", action: "whatsapp", message: "مرحباً {name}، نبي نتأكد إنك لقيت اللي تحتاجه. هل تحتاج مساعدة؟" },
      { delay: "168h", action: "whatsapp", message: "{name}، عندنا عرض خاص لك! تواصل معنا للتفاصيل." },
    ],
  },
  {
    name: "تذكير الموعد",
    icon: Calendar,
    color: "text-blue-600 bg-blue-50",
    trigger: "appointment_created",
    description: "ذكّر العميل قبل الموعد",
    steps: [
      { delay: "-24h", action: "whatsapp", message: "تذكير: عندك موعد بكرة الساعة {time}. نتطلع لزيارتك!" },
      { delay: "-1h", action: "whatsapp", message: "موعدك بعد ساعة! الموقع: {location}" },
    ],
  },
  {
    name: "إعادة تفعيل العميل",
    icon: RefreshCw,
    color: "text-orange-600 bg-orange-50",
    trigger: "inactive_30_days",
    description: "أعد تفعيل العملاء الخاملين",
    steps: [
      { delay: "0h", action: "whatsapp", message: "وحشتنا {name}! عندنا جديد يهمك. زورنا أو تواصل معنا." },
      { delay: "72h", action: "email", message: "عرض خاص لعملائنا المميزين — خصم 15% لفترة محدودة!" },
    ],
  },
  {
    name: "متابعة بعد الاجتماع",
    icon: MessageSquare,
    color: "text-purple-600 bg-purple-50",
    trigger: "meeting_completed",
    description: "تابع بعد كل اجتماع",
    steps: [
      { delay: "2h", action: "whatsapp", message: "شكراً على وقتك اليوم {name}! نرسل لك الملخص قريباً." },
      { delay: "48h", action: "email", message: "مرفق ملخص اجتماعنا. هل عندك أسئلة إضافية؟" },
      { delay: "168h", action: "whatsapp", message: "مرحباً {name}، هل اطلعت على العرض؟ نحب نسمع رأيك." },
    ],
  },
];

export default function AutomationsPage() {
  const [seqs, setSeqs] = useState<Sequence[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [creating, setCreating] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<typeof TEMPLATES[0] | null>(null);
  const [newName, setNewName] = useState("");

  const loadSequences = () => {
    setLoading(true);
    sequences.list()
      .then((data: any) => setSeqs(Array.isArray(data) ? data : data.items || data.data || []))
      .catch((err: any) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => { loadSequences(); }, []);

  const createFromTemplate = async () => {
    if (!selectedTemplate) return;
    setCreating(true);
    setError("");
    try {
      await sequences.create({
        name: newName || selectedTemplate.name,
        trigger_type: selectedTemplate.trigger,
        steps: selectedTemplate.steps,
        is_active: false,
      });
      setShowModal(false);
      setSelectedTemplate(null);
      setNewName("");
      loadSequences();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setCreating(false);
    }
  };

  const toggleActive = async (seq: Sequence) => {
    try {
      await sequences.update(seq.id, { is_active: !seq.is_active });
      loadSequences();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const deleteSeq = async (id: string) => {
    try {
      await sequences.delete(id);
      loadSequences();
    } catch (err: any) {
      setError(err.message);
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center py-20"><Loader2 className="w-8 h-8 animate-spin text-secondary" /></div>;
  }

  return (
    <div className="space-y-6">
      {error && <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm">{error}</div>}

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
            <Zap className="w-6 h-6 text-secondary" /> الأتمتة والمتابعة التلقائية
          </h2>
          <p className="text-sm text-gray-500 mt-1">أنشئ سلاسل متابعة تلقائية عبر واتساب والإيميل</p>
        </div>
        <button onClick={() => setShowModal(true)}
          className="bg-secondary hover:bg-secondary-600 text-white px-4 py-2.5 rounded-lg text-sm font-medium flex items-center gap-2 transition">
          <Plus className="w-4 h-4" /> إنشاء أتمتة
        </button>
      </div>

      {/* Templates */}
      <div>
        <h3 className="text-sm font-semibold text-gray-500 mb-3">قوالب جاهزة</h3>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {TEMPLATES.map((t) => (
            <button key={t.name} onClick={() => { setSelectedTemplate(t); setNewName(t.name); setShowModal(true); }}
              className="bg-white rounded-xl border border-gray-200 p-4 text-right hover:border-secondary hover:shadow-md transition group">
              <div className={`w-10 h-10 rounded-lg flex items-center justify-center mb-3 ${t.color}`}>
                <t.icon className="w-5 h-5" />
              </div>
              <h4 className="font-bold text-gray-900 text-sm mb-1">{t.name}</h4>
              <p className="text-xs text-gray-500">{t.description}</p>
              <p className="text-xs text-secondary mt-2 opacity-0 group-hover:opacity-100 transition">{t.steps.length} خطوات</p>
            </button>
          ))}
        </div>
      </div>

      {/* Active Sequences */}
      <div>
        <h3 className="text-sm font-semibold text-gray-500 mb-3">الأتمتة الحالية ({seqs.length})</h3>
        {seqs.length === 0 ? (
          <div className="bg-white rounded-xl border border-gray-200 p-10 text-center text-gray-400">
            <Zap className="w-10 h-10 mx-auto mb-3 opacity-50" />
            <p className="text-sm">لم تنشئ أي أتمتة بعد</p>
            <p className="text-xs mt-1">اختر من القوالب أعلاه أو أنشئ واحدة جديدة</p>
          </div>
        ) : (
          <div className="space-y-3">
            {seqs.map((seq) => (
              <div key={seq.id} className="bg-white rounded-xl border border-gray-200 p-5 flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${seq.is_active ? "bg-green-50 text-green-600" : "bg-gray-100 text-gray-400"}`}>
                    <Zap className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="font-bold text-gray-900">{seq.name}</h4>
                    <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
                      {seq.trigger_type && <span className="flex items-center gap-1"><Bell className="w-3 h-3" /> {seq.trigger_type}</span>}
                      {seq.steps && <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {seq.steps.length} خطوات</span>}
                      {seq.enrolled_count !== undefined && <span className="flex items-center gap-1"><Users className="w-3 h-3" /> {seq.enrolled_count} مسجل</span>}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button onClick={() => toggleActive(seq)}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                      seq.is_active ? "bg-green-100 text-green-700 hover:bg-green-200" : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                    }`}>
                    {seq.is_active ? <><Pause className="w-3 h-3" /> إيقاف</> : <><Play className="w-3 h-3" /> تشغيل</>}
                  </button>
                  <button onClick={() => deleteSeq(seq.id)}
                    className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Create Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl w-full max-w-lg p-6 shadow-xl max-h-[90vh] overflow-y-auto" dir="rtl">
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-lg font-bold text-gray-900">
                {selectedTemplate ? `إنشاء: ${selectedTemplate.name}` : "أتمتة جديدة"}
              </h3>
              <button onClick={() => { setShowModal(false); setSelectedTemplate(null); }} className="text-gray-400 hover:text-gray-600"><X className="w-5 h-5" /></button>
            </div>

            {!selectedTemplate ? (
              <div className="space-y-3">
                <p className="text-sm text-gray-500 mb-4">اختر قالب:</p>
                {TEMPLATES.map((t) => (
                  <button key={t.name} onClick={() => { setSelectedTemplate(t); setNewName(t.name); }}
                    className="w-full flex items-center gap-3 p-4 rounded-xl border border-gray-200 hover:border-secondary transition text-right">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center shrink-0 ${t.color}`}>
                      <t.icon className="w-5 h-5" />
                    </div>
                    <div>
                      <h4 className="font-bold text-gray-900 text-sm">{t.name}</h4>
                      <p className="text-xs text-gray-500">{t.description}</p>
                    </div>
                  </button>
                ))}
              </div>
            ) : (
              <div className="space-y-5">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">اسم الأتمتة</label>
                  <input type="text" value={newName} onChange={(e) => setNewName(e.target.value)}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary outline-none" />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">الخطوات</label>
                  <div className="space-y-3">
                    {selectedTemplate.steps.map((step, i) => (
                      <div key={i} className="flex gap-3">
                        <div className="flex flex-col items-center">
                          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${
                            step.action === "whatsapp" ? "bg-green-100 text-green-700" : "bg-blue-100 text-blue-700"
                          }`}>
                            {i + 1}
                          </div>
                          {i < selectedTemplate.steps.length - 1 && <div className="w-0.5 h-8 bg-gray-200 mt-1" />}
                        </div>
                        <div className="flex-1 bg-gray-50 rounded-lg p-3">
                          <div className="flex items-center gap-2 text-xs text-gray-500 mb-1">
                            <Clock className="w-3 h-3" />
                            <span>{step.delay === "0h" ? "فوراً" : step.delay.startsWith("-") ? `قبل ${step.delay.replace("-", "")}` : `بعد ${step.delay}`}</span>
                            <span className="mx-1">•</span>
                            {step.action === "whatsapp" ? <MessageSquare className="w-3 h-3 text-green-600" /> : <Mail className="w-3 h-3 text-blue-600" />}
                            <span>{step.action === "whatsapp" ? "واتساب" : "إيميل"}</span>
                          </div>
                          <p className="text-sm text-gray-700">{step.message}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="flex items-center justify-end gap-3 pt-4 border-t">
                  <button onClick={() => setSelectedTemplate(null)} className="px-4 py-2.5 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition">رجوع</button>
                  <button onClick={createFromTemplate} disabled={creating}
                    className="bg-secondary hover:bg-secondary-600 text-white px-5 py-2.5 rounded-lg text-sm font-medium transition disabled:opacity-50 flex items-center gap-2">
                    {creating && <Loader2 className="w-4 h-4 animate-spin" />} إنشاء الأتمتة
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
