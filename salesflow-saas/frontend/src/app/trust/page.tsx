import Link from "next/link";
import { Shield, CheckCircle, Calendar, Lock, Eye, UserCheck, Ban } from "lucide-react";

export const metadata = {
  title: "Dealix — الأمان والثقة",
  description: "كيف Dealix يحمي بياناتك ويلتزم بسياسات المنصات وأنظمة حماية البيانات.",
};

const CALENDLY = "https://calendly.com/sami-assiri11/dealix-demo";

const principles = [
  {
    icon: UserCheck,
    title: "إرسال بموافقة بشرية",
    desc: "AI يجهّز ويصيغ ويقترح. الإنسان يوافق ويرسل. لا رسائل تلقائية بدون موافقة.",
  },
  {
    icon: Ban,
    title: "لا Spam ولا Scraping",
    desc: "لا نكشط LinkedIn. لا نرسل WhatsApp عشوائي. لا mass DMs. لا fake engagement.",
  },
  {
    icon: Shield,
    title: "احترام سياسات المنصات",
    desc: "نلتزم بقواعد LinkedIn وX وInstagram وWhatsApp. يدوي + human-approved فقط.",
  },
  {
    icon: Eye,
    title: "شفافية كاملة",
    desc: "كل رسالة فيها هوية واضحة + سبب التواصل + خيار إيقاف.",
  },
  {
    icon: Lock,
    title: "حماية البيانات (PDPL)",
    desc: "نحترم نظام حماية البيانات الشخصية السعودي. بياناتك ما تُشارك مع أطراف ثالثة.",
  },
  {
    icon: CheckCircle,
    title: "ادعاءات مثبتة فقط",
    desc: "لا نقول 'مضمون' ولا 'أفضل' ولا '100%'. نقول 'مصمم لـ' و'يساعد في' و'pilot لقياس النتائج'.",
  },
];

const platformRules = [
  { platform: "LinkedIn", rule: "لا bots / لا scraping / لا automated DMs / يدوي فقط" },
  { platform: "X / Twitter", rule: "لا automated mass mentions / replies / محتوى + ردود يدوية" },
  { platform: "Instagram", rule: "لا mass cold DMs / inbound + warm فقط" },
  { platform: "WhatsApp", rule: "warm + opted-in فقط / opt-out إلزامي / stop فوري" },
  { platform: "Email", rule: "targeted + هوية واضحة + opt-out / max 3 في sequence" },
];

export default function TrustPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-slate-100">
      {/* Hero */}
      <section className="mx-auto max-w-4xl px-6 pb-12 pt-20 text-center">
        <Shield className="mx-auto h-12 w-12 text-emerald-400" />
        <h1 className="mt-6 text-4xl font-extrabold lg:text-5xl">
          الأمان{" "}
          <span className="bg-gradient-to-l from-emerald-400 to-teal-500 bg-clip-text text-transparent">
            والثقة
          </span>
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-300">
          Dealix مبني على مبدأ: الذكاء يجهّز، الإنسان يوافق، النظام يتتبّع. لا spam. لا scraping. لا ادعاءات كاذبة.
        </p>
      </section>

      {/* Principles */}
      <section className="border-y border-white/10 bg-slate-900/50 py-16">
        <div className="mx-auto max-w-5xl px-6">
          <h2 className="text-center text-2xl font-bold">6 مبادئ أساسية</h2>
          <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {principles.map((p) => (
              <div key={p.title} className="rounded-2xl border border-white/10 bg-white/5 p-6">
                <p.icon className="h-8 w-8 text-emerald-400" />
                <h3 className="mt-4 font-semibold">{p.title}</h3>
                <p className="mt-2 text-sm text-slate-400">{p.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Platform Rules */}
      <section className="py-16">
        <div className="mx-auto max-w-3xl px-6">
          <h2 className="text-center text-2xl font-bold">قواعد كل منصة</h2>
          <div className="mt-8 space-y-3">
            {platformRules.map((r) => (
              <div key={r.platform} className="flex items-start gap-4 rounded-xl border border-white/10 bg-white/5 p-4">
                <span className="shrink-0 rounded-lg bg-emerald-500/10 px-3 py-1 text-sm font-bold text-emerald-400">
                  {r.platform}
                </span>
                <span className="text-sm text-slate-300">{r.rule}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Opt-out */}
      <section className="border-y border-white/10 bg-slate-900/50 py-12">
        <div className="mx-auto max-w-2xl px-6 text-center">
          <h2 className="text-xl font-bold">حق الإيقاف</h2>
          <p className="mt-4 text-slate-300">
            كل رسالة أولى من Dealix تنتهي بـ:
          </p>
          <div className="mt-4 rounded-xl border border-white/10 bg-white/5 p-4 text-slate-300">
            &ldquo;إذا ما يناسبكم هالنوع من الرسائل، ردوا <strong className="text-amber-400">&ldquo;إيقاف&rdquo;</strong> وما بنتواصل مرة ثانية.&rdquo;
          </div>
          <p className="mt-4 text-sm text-slate-500">
            لو أحد قال &ldquo;إيقاف&rdquo; أو &ldquo;لا&rdquo; أو &ldquo;stop&rdquo; — نوقف فوراً. بدون استثناء.
          </p>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16">
        <div className="mx-auto max-w-2xl px-6 text-center">
          <p className="text-lg text-slate-300">
            أي سؤال عن الأمان؟ تواصل مع المؤسس مباشرة:
          </p>
          <a href="tel:+966597788539" className="mt-3 inline-block text-2xl font-bold text-amber-400" dir="ltr">0597788539</a>
          <p className="mt-1 text-sm text-slate-500">سامي العسيري — مؤسس Dealix</p>
          <a
            href={CALENDLY}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-6 inline-flex items-center gap-2 rounded-xl bg-emerald-500 px-8 py-3.5 text-base font-bold text-white transition hover:bg-emerald-400"
          >
            <Calendar className="h-5 w-5" />
            احجز ديمو آمن
          </a>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/10 py-8">
        <div className="mx-auto flex max-w-4xl flex-wrap items-center justify-center gap-6 px-6 text-sm text-slate-500">
          <Link href="/" className="hover:text-teal-400">الرئيسية</Link>
          <Link href="/marketers" className="hover:text-teal-400">المسوّقين</Link>
          <Link href="/partners" className="hover:text-teal-400">الشراكات</Link>
          <Link href="/pricing" className="hover:text-teal-400">الباقات</Link>
          <Link href="/use-cases" className="hover:text-teal-400">حالات الاستخدام</Link>
          <Link href="/privacy" className="hover:text-teal-400">الخصوصية</Link>
          <span>© {new Date().getFullYear()} Dealix</span>
        </div>
      </footer>
    </div>
  );
}
