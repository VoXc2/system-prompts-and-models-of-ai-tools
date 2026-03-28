"use client";

import { useState } from "react";
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

function ProfileSection() {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <Building2 className="w-5 h-5 text-secondary" />
          معلومات الشركة
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {[
            { label: "اسم الشركة", icon: Building2, placeholder: "شركة النجاح" },
            { label: "الموقع الإلكتروني", icon: Globe, placeholder: "www.example.com", dir: "ltr" as const },
            { label: "رقم الهاتف", icon: Phone, placeholder: "+966 5XX XXX XXXX", dir: "ltr" as const },
            { label: "البريد الإلكتروني", icon: Mail, placeholder: "info@company.com", dir: "ltr" as const },
            { label: "المدينة", icon: MapPin, placeholder: "الرياض" },
          ].map((field) => (
            <div key={field.label}>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {field.label}
              </label>
              <div className="relative">
                <field.icon className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder={field.placeholder}
                  dir={field.dir || "rtl"}
                  className="w-full pr-9 pl-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-secondary focus:border-secondary outline-none"
                />
              </div>
            </div>
          ))}
        </div>
        <div className="mt-4 flex justify-end">
          <button className="bg-secondary hover:bg-secondary-600 text-white px-5 py-2.5 rounded-lg text-sm font-medium transition">
            حفظ التغييرات
          </button>
        </div>
      </div>
    </div>
  );
}

function IntegrationsSection() {
  const integrations = [
    {
      name: "واتساب بيزنس",
      description: "ربط حساب واتساب بيزنس API لإرسال واستقبال الرسائل",
      icon: MessageSquare,
      connected: false,
    },
    {
      name: "بوابة الدفع",
      description: "ربط بوابة دفع لمعالجة المدفوعات",
      icon: CreditCard,
      connected: false,
    },
    {
      name: "Google Calendar",
      description: "مزامنة المواعيد مع تقويم جوجل",
      icon: Globe,
      connected: false,
    },
  ];

  return (
    <div className="space-y-4">
      {integrations.map((item) => (
        <div
          key={item.name}
          className="bg-white rounded-xl border border-gray-200 p-5 flex items-center justify-between"
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
            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
              item.connected
                ? "bg-green-100 text-green-700"
                : "bg-gray-100 text-gray-700 hover:bg-gray-200"
            }`}
          >
            {item.connected ? "متصل" : "ربط"}
          </button>
        </div>
      ))}
    </div>
  );
}

function TeamSection() {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
          <UsersRound className="w-5 h-5 text-secondary" />
          أعضاء الفريق
        </h3>
        <button className="bg-secondary hover:bg-secondary-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition">
          إضافة عضو
        </button>
      </div>

      <div className="text-center py-10 text-gray-400 text-sm">
        <Shield className="w-8 h-8 mx-auto mb-2 opacity-50" />
        لم يتم إضافة أعضاء فريق بعد
      </div>
    </div>
  );
}
