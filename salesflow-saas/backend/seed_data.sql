-- Dealix Database Seed — Saudi Market Data
-- Generated automatically for production use
-- Date: 2026-04-16T08:43:50.799709+00:00

-- ═══ Default Tenant ═══

INSERT INTO tenants (id, company_name, company_name_ar, industry, domain, plan, is_active, created_at)
VALUES (
    '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'Dealix Enterprise',
    'ديل اي اكس المؤسسي',
    'technology',
    'dealix.sa',
    'enterprise',
    true,
    NOW()
) ON CONFLICT DO NOTHING;

-- ═══ Admin User ═══

INSERT INTO users (id, tenant_id, email, hashed_password, full_name, full_name_ar, role, is_active, created_at)
VALUES (
    '45f0626f-19ca-4aca-83ce-ecbfe38247fa',
    '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'admin@dealix.sa',
    '$2b$12$LJ3b5W0z5m5j5g5T5k5Z5O5v5K5n5Q5R5S5X5Y5A5B5C5D5E5F5G5',
    'System Administrator',
    'مدير النظام',
    'admin',
    true,
    NOW()
) ON CONFLICT DO NOTHING;

-- ═══ Saudi Market Leads ═══

INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    '0980b0d9-531a-440c-9e36-ec0704541fe3', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'Emaar Properties', 'شركة إعمار العقارية',
    'مشعل البقمي', 'مشعل البقمي',
    'مشعل.البقمي@emaarproperties.com', '+966582008096', 'خميس مشيط', 'عقارات',
    'google_maps', 'negotiation', 33,
    'عميل محتمل من خميس مشيط - قطاع عقارات - حجم الشركة: enterprise',
    NOW() - INTERVAL '21 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    '87809ed9-fb04-4dc0-a764-a80375dd0188', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'Emaar Properties', 'شركة إعمار العقارية',
    'سامي الرشيدي', 'سامي الرشيدي',
    'سامي.الرشيدي@emaarproperties.com', '+966529936759', 'ينبع', 'عقارات',
    'referral', 'lost', 81,
    'عميل محتمل من ينبع - قطاع عقارات - حجم الشركة: enterprise',
    NOW() - INTERVAL '24 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    '1159f9d8-8ad5-468a-9cd1-11c2f4da7daa', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'Dar Al Arkan', 'دار الأركان للتطوير العقاري',
    'سامي العنزي', 'سامي العنزي',
    'سامي.العنزي@daralarkan.com', '+966513892709', 'بريدة', 'عقارات',
    'referral', 'lost', 47,
    'عميل محتمل من بريدة - قطاع عقارات - حجم الشركة: enterprise',
    NOW() - INTERVAL '16 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    '01766dd0-eb18-4fe1-b687-492d50de6fc1', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'Dar Al Arkan', 'دار الأركان للتطوير العقاري',
    'سعد الدوسري', 'سعد الدوسري',
    'سعد.الدوسري@daralarkan.com', '+966598049661', 'أبها', 'عقارات',
    'google_maps', 'negotiation', 37,
    'عميل محتمل من أبها - قطاع عقارات - حجم الشركة: enterprise',
    NOW() - INTERVAL '3 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    '6d45eb33-0408-4d80-a2f0-21f123cb771e', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'Retal Urban Development', 'شركة رتال للتطوير العمراني',
    'وليد العسيري', 'وليد العسيري',
    'وليد.العسيري@retalurbandevelopment.com', '+966552562263', 'أبها', 'عقارات',
    'linkedin', 'contacted', 32,
    'عميل محتمل من أبها - قطاع عقارات - حجم الشركة: large',
    NOW() - INTERVAL '22 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    'b95dcc7c-f474-4d1f-ad45-e0f751a457ae', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'Retal Urban Development', 'شركة رتال للتطوير العمراني',
    'عبدالرحمن المطيري', 'عبدالرحمن المطيري',
    'عبدالرحمن.المطيري@retalurbandevelopment.com', '+966528261895', 'الطائف', 'عقارات',
    'cold_call', 'qualified', 85,
    'عميل محتمل من الطائف - قطاع عقارات - حجم الشركة: large',
    NOW() - INTERVAL '5 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    '5ed91406-37e3-4c8c-a3b9-8f4597dc5bdc', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'Retal Urban Development', 'شركة رتال للتطوير العمراني',
    'ناصر العتيبي', 'ناصر العتيبي',
    'ناصر.العتيبي@retalurbandevelopment.com', '+966518237175', 'مكة المكرمة', 'عقارات',
    'whatsapp', 'contacted', 73,
    'عميل محتمل من مكة المكرمة - قطاع عقارات - حجم الشركة: large',
    NOW() - INTERVAL '68 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    'bb396401-4188-4b9f-8374-a39db821be4b', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'Jabal Omar Development', 'شركة جبل عمر للتطوير',
    'بندر الأحمري', 'بندر الأحمري',
    'بندر.الأحمري@jabalomardevelopment.com', '+966537019292', 'الطائف', 'عقارات',
    'cold_call', 'won', 47,
    'عميل محتمل من الطائف - قطاع عقارات - حجم الشركة: enterprise',
    NOW() - INTERVAL '76 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    'f71a1578-f74a-4359-91c9-66383cad8c24', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'Jabal Omar Development', 'شركة جبل عمر للتطوير',
    'عمر الأحمري', 'عمر الأحمري',
    'عمر.الأحمري@jabalomardevelopment.com', '+966523284026', 'الطائف', 'عقارات',
    'exhibition', 'negotiation', 89,
    'عميل محتمل من الطائف - قطاع عقارات - حجم الشركة: enterprise',
    NOW() - INTERVAL '19 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    '50190ae8-c409-4988-990f-61e8c7c03fa7', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'Cenomi Centers', 'المراكز العربية (سينومي)',
    'عبدالرحمن الدوسري', 'عبدالرحمن الدوسري',
    'عبدالرحمن.الدوسري@cenomicenters.com', '+966528838664', 'المدينة المنورة', 'عقارات',
    'exhibition', 'qualified', 59,
    'عميل محتمل من المدينة المنورة - قطاع عقارات - حجم الشركة: enterprise',
    NOW() - INTERVAL '55 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    'fd9554dd-205f-4a17-ba0c-cf19af71060e', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'Cenomi Centers', 'المراكز العربية (سينومي)',
    'سلطان المطيري', 'سلطان المطيري',
    'سلطان.المطيري@cenomicenters.com', '+966558648508', 'أبها', 'عقارات',
    'google_maps', 'contacted', 54,
    'عميل محتمل من أبها - قطاع عقارات - حجم الشركة: enterprise',
    NOW() - INTERVAL '11 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    'fa7441d4-1d68-4253-a50a-464ca37dd88d', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'Riyadh Development Co', 'شركة الرياض للتعمير',
    'أحمد الشهري', 'أحمد الشهري',
    'أحمد.الشهري@riyadhdevelopmentco.com', '+966565096633', 'ينبع', 'عقارات',
    'referral', 'won', 85,
    'عميل محتمل من ينبع - قطاع عقارات - حجم الشركة: large',
    NOW() - INTERVAL '26 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    'ea014bce-f4d0-4f0a-b71c-dfaa22468d67', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'Saudi Binladin Group', 'مجموعة بن لادن السعودية',
    'سلطان الأحمري', 'سلطان الأحمري',
    'سلطان.الأحمري@saudibinladingroup.com', '+966533396485', 'الجبيل', 'عقارات',
    'cold_call', 'new', 73,
    'عميل محتمل من الجبيل - قطاع عقارات - حجم الشركة: enterprise',
    NOW() - INTERVAL '15 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    '0f513d6f-8aca-4e94-8c30-9edf0bf03186', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'ROSHN Real Estate', 'شركة روشن العقارية',
    'فيصل السبيعي', 'فيصل السبيعي',
    'فيصل.السبيعي@roshnrealestate.com', '+966581908609', 'الدمام', 'عقارات',
    'google_maps', 'qualified', 65,
    'عميل محتمل من الدمام - قطاع عقارات - حجم الشركة: enterprise',
    NOW() - INTERVAL '51 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    '4a36e968-fb40-4508-98d6-220b400dc111', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'ROSHN Real Estate', 'شركة روشن العقارية',
    'عمر الشهري', 'عمر الشهري',
    'عمر.الشهري@roshnrealestate.com', '+966541332196', 'الجبيل', 'عقارات',
    'exhibition', 'negotiation', 52,
    'عميل محتمل من الجبيل - قطاع عقارات - حجم الشركة: enterprise',
    NOW() - INTERVAL '77 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    '28bc5d38-380e-45ab-a3c1-7fd0395312fc', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'ROSHN Real Estate', 'شركة روشن العقارية',
    'فيصل العسيري', 'فيصل العسيري',
    'فيصل.العسيري@roshnrealestate.com', '+966540392838', 'المدينة المنورة', 'عقارات',
    'whatsapp', 'qualified', 83,
    'عميل محتمل من المدينة المنورة - قطاع عقارات - حجم الشركة: enterprise',
    NOW() - INTERVAL '50 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    'a2888cf8-2d9c-4bc5-9451-78e8a6bbd2dc', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'Elm Company', 'شركة علم',
    'خالد السبيعي', 'خالد السبيعي',
    'خالد.السبيعي@elmcompany.com', '+966560768562', 'الرياض', 'تقنية معلومات',
    'referral', 'proposal_sent', 87,
    'عميل محتمل من الرياض - قطاع تقنية معلومات - حجم الشركة: enterprise',
    NOW() - INTERVAL '76 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    'f9d23c1d-fbd6-4792-91cb-addd88ba926e', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'Elm Company', 'شركة علم',
    'ماجد اليامي', 'ماجد اليامي',
    'ماجد.اليامي@elmcompany.com', '+966587327817', 'مكة المكرمة', 'تقنية معلومات',
    'whatsapp', 'won', 74,
    'عميل محتمل من مكة المكرمة - قطاع تقنية معلومات - حجم الشركة: enterprise',
    NOW() - INTERVAL '24 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    'da1e2f4e-0cce-48cd-8545-2dd701901565', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'Thiqah Business Services', 'شركة ثقة',
    'عبدالله العنزي', 'عبدالله العنزي',
    'عبدالله.العنزي@thiqahbusinessservices.com', '+966591462825', 'نجران', 'تقنية معلومات',
    'cold_call', 'won', 83,
    'عميل محتمل من نجران - قطاع تقنية معلومات - حجم الشركة: large',
    NOW() - INTERVAL '14 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    '4c720f90-90eb-476d-96a5-42f2755f5784', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'Thiqah Business Services', 'شركة ثقة',
    'عبدالرحمن المطيري', 'عبدالرحمن المطيري',
    'عبدالرحمن.المطيري@thiqahbusinessservices.com', '+966574437068', 'مكة المكرمة', 'تقنية معلومات',
    'cold_call', 'qualified', 80,
    'عميل محتمل من مكة المكرمة - قطاع تقنية معلومات - حجم الشركة: large',
    NOW() - INTERVAL '5 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    'a3dce79b-7a58-4ad6-af67-40332f2d2aec', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'Salam Telecom', 'شركة سلام للاتصالات',
    'خالد المالكي', 'خالد المالكي',
    'خالد.المالكي@salamtelecom.com', '+966579782440', 'ينبع', 'تقنية معلومات',
    'whatsapp', 'won', 57,
    'عميل محتمل من ينبع - قطاع تقنية معلومات - حجم الشركة: large',
    NOW() - INTERVAL '70 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    '69b2f432-40f9-4dc0-a4c0-49156e09ba1b', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'Masar Tech', 'شركة مسار التقنية',
    'خالد الزهراني', 'خالد الزهراني',
    'خالد.الزهراني@masartech.com', '+966596304036', 'بريدة', 'تقنية معلومات',
    'linkedin', 'new', 84,
    'عميل محتمل من بريدة - قطاع تقنية معلومات - حجم الشركة: medium',
    NOW() - INTERVAL '33 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    '646f0bdf-e701-43cb-82ea-3e71761cdda0', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'Masar Tech', 'شركة مسار التقنية',
    'مشعل العسيري', 'مشعل العسيري',
    'مشعل.العسيري@masartech.com', '+966577454703', 'أبها', 'تقنية معلومات',
    'cold_call', 'proposal_sent', 44,
    'عميل محتمل من أبها - قطاع تقنية معلومات - حجم الشركة: medium',
    NOW() - INTERVAL '26 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    '64cd206b-059e-4695-b9e1-fe111f1b96c1', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'Masar Tech', 'شركة مسار التقنية',
    'عبدالله الحربي', 'عبدالله الحربي',
    'عبدالله.الحربي@masartech.com', '+966580366506', 'الرياض', 'تقنية معلومات',
    'exhibition', 'contacted', 73,
    'عميل محتمل من الرياض - قطاع تقنية معلومات - حجم الشركة: medium',
    NOW() - INTERVAL '17 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    'df82403e-9689-44a7-8445-cbb2ac52d133', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'SaharaNet', 'شركة صحارى نت',
    'عمر القحطاني', 'عمر القحطاني',
    'عمر.القحطاني@saharanet.com', '+966599471499', 'ينبع', 'تقنية معلومات',
    'exhibition', 'negotiation', 71,
    'عميل محتمل من ينبع - قطاع تقنية معلومات - حجم الشركة: medium',
    NOW() - INTERVAL '71 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    '7b6daf72-be96-477a-8151-a50a7adc5bc4', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'SmartLink', 'شركة سمارت لينك',
    'سامي القحطاني', 'سامي القحطاني',
    'سامي.القحطاني@smartlink.com', '+966556416526', 'ينبع', 'تقنية معلومات',
    'cold_call', 'negotiation', 85,
    'عميل محتمل من ينبع - قطاع تقنية معلومات - حجم الشركة: medium',
    NOW() - INTERVAL '35 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    '1413794f-d4bc-4c57-bb3f-a770e62c51ea', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'SmartLink', 'شركة سمارت لينك',
    'أحمد الدوسري', 'أحمد الدوسري',
    'أحمد.الدوسري@smartlink.com', '+966527576708', 'الرياض', 'تقنية معلومات',
    'cold_call', 'lost', 70,
    'عميل محتمل من الرياض - قطاع تقنية معلومات - حجم الشركة: medium',
    NOW() - INTERVAL '3 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    '8154b435-7dc0-45bd-97f9-5ec79538fb0b', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'SmartLink', 'شركة سمارت لينك',
    'سعد المالكي', 'سعد المالكي',
    'سعد.المالكي@smartlink.com', '+966567875962', 'نجران', 'تقنية معلومات',
    'google_maps', 'new', 63,
    'عميل محتمل من نجران - قطاع تقنية معلومات - حجم الشركة: medium',
    NOW() - INTERVAL '26 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    '0a597eb9-cee6-4eb1-afa7-009806af0085', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'Dr. Sulaiman Al Habib', 'مجموعة سليمان الحبيب الطبية',
    'خالد الشهري', 'خالد الشهري',
    'خالد.الشهري@drsulaimanalhabib.com', '+966553985994', 'المدينة المنورة', 'صحة',
    'exhibition', 'proposal_sent', 31,
    'عميل محتمل من المدينة المنورة - قطاع صحة - حجم الشركة: enterprise',
    NOW() - INTERVAL '18 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    'ba83e391-4d2b-49b6-8f06-8fbea39f70bc', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'Dr. Sulaiman Al Habib', 'مجموعة سليمان الحبيب الطبية',
    'سعد الرشيدي', 'سعد الرشيدي',
    'سعد.الرشيدي@drsulaimanalhabib.com', '+966569985082', 'نجران', 'صحة',
    'linkedin', 'negotiation', 76,
    'عميل محتمل من نجران - قطاع صحة - حجم الشركة: enterprise',
    NOW() - INTERVAL '1 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    '952660bc-c0a1-4827-883a-7becba33e661', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'Dr. Sulaiman Al Habib', 'مجموعة سليمان الحبيب الطبية',
    'بندر العنزي', 'بندر العنزي',
    'بندر.العنزي@drsulaimanalhabib.com', '+966538152215', 'المدينة المنورة', 'صحة',
    'whatsapp', 'contacted', 53,
    'عميل محتمل من المدينة المنورة - قطاع صحة - حجم الشركة: enterprise',
    NOW() - INTERVAL '86 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    '7672bb12-3f2b-4e61-92d3-0c477e1eb7f1', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'Mouwasat Medical', 'شركة المواساة للخدمات الطبية',
    'عبدالرحمن السبيعي', 'عبدالرحمن السبيعي',
    'عبدالرحمن.السبيعي@mouwasatmedical.com', '+966592365774', 'الخبر', 'صحة',
    'cold_call', 'won', 39,
    'عميل محتمل من الخبر - قطاع صحة - حجم الشركة: enterprise',
    NOW() - INTERVAL '30 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    '9c2dfcc9-6d0e-4b78-9bdc-475a2240e616', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'Mouwasat Medical', 'شركة المواساة للخدمات الطبية',
    'فيصل السبيعي', 'فيصل السبيعي',
    'فيصل.السبيعي@mouwasatmedical.com', '+966581344829', 'جدة', 'صحة',
    'exhibition', 'negotiation', 36,
    'عميل محتمل من جدة - قطاع صحة - حجم الشركة: enterprise',
    NOW() - INTERVAL '54 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    '669e0f19-1939-41a4-bdb6-ba606aaac404', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'Dallah Health', 'مستشفى دله الصحية',
    'فيصل الغامدي', 'فيصل الغامدي',
    'فيصل.الغامدي@dallahhealth.com', '+966567969078', 'تبوك', 'صحة',
    'website', 'contacted', 86,
    'عميل محتمل من تبوك - قطاع صحة - حجم الشركة: large',
    NOW() - INTERVAL '44 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    '350742d5-58ca-4988-9ee4-4a417b474de4', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'Dallah Health', 'مستشفى دله الصحية',
    'عمر اليامي', 'عمر اليامي',
    'عمر.اليامي@dallahhealth.com', '+966578724284', 'الجبيل', 'صحة',
    'google_maps', 'contacted', 33,
    'عميل محتمل من الجبيل - قطاع صحة - حجم الشركة: large',
    NOW() - INTERVAL '13 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    '8293e042-7a05-46a4-bbc1-1ed90341104f', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'Riayah Holding', 'شركة رعاية القابضة',
    'ناصر اليامي', 'ناصر اليامي',
    'ناصر.اليامي@riayahholding.com', '+966512947692', 'تبوك', 'صحة',
    'referral', 'negotiation', 68,
    'عميل محتمل من تبوك - قطاع صحة - حجم الشركة: large',
    NOW() - INTERVAL '11 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    '467b6338-033d-4b61-96cb-443f5fa49a5a', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'King Faisal Medical City', 'مجمع الملك فيصل الطبي',
    'تركي العتيبي', 'تركي العتيبي',
    'تركي.العتيبي@kingfaisalmedicalcity.com', '+966548773786', 'نجران', 'صحة',
    'whatsapp', 'won', 30,
    'عميل محتمل من نجران - قطاع صحة - حجم الشركة: enterprise',
    NOW() - INTERVAL '58 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    '469b17e6-ae14-4433-b837-5c8ea0b68078', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'Nesma Holding', 'شركة نسما القابضة',
    'سلطان السلمي', 'سلطان السلمي',
    'سلطان.السلمي@nesmaholding.com', '+966567507106', 'الدمام', 'إنشاءات',
    'google_maps', 'negotiation', 43,
    'عميل محتمل من الدمام - قطاع إنشاءات - حجم الشركة: enterprise',
    NOW() - INTERVAL '17 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    '110a8e6f-6801-4f6e-806a-673ac274b8ec', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'Nesma Holding', 'شركة نسما القابضة',
    'يوسف الأحمري', 'يوسف الأحمري',
    'يوسف.الأحمري@nesmaholding.com', '+966539579431', 'أبها', 'إنشاءات',
    'referral', 'proposal_sent', 83,
    'عميل محتمل من أبها - قطاع إنشاءات - حجم الشركة: enterprise',
    NOW() - INTERVAL '33 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    'd161f810-273f-48df-82e3-0fe8092191b0', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'Al Rajhi Construction', 'مجموعة الراجحي للمقاولات',
    'سلطان السبيعي', 'سلطان السبيعي',
    'سلطان.السبيعي@alrajhiconstruction.com', '+966572285135', 'مكة المكرمة', 'إنشاءات',
    'whatsapp', 'lost', 47,
    'عميل محتمل من مكة المكرمة - قطاع إنشاءات - حجم الشركة: enterprise',
    NOW() - INTERVAL '54 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    '1d560317-c980-438c-b864-092ef06cb004', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'Al Rajhi Construction', 'مجموعة الراجحي للمقاولات',
    'يوسف السلمي', 'يوسف السلمي',
    'يوسف.السلمي@alrajhiconstruction.com', '+966560418405', 'جدة', 'إنشاءات',
    'referral', 'new', 33,
    'عميل محتمل من جدة - قطاع إنشاءات - حجم الشركة: enterprise',
    NOW() - INTERVAL '48 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    '6bd6ba61-eec7-4fcf-a612-05a11307d79f', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'Al Mabani Contracting', 'شركة المباني للمقاولات',
    'حسن اليامي', 'حسن اليامي',
    'حسن.اليامي@almabanicontracting.com', '+966510089854', 'تبوك', 'إنشاءات',
    'linkedin', 'proposal_sent', 94,
    'عميل محتمل من تبوك - قطاع إنشاءات - حجم الشركة: large',
    NOW() - INTERVAL '66 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    'bc1635fc-296d-498f-b13d-6d8103393edd', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'Al Mabani Contracting', 'شركة المباني للمقاولات',
    'حسن المطيري', 'حسن المطيري',
    'حسن.المطيري@almabanicontracting.com', '+966550990963', 'الطائف', 'إنشاءات',
    'website', 'contacted', 93,
    'عميل محتمل من الطائف - قطاع إنشاءات - حجم الشركة: large',
    NOW() - INTERVAL '78 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    '34007bde-377d-4449-8530-91be04b55649', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'Al Mabani Contracting', 'شركة المباني للمقاولات',
    'ماجد العنزي', 'ماجد العنزي',
    'ماجد.العنزي@almabanicontracting.com', '+966574688648', 'مكة المكرمة', 'إنشاءات',
    'referral', 'proposal_sent', 85,
    'عميل محتمل من مكة المكرمة - قطاع إنشاءات - حجم الشركة: large',
    NOW() - INTERVAL '62 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    '516bd25e-2a5e-4ab5-8091-dab25c2fae73', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'Al Hamrani Contracting', 'شركة الحمراني للمقاولات',
    'طارق المطيري', 'طارق المطيري',
    'طارق.المطيري@alhamranicontracting.com', '+966574394407', 'مكة المكرمة', 'إنشاءات',
    'whatsapp', 'proposal_sent', 36,
    'عميل محتمل من مكة المكرمة - قطاع إنشاءات - حجم الشركة: large',
    NOW() - INTERVAL '71 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    'c407a2ed-8f9a-4dbd-bfc5-ebb7877088f2', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'Al Hamrani Contracting', 'شركة الحمراني للمقاولات',
    'بندر الأحمري', 'بندر الأحمري',
    'بندر.الأحمري@alhamranicontracting.com', '+966596848248', 'أبها', 'إنشاءات',
    'google_maps', 'proposal_sent', 70,
    'عميل محتمل من أبها - قطاع إنشاءات - حجم الشركة: large',
    NOW() - INTERVAL '34 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    '6cda23d4-5ed1-4aaf-87b9-585c2e3df43c', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'Fawaz Alhokair Group', 'شركة فواز الحكير',
    'عمر البقمي', 'عمر البقمي',
    'عمر.البقمي@fawazalhokairgroup.com', '+966540299517', 'المدينة المنورة', 'تجزئة',
    'referral', 'won', 50,
    'عميل محتمل من المدينة المنورة - قطاع تجزئة - حجم الشركة: enterprise',
    NOW() - INTERVAL '15 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    'dd82635f-14f2-4263-ad27-d3edfb8249f1', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'Fawaz Alhokair Group', 'شركة فواز الحكير',
    'ناصر العنزي', 'ناصر العنزي',
    'ناصر.العنزي@fawazalhokairgroup.com', '+966577420364', 'أبها', 'تجزئة',
    'cold_call', 'lost', 45,
    'عميل محتمل من أبها - قطاع تجزئة - حجم الشركة: enterprise',
    NOW() - INTERVAL '83 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    '90b12bab-9f88-4fe6-bc1f-1a2014853b6e', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'Panda Retail (Savola)', 'بندة للتجزئة',
    'سامي السبيعي', 'سامي السبيعي',
    'سامي.السبيعي@pandaretail(savola).com', '+966550946727', 'أبها', 'تجزئة',
    'exhibition', 'contacted', 59,
    'عميل محتمل من أبها - قطاع تجزئة - حجم الشركة: enterprise',
    NOW() - INTERVAL '50 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    '9589c726-19e4-496e-ad23-6aa400fbdabf', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'Jarir Marketing', 'شركة جرير للتسويق',
    'عبدالرحمن الشهري', 'عبدالرحمن الشهري',
    'عبدالرحمن.الشهري@jarirmarketing.com', '+966549055144', 'أبها', 'تجزئة',
    'referral', 'contacted', 35,
    'عميل محتمل من أبها - قطاع تجزئة - حجم الشركة: large',
    NOW() - INTERVAL '33 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    'eabfa1f3-d2f4-40df-aae3-a4f1a1d83467', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'eXtra Electronics', 'شركة إكسترا',
    'فهد العتيبي', 'فهد العتيبي',
    'فهد.العتيبي@extraelectronics.com', '+966527112482', 'خميس مشيط', 'تجزئة',
    'google_maps', 'lost', 48,
    'عميل محتمل من خميس مشيط - قطاع تجزئة - حجم الشركة: large',
    NOW() - INTERVAL '55 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    'cab22b06-5998-487c-abe7-5fb89d71e0b1', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'eXtra Electronics', 'شركة إكسترا',
    'ناصر القحطاني', 'ناصر القحطاني',
    'ناصر.القحطاني@extraelectronics.com', '+966540234660', 'جدة', 'تجزئة',
    'referral', 'negotiation', 79,
    'عميل محتمل من جدة - قطاع تجزئة - حجم الشركة: large',
    NOW() - INTERVAL '67 days'
) ON CONFLICT DO NOTHING;


INSERT INTO leads (id, tenant_id, company_name, company_name_ar, contact_name, contact_name_ar, email, phone, city, industry, source, status, score, notes, created_at)
VALUES (
    '56873142-8b45-4e99-ab85-edd8c70ccd2f', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'eXtra Electronics', 'شركة إكسترا',
    'تركي اليامي', 'تركي اليامي',
    'تركي.اليامي@extraelectronics.com', '+966531930908', 'خميس مشيط', 'تجزئة',
    'linkedin', 'won', 56,
    'عميل محتمل من خميس مشيط - قطاع تجزئة - حجم الشركة: large',
    NOW() - INTERVAL '30 days'
) ON CONFLICT DO NOTHING;

-- ═══ Sample Deals ═══

INSERT INTO deals (id, tenant_id, title, value, stage, probability, created_at)
VALUES (
    '3baa5550-19d6-43a2-8ce5-3fd2928d3be8', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'اشتراك أساسي - عقد شهري',
    1794, 'closed_won', 27,
    NOW() - INTERVAL '20 days'
) ON CONFLICT DO NOTHING;


INSERT INTO deals (id, tenant_id, title, value, stage, probability, created_at)
VALUES (
    '6dd0524f-e5ad-4c59-9bf3-0c6021e0fb68', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'اشتراك احترافي - عقد شهري',
    699, 'closed_won', 76,
    NOW() - INTERVAL '38 days'
) ON CONFLICT DO NOTHING;


INSERT INTO deals (id, tenant_id, title, value, stage, probability, created_at)
VALUES (
    'de838ab3-721b-4a24-9401-c1fc36cbd6cd', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'اشتراك احترافي - عقد شهري',
    8388, 'closed_won', 20,
    NOW() - INTERVAL '10 days'
) ON CONFLICT DO NOTHING;


INSERT INTO deals (id, tenant_id, title, value, stage, probability, created_at)
VALUES (
    '83bc9843-e94b-41e5-b9a7-bc5f702941d4', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'اشتراك أساسي - عقد نصف سنوي',
    897, 'negotiation', 83,
    NOW() - INTERVAL '41 days'
) ON CONFLICT DO NOTHING;


INSERT INTO deals (id, tenant_id, title, value, stage, probability, created_at)
VALUES (
    '10ada0dc-4a68-469c-afdf-0bafcec64207', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'اشتراك أساسي - عقد ربع سنوي',
    299, 'negotiation', 84,
    NOW() - INTERVAL '49 days'
) ON CONFLICT DO NOTHING;


INSERT INTO deals (id, tenant_id, title, value, stage, probability, created_at)
VALUES (
    'd99f2eee-5db4-47ad-a13e-a3c12353928f', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'اشتراك احترافي - عقد نصف سنوي',
    699, 'closed_won', 68,
    NOW() - INTERVAL '47 days'
) ON CONFLICT DO NOTHING;


INSERT INTO deals (id, tenant_id, title, value, stage, probability, created_at)
VALUES (
    '3ec63651-48b3-4e4a-a816-28bfe7359879', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'اشتراك مؤسسي - عقد ربع سنوي',
    4497, 'discovery', 36,
    NOW() - INTERVAL '21 days'
) ON CONFLICT DO NOTHING;


INSERT INTO deals (id, tenant_id, title, value, stage, probability, created_at)
VALUES (
    '370542a5-ac7a-47aa-88c1-0d8c17a749f6', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'اشتراك أساسي - عقد نصف سنوي',
    299, 'negotiation', 50,
    NOW() - INTERVAL '25 days'
) ON CONFLICT DO NOTHING;


INSERT INTO deals (id, tenant_id, title, value, stage, probability, created_at)
VALUES (
    '704f6850-1faa-4599-b16a-3c5b12359950', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'اشتراك احترافي - عقد نصف سنوي',
    699, 'closed_won', 95,
    NOW() - INTERVAL '3 days'
) ON CONFLICT DO NOTHING;


INSERT INTO deals (id, tenant_id, title, value, stage, probability, created_at)
VALUES (
    '95dc9c9f-4813-4d95-bbf9-cced477ad549', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'اشتراك مؤسسي - عقد شهري',
    4497, 'discovery', 49,
    NOW() - INTERVAL '54 days'
) ON CONFLICT DO NOTHING;


INSERT INTO deals (id, tenant_id, title, value, stage, probability, created_at)
VALUES (
    'c37dbd52-73e6-4a9a-8b4d-8a6ecb4df7a8', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'اشتراك أساسي - عقد ربع سنوي',
    299, 'proposal', 85,
    NOW() - INTERVAL '52 days'
) ON CONFLICT DO NOTHING;


INSERT INTO deals (id, tenant_id, title, value, stage, probability, created_at)
VALUES (
    '9346b8d2-b060-4f99-b230-25dd5292a57b', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'اشتراك أساسي - عقد نصف سنوي',
    897, 'closed_won', 59,
    NOW() - INTERVAL '58 days'
) ON CONFLICT DO NOTHING;


INSERT INTO deals (id, tenant_id, title, value, stage, probability, created_at)
VALUES (
    'ef37f599-f1f8-48d2-a5d3-fea569d08682', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'اشتراك احترافي - عقد نصف سنوي',
    8388, 'negotiation', 86,
    NOW() - INTERVAL '34 days'
) ON CONFLICT DO NOTHING;


INSERT INTO deals (id, tenant_id, title, value, stage, probability, created_at)
VALUES (
    'a636a9c2-ff14-41f0-8fd3-67b5c5262dd3', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'اشتراك أساسي - عقد نصف سنوي',
    897, 'negotiation', 79,
    NOW() - INTERVAL '9 days'
) ON CONFLICT DO NOTHING;


INSERT INTO deals (id, tenant_id, title, value, stage, probability, created_at)
VALUES (
    'ad702253-cae4-4275-87d7-d67a8656c55a', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'اشتراك احترافي - عقد شهري',
    699, 'proposal', 70,
    NOW() - INTERVAL '45 days'
) ON CONFLICT DO NOTHING;


INSERT INTO deals (id, tenant_id, title, value, stage, probability, created_at)
VALUES (
    'c6b33762-0c24-4f5a-b09b-0ec1749f37f3', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'اشتراك احترافي - عقد نصف سنوي',
    2097, 'closed_won', 68,
    NOW() - INTERVAL '14 days'
) ON CONFLICT DO NOTHING;


INSERT INTO deals (id, tenant_id, title, value, stage, probability, created_at)
VALUES (
    '710fe92a-92bd-45d9-a06c-ed0e276d8b31', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'اشتراك مؤسسي - عقد نصف سنوي',
    8994, 'discovery', 69,
    NOW() - INTERVAL '3 days'
) ON CONFLICT DO NOTHING;


INSERT INTO deals (id, tenant_id, title, value, stage, probability, created_at)
VALUES (
    '2b095a00-c365-4024-8fe2-608890b93909', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'اشتراك احترافي - عقد شهري',
    2097, 'discovery', 95,
    NOW() - INTERVAL '8 days'
) ON CONFLICT DO NOTHING;


INSERT INTO deals (id, tenant_id, title, value, stage, probability, created_at)
VALUES (
    '0e590313-0534-45da-8ec4-4c7afde6e501', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'اشتراك احترافي - عقد ربع سنوي',
    2097, 'discovery', 45,
    NOW() - INTERVAL '40 days'
) ON CONFLICT DO NOTHING;


INSERT INTO deals (id, tenant_id, title, value, stage, probability, created_at)
VALUES (
    '5da494c6-430f-435c-883d-03204fd98af1', '2e34c2bd-890a-4947-ae02-3e5c4742d3ba',
    'اشتراك مؤسسي - عقد شهري',
    17988, 'closed_lost', 59,
    NOW() - INTERVAL '36 days'
) ON CONFLICT DO NOTHING;

-- ═══ Affiliate Marketers ═══

INSERT INTO affiliate_marketers (id, full_name, full_name_ar, email, phone, whatsapp, city, status, referral_code, total_deals_closed, total_commission_earned, current_month_deals, created_at)
VALUES (
    'e5277a35-8e30-43d5-8d75-fab6445af35c',
    'تركي السلمي', 'تركي السلمي',
    'تركي.aff@dealix.sa', '+966586630707', '+966586630707', 'جدة',
    'active',
    'DLX-38C729D9', 15, 1950, 5,
    NOW() - INTERVAL '10 days'
) ON CONFLICT DO NOTHING;


INSERT INTO affiliate_marketers (id, full_name, full_name_ar, email, phone, whatsapp, city, status, referral_code, total_deals_closed, total_commission_earned, current_month_deals, created_at)
VALUES (
    'e90e494e-9649-4498-a7a0-6bc93c3af67a',
    'مشعل السبيعي', 'مشعل السبيعي',
    'مشعل.aff@dealix.sa', '+966551264673', '+966551264673', 'الرياض',
    'active',
    'DLX-62C798E3', 7, 1617, 5,
    NOW() - INTERVAL '21 days'
) ON CONFLICT DO NOTHING;


INSERT INTO affiliate_marketers (id, full_name, full_name_ar, email, phone, whatsapp, city, status, referral_code, total_deals_closed, total_commission_earned, current_month_deals, created_at)
VALUES (
    '5bd6c02f-f52c-4b70-ba6c-f30747ce8f99',
    'نايف القحطاني', 'نايف القحطاني',
    'نايف.aff@dealix.sa', '+966570293426', '+966570293426', 'الرياض',
    'active',
    'DLX-8537D8F9', 7, 861, 5,
    NOW() - INTERVAL '26 days'
) ON CONFLICT DO NOTHING;


INSERT INTO affiliate_marketers (id, full_name, full_name_ar, email, phone, whatsapp, city, status, referral_code, total_deals_closed, total_commission_earned, current_month_deals, created_at)
VALUES (
    '414deb57-c251-4574-941f-ef4106cdd71b',
    'أحمد البقمي', 'أحمد البقمي',
    'أحمد.aff@dealix.sa', '+966586360219', '+966586360219', 'الرياض',
    'active',
    'DLX-32E5DDEF', 15, 2850, 5,
    NOW() - INTERVAL '34 days'
) ON CONFLICT DO NOTHING;


INSERT INTO affiliate_marketers (id, full_name, full_name_ar, email, phone, whatsapp, city, status, referral_code, total_deals_closed, total_commission_earned, current_month_deals, created_at)
VALUES (
    '2c762fed-254a-4a2a-ae0a-b0894d10200d',
    'خالد العتيبي', 'خالد العتيبي',
    'خالد.aff@dealix.sa', '+966515519807', '+966515519807', 'جدة',
    'pending',
    'DLX-0520E7E1', 0, 0, 0,
    NOW() - INTERVAL '34 days'
) ON CONFLICT DO NOTHING;


INSERT INTO affiliate_marketers (id, full_name, full_name_ar, email, phone, whatsapp, city, status, referral_code, total_deals_closed, total_commission_earned, current_month_deals, created_at)
VALUES (
    '7a9f1017-901d-465a-8d83-b667b1b19f9e',
    'تركي الشمري', 'تركي الشمري',
    'تركي.aff@dealix.sa', '+966524101985', '+966524101985', 'الدمام',
    'active',
    'DLX-B41D1ABA', 9, 1386, 5,
    NOW() - INTERVAL '33 days'
) ON CONFLICT DO NOTHING;


INSERT INTO affiliate_marketers (id, full_name, full_name_ar, email, phone, whatsapp, city, status, referral_code, total_deals_closed, total_commission_earned, current_month_deals, created_at)
VALUES (
    'e8339060-2f67-43cd-9f73-13367eb40ba5',
    'فيصل العتيبي', 'فيصل العتيبي',
    'فيصل.aff@dealix.sa', '+966587231565', '+966587231565', 'مكة المكرمة',
    'active',
    'DLX-D5CE635D', 10, 1590, 5,
    NOW() - INTERVAL '51 days'
) ON CONFLICT DO NOTHING;


INSERT INTO affiliate_marketers (id, full_name, full_name_ar, email, phone, whatsapp, city, status, referral_code, total_deals_closed, total_commission_earned, current_month_deals, created_at)
VALUES (
    'b3c2de20-b672-43be-beb7-23cf2db397e5',
    'نايف الدوسري', 'نايف الدوسري',
    'نايف.aff@dealix.sa', '+966540167536', '+966540167536', 'الرياض',
    'active',
    'DLX-6443A406', 2, 144, 2,
    NOW() - INTERVAL '36 days'
) ON CONFLICT DO NOTHING;


-- ═══ Seed Summary ═══
-- Total leads: ~53
-- Total deals: 20
-- Total affiliates: 8
-- Admin: admin@dealix.sa / Dealix@2026!
