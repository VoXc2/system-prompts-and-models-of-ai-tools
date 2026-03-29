# Widget SDK Architecture

## Widget Types

| Widget | Purpose | Embed Method |
|--------|---------|-------------|
| **Lead Capture Form** | Collect name, phone, email + custom fields | JS snippet / iframe |
| **Qualification Form** | Multi-step qualifying questions | JS snippet / iframe |
| **Demo Request** | Book a demo with form + calendar | JS snippet / iframe |
| **Floating CTA** | Bottom-right button that opens form | JS snippet |
| **Booking Widget** | Calendar-based appointment booking | JS snippet / iframe |
| **ROI Calculator** | Interactive calculator → lead capture | JS snippet / iframe |

## Embed Methods

### 1. JavaScript Snippet (Recommended)
```html
<script src="https://cdn.dealix.sa/widget.js"></script>
<script>
  Dealix.init({
    tenantId: "tenant-slug",
    formId: "form-uuid",
    theme: "light",      // light | dark | auto
    locale: "ar",        // ar | en
    position: "bottom-right",  // for floating CTA
    primaryColor: "#0B3B66",
    onSubmit: function(data) {
      // optional callback
      console.log("Lead captured:", data.lead_id);
    }
  });
</script>
```

### 2. Iframe Embed
```html
<iframe
  src="https://forms.dealix.sa/embed/{tenant-slug}/{form-id}"
  width="100%"
  height="500"
  frameborder="0"
  style="border: none;"
></iframe>
```

## Widget Configuration (Stored in Tenant)

```json
{
  "form_id": "uuid",
  "tenant_id": "uuid",
  "type": "lead_capture",
  "name": "نموذج التواصل الرئيسي",
  "fields": [
    {"name": "name", "label": "الاسم", "label_en": "Name", "type": "text", "required": true},
    {"name": "phone", "label": "رقم الجوال", "label_en": "Phone", "type": "phone", "required": true},
    {"name": "email", "label": "البريد", "label_en": "Email", "type": "email", "required": false},
    {"name": "company_size", "label": "حجم الشركة", "label_en": "Company Size", "type": "select",
     "options": ["1-10", "11-50", "51-200", "200+"]}
  ],
  "branding": {
    "logo_url": "https://...",
    "primary_color": "#0B3B66",
    "secondary_color": "#0FAF9A",
    "font_family": "IBM Plex Sans Arabic",
    "hide_dealix_badge": false  // true for enterprise/white-label
  },
  "behavior": {
    "redirect_url": null,
    "success_message": "شكراً! سنتواصل معك قريباً",
    "auto_sequence": "uuid-of-sequence",  // auto-enroll in sequence
    "notify_whatsapp": true,
    "notify_email": true
  },
  "tracking": {
    "capture_utm": true,
    "capture_referrer": true,
    "capture_device": true,
    "google_analytics_id": null,
    "facebook_pixel_id": null
  }
}
```

## White-Label Widget Theming

For white-label partners, widgets use the partner's branding:
- Partner logo replaces Dealix logo
- Partner colors applied to form
- Partner domain used for embed URLs
- "Powered by Dealix" badge removable on enterprise plans

## SDK Architecture (Future — packages/sdk-js)

```
packages/sdk-js/
├── src/
│   ├── core/
│   │   ├── init.ts          # Dealix.init()
│   │   ├── api.ts           # API client for public endpoints
│   │   └── tracking.ts      # UTM, referrer, device detection
│   ├── widgets/
│   │   ├── form.ts          # Lead capture form renderer
│   │   ├── booking.ts       # Booking calendar widget
│   │   ├── cta.ts           # Floating CTA button
│   │   └── calculator.ts    # ROI calculator
│   ├── themes/
│   │   ├── light.ts
│   │   ├── dark.ts
│   │   └── custom.ts
│   └── index.ts
├── dist/                     # Built bundle (widget.js)
├── package.json
└── tsconfig.json
```

## Build Output
- Single `widget.js` file (< 50KB gzipped)
- No external dependencies
- Shadow DOM for style isolation
- CSP-compatible (no inline styles if possible)
