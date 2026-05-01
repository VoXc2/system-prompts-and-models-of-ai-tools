/* =========================================================
   Dealix Landing v2 — interactions, analytics, form
   ========================================================= */
(function () {
  'use strict';

  // ---- i18n-ready dictionary (strings factored out for later EN) ----
  const I18N = {
    ar: {
      themeLight: 'التبديل إلى الوضع الفاتح',
      themeDark:  'التبديل إلى الوضع الداكن',
      formSending: 'جاري الإرسال…',
      formSuccess: 'تم — سنتواصل خلال ٤ ساعات (كما تنص اتفاقيتنا الداخلية)',
      formErrorGeneric: 'تعذّر الإرسال. جرّب مرة أخرى أو تواصل مباشرة عبر البريد: ',
      formErrorEmail:   'البريد الإلكتروني غير صالح.',
      formErrorPhone:   'رقم الجوال يجب أن يكون بصيغة سعودية (+966 5XXXXXXXX).',
      formErrorConsent: 'الرجاء الموافقة على معالجة البيانات للمتابعة.',
      formErrorReq:     'الرجاء تعبئة جميع الحقول المطلوبة.',
      retryIn: 'متاح بعد'
    }
  };
  const L = I18N.ar;

  // ---- Config ----
  // Backend URL — set to Railway production URL once deployed.
  // Example: 'https://dealix-api.up.railway.app/api/v1/public/demo-request'
  // Falls back to relative path for local dev / same-origin deployments.
  const API_BASE = (window.DEALIX_API_BASE || '').replace(/\/$/, '');
  const CONFIG = {
    apiEndpoint: (API_BASE || '') + '/api/v1/public/demo-request',
    fallbackEmail: 'sami.assiri11@gmail.com',
    posthogKey: '__POSTHOG_KEY__', // replaced via env or kept as placeholder
    posthogHost: 'https://app.posthog.com',
    gaId: '__GA4_ID__',
    rateLimitSeconds: 60
  };

  // ====================================================================
  // THEME TOGGLE
  // ====================================================================
  const root = document.documentElement;
  const toggle = document.querySelector('[data-theme-toggle]');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  // In-memory theme state (preview iframe blocks storage APIs)
  let theme = (window.__dlxTheme) || (prefersDark ? 'dark' : 'light');
  window.__dlxTheme = theme;
  root.setAttribute('data-theme', theme);

  const sunSvg = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>';
  const moonSvg = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';

  function renderToggle() {
    if (!toggle) return;
    toggle.innerHTML = theme === 'dark' ? sunSvg : moonSvg;
    toggle.setAttribute('aria-label', theme === 'dark' ? L.themeLight : L.themeDark);
  }
  renderToggle();
  if (toggle) {
    toggle.addEventListener('click', function () {
      theme = theme === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', theme);
      window.__dlxTheme = theme;
      renderToggle();
      track('theme_toggle', { theme });
    });
  }

  // ====================================================================
  // MOBILE MENU
  // ====================================================================
  const burger = document.querySelector('[data-menu-toggle]');
  const links = document.querySelector('.nav__links');
  if (burger && links) {
    burger.addEventListener('click', function () {
      const open = links.classList.toggle('is-open');
      burger.setAttribute('aria-expanded', String(open));
    });
    links.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () {
        links.classList.remove('is-open');
        burger.setAttribute('aria-expanded', 'false');
      });
    });
  }

  // ====================================================================
  // TABS
  // ====================================================================
  const tabs = document.querySelectorAll('.tab');
  const panels = document.querySelectorAll('.tab-panel');
  tabs.forEach(function (tab) {
    tab.addEventListener('click', function () {
      const key = tab.getAttribute('data-tab');
      tabs.forEach(function (t) {
        t.classList.toggle('is-active', t === tab);
        t.setAttribute('aria-selected', t === tab ? 'true' : 'false');
      });
      panels.forEach(function (p) {
        const match = p.getAttribute('data-panel') === key;
        p.classList.toggle('is-active', match);
        if (match) p.removeAttribute('hidden'); else p.setAttribute('hidden', '');
      });
      track('sector_tab_view', { sector: key });
    });
  });

  // ====================================================================
  // INTERSECTION OBSERVER — reveal + section_view
  // ====================================================================
  if ('IntersectionObserver' in window) {
    // Reveal animation
    const revealEls = document.querySelectorAll('.pillar, .icp, .plan, .trust-card, .step, .faq__item, .proof__card');
    revealEls.forEach(function (el) {
      el.style.opacity = '0';
      el.style.transform = 'translateY(16px)';
      el.style.transition = 'opacity 500ms ease, transform 500ms cubic-bezier(0.16, 1, 0.3, 1)';
    });
    const io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });
    revealEls.forEach(function (el) { io.observe(el); });

    // Section view tracker
    const sections = document.querySelectorAll('section[id]');
    const sectionIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting && !entry.target.dataset.seen) {
          entry.target.dataset.seen = '1';
          track('section_view', { section: entry.target.id });
        }
      });
    }, { threshold: 0.4 });
    sections.forEach(function (s) { sectionIO.observe(s); });
  }

  // ====================================================================
  // CTA CLICK TRACKING
  // ====================================================================
  document.querySelectorAll('[data-analytics]').forEach(function (el) {
    el.addEventListener('click', function () {
      track('cta_click', { id: el.getAttribute('data-analytics'), href: el.getAttribute('href') || '' });
    });
  });

  // ====================================================================
  // FORM SUBMISSION
  // ====================================================================
  const form = document.getElementById('demoForm');
  if (form) {
    const submitBtn = document.getElementById('submitBtn');
    const response = document.getElementById('formResponse');
    let rateLimitTimer = null;

    form.addEventListener('submit', async function (e) {
      e.preventDefault();

      // Honeypot
      const hp = form.querySelector('input[name="website"]');
      if (hp && hp.value.trim() !== '') {
        // silent drop
        return;
      }

      // Reset aria-invalid
      form.querySelectorAll('[aria-invalid]').forEach(function (el) { el.removeAttribute('aria-invalid'); });

      const data = {
        name: form.name.value.trim(),
        company: form.company.value.trim(),
        sector: form.sector.value,
        size: form.size.value,
        phone: form.phone.value.trim(),
        email: form.email.value.trim(),
        message: form.message.value.trim(),
        source: 'landing',
        ref: document.referrer || '',
        consent: !!form.consent.checked,
        ts: new Date().toISOString()
      };

      // Validation
      const errors = validate(data, form);
      if (errors.length) {
        setResponse(errors[0], 'error');
        return;
      }

      // Submit
      setLoading(true);
      track('form_submit', { sector: data.sector, size: data.size });

      try {
        const res = await fetch(CONFIG.apiEndpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        });

        if (!res.ok) throw new Error('http_' + res.status);

        const json = await res.json().catch(function () { return {}; });

        // Success
        setResponse(L.formSuccess, 'success');
        track('form_success', { sector: data.sector });
        form.reset();
        startRateLimit();

        // Redirect to Calendly booking after short delay
        if (json && json.calendly_url) {
          setTimeout(function () {
            window.location.href = json.calendly_url;
          }, 1500);
        }
      } catch (err) {
        // Failure → graceful + mailto fallback
        const mailto = buildMailto(data);
        setResponse(
          L.formErrorGeneric +
          '<a href="mailto:' + CONFIG.fallbackEmail + '">' + CONFIG.fallbackEmail + '</a> ' +
          ' · <a href="' + mailto + '">إرسال عبر البريد مباشرة</a>',
          'error',
          true
        );
        track('form_error', { error: String(err) });
        setLoading(false);
      }
    });

    function setLoading(on) {
      if (!submitBtn) return;
      submitBtn.classList.toggle('is-loading', on);
      submitBtn.disabled = on;
    }

    function setResponse(html, kind, asHtml) {
      if (!response) return;
      response.className = 'form-response ' + (kind === 'success' ? 'is-success' : kind === 'error' ? 'is-error' : '');
      if (asHtml) response.innerHTML = html; else response.textContent = html;
    }

    function startRateLimit() {
      if (!submitBtn) return;
      let sec = CONFIG.rateLimitSeconds;
      submitBtn.disabled = true;
      submitBtn.classList.remove('is-loading');
      const originalLabel = submitBtn.querySelector('.btn__label').textContent;
      const labelEl = submitBtn.querySelector('.btn__label');
      labelEl.textContent = L.retryIn + ' ' + sec + 'ث';
      rateLimitTimer = setInterval(function () {
        sec -= 1;
        if (sec <= 0) {
          clearInterval(rateLimitTimer);
          submitBtn.disabled = false;
          labelEl.textContent = originalLabel;
          return;
        }
        labelEl.textContent = L.retryIn + ' ' + sec + 'ث';
      }, 1000);
    }

    function validate(d, f) {
      const errs = [];
      if (!d.name || !d.company || !d.sector || !d.phone || !d.email) {
        errs.push(L.formErrorReq);
        ['name','company','sector','phone','email'].forEach(function (k) {
          if (!d[k]) f[k] && f[k].setAttribute('aria-invalid', 'true');
        });
      }
      if (!d.consent) {
        errs.push(L.formErrorConsent);
      }
      if (d.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(d.email)) {
        errs.push(L.formErrorEmail);
        f.email.setAttribute('aria-invalid', 'true');
      }
      // Saudi phone: +966 5XX XXX XXXX, or 05X..., or 5X... — normalize to digits
      if (d.phone) {
        const digits = d.phone.replace(/[^\d+]/g, '');
        const saudi = /^(?:\+?966|0)?5\d{8}$/;
        if (!saudi.test(digits)) {
          errs.push(L.formErrorPhone);
          f.phone.setAttribute('aria-invalid', 'true');
        }
      }
      return errs;
    }

    function buildMailto(d) {
      const subj = encodeURIComponent('طلب تجربة Dealix — ' + (d.company || ''));
      const body = encodeURIComponent(
        'الاسم: ' + d.name + '\n' +
        'الشركة: ' + d.company + '\n' +
        'القطاع: ' + d.sector + '\n' +
        'الحجم: ' + d.size + '\n' +
        'الجوال: ' + d.phone + '\n' +
        'البريد: ' + d.email + '\n\n' +
        'الرسالة:\n' + (d.message || '')
      );
      return 'mailto:' + CONFIG.fallbackEmail + '?subject=' + subj + '&body=' + body;
    }
  }

  // ====================================================================
  // CONSENT BANNER
  // ====================================================================
  const consentBanner = document.getElementById('consentBanner');
  if (consentBanner) {
    // In-memory consent state (preview iframe blocks storage APIs)
    const decided = window.__dlxConsent;
    if (!decided) {
      consentBanner.hidden = false;
    } else if (decided === 'accept') {
      loadAnalytics();
    }
    consentBanner.querySelectorAll('[data-consent]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        const choice = btn.getAttribute('data-consent');
        window.__dlxConsent = choice;
        consentBanner.hidden = true;
        if (choice === 'accept') loadAnalytics();
        track('consent_' + choice, {});
      });
    });
  }

  // ====================================================================
  // ANALYTICS LOADERS (PostHog + GA4) — load only with consent
  // ====================================================================
  function loadAnalytics() {
    // PostHog
    if (CONFIG.posthogKey && CONFIG.posthogKey.indexOf('__') !== 0) {
      !function(t,e){var o,n,p,r;e.__SV||(window.posthog=e,e._i=[],e.init=function(i,s,a){function g(t,e){var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}(p=t.createElement("script")).type="text/javascript",p.async=!0,p.src=s.api_host.replace(".i.posthog.com","-assets.i.posthog.com")+"/static/array.js",(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],u.toString=function(t){var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e},u.people.toString=function(){return u.toString(1)+".people (stub)"},o="capture identify alias people.set people.set_once set_config register register_once unregister opt_out_capturing has_opted_out_capturing opt_in_capturing reset isFeatureEnabled onFeatureFlags getFeatureFlag getFeatureFlagPayload reloadFeatureFlags group updateEarlyAccessFeatureEnrollment getEarlyAccessFeatures getActiveMatchingSurveys getSurveys getNextSurveyStep".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}(document,window.posthog||[]);
      window.posthog.init(CONFIG.posthogKey, { api_host: CONFIG.posthogHost });
    }
    // GA4
    if (CONFIG.gaId && CONFIG.gaId.indexOf('__') !== 0) {
      const s = document.createElement('script');
      s.async = true;
      s.src = 'https://www.googletagmanager.com/gtag/js?id=' + CONFIG.gaId;
      document.head.appendChild(s);
      window.dataLayer = window.dataLayer || [];
      function gtag(){ dataLayer.push(arguments); }
      window.gtag = gtag;
      gtag('js', new Date());
      gtag('config', CONFIG.gaId, { anonymize_ip: true });
    }
    track('page_view', { path: location.pathname });
  }

  // Universal track helper — routes to PH / GA / console
  function track(event, props) {
    props = props || {};
    try {
      if (window.posthog && typeof window.posthog.capture === 'function') {
        window.posthog.capture(event, props);
      }
      if (typeof window.gtag === 'function') {
        window.gtag('event', event, props);
      }
      // Always log in dev
      if (location.hostname === 'localhost' || location.hostname === '127.0.0.1') {
        // eslint-disable-next-line no-console
        console.log('[track]', event, props);
      }
    } catch (_) {}
  }

  // ====================================================================
  // LOAD READINESS STATS FROM EMBEDDED OR STATIC (fallback to known summary)
  // ====================================================================
  // Numbers pulled from SERVICE_READINESS_MATRIX.yaml summary
  const stats = { total: 32, live: 0, partial: 7, pilot: 1, target: 24 };
  const setNum = (id, n) => { const el = document.getElementById(id); if (el) el.textContent = String(n); };
  setNum('stat-live', stats.live);
  setNum('stat-partial', stats.partial + stats.pilot); // 8
  setNum('stat-target', stats.target);

  // ====================================================================
  // FOOTER YEAR
  // ====================================================================
  const yearEl = document.getElementById('year');
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());

  // Initial page_view (even before consent — minimal, no PII)
  track('page_view_init', { path: location.pathname });
})();

// ====================================================================
// PROSPECTOR (LIVE LEAD MACHINE) — calls /api/v1/prospect/discover
// ====================================================================
(function prospectorInit() {
  const form = document.getElementById('prospector-form');
  if (!form) return;

  const icpEl = document.getElementById('prospector-icp');
  const useCaseEl = document.getElementById('prospector-usecase');
  const countEl = document.getElementById('prospector-count');
  const submitBtn = document.getElementById('prospector-submit');
  const statusEl = document.getElementById('prospector-status');
  const resultsEl = document.getElementById('prospector-results');
  const gridEl = document.getElementById('prospector-grid');
  const countOutEl = document.getElementById('prospector-count-out');
  const notesEl = document.getElementById('prospector-notes');

  const API_BASE_PRIMARY = (window.DEALIX_API_BASE || 'https://web-dealix.up.railway.app').replace(/\/$/, '');
  const API_BASE_FALLBACK = 'https://web-dealix.up.railway.app';

  function setStatus(msg, kind) {
    if (!msg) {
      statusEl.hidden = true;
      statusEl.textContent = '';
      statusEl.className = 'prospector__status';
      return;
    }
    statusEl.hidden = false;
    statusEl.textContent = msg;
    statusEl.className = 'prospector__status' + (kind ? ' prospector__status--' + kind : '');
  }

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[c]));
  }

  function renderCard(lead) {
    const openings = lead.outreach_opening
      ? `<div class="prospector-card__section">
           <h4>سطر افتتاحي مقترح</h4>
           <div class="prospector-card__opening">${esc(lead.outreach_opening)}</div>
         </div>`
      : '';

    const dmHints = (lead.decision_maker_hints || []).filter(Boolean);
    const signals = (lead.signals || []).filter(Boolean);

    const links = [];
    if (lead.website) links.push(`<a href="${esc(lead.website)}" target="_blank" rel="noopener">موقع</a>`);
    if (lead.linkedin) links.push(`<a href="${esc(lead.linkedin)}" target="_blank" rel="noopener">LinkedIn</a>`);

    return `
      <article class="prospector-card">
        <div class="prospector-card__head">
          <div>
            <h4 class="prospector-card__name">${esc(lead.company_ar)}</h4>
            <span class="prospector-card__name-en">${esc(lead.company_en)}</span>
          </div>
          <span class="prospector-card__score" title="fit × confidence">${lead.fit_score}/${lead.confidence}</span>
        </div>
        <div class="prospector-card__meta">
          <span>${esc(lead.industry || '—')}</span>
          <span>${esc(lead.est_size || '—')}</span>
        </div>
        ${signals.length ? `
          <div class="prospector-card__section">
            <h4>إشارات</h4>
            <ul>${signals.map(s => `<li>${esc(s)}</li>`).join('')}</ul>
          </div>` : ''}
        ${dmHints.length ? `
          <div class="prospector-card__section">
            <h4>متخذو قرار محتملون</h4>
            <ul>${dmHints.map(s => `<li>${esc(s)}</li>`).join('')}</ul>
          </div>` : ''}
        ${openings}
        ${lead.evidence ? `
          <div class="prospector-card__section">
            <h4>لماذا تطابق</h4>
            <div>${esc(lead.evidence)}</div>
          </div>` : ''}
        ${links.length ? `<div class="prospector-card__links">${links.join(' · ')}</div>` : ''}
      </article>
    `;
  }

  function renderResults(data) {
    const leads = Array.isArray(data.leads) ? data.leads : [];
    countOutEl.textContent = `${leads.length} نتيجة من ${data.count_requested || leads.length} مطلوبة`;
    gridEl.innerHTML = leads.map(renderCard).join('');
    notesEl.textContent = data.search_notes || '';
    resultsEl.hidden = leads.length === 0;
  }

  async function callApi(path, body) {
    const attempt = async (base) => {
      const r = await fetch(base + path, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body || {}),
      });
      return r;
    };
    try {
      const r = await attempt(API_BASE_PRIMARY);
      if (r.ok || (r.status >= 400 && r.status < 500)) return r;
      // 5xx → try fallback
      if (API_BASE_PRIMARY !== API_BASE_FALLBACK) return attempt(API_BASE_FALLBACK);
      return r;
    } catch (e) {
      if (API_BASE_PRIMARY !== API_BASE_FALLBACK) return attempt(API_BASE_FALLBACK);
      throw e;
    }
  }

  form.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    const icp = (icpEl.value || '').trim();
    const use_case = useCaseEl.value || 'sales';
    const count = parseInt(countEl.value || '10', 10);

    if (icp.length < 20) {
      setStatus('أضف وصفاً أطول (20 حرف على الأقل) للعميل المثالي.', 'error');
      return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = 'يبحث...';
    setStatus('يبحث عن leads مطابقة... (15-45 ثانية)', 'loading');
    resultsEl.hidden = true;

    try {
      const t0 = performance.now();
      const r = await callApi('/api/v1/prospect/discover', { icp, use_case, count });
      const data = await r.json();
      const dt = ((performance.now() - t0) / 1000).toFixed(1);

      if (!r.ok) {
        const detail = data && data.detail ? data.detail : ('HTTP ' + r.status);
        throw new Error(detail);
      }
      renderResults(data);
      setStatus(`اكتمل في ${dt} ثانية`, null);
      setTimeout(() => setStatus(''), 3000);
      if (window.track) window.track('prospector_run', { use_case, count, returned: (data.leads || []).length });
    } catch (err) {
      console.error('prospector error', err);
      setStatus('حدث خطأ: ' + (err && err.message ? err.message : 'غير معروف') + ' — جرّب مرة ثانية.', 'error');
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = 'ابحث الآن';
    }
  });

  // Prefill demo ICP on first load (only if empty)
  if (icpEl && !icpEl.value) {
    icpEl.setAttribute('data-default-demo',
      'شركات SaaS B2B في السعودية بحجم 20-100 موظف، تبيع للشركات المتوسطة، أحد المؤسسين أعلن عن جولة تمويل في آخر 12 شهر.'
    );
  }
})();
