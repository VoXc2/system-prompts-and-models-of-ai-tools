"use client";

import { useEffect, useState } from "react";
import { tenant as tenantApi, users as usersApi, integrations as integrationsApi } from "@/lib/api";
import {
  Settings,
  Building2,
  Link2,
  UsersRound,
  ChevronLeft,
  Globe,
  Phone,
  Mail,
  MapPin,
  MessageSquare,
  CreditCard,
  Shield,
  Loader2,
  Check,
  Plus,
  Pencil,
  Trash2,
  X,
  Wifi,
  WifiOff,
  UserPlus,
  Eye,
  EyeOff,
} from "lucide-react";

type SettingsTab = "profile" | "integrations" | "team";

const tabs: { key: SettingsTab; label: string; icon: any }[] = [
  { key: "profile", label: "الملف التجاري", icon: Building2 },
  { key: "integrations", label: "الربط", icon: Link2 },
  { key: "team", label: "الفريق", icon: UsersRound },
];

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<SettingsTab>("profile");

  return (
    <div className="flex flex-col lg:flex-row gap-6">
      {/* Sidebar tabs */}
      <div className="lg:w-64 shrink-0">
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`w-full flex items-center justify-between px-4 py-3 text-sm font-medium transition border-b border-gray-100 last:border-b-0 ${
                activeTab === tab.key
                  ? "bg-secondary-50 text-secondary-700"
                  : "text-gray-600 hover:bg-gray-50"
              }`}
            >
              <div className="flex items-center gap-3">
                <tab.icon className="w-5 h-5" />
                {tab.label}
              </div>
              <ChevronLeft className="w-4 h-4 opacity-40" />
            </button>
          ))}
        </div>
      </div>

      {/* Content area */}
      <div className="flex-1">
        {activeTab === "profile" && <ProfileSection />}
        {activeTab === "integrations" && <IntegrationsSection />}
        {activeTab === "team" && <TeamSection />}
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════
   Profile Section
   ═══════════════════════════════════════════════════════════════ */

function ProfileSection() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    name: "",
    name_ar: "",
    phone: "",
    email: "",
    whatsapp_number: "",
    industry: "",
  });

  useEffect(() => {
    tenantApi
      .get()
      .then((data: any) => {
        setForm({
          name: data.name || "",
          name_ar: data.name_ar || "",
          phone: data.phone || "",
          email: data.email || "",
          whatsapp_number: data.whatsapp_number || "",
          industry: data.industry || "",
        });
      })
      .catch((err: any) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async () => {
    setSaving(true);
    setError("");
    setSaved(false);
    try {
      await tenantApi.update(form);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const updateField = (field: string, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-secondary" />
      </div>
    );
  }

  const fields = [
    { key: "name", label: "اسم الشركة (English)", icon: Building2, placeholder: "Success Co." },
    { key: "name_ar", label: "اسم الشركة (عربي)", icon: Building2, placeholder: "شركة النجاح" },
    { key: "phone", label: "رقم الهاتف", icon: Phone, placeholder: "+966 5XX XXX XXXX", dir: "ltr" as const },
    { key: "email", label: "البريد الإلكتروني", icon: Mail, placeholder: "info@company.com", dir: "ltr" as const },
    { key: "whatsapp_number", label: "واتساب بيزنس", icon: MessageSquare, placeholder: "+966 5XX XXX XXXX", dir: "ltr" as const },
    { key: "industry", label: "القطاع", icon: Building2, placeholder: "عقارات، عيادات، مقاولات..." },
  ];

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <Building2 className="w-5 h-5 text-secondary" />
          معلومات الشركة
        </h3>

        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {fields.map((field) => (
            <div key={field.key}>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {field.label}
              </label>
              <div className="relative">
                <field.icon className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder={field.placeholder}
                  dir={field.dir || "rtl"}
                  value={form[field.key as keyof typeof form]}
                  onChange={(e) => updateField(field.key, e.target.value)}
                  className="w-full pr-9 pl-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary focus:border-secondary outline-none"
                />
              </div>
            </div>
          ))}
        </div>
        <div className="mt-4 flex items-center justify-end gap-3">
          {saved && (
            <span className="text-green-600 text-sm flex items-center gap-1">
              <Check className="w-4 h-4" />
              تم الحفظ
            </span>
          )}
          <button
            onClick={handleSave}
            disabled={saving}
            className="bg-secondary hover:bg-secondary-600 text-white px-5 py-2.5 rounded-lg text-sm font-medium transition disabled:opacity-50 flex items-center gap-2"
          >
            {saving && <Loader2 className="w-4 h-4 animate-spin" />}
            حفظ التغييرات
          </button>
        </div>
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════
   Integrations Section
   ═══════════════════════════════════════════════════════════════ */

const AVAILABLE_PROVIDERS = [
  { provider: "meta", name: "واتساب بيزنس", description: "ربط حساب واتساب بيزنس API لإرسال واستقبال الرسائل", icon: MessageSquare },
  { provider: "google", name: "Google Calendar", description: "مزامنة المواعيد مع تقويم جوجل", icon: Globe },
  { provider: "sendgrid", name: "SendGrid Email", description: "إرسال إيميلات تسويقية ومتابعة", icon: Mail },
  { provider: "vapi", name: "Voice AI (Vapi)", description: "مكالمات صوتية ذكية بالذكاء الاصطناعي", icon: Phone },
  { provider: "linkedin", name: "LinkedIn", description: "ربط حساب LinkedIn للتواصل المهني", icon: Globe },
  { provider: "hunter", name: "Hunter.io", description: "البحث عن إيميلات العملاء المحتملين", icon: Mail },
];

function IntegrationsSection() {
  const [loading, setLoading] = useState(true);
  const [connected, setConnected] = useState<any[]>([]);
  const [error, setError] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [connectingProvider, setConnectingProvider] = useState<typeof AVAILABLE_PROVIDERS[0] | null>(null);
  const [connectForm, setConnectForm] = useState({ account_id: "", account_name: "", credentials: "" });
  const [submitting, setSubmitting] = useState(false);

  const loadIntegrations = () => {
    setLoading(true);
    integrationsApi
      .list()
      .then((data: any) => {
        setConnected(Array.isArray(data) ? data : data.items || []);
      })
      .catch((err: any) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadIntegrations();
  }, []);

  const handleConnect = async () => {
    if (!connectingProvider) return;
    setSubmitting(true);
    setError("");
    try {
      await integrationsApi.connect({
        provider: connectingProvider.provider,
        account_id: connectForm.account_id,
        account_name: connectForm.account_name || connectingProvider.name,
        credentials: connectForm.credentials ? JSON.parse(connectForm.credentials) : {},
      });
      setShowModal(false);
      setConnectForm({ account_id: "", account_name: "", credentials: "" });
      setConnectingProvider(null);
      loadIntegrations();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDisconnect = async (id: string) => {
    try {
      await integrationsApi.disconnect(id);
      loadIntegrations();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const connectedProviders = new Set(connected.filter((c) => c.is_active !== false).map((c: any) => c.provider));

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-secondary" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm">
          {error}
        </div>
      )}

      {/* Connected integrations */}
      {connected.filter((c) => c.is_active !== false).length > 0 && (
        <div className="mb-2">
          <h4 className="text-sm font-semibold text-gray-500 mb-3">متصل</h4>
          {connected
            .filter((c) => c.is_active !== false)
            .map((item: any) => {
              const providerInfo = AVAILABLE_PROVIDERS.find((p) => p.provider === item.provider);
              const Icon = providerInfo?.icon || Globe;
              return (
                <div
                  key={item.id}
                  className="bg-white rounded-xl border border-green-200 p-5 flex items-center justify-between mb-3"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-green-50 text-green-600 rounded-xl flex items-center justify-center">
                      <Icon className="w-6 h-6" />
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900">
                        {providerInfo?.name || item.provider}
                      </p>
                      <p className="text-sm text-gray-500">
                        {item.account_name || item.account_id}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-green-600 text-xs font-medium flex items-center gap-1">
                      <Wifi className="w-3.5 h-3.5" />
                      متصل
                    </span>
                    <button
                      onClick={() => handleDisconnect(item.id)}
                      className="text-red-500 hover:text-red-700 text-sm px-3 py-1.5 rounded-lg hover:bg-red-50 transition"
                    >
                      فصل
                    </button>
                  </div>
                </div>
              );
            })}
        </div>
      )}

      {/* Available integrations */}
      <div>
        <h4 className="text-sm font-semibold text-gray-500 mb-3">
          {connectedProviders.size > 0 ? "متاح للربط" : "الربط المتاح"}
        </h4>
        {AVAILABLE_PROVIDERS.filter((p) => !connectedProviders.has(p.provider)).map((item) => (
          <div
            key={item.provider}
            className="bg-white rounded-xl border border-gray-200 p-5 flex items-center justify-between mb-3"
          >
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-primary-50 text-primary-600 rounded-xl flex items-center justify-center">
                <item.icon className="w-6 h-6" />
              </div>
              <div>
                <p className="font-semibold text-gray-900">{item.name}</p>
                <p className="text-sm text-gray-500">{item.description}</p>
              </div>
            </div>
            <button
              onClick={() => {
                setConnectingProvider(item);
                setShowModal(true);
                setError("");
              }}
              className="bg-gray-100 text-gray-700 hover:bg-gray-200 px-4 py-2 rounded-lg text-sm font-medium transition"
            >
              ربط
            </button>
          </div>
        ))}
      </div>

      {/* Connect Modal */}
      {showModal && connectingProvider && (
        <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl w-full max-w-md p-6 shadow-xl" dir="rtl">
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-lg font-bold text-gray-900">
                ربط {connectingProvider.name}
              </h3>
              <button
                onClick={() => { setShowModal(false); setConnectingProvider(null); }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">معرّف الحساب</label>
                <input
                  type="text"
                  dir="ltr"
                  placeholder="Account ID"
                  value={connectForm.account_id}
                  onChange={(e) => setConnectForm((p) => ({ ...p, account_id: e.target.value }))}
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary focus:border-secondary outline-none"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">اسم الحساب</label>
                <input
                  type="text"
                  placeholder={connectingProvider.name}
                  value={connectForm.account_name}
                  onChange={(e) => setConnectForm((p) => ({ ...p, account_name: e.target.value }))}
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary focus:border-secondary outline-none"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">بيانات الاعتماد (JSON)</label>
                <textarea
                  dir="ltr"
                  rows={3}
                  placeholder='{"api_key": "..."}'
                  value={connectForm.credentials}
                  onChange={(e) => setConnectForm((p) => ({ ...p, credentials: e.target.value }))}
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary focus:border-secondary outline-none font-mono"
                />
              </div>
            </div>

            <div className="mt-5 flex items-center justify-end gap-3">
              <button
                onClick={() => { setShowModal(false); setConnectingProvider(null); }}
                className="px-4 py-2.5 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition"
              >
                إلغاء
              </button>
              <button
                onClick={handleConnect}
                disabled={submitting || !connectForm.account_id}
                className="bg-secondary hover:bg-secondary-600 text-white px-5 py-2.5 rounded-lg text-sm font-medium transition disabled:opacity-50 flex items-center gap-2"
              >
                {submitting && <Loader2 className="w-4 h-4 animate-spin" />}
                ربط
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════
   Team Section
   ═══════════════════════════════════════════════════════════════ */

const ROLE_LABELS: Record<string, { label: string; color: string }> = {
  owner: { label: "مالك", color: "bg-purple-100 text-purple-700" },
  admin: { label: "مشرف", color: "bg-red-100 text-red-700" },
  manager: { label: "مدير", color: "bg-blue-100 text-blue-700" },
  agent: { label: "موظف", color: "bg-gray-100 text-gray-700" },
};

function TeamSection() {
  const [loading, setLoading] = useState(true);
  const [members, setMembers] = useState<any[]>([]);
  const [error, setError] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [editingMember, setEditingMember] = useState<any>(null);
  const [showPassword, setShowPassword] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState({
    email: "",
    password: "",
    full_name: "",
    full_name_ar: "",
    role: "agent",
    phone: "",
  });

  const loadMembers = () => {
    setLoading(true);
    usersApi
      .list()
      .then((data: any) => {
        setMembers(Array.isArray(data) ? data : data.items || []);
      })
      .catch((err: any) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadMembers();
  }, []);

  const resetForm = () => {
    setForm({ email: "", password: "", full_name: "", full_name_ar: "", role: "agent", phone: "" });
    setEditingMember(null);
    setShowPassword(false);
  };

  const openCreate = () => {
    resetForm();
    setShowModal(true);
    setError("");
  };

  const openEdit = (member: any) => {
    setEditingMember(member);
    setForm({
      email: member.email || "",
      password: "",
      full_name: member.full_name || "",
      full_name_ar: member.full_name_ar || "",
      role: member.role || "agent",
      phone: member.phone || "",
    });
    setShowModal(true);
    setError("");
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    setError("");
    try {
      if (editingMember) {
        await usersApi.update(editingMember.id, {
          full_name: form.full_name,
          full_name_ar: form.full_name_ar,
          role: form.role,
          phone: form.phone,
        });
      } else {
        await usersApi.create(form);
      }
      setShowModal(false);
      resetForm();
      loadMembers();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: string) => {
    setError("");
    try {
      await usersApi.delete(id);
      loadMembers();
    } catch (err: any) {
      setError(err.message);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-secondary" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
            <UsersRound className="w-5 h-5 text-secondary" />
            أعضاء الفريق
            <span className="text-sm font-normal text-gray-400">({members.length})</span>
          </h3>
          <button
            onClick={openCreate}
            className="bg-secondary hover:bg-secondary-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition flex items-center gap-2"
          >
            <UserPlus className="w-4 h-4" />
            إضافة عضو
          </button>
        </div>

        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm">
            {error}
          </div>
        )}

        {members.length === 0 ? (
          <div className="text-center py-10 text-gray-400 text-sm">
            <Shield className="w-8 h-8 mx-auto mb-2 opacity-50" />
            لم يتم إضافة أعضاء فريق بعد
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 text-gray-500">
                  <th className="text-right pb-3 font-medium">العضو</th>
                  <th className="text-right pb-3 font-medium">البريد</th>
                  <th className="text-right pb-3 font-medium">الدور</th>
                  <th className="text-right pb-3 font-medium">الحالة</th>
                  <th className="text-right pb-3 font-medium">إجراءات</th>
                </tr>
              </thead>
              <tbody>
                {members.map((member: any) => {
                  const role = ROLE_LABELS[member.role] || ROLE_LABELS.agent;
                  return (
                    <tr key={member.id} className="border-b border-gray-100 last:border-b-0">
                      <td className="py-3">
                        <div className="flex items-center gap-3">
                          <div className="w-9 h-9 rounded-full bg-secondary-100 text-secondary-700 flex items-center justify-center font-bold text-xs">
                            {(member.full_name_ar || member.full_name || member.email || "?").charAt(0)}
                          </div>
                          <div>
                            <p className="font-medium text-gray-900">
                              {member.full_name_ar || member.full_name || "-"}
                            </p>
                            {member.phone && (
                              <p className="text-xs text-gray-400" dir="ltr">{member.phone}</p>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="py-3 text-gray-600" dir="ltr">{member.email}</td>
                      <td className="py-3">
                        <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${role.color}`}>
                          {role.label}
                        </span>
                      </td>
                      <td className="py-3">
                        <span
                          className={`px-2.5 py-1 rounded-full text-xs font-medium ${
                            member.is_active !== false
                              ? "bg-green-100 text-green-700"
                              : "bg-gray-100 text-gray-500"
                          }`}
                        >
                          {member.is_active !== false ? "نشط" : "معطّل"}
                        </span>
                      </td>
                      <td className="py-3">
                        <div className="flex items-center gap-1">
                          <button
                            onClick={() => openEdit(member)}
                            className="p-1.5 text-gray-400 hover:text-secondary hover:bg-secondary-50 rounded-lg transition"
                            title="تعديل"
                          >
                            <Pencil className="w-4 h-4" />
                          </button>
                          {member.role !== "owner" && (
                            <button
                              onClick={() => handleDelete(member.id)}
                              className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition"
                              title="حذف"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Add/Edit Member Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl w-full max-w-md p-6 shadow-xl" dir="rtl">
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-lg font-bold text-gray-900">
                {editingMember ? "تعديل عضو" : "إضافة عضو جديد"}
              </h3>
              <button
                onClick={() => { setShowModal(false); resetForm(); }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              {!editingMember && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">البريد الإلكتروني</label>
                    <input
                      type="email"
                      dir="ltr"
                      placeholder="user@company.com"
                      value={form.email}
                      onChange={(e) => setForm((p) => ({ ...p, email: e.target.value }))}
                      className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary focus:border-secondary outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">كلمة المرور</label>
                    <div className="relative">
                      <input
                        type={showPassword ? "text" : "password"}
                        dir="ltr"
                        placeholder="********"
                        value={form.password}
                        onChange={(e) => setForm((p) => ({ ...p, password: e.target.value }))}
                        className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary focus:border-secondary outline-none pl-10"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
                      >
                        {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>
                </>
              )}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">الاسم (English)</label>
                  <input
                    type="text"
                    dir="ltr"
                    placeholder="Full Name"
                    value={form.full_name}
                    onChange={(e) => setForm((p) => ({ ...p, full_name: e.target.value }))}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary focus:border-secondary outline-none"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">الاسم (عربي)</label>
                  <input
                    type="text"
                    placeholder="الاسم الكامل"
                    value={form.full_name_ar}
                    onChange={(e) => setForm((p) => ({ ...p, full_name_ar: e.target.value }))}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary focus:border-secondary outline-none"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">رقم الهاتف</label>
                <input
                  type="text"
                  dir="ltr"
                  placeholder="+966 5XX XXX XXXX"
                  value={form.phone}
                  onChange={(e) => setForm((p) => ({ ...p, phone: e.target.value }))}
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary focus:border-secondary outline-none"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">الدور</label>
                <select
                  value={form.role}
                  onChange={(e) => setForm((p) => ({ ...p, role: e.target.value }))}
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary focus:border-secondary outline-none bg-white"
                >
                  <option value="agent">موظف</option>
                  <option value="manager">مدير</option>
                  <option value="admin">مشرف</option>
                </select>
              </div>
            </div>

            <div className="mt-5 flex items-center justify-end gap-3">
              <button
                onClick={() => { setShowModal(false); resetForm(); }}
                className="px-4 py-2.5 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition"
              >
                إلغاء
              </button>
              <button
                onClick={handleSubmit}
                disabled={submitting || (!editingMember && (!form.email || !form.password))}
                className="bg-secondary hover:bg-secondary-600 text-white px-5 py-2.5 rounded-lg text-sm font-medium transition disabled:opacity-50 flex items-center gap-2"
              >
                {submitting && <Loader2 className="w-4 h-4 animate-spin" />}
                {editingMember ? "حفظ التعديلات" : "إضافة"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
