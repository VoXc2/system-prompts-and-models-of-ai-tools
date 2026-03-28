"""
Dealix WhatsApp Human Engine — Messages that feel like a real person.
Makes AI messages sound like the business owner personally texting.
"""
import random
import re
from typing import Optional


# ─── Saudi Filler Phrases ────────────────────────────────────────────────────

SAUDI_FILLER_PHRASES = {
    "greeting": ["هلا والله", "أهلين", "هلا هلا", "مرحبا", "هلا فيك", "أهلاً وسهلاً"],
    "agreement": ["إي والله", "صحيح", "تمام", "أكيد", "بالضبط", "مية بالمية"],
    "transition": ["المهم", "بس حبيت أقولك", "الشاهد", "القصة باختصار", "يعني"],
    "closing": [
        "الله يوفقك", "ما قصرت", "نتواصل إن شاء الله",
        "تأمر على شي", "في أمان الله", "موفق يا رب",
    ],
    "excitement": ["والله حلو!", "ما شاء الله", "ممتاز", "رهيب!", "حياك الله"],
}

# ─── Message Templates ───────────────────────────────────────────────────────
# Each message_type maps to a list of variants.
# Each variant is a list of bubble templates with placeholders:
#   {greeting}, {lead_name}, {owner_name}, {company}, {value_prop}

MESSAGE_TEMPLATES = {
    "first_contact": [
        [
            "{greeting} {lead_name} 👋",
            "أنا {owner_name} من {company}",
            "{value_prop}",
            "وش رأيك نتكلم 5 دقايق؟",
        ],
        [
            "{greeting} {lead_name}",
            "معك {owner_name}، {company}",
            "شفت نشاطكم وحبيت أتواصل معكم",
            "{value_prop}",
            "يناسبك نتكلم اليوم؟ ⏰",
        ],
        [
            "{greeting} {lead_name}",
            "أنا {owner_name} 🙋‍♂️ من {company}",
            "{value_prop}",
            "لو عندك دقيقتين أشرحلك بالضبط كيف نقدر نفيدكم",
        ],
    ],
    "followup_1day": [
        [
            "هلا {lead_name} 👋",
            "أنا {owner_name} كلمتك أمس من {company}",
            "بس حبيت أتأكد وصلتك الرسالة",
            "عندك وقت نتكلم اليوم؟",
        ],
        [
            "السلام عليكم {lead_name}",
            "معك {owner_name} من {company}",
            "تواصلت معك أمس بخصوص {value_prop}",
            "هل تبي أرسلك تفاصيل أكثر؟",
        ],
    ],
    "followup_3days": [
        [
            "هلا {lead_name}",
            "أنا {owner_name} من {company}، تواصلنا قبل كم يوم",
            "حبيت أشوف إذا عندك أي أسئلة",
            "أنا موجود لأي استفسار 👍",
        ],
        [
            "{lead_name} هلا والله",
            "قلت أمر عليك.. أنا {owner_name} من {company}",
            "لو تبي نحدد موعد مكالمة سريعة أنا متفرغ هالأسبوع",
        ],
    ],
    "followup_7days": [
        [
            "هلا {lead_name} 👋",
            "عساك بخير.. أنا {owner_name} من {company}",
            "مو ضاغط عليك بس حبيت أتأكد إنك شفت عرضنا",
            "لو مهتم نتكلم، لو لا ما عليك أمر 🙏",
        ],
        [
            "السلام عليكم {lead_name}",
            "معك {owner_name} من {company}",
            "مرّ أسبوع وحبيت أرجع أتواصل معك",
            "عندنا عروض جديدة ممكن تهمك.. تبي التفاصيل؟",
        ],
    ],
    "special_offer": [
        [
            "{lead_name}! 🎉",
            "عندنا عرض خاص هالأسبوع",
            "{value_prop}",
            "العرض لفترة محدودة.. تبي التفاصيل؟",
        ],
        [
            "هلا {lead_name}",
            "أنا {owner_name} من {company}",
            "حبيت أخبرك عن عرض حصري عندنا 🔥",
            "{value_prop}",
            "تبي أحجزلك مكان؟",
        ],
    ],
    "appointment_reminder": [
        [
            "هلا {lead_name} 👋",
            "تذكير بموعدنا بكرة إن شاء الله",
            "أنا {owner_name} من {company}",
            "هل الموعد يناسبك ولا نغيره؟",
        ],
        [
            "{lead_name} السلام عليكم",
            "مجرد تذكير بموعدنا 📅",
            "إذا تبي تأجل أو تقدّم عادي خبرني",
            "نتواصل إن شاء الله",
        ],
    ],
    "after_meeting": [
        [
            "هلا {lead_name}",
            "شكراً على وقتك اليوم 🙏",
            "كان اجتماع ممتاز ما شاء الله",
            "مثل ما اتفقنا، بارسلك العرض خلال اليوم",
            "أي سؤال أنا موجود",
        ],
        [
            "{lead_name} أهلين",
            "حبيت أشكرك على الاجتماع",
            "إن شاء الله اللي ناقشناه واضح",
            "بارسلك الملخص مع العرض قريب",
            "ما قصرت 👍",
        ],
    ],
    "referral_ask": [
        [
            "هلا {lead_name} 👋",
            "أنا {owner_name} من {company}",
            "إن شاء الله الخدمة عاجبتكم",
            "لو عندك أحد تعرفه يحتاج نفس الشي، حبيت أسألك لو تقدر تدلنا عليه",
            "الله يعطيك العافية 🙏",
        ],
    ],
    "reactivation": [
        [
            "هلا {lead_name} 👋",
            "عساك بخير.. أنا {owner_name} من {company}",
            "فترة ما تواصلنا وحبيت أمر عليك",
            "عندنا تحديثات جديدة ممكن تهمك",
            "تبي أخبرك عنها؟",
        ],
        [
            "{lead_name} وحشتنا! 😄",
            "أنا {owner_name} من {company}",
            "صار عندنا أشياء جديدة من آخر مرة تكلمنا",
            "لو تبي نرجع نتواصل أنا موجود",
        ],
    ],
}

# ─── Formal -> Casual Saudi Replacements ─────────────────────────────────────

_FORMAL_TO_CASUAL = [
    ("عزيزي العميل", "{lead_name}"),
    ("عزيزي", "{lead_name}"),
    ("سيدي الفاضل", "{lead_name}"),
    ("سيدي", "{lead_name}"),
    ("نود إبلاغكم", "حبيت أقولك"),
    ("نود أن نعلمكم", "حبيت أخبرك"),
    ("يسرنا أن", "حبينا"),
    ("يسعدنا", "نحن سعيدين"),
    ("نحيطكم علماً", "حبيت تعرف"),
    ("نود إعلامكم", "حبيت أقولك"),
    ("نتقدم لكم بجزيل الشكر", "شكراً"),
    ("بالغ الاحترام", ""),
    ("مع فائق التحية", ""),
    ("تفضلوا بقبول", ""),
    ("أتقدم لكم", "أقولك"),
    ("نفيدكم", "أخبرك"),
    ("لا تتردد", "لا تستحي"),
    ("لا تتردد في التواصل", "كلمني على طول"),
    ("نأمل", "نتمنى"),
    ("إلى حضرتكم", "لك"),
    ("سعادتكم", ""),
    ("نحن في شركة", "أنا من"),
    ("يسرنا إبلاغكم", "حبيت أقولك"),
    ("نرجو منكم", "ياليت"),
    ("نتشرف", "يسعدني"),
    ("لذا نرجو", "فياليت"),
    ("بناءً على طلبكم", "مثل ما طلبت"),
    ("إشارة إلى", "بخصوص"),
    ("يرجى العلم", "خلني أقولك"),
    ("المرفق طيه", "مرفق لك"),
]

# ─── Casual Saudi Dialect Markers ────────────────────────────────────────────
# Phrases to sprinkle into messages to sound natural.

_DIALECT_MARKERS = [
    "وش رأيك",
    "إن شاء الله",
    "ما قصرت",
    "الله يعطيك العافية",
    "يا طويل العمر",
]


class WhatsAppHumanEngine:
    """
    Makes AI-generated messages indistinguishable from a real Saudi
    business owner texting on WhatsApp.

    Core philosophy: real people don't send one giant block of text.
    They send short bursts — like voice notes turned into text.
    """

    # ─── Public API ───────────────────────────────────────────────────

    def generate_human_message(
        self,
        lead_data: dict,
        message_type: str,
        owner_name: str,
        company: str,
        industry: str = "",
        time_of_day: Optional[int] = None,
    ) -> list[str]:
        """
        Generate a full WhatsApp message sequence that reads like a real
        person texting.  Returns a list of short message bubbles.

        Args:
            lead_data: Dict with at least 'name'. May include 'city',
                       'business', 'source', 'district', 'website',
                       'value_prop', etc.
            message_type: One of the MESSAGE_TEMPLATES keys
                          (first_contact, followup_1day, ...).
            owner_name: Business owner's first name.
            company: Company / brand name.
            industry: Optional industry context for smarter value props.
            time_of_day: Hour 0-23.  Used to pick the right greeting.

        Returns:
            List of short strings — each one is a WhatsApp bubble.

        Example:
            >>> engine = WhatsAppHumanEngine()
            >>> engine.generate_human_message(
            ...     lead_data={"name": "محمد العتيبي", "business": "عيادة أسنان"},
            ...     message_type="first_contact",
            ...     owner_name="أحمد",
            ...     company="عيادات النور",
            ...     time_of_day=10,
            ... )
            ['صباح الخير محمد 👋',
             'أنا أحمد من عيادات النور',
             'نشاطكم في عيادة أسنان ما شاء الله',
             'عندنا حل يناسبكم بالضبط',
             'وش رأيك نتكلم 5 دقايق؟']
        """
        lead_name = (
            lead_data.get("name", "").split()[0]
            if lead_data.get("name")
            else ""
        )
        greeting = self.get_greeting(time_of_day)
        value_prop = lead_data.get(
            "value_prop", "عندنا حل يناسبكم بالضبط"
        )

        # Pick a random template variant for this message type
        templates = MESSAGE_TEMPLATES.get(
            message_type, MESSAGE_TEMPLATES["first_contact"]
        )
        template_variant = random.choice(templates)

        bubbles: list[str] = []
        for bubble_tmpl in template_variant:
            filled = bubble_tmpl.format(
                greeting=greeting,
                lead_name=lead_name,
                owner_name=owner_name,
                company=company,
                value_prop=value_prop,
            )
            bubbles.append(filled.strip())

        # Add a personal touch if we have enough lead data
        if (
            lead_data.get("district")
            or lead_data.get("business")
            or lead_data.get("source")
            or lead_data.get("website")
        ):
            personal = self.add_personal_touch("", lead_data)
            if personal:
                # Insert the personal touch after the intro (position 2)
                insert_pos = min(2, len(bubbles))
                bubbles.insert(insert_pos, personal)

        return bubbles

    def get_greeting(self, time_of_day: Optional[int] = None) -> str:
        """
        Return an appropriate Saudi greeting for the time of day.

        Ranges:
            Morning   (6-12):  صباح الخير / صباح النور
            Afternoon (12-18): مساء الخير / هلا والله
            Evening   (18-24): مساء النور / هلا
            Late night (0-6):  السلام عليكم (formal, respectful)

        Args:
            time_of_day: Hour 0-23, or None for a safe default.
        """
        if time_of_day is None:
            return random.choice(["هلا", "السلام عليكم"])

        if 0 <= time_of_day < 6:
            # Late night — keep it formal / respectful
            return "السلام عليكم"
        elif 6 <= time_of_day < 12:
            return random.choice(
                ["صباح الخير", "صباح النور", "صباح الخير عليكم"]
            )
        elif 12 <= time_of_day < 18:
            return random.choice(["مساء الخير", "هلا والله", "أهلين"])
        else:
            # 18-24
            return random.choice(["مساء النور", "هلا", "مساء الخير"])

    def humanize_message(
        self,
        ai_message: str,
        owner_name: str = "",
        company: str = "",
        lead_name: str = "",
    ) -> str:
        """
        Take a potentially formal / robotic AI message and re-write it
        to sound like a real Saudi business owner texting.

        Transformations applied:
        1. Replace formal Arabic phrases with Saudi casual equivalents
        2. Add Saudi dialect markers (وش رأيك، إن شاء الله، ما قصرت)
        3. Remove excessive formality
        4. Limit emojis to 1-2 contextual ones
        5. Inject first-person ownership voice: "أنا [owner_name] من [company]"
        6. Keep it short and punchy

        Args:
            ai_message: The AI-generated text to humanize.
            owner_name: Business owner's first name.
            company: Company / brand name.
            lead_name: Lead's first name (replaces formal titles).
        """
        text = ai_message

        # 1. Replace formal phrases with casual Saudi equivalents
        for formal, casual in _FORMAL_TO_CASUAL:
            casual_filled = (
                casual.format(lead_name=lead_name)
                if "{lead_name}" in casual
                else casual
            )
            text = text.replace(formal, casual_filled)

        # 2. Add first-person voice if the message doesn't already have it
        if owner_name and company and f"أنا {owner_name}" not in text:
            # Only prepend if the message is long enough to warrant it
            if len(text) > 60:
                text = f"أنا {owner_name} من {company}. " + text

        # 3. Limit emojis — keep at most 2
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+",
            flags=re.UNICODE,
        )
        emojis_found = emoji_pattern.findall(text)
        if len(emojis_found) > 2:
            # Remove all emojis then re-add up to 2 at the end
            kept = emojis_found[:2]
            text = emoji_pattern.sub("", text).strip()
            text = text + " " + " ".join(kept)

        # 4. Strip leftover double spaces / trailing formalities
        text = re.sub(r"\s{2,}", " ", text).strip()
        text = text.rstrip(".")

        return text

    def split_into_bubbles(
        self, message: str, max_chars: int = 200
    ) -> list[str]:
        """
        Split a long message into multiple WhatsApp-style bubbles.
        Nobody sends a wall of text on WhatsApp — real people break
        messages into short chunks.

        Strategy:
        1. Split on newlines first (natural breaks).
        2. If a segment is still too long, split on sentence-ending
           punctuation (. ، ؟ !).
        3. Hard-split as a last resort.

        Args:
            message: The full message text.
            max_chars: Maximum characters per bubble (default 200).

        Returns:
            List of short message strings.
        """
        # First try splitting on newlines (natural breaks)
        lines = [ln.strip() for ln in message.split("\n") if ln.strip()]

        bubbles: list[str] = []
        current = ""

        for line in lines:
            # If the line alone is already short enough, it can be a bubble
            if len(line) <= max_chars and not current:
                bubbles.append(line)
                continue

            # See if we can append to the current buffer
            candidate = f"{current} {line}".strip() if current else line
            if len(candidate) <= max_chars:
                current = candidate
            else:
                # Flush current and start fresh
                if current:
                    bubbles.append(current)
                # If this single line is too long, break on sentence
                # boundaries
                if len(line) > max_chars:
                    parts = re.split(r"(?<=[.،؟!])\s+", line)
                    for part in parts:
                        if len(part) <= max_chars:
                            bubbles.append(part)
                        else:
                            # Hard split as last resort
                            for i in range(0, len(part), max_chars):
                                bubbles.append(part[i : i + max_chars])
                    current = ""
                else:
                    current = line

        if current:
            bubbles.append(current)

        # Ensure we have at least 1 bubble
        return bubbles if bubbles else [message[:max_chars]]

    def add_personal_touch(self, message: str, lead_data: dict) -> str:
        """
        Add a contextual, personal reference based on what we know about
        the lead.  Makes the message feel like you actually looked them up.

        Possible touches:
        - District/neighbourhood: "شفت إنكم في حي النرجس"
        - Business type: "عيادتكم تقدم خدمات ممتازة"
        - Source: "وصلني رقمك من..."
        - Website: "شفت موقعكم وعجبني"

        Args:
            message: Existing message to append to (can be empty).
            lead_data: Lead dict with optional keys: district, business,
                       source, website.

        Returns:
            The personal touch string (can be used as its own bubble or
            appended to an existing message).
        """
        touches: list[str] = []

        district = lead_data.get("district", "")
        if district:
            touches.append(f"شفت إنكم في {district}")

        business = lead_data.get("business", "")
        if business:
            touches.append(f"نشاطكم في {business} ما شاء الله")

        source = lead_data.get("source", "")
        if source and source not in ("واتساب", "whatsapp", "manual"):
            touches.append(f"وصلني رقمك من {source}")

        website = lead_data.get("website", "")
        if website:
            touches.append("شفت موقعكم وعجبني")

        if not touches:
            return ""

        # Pick one at random so we're not dumping everything at once
        personal = random.choice(touches)

        if message:
            return f"{message} — {personal}"
        return personal


# ─── Module-level convenience instance ────────────────────────────────────────

whatsapp_human = WhatsAppHumanEngine()
