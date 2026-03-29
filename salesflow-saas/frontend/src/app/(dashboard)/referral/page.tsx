"use client";

import { useEffect, useState } from "react";
import { tenant as tenantApi } from "@/lib/api";
import {
  Gift, Share2, Copy, Check, Users, Trophy, Zap,
  MessageSquare, Mail, Loader2, Sparkles, Crown, Star,
} from "lucide-react";

export default function ReferralPage() {
  const [tenantData, setTenantData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [copiedLink, setCopiedLink] = useState(false);
  const [copiedTemplate, setCopiedTemplate] = useState(-1);

  useEffect(() => {
    tenantApi
      .get()
      .then((data: any) => setTenantData(data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const origin = typeof window !== "undefined" ? window.location.origin : "";
  const slug = tenantData?.slug || tenantData?.company_name?.toLowerCase().replace(/\s+/g, "-") || "my-business";
  const referralLink = `${origin}/book/${slug}?ref=referral`;

  const shareTemplates = [
    `جرب نظام إدارة العملاء الذكي — احجز موعدك من هنا: ${referralLink}`,
    `وفرت وقت كبير مع Dealix! جربه مجاناً: ${referralLink}`,
    `أفضل نظام CRM عربي — سجل الآن وابدأ مجاناً: ${referralLink}`,
  ];

  const copyToClipboard = (text: string, idx?: number) => {
    navigator.clipboard.writeText(text);
    if (idx !== undefined) {
      setCopiedTemplate(idx);
      setTimeout(() => setCopiedTemplate(-1), 2000);
    } else {
      setCopiedLink(true);
      setTimeout(() => setCopiedLink(false), 2000);
    }
  };

  const shareWhatsApp = () => {
    const msg = encodeURIComponent(shareTemplates[0]);
    window.open(`https://wa.me/?text=${msg}`, "_blank");
  };

  const shareTwitter = () => {
    const msg = encodeURIComponent(`جرب نظام Dealix لإدارة العملاء بالذكاء الاصطناعي! ${referralLink}`);
    window.open(`https://twitter.com/intent/tweet?text=${msg}`, "_blank");
  };

  const shareEmail = () => {
    const subject = encodeURIComponent("جرب نظام Dealix لإدارة العملاء");
    const body = encodeURIComponent(shareTemplates[0]);
    window.open(`mailto:?subject=${subject}&body=${body}`, "_blank");
  };

  const stats = [
    { label: "مشاركات", value: 0, icon: Share2, color: "text-blue-600 bg-blue-50" },
    { label: "نقرات", value: 0, icon: Users, color: "text-purple-600 bg-purple-50" },
    { label: "إحالات ناجحة", value: 0, icon: Trophy, color: "text-green-600 bg-green-50" },
    { label: "أشهر مجانية", value: 0, icon: Crown, color: "text-yellow-600 bg-yellow-50" },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-secondary" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Hero Card */}
      <div className="bg-gradient-to-l from-primary-900 to-primary-800 rounded-2xl p-8 text-white relative overflow-hidden">
        <div className="absolute top-0 left-0 w-64 h-64 bg-secondary/10 rounded-full -translate-x-1/2 -translate-y-1/2" />
        <div className="absolute bottom-0 right-0 w-48 h-48 bg-secondary/10 rounded-full translate-x-1/4 translate-y-1/4" />
        <div className="relative">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-14 h-14 bg-secondary/20 rounded-2xl flex items-center justify-center">
              <Gift className="w-7 h-7 text-secondary" />
            </div>
            <div>
              <h2 className="text-2xl font-bold">انشر نظامك واكسب</h2>
              <p className="text-primary-200 text-sm">برنامج الإحالة من Dealix</p>
            </div>
          </div>
          <p className="text-primary-100 text-sm leading-relaxed max-w-xl">
            شارك رابط الحجز الخاص بك مع أصدقائك وزملائك. عند تسجيل عميل جديد عبر رابطك،
            تحصل على شهر مجاني لكل إحالة ناجحة. كل ما عليك هو المشاركة!
          </p>
        </div>
      </div>

      {/* Referral Link */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <Share2 className="w-5 h-5 text-secondary" /> رابط الإحالة الخاص بك
        </h3>
        <div className="flex gap-2 mb-4">
          <div className="flex-1 bg-gray-50 border border-gray-200 rounded-lg px-4 py-3 text-sm text-gray-700 font-mono truncate" dir="ltr">
            {referralLink}
          </div>
          <button
            onClick={() => copyToClipboard(referralLink)}
            className="px-4 py-3 bg-secondary hover:bg-secondary-600 text-white rounded-lg text-sm font-medium transition flex items-center gap-2 shrink-0"
          >
            {copiedLink ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
            {copiedLink ? "تم النسخ" : "نسخ"}
          </button>
        </div>
        <div className="flex gap-3">
          <button
            onClick={shareWhatsApp}
            className="flex-1 flex items-center justify-center gap-2 py-2.5 bg-green-50 text-green-700 hover:bg-green-100 rounded-lg text-sm font-medium transition"
          >
            <MessageSquare className="w-4 h-4" /> واتساب
          </button>
          <button
            onClick={shareTwitter}
            className="flex-1 flex items-center justify-center gap-2 py-2.5 bg-blue-50 text-blue-700 hover:bg-blue-100 rounded-lg text-sm font-medium transition"
          >
            <Sparkles className="w-4 h-4" /> تويتر / X
          </button>
          <button
            onClick={shareEmail}
            className="flex-1 flex items-center justify-center gap-2 py-2.5 bg-purple-50 text-purple-700 hover:bg-purple-100 rounded-lg text-sm font-medium transition"
          >
            <Mail className="w-4 h-4" /> إيميل
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <div key={stat.label} className="bg-white rounded-xl border border-gray-200 p-5">
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center mb-3 ${stat.color}`}>
              <stat.icon className="w-5 h-5" />
            </div>
            <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
            <p className="text-sm text-gray-500 mt-0.5">{stat.label}</p>
          </div>
        ))}
      </div>

      {/* Share Templates */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <MessageSquare className="w-5 h-5 text-secondary" /> رسائل جاهزة للمشاركة
        </h3>
        <div className="space-y-3">
          {shareTemplates.map((template, i) => (
            <div key={i} className="flex items-start gap-3 bg-gray-50 rounded-lg p-4">
              <div className="flex-1 text-sm text-gray-700 leading-relaxed">{template}</div>
              <button
                onClick={() => copyToClipboard(template, i)}
                className="shrink-0 p-2 text-gray-400 hover:text-secondary hover:bg-white rounded-lg transition"
              >
                {copiedTemplate === i ? <Check className="w-4 h-4 text-green-500" /> : <Copy className="w-4 h-4" />}
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* How it Works */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-6 flex items-center gap-2">
          <Zap className="w-5 h-5 text-secondary" /> كيف يعمل البرنامج؟
        </h3>
        <div className="grid sm:grid-cols-3 gap-6">
          {[
            { step: 1, icon: Share2, title: "شارك الرابط", desc: "انسخ رابط الإحالة وشاركه مع أصدقائك وزملائك عبر واتساب أو أي منصة" },
            { step: 2, icon: Users, title: "صديقك يسجل", desc: "عندما يسجل صديقك عبر رابطك ويبدأ استخدام النظام" },
            { step: 3, icon: Gift, title: "تكسب شهر مجاني", desc: "تحصل على شهر مجاني من اشتراكك عن كل إحالة ناجحة" },
          ].map((item) => (
            <div key={item.step} className="text-center">
              <div className="w-14 h-14 bg-secondary/10 text-secondary rounded-2xl flex items-center justify-center mx-auto mb-3">
                <item.icon className="w-6 h-6" />
              </div>
              <div className="w-8 h-8 bg-secondary text-white rounded-full flex items-center justify-center mx-auto mb-2 text-sm font-bold">
                {item.step}
              </div>
              <h4 className="font-bold text-gray-900 mb-1">{item.title}</h4>
              <p className="text-sm text-gray-500">{item.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Leaderboard Placeholder */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <Trophy className="w-5 h-5 text-yellow-500" /> المتصدرين
        </h3>
        <div className="text-center py-8 text-gray-400">
          <Star className="w-10 h-10 mx-auto mb-3 opacity-50" />
          <p className="text-sm font-medium">قريباً</p>
          <p className="text-xs mt-1">سيتم عرض أفضل المُحيلين هنا</p>
        </div>
      </div>
    </div>
  );
}
