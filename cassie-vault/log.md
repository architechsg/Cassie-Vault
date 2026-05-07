# Cassie Wiki — Change Log

Append-only. Format: `## [YYYY-MM-DD] {type} | {description}`
Types: `ingest`, `query`, `lint`, `update`

---

## [2026-05-08] update | Real-world KB gaps patched from WhatsApp conversation analysis
- Source: 3 WhatsApp conversation files (Chat AB Course Conversation, Chat CT Course Conversation, Conversation) containing ~15 real customer journeys via SalesIQ → Coursemology.sg
- faq/general.md — added 4 new Q&As: (1) all courses are face-to-face only (no online option); (2) Work Permit holders can attend and receive WSQ cert, full fee applies, Gmail for e-attendance; (3) Mid-Career Enhanced SFC has separate approved course list, not all Coursemology courses qualify; (4) food safety cert renewal — refresher (not full course) at 5-year mark, then every 10 years
- company/locations.md — Toa Payoh: added "no lift, staircase only" accessibility warning
- courses/drone-media/drone-media-courses.md — Aerial Photography (#CT11): added course structure note (Day 1 theory at Toa Payoh, Days 2–4 practical at Sin Ming Open Field, trainer WhatsApp group for coordination); Video Production (#CT61): added marketing alias "Mobile Photography & Videography for Beginners"
- funding/skillsfuture-credit.md — added Mid-Career Enhanced SFC section (two credit types, how to check balance breakdown); added one.coursemology.sg personalised SFC submission portal explanation with NRIC/DOB accuracy note
- courses/cleaning/cleaning-courses.md — added Work Permit Holders section (eligible to attend, full fee, WSQ cert valid, FIN + Gmail for e-attendance)
- policies/payment-methods.md — added PayNow UENs by provider: AesthetiCar (201400645KATT), Cantley LifeCare (201703024GCCC + UOB 360-309-963-8)

## [2026-05-08] update | Post-build fixes after DB data scan + full vault review
- Added Cheque as accepted payment method (payment-methods.md)
- Fixed 4 broken wikilinks: [[courses/ms-office/microsoft-copilot]] → [[courses/ms-office/ms-office-courses]] in 3 AI Tech files; [[courses/drone-media/video-production-social-media]] → [[courses/drone-media/drone-media-courses]] in visual-content-creation-ai.md
- Full DB data scan (34 files): no new pages required; confirmed vault content matches DB

## [2026-05-08] ingest | Initial vault build from cassie_knowledge_base.md + db2_active_modules_full.json + business-logic docs
- Created all company, course, policy, funding, FAQ, and concept pages
- 65+ course pages across 12 categories
- Sources: cassie_knowledge_base.md (May 2026), db2_active_modules_full.json, business-logic extracted docs
- Added #AB51A Copilot Training Workshop (from JSON, missing from original KB)
- Added PSEA eligibility flags to relevant courses
- Deposit policy updated to reflect actual range ($20–$100+ depending on course)
