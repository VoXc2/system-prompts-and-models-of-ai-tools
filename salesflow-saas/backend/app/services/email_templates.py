"""
Dealix Email Templates - Professional Arabic email templates.
Covers the full customer lifecycle from welcome to reactivation.
"""
from typing import Optional
from app.config import get_settings

settings = get_settings()

# Base HTML wrapper for all emails
EMAIL_BASE = """<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
body {{ font-family: 'IBM Plex Sans Arabic', 'Segoe UI', Tahoma, sans-serif; background: #F8FAFC; margin: 0; padding: 20px; direction: rtl; }}
.container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
.header {{ background: linear-gradient(135deg, #0B3B66, #0F172A); padding: 30px; text-align: center; }}
.header img {{ height: 40px; }}
.header h2 {{ color: white; margin: 10px 0 0; font-size: 18px; }}
.body {{ padding: 30px; color: #374151; line-height: 1.8; font-size: 15px; }}
.body h1 {{ color: #0B3B66; font-size: 22px; margin-bottom: 15px; }}
.body p {{ margin-bottom: 15px; }}
.cta {{ display: inline-block; background: #F97316; color: white; padding: 14px 32px; border-radius: 12px; text-decoration: none; font-weight: bold; font-size: 16px; margin: 10px 0; }}
.cta:hover {{ background: #E05E07; }}
.highlight {{ background: #F0FDF4; border-right: 4px solid #0FAF9A; padding: 15px; border-radius: 8px; margin: 15px 0; }}
.footer {{ background: #F8FAFC; padding: 20px 30px; text-align: center; font-size: 12px; color: #9CA3AF; border-top: 1px solid #E5E7EB; }}
.footer a {{ color: #0B3B66; text-decoration: none; }}
ul {{ padding-right: 20px; }}
li {{ margin-bottom: 8px; }}
</style>
</head>
<body>
<div class="container">
<div class="header">
<h2 style="color: #0FAF9A; font-size: 24px; font-weight: bold;">Dealix</h2>
<p style="color: rgba(255,255,255,0.7); font-size: 12px; margin: 5px 0 0;">نظام ذكاء تشغيلي للمبيعات</p>
</div>
<div class="body">
{content}
</div>
<div class="footer">
<p>Dealix - خلّي البيع يمشي بنظام</p>
<p><a href="{{{{unsubscribe_url}}}}">إلغاء الاشتراك</a> | <a href="{{{{privacy_url}}}}">سياسة الخصوصية</a></p>
<p>&copy; 2025 Dealix. جميع الحقوق محفوظة</p>
</div>
</div>
</body>
</html>"""


def _wrap(content: str) -> str:
    return EMAIL_BASE.format(content=content)


class EmailTemplates:
    """All Dealix email templates."""

    @staticmethod
    def welcome(name: str, company: str = "") -> dict:
        content = f"""
<h1>أهلاً {name}! مرحباً في Dealix</h1>
<p>شكراً لانضمامك. حسابك جاهز وتقدر تبدأ الحين.</p>
<div class="highlight">
<strong>خطواتك الأولى:</strong>
<ul>
<li>اربط حسابك بواتساب بزنس</li>
<li>أضف أول عميل محتمل</li>
<li>فعّل المتابعة التلقائية</li>
<li>استكشف لوحة التقارير</li>
</ul>
</div>
<p style="text-align: center;">
<a href="{{{{dashboard_url}}}}" class="cta">ادخل لوحة التحكم</a>
</p>
<p>تجربتك المجانية تنتهي بعد 14 يوم. استفد منها!</p>
<p>إذا تحتاج مساعدة، فريقنا جاهز لك.</p>
"""
        return {"subject": f"مرحباً {name}! حسابك في Dealix جاهز", "html": _wrap(content)}

    @staticmethod
    def demo_confirmation(name: str, date: str, time: str) -> dict:
        content = f"""
<h1>تم تأكيد موعد العرض التوضيحي</h1>
<p>مرحباً {name}،</p>
<p>موعدك محجوز وفريقنا جاهز يعرض لك النظام.</p>
<div class="highlight">
<strong>تفاصيل الموعد:</strong><br>
📅 التاريخ: {date}<br>
🕐 الوقت: {time}<br>
⏱ المدة: 20 دقيقة<br>
📍 اجتماع فيديو (الرابط يوصلك قبل الموعد)
</div>
<p><strong>استعد للعرض:</strong></p>
<ul>
<li>جهّز أسئلتك عن النظام</li>
<li>فكّر في أكبر تحدي بيعي عندك</li>
<li>كم شخص في فريق المبيعات؟</li>
</ul>
<p>إذا تحتاج تغيير الموعد، رد على هذا الإيميل.</p>
"""
        return {"subject": f"تأكيد موعد العرض - {date}", "html": _wrap(content)}

    @staticmethod
    def proposal_sent(name: str, proposal_title: str, proposal_url: str) -> dict:
        content = f"""
<h1>عرض سعر جديد لك</h1>
<p>مرحباً {name}،</p>
<p>أرسلنا لك عرض سعر: <strong>{proposal_title}</strong></p>
<p style="text-align: center;">
<a href="{proposal_url}" class="cta">اطلع على العرض</a>
</p>
<p>العرض صالح لمدة 14 يوم. إذا عندك أي سؤال، لا تتردد.</p>
"""
        return {"subject": f"عرض سعر: {proposal_title}", "html": _wrap(content)}

    @staticmethod
    def followup_reminder_1(name: str) -> dict:
        content = f"""
<h1>تذكير ودي</h1>
<p>مرحباً {name}،</p>
<p>لاحظنا إنك سجلت معنا لكن ما بدأت تستخدم النظام بعد.</p>
<p>نبي نساعدك تبدأ! تقدر:</p>
<ul>
<li>تحجز جلسة تعريفية مجانية مع فريقنا</li>
<li>تشوف الفيديوهات التعليمية</li>
<li>تبدأ بإضافة أول 5 عملاء</li>
</ul>
<p style="text-align: center;">
<a href="{{{{dashboard_url}}}}" class="cta">ابدأ الآن</a>
</p>
"""
        return {"subject": f"{name}، جاهز تبدأ مع Dealix؟", "html": _wrap(content)}

    @staticmethod
    def followup_reminder_2(name: str) -> dict:
        content = f"""
<h1>فاضل لك كم يوم على نهاية التجربة</h1>
<p>مرحباً {name}،</p>
<p>تجربتك المجانية قاربت تنتهي. ما نبيك تفوّت الفرصة!</p>
<div class="highlight">
<strong>اللي تفوّتك إذا ما كملت:</strong>
<ul>
<li>متابعة تلقائية للعملاء 24/7</li>
<li>تنظيم كامل لصفقاتك</li>
<li>تقارير أداء فورية</li>
</ul>
</div>
<p style="text-align: center;">
<a href="{{{{pricing_url}}}}" class="cta">اختر خطتك الآن</a>
</p>
"""
        return {"subject": "تجربتك المجانية قاربت تنتهي!", "html": _wrap(content)}

    @staticmethod
    def no_show_followup(name: str, date: str) -> dict:
        content = f"""
<h1>فاتك الموعد؟ لا مشكلة!</h1>
<p>مرحباً {name}،</p>
<p>كان عندنا موعد يوم {date} لكن ما قدرت تحضر. نفهم إن الأمور تكون مشغولة!</p>
<p>نبي نساعدك نختار وقت ثاني يناسبك.</p>
<p style="text-align: center;">
<a href="{{{{booking_url}}}}" class="cta">احجز موعد جديد</a>
</p>
"""
        return {"subject": "فاتك الموعد؟ خلنا نحجز وقت ثاني", "html": _wrap(content)}

    @staticmethod
    def trial_activated(name: str, end_date: str) -> dict:
        content = f"""
<h1>تم تفعيل تجربتك المجانية!</h1>
<p>مرحباً {name}،</p>
<p>حسابك فعّال الآن بكامل المميزات حتى <strong>{end_date}</strong>.</p>
<div class="highlight">
<strong>نصيحتنا:</strong> استخدم أول 3 أيام لإعداد النظام (ربط الواتساب + إضافة فريقك + استيراد عملاءك). بعدها المتابعة التلقائية تبدأ تشتغل لك.
</div>
<p style="text-align: center;">
<a href="{{{{dashboard_url}}}}" class="cta">ابدأ الإعداد</a>
</p>
"""
        return {"subject": "تجربتك المجانية بدأت! 14 يوم كاملة", "html": _wrap(content)}

    @staticmethod
    def trial_ending(name: str, days_left: int) -> dict:
        content = f"""
<h1>باقي {days_left} يوم على نهاية التجربة</h1>
<p>مرحباً {name}،</p>
<p>تجربتك المجانية تنتهي بعد <strong>{days_left} أيام</strong>.</p>
<p>إذا عجبك النظام، اختر خطة واستمر بدون انقطاع. بياناتك وإعداداتك كلها تبقى كما هي.</p>
<p style="text-align: center;">
<a href="{{{{pricing_url}}}}" class="cta">اختر خطتك</a>
</p>
<p>إذا تحتاج وقت إضافي أو عندك أسئلة، رد على هذا الإيميل.</p>
"""
        return {"subject": f"باقي {days_left} أيام - اختر خطتك", "html": _wrap(content)}

    @staticmethod
    def payment_receipt(name: str, plan: str, amount: str, date: str, invoice_url: str = "") -> dict:
        content = f"""
<h1>تم استلام الدفعة بنجاح</h1>
<p>مرحباً {name}،</p>
<p>شكراً لثقتك! تم تأكيد اشتراكك.</p>
<div class="highlight">
<strong>تفاصيل الفاتورة:</strong><br>
الخطة: {plan}<br>
المبلغ: {amount} ر.س (شامل الضريبة)<br>
التاريخ: {date}
</div>
{"<p><a href='" + invoice_url + "'>تحميل الفاتورة</a></p>" if invoice_url else ""}
<p>اشتراكك يتجدد تلقائياً. تقدر تدير اشتراكك من إعدادات الحساب.</p>
"""
        return {"subject": f"فاتورة Dealix - {plan}", "html": _wrap(content)}

    @staticmethod
    def contract_ready(name: str, contract_title: str, contract_url: str) -> dict:
        content = f"""
<h1>العقد جاهز للتوقيع</h1>
<p>مرحباً {name}،</p>
<p>العقد <strong>{contract_title}</strong> جاهز ويحتاج توقيعك.</p>
<p style="text-align: center;">
<a href="{contract_url}" class="cta">اطلع ووقّع العقد</a>
</p>
<p>العقد صالح لمدة 7 أيام. إذا عندك أي ملاحظة، تواصل معنا.</p>
"""
        return {"subject": f"العقد جاهز: {contract_title}", "html": _wrap(content)}

    @staticmethod
    def reactivation(name: str, offer: str = "خصم 20%") -> dict:
        content = f"""
<h1>وحشتنا يا {name}!</h1>
<p>لاحظنا إنك ما استخدمت Dealix من فترة.</p>
<p>عندنا عرض خاص لك:</p>
<div class="highlight" style="text-align: center;">
<span style="font-size: 28px; font-weight: bold; color: #0B3B66;">{offer}</span><br>
<span style="color: #6B7280;">على أي خطة لمدة 3 شهور</span>
</div>
<p style="text-align: center;">
<a href="{{{{pricing_url}}}}" class="cta">استفد من العرض</a>
</p>
<p>العرض صالح لمدة 7 أيام فقط.</p>
"""
        return {"subject": f"{name}، عندنا عرض خاص لك!", "html": _wrap(content)}
