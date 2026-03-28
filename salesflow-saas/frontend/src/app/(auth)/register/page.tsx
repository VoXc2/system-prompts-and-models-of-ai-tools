"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { auth } from "@/lib/api";
import {
  UserPlus,
  Building2,
  User,
  Mail,
  Phone,
  Lock,
  Loader2,
} from "lucide-react";
import Link from "next/link";

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState({
    company_name: "",
    full_name: "",
    email: "",
    phone: "",
    password: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function update(field: string, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await auth.register(form);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "حدث خطأ أثناء إنشاء الحساب");
    } finally {
      setLoading(false);
    }
  }

  const fields = [
    {
      key: "company_name",
      label: "اسم الشركة",
      type: "text",
      icon: Building2,
      placeholder: "مثال: شركة النجاح",
      dir: "rtl" as const,
    },
    {
      key: "full_name",
      label: "الاسم الكامل",
      type: "text",
      icon: User,
      placeholder: "محمد أحمد",
      dir: "rtl" as const,
    },
    {
      key: "email",
      label: "البريد الإلكتروني",
      type: "email",
      icon: Mail,
      placeholder: "example@company.com",
      dir: "ltr" as const,
    },
    {
      key: "phone",
      label: "رقم الهاتف",
      type: "tel",
      icon: Phone,
      placeholder: "+966 5XX XXX XXXX",
      dir: "ltr" as const,
    },
    {
      key: "password",
      label: "كلمة المرور",
      type: "password",
      icon: Lock,
      placeholder: "••••••••",
      dir: "ltr" as const,
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-900 via-dark to-primary-800 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Dealix</h1>
          <p className="text-primary-200">أنشئ حسابك وابدأ الآن</p>
        </div>

        <div className="bg-white rounded-2xl shadow-2xl p-8">
          <h2 className="text-2xl font-bold text-primary-900 mb-6 text-center">
            إنشاء حساب جديد
          </h2>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg p-3 mb-4 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {fields.map((f) => (
              <div key={f.key}>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {f.label}
                </label>
                <div className="relative">
                  <f.icon className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type={f.type}
                    required={f.key !== "phone"}
                    value={form[f.key as keyof typeof form]}
                    onChange={(e) => update(f.key, e.target.value)}
                    placeholder={f.placeholder}
                    dir={f.dir}
                    className="w-full pr-10 pl-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-secondary focus:border-secondary outline-none transition text-sm"
                  />
                </div>
              </div>
            ))}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-secondary hover:bg-secondary-600 text-white font-semibold py-3 rounded-lg transition flex items-center justify-center gap-2 disabled:opacity-60 mt-2"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <UserPlus className="w-5 h-5" />
              )}
              {loading ? "جاري التسجيل..." : "إنشاء الحساب"}
            </button>
          </form>

          <div className="mt-6 text-center text-sm text-gray-600">
            لديك حساب بالفعل؟{" "}
            <Link
              href="/login"
              className="text-secondary font-semibold hover:underline"
            >
              تسجيل الدخول
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
